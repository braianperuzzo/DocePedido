"""Rotas e regras do carrinho da Doce Pedido."""

from decimal import Decimal

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user

from aplicacao import banco
from aplicacao.modelos import Produto
from aplicacao.servicos.cupons import (
    CODIGO_BEMVINDO,
    calcular_resumo,
    normalizar_codigo,
    validar_cupom,
)
from aplicacao.servicos.navegacao import caminho_de_referencia_seguro

carrinho = Blueprint("carrinho", __name__)
CHAVE_CARRINHO = "carrinho"
CHAVE_CUPOM = "cupom_aplicado"


def conteudo_carrinho():
    """Obtém o carrinho da sessão e descarta valores fora do formato esperado."""
    conteudo = session.get(CHAVE_CARRINHO, {})
    if not isinstance(conteudo, dict):
        return {}

    normalizado = {}
    for produto_id, quantidade in conteudo.items():
        try:
            id_numerico = int(produto_id)
            quantidade_numerica = int(quantidade)
        except (TypeError, ValueError):
            continue
        if id_numerico > 0 and quantidade_numerica > 0:
            normalizado[str(id_numerico)] = quantidade_numerica
    return normalizado


def quantidade_informada():
    """Valida a quantidade enviada pelo formulário."""
    try:
        quantidade = int(request.form.get("quantidade", ""))
    except (TypeError, ValueError):
        return None
    return quantidade if quantidade > 0 else None


def itens_e_total():
    """Resolve os produtos existentes no carrinho e calcula o subtotal atual."""
    conteudo = conteudo_carrinho()
    itens = []
    subtotal = Decimal("0.00")
    conteudo_existente = {}

    for produto_id, quantidade in conteudo.items():
        produto = banco.session.get(Produto, int(produto_id))
        if not produto:
            continue
        conteudo_existente[produto_id] = quantidade
        subtotal_item = produto.preco * quantidade
        itens.append(
            {
                "produto": produto,
                "quantidade": quantidade,
                "subtotal": subtotal_item,
            }
        )
        subtotal += subtotal_item

    if conteudo_existente != conteudo:
        if conteudo_existente:
            session[CHAVE_CARRINHO] = conteudo_existente
        else:
            session.pop(CHAVE_CARRINHO, None)

    return itens, subtotal


def resumo_valores(subtotal):
    """Aplica o cupom da sessão somente enquanto o cliente continuar elegível."""
    codigo = session.get(CHAVE_CUPOM)
    cliente = current_user if current_user.is_authenticated else None
    resumo = calcular_resumo(subtotal, codigo, cliente)
    if codigo and current_user.is_authenticated and not resumo["cupom"]:
        session.pop(CHAVE_CUPOM, None)
    return resumo


def _resposta_ajax(mensagem, status):
    """Retorna JSON para a interface assíncrona ou registra uma mensagem normal."""
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(ok=False, mensagem=mensagem), status
    flash(mensagem, "danger")
    return None


def _formatar_moeda(valor):
    """Formata valores monetários para as respostas JSON do carrinho."""
    return f"R$ {valor:.2f}".replace(".", ",")


@carrinho.app_context_processor
def disponibilizar_quantidade_carrinho():
    """Disponibiliza a quantidade total do carrinho nos templates."""
    return {"quantidade_carrinho": sum(conteudo_carrinho().values())}


@carrinho.get("/carrinho")
def visualizar():
    """Exibe itens, cupom e valores atuais do carrinho."""
    itens, subtotal = itens_e_total()
    resumo = resumo_valores(subtotal)
    return render_template(
        "carrinho/carrinho.html",
        itens=itens,
        subtotal=resumo["subtotal"],
        desconto=resumo["desconto"],
        total=resumo["total"],
        cupom=resumo["cupom"],
    )


@carrinho.post("/carrinho/cupom")
def aplicar_cupom():
    """Valida e guarda o cupom de boas-vindas na sessão do carrinho."""
    codigo = normalizar_codigo(request.form.get("cupom"))
    if codigo != CODIGO_BEMVINDO:
        session.pop(CHAVE_CUPOM, None)
        flash("Cupom não encontrado.", "danger")
        return redirect(url_for("carrinho.visualizar"))

    if not current_user.is_authenticated:
        session.pop(CHAVE_CUPOM, None)
        flash(
            "Entre na sua conta e aplique o cupom BEMVINDO para validar seu CPF.",
            "info",
        )
        return redirect(
            url_for("autenticacao.login", next=url_for("carrinho.visualizar"))
        )

    valido, mensagem = validar_cupom(codigo, current_user)
    if not valido:
        session.pop(CHAVE_CUPOM, None)
        flash(mensagem, "warning")
        return redirect(url_for("carrinho.visualizar"))

    session[CHAVE_CUPOM] = CODIGO_BEMVINDO
    flash("Cupom BEMVINDO aplicado: 10% de desconto na primeira compra.", "success")
    return redirect(url_for("carrinho.visualizar"))


@carrinho.post("/carrinho/cupom/remover")
def remover_cupom():
    """Remove o cupom salvo sem alterar os itens do carrinho."""
    session.pop(CHAVE_CUPOM, None)
    flash("Cupom removido.", "info")
    return redirect(url_for("carrinho.visualizar"))


@carrinho.post("/carrinho/adicionar/<int:produto_id>")
def adicionar(produto_id):
    """Adiciona uma quantidade válida de um produto disponível ao carrinho."""
    produto = banco.session.get(Produto, produto_id)
    quantidade = quantidade_informada()
    if not produto:
        erro = _resposta_ajax("Produto não encontrado.", 404)
    elif not produto.ativo:
        erro = _resposta_ajax("Este produto não está disponível.", 404)
    elif quantidade is None:
        erro = _resposta_ajax(
            "Informe uma quantidade inteira maior que zero.", 400
        )
    else:
        atual = conteudo_carrinho().get(str(produto_id), 0)
        nova_quantidade = atual + quantidade
        if nova_quantidade > produto.estoque:
            erro = _resposta_ajax(
                "A quantidade solicitada ultrapassa o estoque disponível.",
                422,
            )
        else:
            produtos = conteudo_carrinho().copy()
            produtos[str(produto_id)] = nova_quantidade
            session[CHAVE_CARRINHO] = produtos
            mensagem = f"{produto.nome} foi Adicionado ao Carrinho."
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify(
                    ok=True,
                    mensagem=mensagem,
                    quantidade_carrinho=sum(produtos.values()),
                )
            flash(mensagem, "success")
            erro = None
    if erro is not None:
        return erro

    destino = caminho_de_referencia_seguro(request.referrer, request.host_url)
    return redirect(destino or url_for("produtos.catalogo"))


@carrinho.post("/carrinho/atualizar/<int:produto_id>")
def atualizar(produto_id):
    """Atualiza uma quantidade sem ultrapassar o estoque disponível."""
    produto = banco.session.get(Produto, produto_id)
    quantidade = quantidade_informada()
    if not produto or not produto.ativo:
        erro = _resposta_ajax("Este produto não está disponível.", 404)
    elif quantidade is None:
        erro = _resposta_ajax(
            "Informe uma quantidade inteira maior que zero.", 400
        )
    elif quantidade > produto.estoque:
        erro = _resposta_ajax(
            "A quantidade solicitada ultrapassa o estoque disponível.", 422
        )
    elif str(produto_id) not in conteudo_carrinho():
        erro = _resposta_ajax("O produto não está no carrinho.", 404)
    else:
        produtos = conteudo_carrinho().copy()
        produtos[str(produto_id)] = quantidade
        session[CHAVE_CARRINHO] = produtos
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            itens, subtotal = itens_e_total()
            resumo = resumo_valores(subtotal)
            item_atualizado = next(
                item for item in itens if item["produto"].id == produto_id
            )
            return jsonify(
                ok=True,
                produto_id=produto_id,
                quantidade=quantidade,
                subtotal=_formatar_moeda(item_atualizado["subtotal"]),
                subtotal_carrinho=_formatar_moeda(resumo["subtotal"]),
                desconto=_formatar_moeda(resumo["desconto"]),
                total=_formatar_moeda(resumo["total"]),
                cupom=bool(resumo["cupom"]),
                quantidade_carrinho=sum(
                    item["quantidade"] for item in itens
                ),
            )
        flash("Quantidade atualizada.", "success")
        erro = None
    if erro is not None:
        return erro
    return redirect(url_for("carrinho.visualizar"))


@carrinho.post("/carrinho/remover/<int:produto_id>")
def remover(produto_id):
    """Remove um produto do carrinho da sessão."""
    produtos = conteudo_carrinho().copy()
    if produtos.pop(str(produto_id), None) is None:
        flash("O produto não está no carrinho.", "danger")
    else:
        if produtos:
            session[CHAVE_CARRINHO] = produtos
        else:
            session.pop(CHAVE_CARRINHO, None)
            session.pop(CHAVE_CUPOM, None)
        flash("Produto removido do carrinho.", "success")
    return redirect(url_for("carrinho.visualizar"))


@carrinho.post("/carrinho/esvaziar")
def esvaziar():
    """Remove todos os itens e o cupom do carrinho."""
    session.pop(CHAVE_CARRINHO, None)
    session.pop(CHAVE_CUPOM, None)
    flash("Carrinho esvaziado.", "success")
    return redirect(url_for("carrinho.visualizar"))
