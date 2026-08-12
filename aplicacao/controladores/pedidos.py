"""Rotas e regras de pedidos da Doce Pedido."""

from decimal import Decimal

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from aplicacao import banco
from aplicacao.controladores.carrinho import (
    CHAVE_CARRINHO,
    CHAVE_CUPOM,
    conteudo_carrinho,
    itens_e_total,
    resumo_valores,
)
from aplicacao.modelos import DetalhePedido, Endereco, ItemPedido, Pedido, Produto
from aplicacao.servicos.email import ErroEnvioEmail, enviar_email

pedidos = Blueprint("pedidos", __name__)

FRETE_GRATIS = Decimal("0.00")
FORMA_PAGAMENTO_ATIVA = "na_entrega"
ROTULO_PAGAMENTO_ATIVO = "Presencial"
FORMAS_RECEBIMENTO = {
    "entrega": "Entrega",
    "retirada": "Retirada na Loja",
}


def enderecos_cliente(cliente_id):
    """Lista endereços do cliente, priorizando o principal e os mais antigos."""
    return banco.session.scalars(
        banco.select(Endereco)
        .where(Endereco.cliente_id == cliente_id)
        .order_by(
            Endereco.principal.desc(),
            Endereco.criado_em.asc(),
            Endereco.id.asc(),
        )
    ).all()


def endereco_principal_cliente(cliente_id):
    """Recupera o endereço principal ou, na ausência dele, o mais antigo."""
    lista = enderecos_cliente(cliente_id)
    return lista[0] if lista else None


def endereco_cliente_por_id(cliente_id, endereco_id):
    """Obtém um endereço específico sem permitir acesso ao de outro cliente."""
    return banco.session.scalar(
        banco.select(Endereco).where(
            Endereco.id == endereco_id,
            Endereco.cliente_id == cliente_id,
        )
    )


def formatar_endereco(endereco):
    """Prepara um endereço salvo para exibição e para o registro do pedido."""
    if not endereco:
        return None

    primeira_linha = f"{endereco.logradouro}, {endereco.numero}"
    if endereco.complemento:
        primeira_linha += f" - {endereco.complemento}"

    linhas = [
        primeira_linha,
        f"{endereco.bairro} - {endereco.cidade}/{endereco.uf}",
        f"CEP {endereco.cep_formatado}",
    ]
    if endereco.referencia:
        linhas.append(f"Referência: {endereco.referencia}")

    return {
        "id": endereco.id,
        "nome": endereco.nome,
        "principal": endereco.principal,
        "linhas": linhas,
        "texto": "\n".join(linhas),
    }


def validar_itens_carrinho():
    """Revalida existência, estado e estoque dos itens antes do fechamento."""
    for produto_id, quantidade in conteudo_carrinho().items():
        produto = banco.session.get(Produto, int(produto_id))
        if not produto:
            return None, None, "Um produto do carrinho não foi encontrado."
        if not produto.ativo:
            return None, None, f"{produto.nome} não está mais disponível."
        if quantidade <= 0 or quantidade > produto.estoque:
            return None, None, f"Estoque insuficiente para {produto.nome}."

    itens, subtotal = itens_e_total()
    if not itens:
        return None, None, "Seu carrinho está vazio."
    return itens, subtotal, None


def validar_checkout():
    """Valida recebimento, endereço e pagamento sem confiar no navegador."""
    endereco_padrao = endereco_principal_cliente(current_user.id)
    tipo_padrao = "entrega" if endereco_padrao else "retirada"
    tipo_entrega = request.form.get("tipo_entrega", tipo_padrao)
    forma_pagamento = request.form.get("forma_pagamento", FORMA_PAGAMENTO_ATIVA)

    if tipo_entrega not in FORMAS_RECEBIMENTO:
        return None, None, "Escolha como deseja receber seu pedido."

    if forma_pagamento != FORMA_PAGAMENTO_ATIVA:
        return (
            None,
            None,
            "No momento, o pagamento disponível é somente presencial na entrega ou retirada.",
        )

    endereco_formatado = None
    if tipo_entrega == "entrega":
        endereco_escolhido = endereco_padrao
        endereco_id = request.form.get("endereco_id", "").strip()
        if endereco_id:
            try:
                endereco_escolhido = endereco_cliente_por_id(
                    current_user.id,
                    int(endereco_id),
                )
            except ValueError:
                endereco_escolhido = None

        endereco_formatado = formatar_endereco(endereco_escolhido)
        if not endereco_formatado:
            return (
                None,
                None,
                "Escolha um endereço válido para entrega ou retire o pedido na loja.",
            )

    return tipo_entrega, endereco_formatado, None


def url_externa(endpoint, **valores):
    """Monta links absolutos usando SITE_URL quando configurado."""
    caminho = url_for(endpoint, **valores)
    site_url = current_app.config.get("SITE_URL", "").rstrip("/")
    if site_url:
        return f"{site_url}{caminho}"
    return url_for(endpoint, _external=True, **valores)


def formatar_moeda_texto(valor):
    """Formata valores monetários para a versão textual do e-mail."""
    return f"R$ {valor:.2f}".replace(".", ",")


def enviar_confirmacao_pedido(pedido):
    """Envia ao cliente os dados do pedido já persistido."""
    detalhes = pedido.detalhes_checkout
    link_pedido = url_externa("pedidos.detalhes", pedido_id=pedido.id)
    html = render_template(
        "emails/pedido_confirmado.html",
        pedido=pedido,
        detalhes=detalhes,
        link_pedido=link_pedido,
    )

    itens_texto = "\n".join(
        (
            f"- {item.produto.nome}: {item.quantidade} × "
            f"{formatar_moeda_texto(item.valor_unitario)} = "
            f"{formatar_moeda_texto(item.subtotal)}"
        )
        for item in pedido.itens
    )
    recebimento = detalhes.tipo_entrega if detalhes else "A confirmar"
    pagamento = detalhes.forma_pagamento if detalhes else ROTULO_PAGAMENTO_ATIVO
    endereco = ""
    if detalhes and detalhes.endereco_entrega:
        endereco = f"\nEndereço:\n{detalhes.endereco_entrega}\n"

    desconto = ""
    if detalhes and detalhes.valor_desconto and detalhes.valor_desconto > 0:
        desconto = (
            f"Cupom: {detalhes.cupom_codigo}\n"
            f"Desconto: -{formatar_moeda_texto(detalhes.valor_desconto)}\n"
        )

    texto = (
        f"Olá, {pedido.cliente.nome}.\n\n"
        f"Seu pedido nº {pedido.id} foi confirmado.\n\n"
        f"{itens_texto}\n\n"
        f"Recebimento: {recebimento}\n"
        f"Pagamento: {pagamento}\n"
        "Frete: grátis\n"
        f"{desconto}"
        f"{endereco}"
        f"Total: {formatar_moeda_texto(pedido.valor_total)}\n\n"
        f"Acompanhe o pedido em: {link_pedido}"
    )
    enviar_email(
        destinatario=pedido.cliente.email,
        assunto=f"Pedido nº {pedido.id} confirmado - Doce Pedido",
        html=html,
        texto=texto,
    )


@pedidos.get("/pedidos/revisar")
def revisar():
    """Exibe a etapa final do pedido com endereço, recebimento e pagamento."""
    if not current_user.is_authenticated:
        flash(
            "Faça ogin para finalizar seu pedido. Seu carrinho foi preservado.",
            "warning",
        )
        return redirect(
            url_for("autenticacao.login", next=url_for("pedidos.revisar"))
        )

    itens, subtotal = itens_e_total()
    if not itens:
        flash("Seu carrinho está vazio.", "warning")
        return redirect(url_for("carrinho.visualizar"))

    resumo = resumo_valores(subtotal)
    lista_enderecos = [
        formatar_endereco(endereco) for endereco in enderecos_cliente(current_user.id)
    ]
    endereco = lista_enderecos[0] if lista_enderecos else None
    return render_template(
        "pedidos/revisar.html",
        itens=itens,
        subtotal=resumo["subtotal"],
        desconto=resumo["desconto"],
        total=resumo["total"],
        cupom=resumo["cupom"],
        endereco=endereco,
        enderecos=lista_enderecos,
        frete=FRETE_GRATIS,
    )


@pedidos.post("/pedidos/confirmar")
@login_required
def confirmar():
    """Confirma o pedido, registra o checkout e envia a confirmação por e-mail."""
    itens, subtotal, erro = validar_itens_carrinho()
    if erro:
        flash(erro, "danger")
        return redirect(url_for("carrinho.visualizar"))

    codigo_cupom = session.get(CHAVE_CUPOM)
    resumo = resumo_valores(subtotal)
    if codigo_cupom and not resumo["cupom"]:
        flash(
            "O cupom informado não pode mais ser aplicado a este pedido. Revise os valores.",
            "warning",
        )
        return redirect(url_for("carrinho.visualizar"))

    tipo_entrega, endereco, erro_checkout = validar_checkout()
    if erro_checkout:
        flash(erro_checkout, "warning")
        return redirect(url_for("pedidos.revisar"))

    try:
        pedido = Pedido(
            cliente_id=current_user.id,
            status="Recebido",
            valor_total=resumo["total"],
        )
        pedido.detalhes_checkout = DetalhePedido(
            tipo_entrega=FORMAS_RECEBIMENTO[tipo_entrega],
            forma_pagamento=ROTULO_PAGAMENTO_ATIVO,
            valor_frete=FRETE_GRATIS,
            cupom_codigo=resumo["cupom"],
            valor_desconto=resumo["desconto"],
            endereco_entrega=endereco["texto"] if endereco else None,
        )
        banco.session.add(pedido)

        for item in itens:
            produto = item["produto"]
            quantidade = item["quantidade"]
            subtotal_item = produto.preco * quantidade
            pedido.itens.append(
                ItemPedido(
                    produto=produto,
                    quantidade=quantidade,
                    valor_unitario=produto.preco,
                    subtotal=subtotal_item,
                )
            )
            produto.estoque -= quantidade

        banco.session.commit()
    except SQLAlchemyError:
        banco.session.rollback()
        flash("Não foi Possível registrar o pedido. Tente novamente.", "danger")
        return redirect(url_for("pedidos.revisar"))

    session.pop(CHAVE_CARRINHO, None)
    session.pop(CHAVE_CUPOM, None)

    try:
        enviar_confirmacao_pedido(pedido)
    except ErroEnvioEmail:
        flash(
            "Pedido confirmado. O e-mail de confirmação não pôde ser enviado agora.",
            "warning",
        )

    return redirect(url_for("pedidos.confirmacao", pedido_id=pedido.id))


def pedido_do_cliente(pedido_id):
    """Obtém um pedido do cliente autenticado com itens e dados do fechamento."""
    return banco.session.scalar(
        banco.select(Pedido)
        .options(
            selectinload(Pedido.itens).selectinload(ItemPedido.produto),
            selectinload(Pedido.detalhes_checkout),
        )
        .where(
            Pedido.id == pedido_id,
            Pedido.cliente_id == current_user.id,
        )
    )


@pedidos.get("/pedidos/confirmacao/<int:pedido_id>")
@login_required
def confirmacao(pedido_id):
    """Exibe a confirmação de um pedido do cliente."""
    pedido = pedido_do_cliente(pedido_id)
    if not pedido:
        flash("Pedido não encontrado.", "danger")
        return redirect(url_for("pedidos.listar"))
    return render_template("pedidos/confirmacao.html", pedido=pedido)


@pedidos.get("/pedidos")
@login_required
def listar():
    """Lista pedidos recentes com itens e dados do fechamento."""
    consulta = (
        banco.select(Pedido)
        .options(
            selectinload(Pedido.itens).selectinload(ItemPedido.produto),
            selectinload(Pedido.detalhes_checkout),
        )
        .where(Pedido.cliente_id == current_user.id)
        .order_by(Pedido.data_pedido.desc())
    )
    return render_template(
        "pedidos/lista.html",
        pedidos=banco.session.scalars(consulta).all(),
    )


@pedidos.get("/pedidos/<int:pedido_id>")
@login_required
def detalhes(pedido_id):
    """Exibe um pedido pertencente ao cliente autenticado."""
    pedido = pedido_do_cliente(pedido_id)
    if not pedido:
        flash("Pedido não encontrado.", "danger")
        return redirect(url_for("pedidos.listar"))
    return render_template("pedidos/detalhes.html", pedido=pedido)
