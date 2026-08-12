"""Endereços e favoritos disponíveis na área autenticada do cliente."""

import json
import re
import urllib.error
import urllib.request

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload

from aplicacao import banco, limitador
from aplicacao.modelos import Endereco, Favorito, Produto

recursos_conta = Blueprint("recursos_conta", __name__)
PADRAO_CEP = re.compile(r"^\d{8}$")
LIMITE_ENDERECOS = 10
NOMES_UFS = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AP": "Amapá",
    "AM": "Amazonas",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MT": "Mato Grosso",
    "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais",
    "PA": "Pará",
    "PB": "Paraíba",
    "PR": "Paraná",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul",
    "RO": "Rondônia",
    "RR": "Roraima",
    "SC": "Santa Catarina",
    "SP": "São Paulo",
    "SE": "Sergipe",
    "TO": "Tocantins",
}
UFS_BRASIL = frozenset(NOMES_UFS)


@recursos_conta.after_request
def proteger_respostas_recursos_conta(resposta):
    """Evita cache de dados pessoais e da lista privada de favoritos."""
    resposta.headers["Cache-Control"] = "no-store, private"
    resposta.headers["Pragma"] = "no-cache"
    if request.path.startswith("/minha-conta"):
        resposta.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resposta


def _normalizar_cep(valor):
    """Mantém somente os oito dígitos esperados na persistência do CEP."""
    return re.sub(r"\D", "", valor or "")


def _uf_valida(valor):
    """Confirma que a sigla pertence a uma Unidade da Federação brasileira."""
    return str(valor or "").strip().upper() in UFS_BRASIL


def _nome_endereco_em_uso(nome, endereco_id=None):
    """Verifica duplicidade de nome dentro da conta atual."""
    consulta = banco.select(Endereco).where(
        Endereco.cliente_id == current_user.id,
        func.lower(Endereco.nome) == nome.lower(),
    )
    if endereco_id is not None:
        consulta = consulta.where(Endereco.id != endereco_id)
    return banco.session.scalar(consulta) is not None


def _dados_endereco(endereco_atual=None):
    """Normaliza e valida o formulário de endereço antes de persistir."""
    dados = {
        "nome": request.form.get("nome", "").strip(),
        "cep": _normalizar_cep(request.form.get("cep", "")),
        "logradouro": request.form.get("logradouro", "").strip(),
        "numero": request.form.get("numero", "").strip(),
        "complemento": request.form.get("complemento", "").strip(),
        "bairro": request.form.get("bairro", "").strip(),
        "cidade": request.form.get("cidade", "").strip(),
        "uf": request.form.get("uf", "").strip().upper(),
        "referencia": request.form.get("referencia", "").strip(),
        "principal": request.form.get("principal") == "on",
    }
    erros = []

    limites = {
        "nome": (60, "O Apelido do Endereço deve possuir no máximo 60 caracteres."),
        "logradouro": (
            160,
            "O logradouro deve possuir no máximo 160 caracteres.",
        ),
        "numero": (20, "O número deve possuir no máximo 20 caracteres."),
        "complemento": (
            100,
            "O complemento deve possuir no máximo 100 caracteres.",
        ),
        "bairro": (100, "O bairro deve possuir no máximo 100 caracteres."),
        "cidade": (100, "A cidade deve possuir no máximo 100 caracteres."),
        "referencia": (
            180,
            "A referência deve possuir no máximo 180 caracteres.",
        ),
    }
    for campo, (limite, mensagem) in limites.items():
        if len(dados[campo]) > limite:
            erros.append(mensagem)

    if not dados["nome"]:
        erros.append(
            "Dê um nome para identificar este endereço, como Casa ou Trabalho."
        )
    elif _nome_endereco_em_uso(
        dados["nome"], endereco_atual.id if endereco_atual else None
    ):
        erros.append("Você já possui um endereço com este nome.")
    if not PADRAO_CEP.fullmatch(dados["cep"]):
        erros.append("Informe um CEP válido com 8 dígitos.")
    if not dados["logradouro"]:
        erros.append("Informe o logradouro.")
    if not dados["numero"]:
        erros.append("Informe o número do endereço.")
    if not dados["bairro"]:
        erros.append("Informe o bairro.")
    if not dados["cidade"]:
        erros.append("Informe a cidade.")
    if not _uf_valida(dados["uf"]):
        erros.append("Selecione uma UF válida.")

    return dados, erros


def _endereco_do_cliente(endereco_id):
    """Retorna um endereço somente se ele pertencer ao cliente autenticado."""
    return banco.session.scalar(
        banco.select(Endereco).where(
            Endereco.id == endereco_id,
            Endereco.cliente_id == current_user.id,
        )
    )


def _definir_principal(endereco):
    """Garante um único endereço principal para o cliente atual."""
    outros = banco.session.scalars(
        banco.select(Endereco).where(
            Endereco.cliente_id == current_user.id,
            Endereco.id != endereco.id,
            Endereco.principal.is_(True),
        )
    ).all()
    for outro in outros:
        outro.principal = False
    endereco.principal = True


def _consultar_json_https(host, caminho):
    """Consulta JSON HTTPS usando o proxy do ambiente quando ele estiver configurado."""
    requisicao = urllib.request.Request(
        f"https://{host}{caminho}",
        headers={
            "Accept": "application/json",
            "User-Agent": "DocePedido/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(requisicao, timeout=5) as resposta:  # nosec B310
            if resposta.status != 200:
                raise RuntimeError("Serviço externo indisponível")
            return json.loads(resposta.read().decode("utf-8"))
    except (
        OSError,
        ValueError,
        TimeoutError,
        urllib.error.HTTPError,
        urllib.error.URLError,
    ) as erro:
        raise RuntimeError("Falha ao consultar serviço externo") from erro


def consultar_cep_viacep(cep):
    """Consulta o ViaCEP e devolve somente os campos usados pelo formulário."""
    dados = _consultar_json_https("viacep.com.br", f"/ws/{cep}/json/")
    if not isinstance(dados, dict):
        raise TypeError("Resposta inesperada do serviço de CEP")
    if dados.get("erro") is True:
        return None

    uf = str(dados.get("uf", "")).strip().upper()
    return {
        "cep": _normalizar_cep(dados.get("cep", cep)),
        "logradouro": str(dados.get("logradouro", "")).strip(),
        "bairro": str(dados.get("bairro", "")).strip(),
        "cidade": str(dados.get("localidade", "")).strip(),
        "uf": uf if _uf_valida(uf) else "",
    }


def consultar_ufs_ibge():
    """Obtém as Unidades da Federação pela API de Localidades do IBGE."""
    dados = _consultar_json_https(
        "servicodados.ibge.gov.br",
        "/api/v1/localidades/estados?orderBy=nome",
    )
    if not isinstance(dados, list):
        raise TypeError("Resposta inesperada do serviço de localidades")

    ufs = []
    for item in dados:
        if not isinstance(item, dict):
            continue
        sigla = str(item.get("sigla", "")).strip().upper()
        nome = str(item.get("nome", "")).strip()
        if _uf_valida(sigla) and nome:
            ufs.append({"sigla": sigla, "nome": nome})
    return ufs


def consultar_municipios_ibge(uf):
    """Obtém os municípios de uma UF pela API de Localidades do IBGE."""
    if not _uf_valida(uf):
        raise RuntimeError("UF inválida")
    dados = _consultar_json_https(
        "servicodados.ibge.gov.br",
        f"/api/v1/localidades/estados/{uf}/municipios?orderBy=nome",
    )
    if not isinstance(dados, list):
        raise TypeError("Resposta inesperada do serviço de localidades")

    return [
        str(item.get("nome", "")).strip()
        for item in dados
        if isinstance(item, dict) and str(item.get("nome", "")).strip()
    ]


@recursos_conta.get("/minha-conta/enderecos")
@login_required
def enderecos():
    """Lista endereços e oferece cadastro, edição e definição do principal."""
    consulta = (
        banco.select(Endereco)
        .where(Endereco.cliente_id == current_user.id)
        .order_by(
            Endereco.principal.desc(),
            Endereco.criado_em.asc(),
            Endereco.id.asc(),
        )
    )
    lista = banco.session.scalars(consulta).all()
    return render_template("conta/enderecos.html", enderecos=lista)


@recursos_conta.post("/minha-conta/enderecos/adicionar")
@login_required
@limitador.limit("20 per hour")
def adicionar_endereco():
    """Adiciona um endereço nomeado à conta autenticada."""
    quantidade = (
        banco.session.scalar(
            banco.select(func.count(Endereco.id)).where(
                Endereco.cliente_id == current_user.id
            )
        )
        or 0
    )
    if quantidade >= LIMITE_ENDERECOS:
        flash(
            f"Você pode manter até {LIMITE_ENDERECOS} endereços salvos.",
            "warning",
        )
        return redirect(url_for("recursos_conta.enderecos"))

    dados, erros = _dados_endereco()
    if erros:
        for erro in erros:
            flash(erro, "danger")
        return redirect(url_for("recursos_conta.enderecos"))

    endereco = Endereco(
        cliente_id=current_user.id,
        nome=dados["nome"],
        cep=dados["cep"],
        logradouro=dados["logradouro"],
        numero=dados["numero"],
        complemento=dados["complemento"] or None,
        bairro=dados["bairro"],
        cidade=dados["cidade"],
        uf=dados["uf"],
        referencia=dados["referencia"] or None,
        principal=False,
    )
    banco.session.add(endereco)
    try:
        banco.session.flush()
        if quantidade == 0 or dados["principal"]:
            _definir_principal(endereco)
        banco.session.commit()
    except SQLAlchemyError:
        banco.session.rollback()
        flash(
            "Não foi Possível salvar este endereço. Revise os dados e tente novamente.",
            "danger",
        )
        return redirect(url_for("recursos_conta.enderecos"))

    flash(f"Endereço {endereco.nome} adicionado com sucesso.", "success")
    return redirect(url_for("recursos_conta.enderecos"))


@recursos_conta.post("/minha-conta/enderecos/<int:endereco_id>/editar")
@login_required
@limitador.limit("30 per hour")
def editar_endereco(endereco_id):
    """Edita somente endereços que pertencem ao cliente autenticado."""
    endereco = _endereco_do_cliente(endereco_id)
    if not endereco:
        flash("Endereço não encontrado.", "danger")
        return redirect(url_for("recursos_conta.enderecos"))

    dados, erros = _dados_endereco(endereco)
    if erros:
        for erro in erros:
            flash(erro, "danger")
        return redirect(url_for("recursos_conta.enderecos"))

    endereco.nome = dados["nome"]
    endereco.cep = dados["cep"]
    endereco.logradouro = dados["logradouro"]
    endereco.numero = dados["numero"]
    endereco.complemento = dados["complemento"] or None
    endereco.bairro = dados["bairro"]
    endereco.cidade = dados["cidade"]
    endereco.uf = dados["uf"]
    endereco.referencia = dados["referencia"] or None
    if dados["principal"] or endereco.principal:
        _definir_principal(endereco)

    try:
        banco.session.commit()
    except SQLAlchemyError:
        banco.session.rollback()
        flash("Não foi Possível atualizar este endereço.", "danger")
        return redirect(url_for("recursos_conta.enderecos"))

    flash(f"Endereço {endereco.nome} atualizado.", "success")
    return redirect(url_for("recursos_conta.enderecos"))


@recursos_conta.post("/minha-conta/enderecos/<int:endereco_id>/principal")
@login_required
def tornar_endereco_principal(endereco_id):
    """Define o endereço preferencial para uso futuro no checkout."""
    endereco = _endereco_do_cliente(endereco_id)
    if not endereco:
        flash("Endereço não encontrado.", "danger")
        return redirect(url_for("recursos_conta.enderecos"))

    _definir_principal(endereco)
    try:
        banco.session.commit()
    except SQLAlchemyError:
        banco.session.rollback()
        flash("Não foi Possível alterar o endereço principal.", "danger")
        return redirect(url_for("recursos_conta.enderecos"))

    flash(f"{endereco.nome} agora é seu endereço principal.", "success")
    return redirect(url_for("recursos_conta.enderecos"))


@recursos_conta.post("/minha-conta/enderecos/<int:endereco_id>/excluir")
@login_required
def excluir_endereco(endereco_id):
    """Remove um endereço e promove outro quando o principal é excluído."""
    endereco = _endereco_do_cliente(endereco_id)
    if not endereco:
        flash("Endereço não encontrado.", "danger")
        return redirect(url_for("recursos_conta.enderecos"))

    era_principal = endereco.principal
    nome = endereco.nome
    try:
        banco.session.delete(endereco)
        banco.session.flush()
        if era_principal:
            substituto = banco.session.scalar(
                banco.select(Endereco)
                .where(Endereco.cliente_id == current_user.id)
                .order_by(Endereco.criado_em.asc(), Endereco.id.asc())
                .limit(1)
            )
            if substituto:
                substituto.principal = True
        banco.session.commit()
    except SQLAlchemyError:
        banco.session.rollback()
        flash("Não foi Possível remover este endereço.", "danger")
        return redirect(url_for("recursos_conta.enderecos"))

    flash(f"Endereço {nome} removido.", "success")
    return redirect(url_for("recursos_conta.enderecos"))


@recursos_conta.get("/api/cep/<cep>")
@login_required
@limitador.limit("30 per minute")
def consultar_cep(cep):
    """Oferece consulta de mesma origem para preencher o formulário de endereço."""
    cep_normalizado = _normalizar_cep(cep)
    if not PADRAO_CEP.fullmatch(cep_normalizado):
        return jsonify({"erro": "Informe um CEP com 8 dígitos."}), 400
    try:
        dados = consultar_cep_viacep(cep_normalizado)
    except RuntimeError:
        return (
            jsonify(
                {
                    "erro": (
                        "Não foi Possível consultar o CEP agora. "
                        "Preencha o endereço manualmente."
                    )
                }
            ),
            502,
        )
    if not dados:
        return jsonify({"erro": "CEP não encontrado."}), 404
    return jsonify(dados)


@recursos_conta.get("/api/localidades/ufs")
@login_required
@limitador.limit("30 per minute")
def listar_ufs():
    """Retorna UFs e usa uma lista local quando o IBGE estiver indisponível."""
    try:
        return jsonify(consultar_ufs_ibge())
    except RuntimeError:
        return jsonify(
            [
                {"sigla": sigla, "nome": nome}
                for sigla, nome in sorted(NOMES_UFS.items(), key=lambda item: item[1])
            ]
        )


@recursos_conta.get("/api/localidades/ufs/<uf>/municipios")
@login_required
@limitador.limit("60 per minute")
def listar_municipios(uf):
    """Retorna os municípios somente quando a UF informada é válida."""
    uf_normalizada = uf.strip().upper()
    if not _uf_valida(uf_normalizada):
        return jsonify({"erro": "UF inválida."}), 400
    try:
        return jsonify(consultar_municipios_ibge(uf_normalizada))
    except RuntimeError:
        # A UF continua válida mesmo que o serviço externo esteja temporariamente fora.
        # O frontend orienta o preenchimento por CEP sem exibir um erro de servidor.
        return jsonify([])


@recursos_conta.get("/minha-conta/favoritos")
@login_required
def favoritos():
    """Lista cupcakes favoritos, do mais recente para o mais antigo."""
    consulta = (
        banco.select(Produto)
        .join(Favorito, Favorito.produto_id == Produto.id)
        .options(selectinload(Produto.categoria))
        .where(
            Favorito.cliente_id == current_user.id,
            Produto.ativo.is_(True),
        )
        .order_by(Favorito.criado_em.desc(), Favorito.id.desc())
    )
    produtos = banco.session.scalars(consulta).unique().all()
    return render_template("conta/favoritos.html", produtos=produtos)


@recursos_conta.get("/favoritos/status")
def status_favoritos():
    """Retorna o estado para os botões de coração em qualquer página."""
    if not current_user.is_authenticated:
        return jsonify({"autenticado": False, "favoritos": []})
    ids = banco.session.scalars(
        banco.select(Favorito.produto_id).where(
            Favorito.cliente_id == current_user.id
        )
    ).all()
    return jsonify({"autenticado": True, "favoritos": ids})


@recursos_conta.post("/favoritos/<int:produto_id>/alternar")
@login_required
@limitador.limit("60 per minute")
def alternar_favorito(produto_id):
    """Adiciona ou remove um produto dos favoritos do cliente."""
    favorito = banco.session.scalar(
        banco.select(Favorito).where(
            Favorito.cliente_id == current_user.id,
            Favorito.produto_id == produto_id,
        )
    )
    favoritado = False
    if favorito:
        banco.session.delete(favorito)
    else:
        produto = banco.session.get(Produto, produto_id)
        if not produto or not produto.ativo:
            return jsonify({"erro": "Produto indisponível."}), 404
        banco.session.add(
            Favorito(cliente_id=current_user.id, produto_id=produto_id)
        )
        favoritado = True

    try:
        banco.session.commit()
    except SQLAlchemyError:
        banco.session.rollback()
        return jsonify({"erro": "Não foi Possível atualizar seus favoritos."}), 409

    mensagem = (
        "Adicionado aos Favoritos."
        if favoritado
        else "Removido dos favoritos."
    )
    if request.headers.get("X-Requested-With") == "fetch":
        return jsonify(
            {
                "sucesso": True,
                "favoritado": favoritado,
                "produto_id": produto_id,
                "mensagem": mensagem,
            }
        )
    flash(mensagem, "success")
    return redirect(url_for("recursos_conta.favoritos"))
