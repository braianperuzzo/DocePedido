"""Dados pessoais, senha e exclusão da conta do cliente autenticado."""

import json
import re
import secrets
from datetime import timedelta
from hashlib import sha256

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, logout_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from aplicacao import banco, limitador
from aplicacao.controladores.autenticacao import (
    autenticar_cliente,
    cliente_por_email,
    validar_regras_senha,
)
from aplicacao.modelos import (
    AlteracaoConta,
    Cliente,
    DispositivoConfiavel,
    Endereco,
    Favorito,
    Pedido,
    SegurancaConta,
)
from aplicacao.modelos.alteracao_conta import agora_utc
from aplicacao.servicos.email import ErroEnvioEmail, enviar_email

conta = Blueprint("conta", __name__)
PADRAO_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PADRAO_CELULAR = re.compile(r"^[1-9]{2}9\d{8}$")


@conta.after_request
def proteger_respostas_conta(resposta):
    """Evita cache e indexação das páginas com dados pessoais."""
    resposta.headers["Cache-Control"] = "no-store, private"
    resposta.headers["Pragma"] = "no-cache"
    resposta.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resposta


def formatar_cpf(cpf):
    """Formata CPF somente para exibição, sem alterar o valor persistido."""
    numeros = re.sub(r"\D", "", cpf or "")
    if len(numeros) != 11:
        return "Não informado"
    return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"


def normalizar_telefone(telefone):
    """Mantém somente os dígitos do celular informado."""
    return re.sub(r"\D", "", telefone or "")


def formatar_telefone(telefone):
    """Formata um celular brasileiro para exibição na conta."""
    numeros = normalizar_telefone(telefone)
    if not PADRAO_CELULAR.fullmatch(numeros):
        return "Não informado"
    return f"({numeros[:2]}) {numeros[2:7]}.{numeros[7:]}"


def fingerprint_senha(cliente):
    """Vincula uma solicitação ao estado atual da senha do cliente."""
    return sha256(cliente.senha_hash.encode("utf-8")).hexdigest()


def hash_token(token):
    """Gera o hash persistido do token enviado por e-mail."""
    return sha256(token.encode("utf-8")).hexdigest()


def url_externa(endpoint, **valores):
    """Monta um link absoluto usando SITE_URL quando estiver configurado."""
    caminho = url_for(endpoint, **valores)
    site_url = current_app.config.get("SITE_URL", "").rstrip("/")
    if site_url:
        return f"{site_url}{caminho}"
    return url_for(endpoint, _external=True, **valores)


def criar_alteracao(cliente, tipo, dados=None, senha_hash_nova=None):
    """Cria uma solicitação e invalida outra pendência do mesmo tipo."""
    pendencias = banco.session.scalars(
        banco.select(AlteracaoConta).where(
            AlteracaoConta.cliente_id == cliente.id,
            AlteracaoConta.tipo == tipo,
            AlteracaoConta.concluida_em.is_(None),
        )
    ).all()
    for pendencia in pendencias:
        banco.session.delete(pendencia)

    token = secrets.token_urlsafe(32)
    ttl = int(current_app.config.get("ACCOUNT_CHANGE_TOKEN_TTL", 86400))
    alteracao = AlteracaoConta(
        cliente_id=cliente.id,
        tipo=tipo,
        token_hash=hash_token(token),
        senha_fingerprint=fingerprint_senha(cliente),
        dados_json=json.dumps(dados or {}, ensure_ascii=False),
        senha_hash_nova=senha_hash_nova,
        expira_em=agora_utc() + timedelta(seconds=max(ttl, 60)),
    )
    banco.session.add(alteracao)
    banco.session.flush()
    return alteracao, token


def enviar_confirmacao(cliente, token, tipo, alteracoes):
    """Envia a confirmação antes de aplicar alterações cadastrais ou de senha."""
    link = url_externa("conta.confirmar", token=token)
    html = render_template(
        "emails/confirmacao_alteracao_conta.html",
        nome=cliente.nome,
        link=link,
        tipo=tipo,
        alteracoes=alteracoes,
    )
    detalhes = "\n".join(
        f"- {item['rotulo']}: {item['anterior']} -> {item['novo']}"
        for item in alteracoes
    )
    texto = (
        f"Olá, {cliente.nome}.\n\n"
        "Recebemos uma solicitação de alteração na sua conta Doce Pedido.\n\n"
        f"{detalhes}\n\n"
        f"Confirme a alteração acessando: {link}\n\n"
        "Se você não solicitou esta mudança, ignore esta mensagem."
    )
    enviar_email(
        destinatario=cliente.email,
        assunto="Confirme a alteração da sua conta - Doce Pedido",
        html=html,
        texto=texto,
    )


def enviar_confirmacao_exclusao(cliente, token):
    """Envia o link que autoriza a exclusão definitiva da conta."""
    link = url_externa("conta.confirmar", token=token)
    html = render_template(
        "emails/confirmacao_exclusao_conta.html",
        nome=cliente.nome,
        link=link,
    )
    texto = (
        f"Olá, {cliente.nome}.\n\n"
        "Recebemos uma solicitação para excluir sua conta Doce Pedido.\n\n"
        "A conta ainda não foi excluída. Para confirmar a exclusão definitiva, "
        f"acesse: {link}\n\n"
        "Se você não solicitou a exclusão, ignore este e-mail e sua conta "
        "permanecerá ativa."
    )
    enviar_email(
        destinatario=cliente.email,
        assunto="Confirme a exclusão da sua conta - Doce Pedido",
        html=html,
        texto=texto,
    )


def validar_dados_perfil(cliente):
    """Normaliza campos editáveis e retorna erros e diferenças solicitadas."""
    telefone_informado = normalizar_telefone(request.form.get("telefone", ""))
    dados = {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip().lower(),
        "telefone": telefone_informado,
    }
    erros = []

    if not dados["nome"]:
        erros.append("Informe seu nome.")
    elif len(dados["nome"]) > 120:
        erros.append("O nome deve possuir no máximo 120 caracteres.")

    if not dados["email"] or not PADRAO_EMAIL.match(dados["email"]):
        erros.append("Informe um e-mail válido.")
    elif len(dados["email"]) > 255:
        erros.append("O e-mail informado é muito longo.")
    elif dados["email"] != cliente.email:
        existente = cliente_por_email(dados["email"])
        if existente and existente.id != cliente.id:
            erros.append("Este e-mail já está vinculado a outra conta.")

    if dados["telefone"] and not PADRAO_CELULAR.fullmatch(dados["telefone"]):
        erros.append("Informe um celular com DDD no formato (XX) XXXXX.XXXX.")

    diferencas = []
    comparacoes = (
        ("Nome", cliente.nome, dados["nome"]),
        ("E-mail", cliente.email, dados["email"]),
        (
            "Celular",
            formatar_telefone(cliente.telefone),
            formatar_telefone(dados["telefone"]),
        ),
    )
    for rotulo, anterior, novo in comparacoes:
        if anterior != novo:
            diferencas.append(
                {"rotulo": rotulo, "anterior": anterior, "novo": novo}
            )

    return erros, dados, diferencas


@conta.get("/minha-conta")
@login_required
def perfil():
    """Exibe os dados e as ações disponíveis na conta do cliente."""
    return render_template(
        "conta/perfil.html",
        cpf_formatado=formatar_cpf(current_user.cpf),
        telefone_formatado=formatar_telefone(current_user.telefone),
    )


@conta.post("/minha-conta/dados")
@login_required
@limitador.limit("5 per hour")
def solicitar_dados():
    """Solicita uma atualização cadastral condicionada à confirmação por e-mail."""
    senha_atual = request.form.get("senha_atual", "")
    if not current_user.verificar_senha(senha_atual):
        flash("Senha Atual incorreta. Nenhuma alteração foi realizada.", "danger")
        return redirect(url_for("conta.perfil"))

    erros, dados, diferencas = validar_dados_perfil(current_user)
    if erros:
        for erro in erros:
            flash(erro, "danger")
        return redirect(url_for("conta.perfil"))
    if not diferencas:
        flash("Nenhuma alteração foi identificada nos seus dados.", "info")
        return redirect(url_for("conta.perfil"))

    try:
        _, token = criar_alteracao(current_user, "dados", dados=dados)
        enviar_confirmacao(current_user, token, "dados", diferencas)
        banco.session.commit()
    except ErroEnvioEmail:
        banco.session.rollback()
        flash(
            "Não foi Possível enviar o e-mail de confirmação agora. Tente novamente.",
            "danger",
        )
        return redirect(url_for("conta.perfil"))
    except SQLAlchemyError:
        banco.session.rollback()
        flash("Não foi Possível registrar a solicitação. Tente novamente.", "danger")
        return redirect(url_for("conta.perfil"))

    flash(
        "Enviamos um e-mail para confirmar a atualização. Seus dados só serão "
        "alterados depois da confirmação.",
        "success",
    )
    return redirect(url_for("conta.perfil"))


@conta.post("/minha-conta/senha")
@login_required
@limitador.limit("5 per hour")
def solicitar_senha():
    """Solicita troca de senha sem aplicar a nova credencial antes do e-mail."""
    senha_atual = request.form.get("senha_atual", "")
    nova_senha = request.form.get("nova_senha", "")
    confirmacao = request.form.get("confirmacao_nova_senha", "")

    if not current_user.verificar_senha(senha_atual):
        flash("Senha Atual incorreta. Nenhuma alteração foi realizada.", "danger")
        return redirect(url_for("conta.perfil"))

    erros = validar_regras_senha(nova_senha, confirmacao)
    if current_user.verificar_senha(nova_senha):
        erros.append("A nova senha deve ser diferente da Senha Atual.")
    if erros:
        for erro in erros:
            flash(erro, "danger")
        return redirect(url_for("conta.perfil"))

    alteracoes = [
        {"rotulo": "Senha", "anterior": "••••••••", "novo": "••••••••"}
    ]
    try:
        _, token = criar_alteracao(
            current_user,
            "senha",
            senha_hash_nova=generate_password_hash(nova_senha),
        )
        enviar_confirmacao(current_user, token, "senha", alteracoes)
        banco.session.commit()
    except ErroEnvioEmail:
        banco.session.rollback()
        flash(
            "Não foi Possível enviar o e-mail de confirmação agora. Tente novamente.",
            "danger",
        )
        return redirect(url_for("conta.perfil"))
    except SQLAlchemyError:
        banco.session.rollback()
        flash("Não foi Possível registrar a solicitação. Tente novamente.", "danger")
        return redirect(url_for("conta.perfil"))

    flash(
        "Enviamos um e-mail para confirmar a nova senha. A Senha Atual continua "
        "válida até você confirmar.",
        "success",
    )
    return redirect(url_for("conta.perfil"))


@conta.post("/minha-conta/excluir")
@login_required
@limitador.limit("3 per hour")
def solicitar_exclusao():
    """Solicita exclusão definitiva sem remover dados antes da confirmação."""
    try:
        _, token = criar_alteracao(current_user, "exclusao")
        enviar_confirmacao_exclusao(current_user, token)
        banco.session.commit()
    except ErroEnvioEmail:
        banco.session.rollback()
        flash(
            "Não foi Possível enviar o e-mail de confirmação agora. Tente novamente.",
            "danger",
        )
        return redirect(url_for("conta.perfil"))
    except SQLAlchemyError:
        banco.session.rollback()
        flash("Não foi Possível registrar a solicitação. Tente novamente.", "danger")
        return redirect(url_for("conta.perfil"))

    flash(
        "Enviamos um e-mail para confirmar a exclusão. Sua conta continua ativa "
        "até você confirmar pelo link recebido.",
        "warning",
    )
    return redirect(url_for("conta.perfil"))


def conflito_dados(cliente, dados):
    """Revalida o e-mail no momento da confirmação da alteração."""
    email = dados.get("email")
    existente_email = cliente_por_email(email) if email else None
    if existente_email and existente_email.id != cliente.id:
        return "O e-mail solicitado passou a estar em uso por outra conta."
    return None


def excluir_cliente_definitivamente(cliente):
    """Remove a conta e todos os registros que dependem diretamente dela."""
    pedidos = banco.session.scalars(
        banco.select(Pedido).where(Pedido.cliente_id == cliente.id)
    ).all()
    for pedido in pedidos:
        banco.session.delete(pedido)

    modelos_dependentes = (
        Endereco,
        Favorito,
        DispositivoConfiavel,
        SegurancaConta,
        AlteracaoConta,
    )
    for modelo in modelos_dependentes:
        registros = banco.session.scalars(
            banco.select(modelo).where(modelo.cliente_id == cliente.id)
        ).all()
        for registro in registros:
            banco.session.delete(registro)

    banco.session.delete(cliente)


def destino_conta_ou_login():
    """Escolhe o destino adequado quando um link não pode ser confirmado."""
    if current_user.is_authenticated:
        return "conta.perfil"
    return "autenticacao.login"


@conta.get("/minha-conta/confirmar/<token>")
def confirmar(token):
    """Aplica uma alteração pendente ou exclui a conta após confirmação por e-mail."""
    alteracao = banco.session.scalar(
        banco.select(AlteracaoConta).where(
            AlteracaoConta.token_hash == hash_token(token)
        )
    )
    if not alteracao:
        flash("Link de confirmação inválido.", "danger")
        return redirect(url_for(destino_conta_ou_login()))

    cliente = banco.session.get(Cliente, alteracao.cliente_id)
    if alteracao.concluida_em:
        if cliente and cliente.ativo:
            autenticar_cliente(cliente)
        flash("Esta alteração já foi confirmada.", "info")
        return redirect(url_for("conta.perfil" if cliente else "autenticacao.login"))

    if alteracao.expira_em < agora_utc():
        flash(
            "Este link de confirmação expirou. Solicite a alteração novamente.",
            "warning",
        )
        return redirect(url_for(destino_conta_ou_login()))

    if not cliente or not cliente.ativo:
        flash("Não foi Possível confirmar esta alteração.", "danger")
        return redirect(url_for("autenticacao.login"))

    if fingerprint_senha(cliente) != alteracao.senha_fingerprint:
        autenticar_cliente(cliente)
        flash(
            "Este link não é mais válido porque a segurança da conta foi alterada.",
            "warning",
        )
        return redirect(url_for("conta.perfil"))

    if alteracao.tipo == "exclusao":
        try:
            excluir_cliente_definitivamente(cliente)
            banco.session.commit()
        except SQLAlchemyError:
            banco.session.rollback()
            flash("Não foi Possível excluir a conta. Tente novamente.", "danger")
            return redirect(url_for("conta.perfil"))

        logout_user()
        flash("Sua conta foi excluída com sucesso.", "success")
        return redirect(url_for("pagina_inicial.inicio"))

    if alteracao.tipo == "dados":
        dados = json.loads(alteracao.dados_json or "{}")
        conflito = conflito_dados(cliente, dados)
        if conflito:
            autenticar_cliente(cliente)
            flash(conflito, "danger")
            return redirect(url_for("conta.perfil"))
        cliente.nome = dados.get("nome", cliente.nome)
        cliente.email = dados.get("email", cliente.email)
        cliente.telefone = dados.get("telefone") or None
        mensagem = "Dados atualizados e confirmados com sucesso."
    elif alteracao.tipo == "senha" and alteracao.senha_hash_nova:
        cliente.senha_hash = alteracao.senha_hash_nova
        mensagem = "Senha Atualizada e confirmada com sucesso."
    else:
        flash("Não foi Possível interpretar esta alteração.", "danger")
        return redirect(url_for("autenticacao.login"))

    alteracao.concluida_em = agora_utc()
    try:
        banco.session.commit()
    except SQLAlchemyError:
        banco.session.rollback()
        flash("Não foi Possível aplicar a alteração. Tente novamente.", "danger")
        return redirect(url_for("autenticacao.login"))

    autenticar_cliente(cliente)
    flash(mensagem, "success")
    return redirect(url_for("conta.perfil"))
