"""Rotação periódica de senha e validação de dispositivos da Doce Pedido."""

import hmac
import os
import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from urllib.parse import urlsplit

from flask import (
    Blueprint,
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, logout_user

from aplicacao import banco, limitador
from aplicacao.controladores.autenticacao import CHAVE_INICIO_AUTENTICACAO
from aplicacao.modelos import Cliente, DispositivoConfiavel, SegurancaConta
from aplicacao.servicos.email import ErroEnvioEmail, enviar_email
from aplicacao.servicos.tokens import fingerprint_senha

seguranca_conta = Blueprint("seguranca_conta", __name__)

CHAVE_DESAFIO_DISPOSITIVO = "desafio_dispositivo"
CHAVE_DESTINO_SEGURANCA = "destino_pos_seguranca"
CHAVE_CLIENTE_PENDENTE = "seguranca_cliente_pendente"
CHAVE_LEMBRAR_PENDENTE = "seguranca_lembrar_pendente"
PADRAO_CODIGO_DISPOSITIVO = re.compile(r"^\d{6}$")


def _config_bool(nome, padrao):
    """Lê flags da configuração Flask ou do ambiente."""
    if nome in current_app.config:
        valor = current_app.config[nome]
        if isinstance(valor, str):
            return valor.strip().lower() in {"1", "true", "yes", "on"}
        return bool(valor)
    if current_app.testing and nome in {
        "PASSWORD_ROTATION_ENABLED",
        "DEVICE_VALIDATION_ENABLED",
    }:
        return False
    valor = os.environ.get(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "yes", "on"}


def _config_int(nome, padrao, minimo=1):
    """Lê valores inteiros de segurança com um limite mínimo."""
    valor = current_app.config.get(nome, os.environ.get(nome, padrao))
    try:
        return max(minimo, int(valor))
    except (TypeError, ValueError):
        return max(minimo, int(padrao))


def _config_texto(nome, padrao):
    valor = current_app.config.get(nome, os.environ.get(nome, padrao))
    return str(valor).strip() or padrao


def _agora_utc():
    return datetime.now(timezone.utc)


def _normalizar_data_utc(valor):
    if valor is None:
        return None
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


def _inicio_autenticacao():
    """Lê o instante absoluto em que as credenciais iniciaram a autenticação."""
    valor = session.get(CHAVE_INICIO_AUTENTICACAO)
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _garantir_inicio_autenticacao():
    """Registra o início uma única vez e o preserva durante etapas de segurança."""
    inicio = _inicio_autenticacao()
    if inicio is None:
        inicio = int(time.time())
        session[CHAVE_INICIO_AUTENTICACAO] = inicio
    return inicio


def _sessao_autenticada_expirou():
    """Verifica o limite absoluto sem renová-lo com a atividade do usuário."""
    inicio = _inicio_autenticacao()
    if inicio is None:
        if session.get("_fresh") is False:
            return True
        _garantir_inicio_autenticacao()
        return False

    dias = _config_int("AUTH_SESSION_MAX_AGE_DAYS", 7)
    return int(time.time()) >= inicio + (dias * 86400)


def _encerrar_sessao_expirada():
    """Remove autenticação vencida e mantém somente o carrinho do visitante."""
    carrinho_atual = session.get("carrinho")
    logout_user()
    session.clear()
    session["_remember"] = "clear"
    if carrinho_atual:
        session["carrinho"] = carrinho_atual
    flash("Sua sessão expirou por segurança. Faça login novamente.", "warning")
    return redirect(url_for("autenticacao.login"))


def _sincronizar_estado_senha(cliente):
    """Mantém a data da senha coerente inclusive com resets feitos por outras rotas."""
    fingerprint = fingerprint_senha(cliente)
    estado = banco.session.get(SegurancaConta, cliente.id)

    if estado is None:
        referencia = _normalizar_data_utc(cliente.data_cadastro) or _agora_utc()
        estado = SegurancaConta(
            cliente_id=cliente.id,
            senha_alterada_em=referencia,
            senha_fingerprint=fingerprint,
        )
        banco.session.add(estado)
        banco.session.commit()
        return estado

    if not estado.senha_fingerprint:
        estado.senha_fingerprint = fingerprint
        banco.session.commit()
    elif not hmac.compare_digest(estado.senha_fingerprint, fingerprint):
        estado.senha_fingerprint = fingerprint
        estado.senha_alterada_em = _agora_utc()
        banco.session.commit()

    return estado


def registrar_alteracao_senha(cliente):
    """Atualiza imediatamente a referência da rotação após uma troca de senha."""
    estado = banco.session.get(SegurancaConta, cliente.id)
    if estado is None:
        estado = SegurancaConta(cliente_id=cliente.id)
        banco.session.add(estado)
    estado.senha_alterada_em = _agora_utc()
    estado.senha_fingerprint = fingerprint_senha(cliente)
    return estado


def senha_precisa_ser_trocada(cliente):
    """Retorna True quando a senha alcançou o prazo configurado."""
    if not _config_bool("PASSWORD_ROTATION_ENABLED", True):
        return False

    estado = _sincronizar_estado_senha(cliente)
    referencia = _normalizar_data_utc(estado.senha_alterada_em)
    if referencia is None:
        return True

    dias = _config_int("PASSWORD_MAX_AGE_DAYS", 180)
    return _agora_utc() >= referencia + timedelta(days=dias)


def _hash_token_dispositivo(token):
    return sha256(token.encode("utf-8")).hexdigest()


def dispositivo_esta_validado(cliente):
    """Confere se o navegador possui um token confiável ainda vigente."""
    if not _config_bool("DEVICE_VALIDATION_ENABLED", True):
        return True

    nome_cookie = _config_texto("DEVICE_COOKIE_NAME", "doce_pedido_dispositivo")
    token = request.cookies.get(nome_cookie, "").strip()
    if not token:
        return False

    dispositivo = banco.session.scalar(
        banco.select(DispositivoConfiavel).where(
            DispositivoConfiavel.cliente_id == cliente.id,
            DispositivoConfiavel.token_hash == _hash_token_dispositivo(token),
        )
    )
    if not dispositivo:
        return False

    expira_em = _normalizar_data_utc(dispositivo.expira_em)
    return bool(expira_em and expira_em > _agora_utc())


def _destino_seguro(valor):
    if not valor:
        return None
    valor = str(valor).strip()
    partes = urlsplit(valor)
    if partes.scheme or partes.netloc or not valor.startswith("/") or valor.startswith("//"):
        return None
    if valor.startswith(
        (
            "/service-worker.js",
            "/manifest.webmanifest",
            "/site.webmanifest",
            "/robots.txt",
            "/sitemap.xml",
            "/static/",
        )
    ):
        return None
    return valor


def _destino_requisicao_atual():
    if request.method != "GET" or request.path == "/":
        return None
    return _destino_seguro(request.full_path.rstrip("?"))


def _destino_final():
    destino = _destino_seguro(session.pop(CHAVE_DESTINO_SEGURANCA, None))
    return destino or url_for("pagina_inicial.inicio")


def _cliente_pendente():
    cliente_id = session.get(CHAVE_CLIENTE_PENDENTE)
    try:
        cliente_id = int(cliente_id)
    except (TypeError, ValueError):
        return None
    return banco.session.get(Cliente, cliente_id)


def _cliente_em_fluxo():
    if current_user.is_authenticated:
        return current_user
    return _cliente_pendente()


def _fluxo_pendente_do_cliente(cliente):
    pendente = _cliente_pendente()
    return bool(pendente and pendente.id == cliente.id)


def _iniciar_fluxo_pendente(cliente, lembrar=False, destino=None):
    """Guarda somente o mínimo necessário sem autenticar o cliente."""
    carrinho_atual = session.get("carrinho")
    inicio_autenticacao = _garantir_inicio_autenticacao()
    limpar_remember = current_user.is_authenticated
    if limpar_remember:
        logout_user()

    session.clear()
    if limpar_remember:
        session["_remember"] = "clear"
    if carrinho_atual:
        session["carrinho"] = carrinho_atual

    session[CHAVE_INICIO_AUTENTICACAO] = inicio_autenticacao
    session[CHAVE_CLIENTE_PENDENTE] = cliente.id
    session[CHAVE_LEMBRAR_PENDENTE] = bool(lembrar)
    destino = _destino_seguro(destino)
    if destino:
        session[CHAVE_DESTINO_SEGURANCA] = destino


def iniciar_login_seguro(cliente, lembrar=False, destino=None):
    """Inicia etapas obrigatórias e só autentica quando todas terminarem."""
    _garantir_inicio_autenticacao()
    precisa_senha = senha_precisa_ser_trocada(cliente)
    precisa_dispositivo = not dispositivo_esta_validado(cliente)
    if not precisa_senha and not precisa_dispositivo:
        return None

    _iniciar_fluxo_pendente(cliente, lembrar=lembrar, destino=destino)
    if precisa_senha:
        return redirect(url_for("seguranca_conta.senha_expirada"))
    return redirect(url_for("seguranca_conta.validar_dispositivo"))


def _finalizar_login_pendente(cliente):
    """Cria a sessão autenticada somente depois de todas as validações."""
    if not _fluxo_pendente_do_cliente(cliente):
        return _destino_final()

    lembrar = bool(session.get(CHAVE_LEMBRAR_PENDENTE, False))
    destino = _destino_final()
    from aplicacao.controladores.autenticacao import autenticar_cliente

    autenticar_cliente(cliente, lembrar=lembrar)
    flash(f"Bem-vindo, {cliente.nome}!", "success")
    return destino


def _gerar_codigo_dispositivo():
    return f"{secrets.randbelow(1_000_000):06d}"


def _assinatura_codigo_dispositivo(cliente, codigo):
    segredo = str(current_app.config["SECRET_KEY"]).encode("utf-8")
    conteudo = f"{cliente.id}:{codigo}".encode()
    return hmac.new(segredo, conteudo, sha256).hexdigest()


def _desafio_dispositivo_ativo(cliente):
    desafio = session.get(CHAVE_DESAFIO_DISPOSITIVO)
    if not isinstance(desafio, dict):
        return False
    return (
        desafio.get("cliente_id") == cliente.id
        and desafio.get("expira_em", 0) > int(time.time())
        and bool(desafio.get("assinatura"))
    )


def _codigo_dispositivo_valido(cliente, codigo):
    desafio = session.get(CHAVE_DESAFIO_DISPOSITIVO)
    if not _desafio_dispositivo_ativo(cliente) or not isinstance(desafio, dict):
        return False
    esperado = desafio.get("assinatura", "")
    recebido = _assinatura_codigo_dispositivo(cliente, codigo)
    return hmac.compare_digest(esperado, recebido)


def enviar_email_codigo_dispositivo(cliente, codigo):
    """Envia o código temporário de aprovação do navegador."""
    minutos = max(1, _config_int("DEVICE_CODE_TTL", 600) // 60)
    html = render_template(
        "emails/codigo_dispositivo.html",
        nome=cliente.nome,
        codigo=codigo,
        minutos=minutos,
    )
    texto = (
        f"Olá, {cliente.nome}.\n\n"
        f"Seu código de acesso à Doce Pedido é: {codigo}\n\n"
        f"Ele expira em {minutos} minutos. "
        "Se você não tentou acessar sua conta, ignore este e-mail."
    )
    enviar_email(
        destinatario=cliente.email,
        assunto="Código de Acesso - Doce Pedido",
        html=html,
        texto=texto,
    )


def enviar_email_senha_atualizada(cliente):
    """Notifica a conclusão da troca periódica da senha."""
    html = render_template("emails/senha_atualizada.html", nome=cliente.nome)
    texto = (
        f"Olá, {cliente.nome}.\n\n"
        "A senha da sua conta Doce Pedido foi atualizada com sucesso.\n\n"
        "Se você não realizou esta alteração, use a opção Esqueceu a Senha "
        "para recuperar sua conta."
    )
    enviar_email(
        destinatario=cliente.email,
        assunto="Senha Atualizada - Doce Pedido",
        html=html,
        texto=texto,
    )


def _iniciar_desafio_dispositivo(cliente, forcar=False):
    """Gera e envia um novo código quando necessário."""
    if not forcar and _desafio_dispositivo_ativo(cliente):
        return False

    codigo = _gerar_codigo_dispositivo()
    enviar_email_codigo_dispositivo(cliente, codigo)
    session[CHAVE_DESAFIO_DISPOSITIVO] = {
        "cliente_id": cliente.id,
        "assinatura": _assinatura_codigo_dispositivo(cliente, codigo),
        "expira_em": int(time.time()) + _config_int("DEVICE_CODE_TTL", 600),
    }
    return True


def _registrar_dispositivo_confiavel(cliente):
    """Persiste somente o hash de um token aleatório entregue em cookie HttpOnly."""
    token = secrets.token_urlsafe(32)
    agora = _agora_utc()
    dias = _config_int("DEVICE_TRUST_DAYS", 30)
    banco.session.add(
        DispositivoConfiavel(
            cliente_id=cliente.id,
            token_hash=_hash_token_dispositivo(token),
            user_agent=request.headers.get("User-Agent", "")[:255] or None,
            criado_em=agora,
            expira_em=agora + timedelta(days=dias),
        )
    )
    banco.session.commit()
    session.pop(CHAVE_DESAFIO_DISPOSITIVO, None)
    return token, dias


def _aplicar_cookie_dispositivo(resposta, token, dias):
    resposta.set_cookie(
        _config_texto("DEVICE_COOKIE_NAME", "doce_pedido_dispositivo"),
        token,
        max_age=dias * 86400,
        httponly=True,
        secure=bool(current_app.config.get("AMBIENTE_PRODUCAO", False)),
        samesite="Lax",
        path="/",
    )
    return resposta


def _proximo_passo(cliente):
    if senha_precisa_ser_trocada(cliente):
        return redirect(url_for("seguranca_conta.senha_expirada"))
    if not dispositivo_esta_validado(cliente):
        return redirect(url_for("seguranca_conta.validar_dispositivo"))
    if _fluxo_pendente_do_cliente(cliente):
        return redirect(_finalizar_login_pendente(cliente))
    return redirect(_destino_final())


@seguranca_conta.before_app_request
def exigir_etapas_seguranca():
    """Impede uma sessão existente de continuar após qualquer etapa obrigatória."""
    if not current_user.is_authenticated:
        return None
    if request.endpoint == "static":
        return None
    if _sessao_autenticada_expirou():
        return _encerrar_sessao_expirada()
    if request.blueprint in {
        "autenticacao",
        "seguranca_conta",
        "seo",
    }:
        return None

    cliente = current_user._get_current_object()
    precisa_senha = senha_precisa_ser_trocada(cliente)
    precisa_dispositivo = not dispositivo_esta_validado(cliente)
    if not precisa_senha and not precisa_dispositivo:
        return None

    destino = _destino_requisicao_atual()
    _iniciar_fluxo_pendente(cliente, destino=destino)
    if precisa_senha:
        return redirect(url_for("seguranca_conta.senha_expirada"))
    return redirect(url_for("seguranca_conta.validar_dispositivo"))


@seguranca_conta.after_app_request
def proteger_respostas_seguranca(resposta):
    """Evita cache e indexação das etapas de segurança."""
    if request.path.startswith(("/senha-expirada", "/validar-dispositivo")):
        resposta.headers["Cache-Control"] = "no-store, private"
        resposta.headers["Pragma"] = "no-cache"
        resposta.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resposta


@seguranca_conta.route("/senha-expirada", methods=["GET", "POST"])
@limitador.limit("10 per hour", methods=["POST"])
def senha_expirada():
    """Exige nova senha antes de concluir a autenticação."""
    cliente = _cliente_em_fluxo()
    if cliente is None:
        return redirect(url_for("autenticacao.login"))
    if not senha_precisa_ser_trocada(cliente):
        return _proximo_passo(cliente)

    if request.method == "POST":
        from aplicacao.controladores.autenticacao import validar_regras_senha

        senha = request.form.get("senha", "")
        confirmacao = request.form.get("confirmacao_senha", "")
        erros = validar_regras_senha(senha, confirmacao)
        if not erros and cliente.verificar_senha(senha):
            erros.append("Escolha uma senha diferente da atual.")

        if erros:
            for erro in erros:
                flash(erro, "danger")
        else:
            cliente.definir_senha(senha)
            registrar_alteracao_senha(cliente)
            banco.session.commit()
            try:
                enviar_email_senha_atualizada(cliente)
            except ErroEnvioEmail:
                current_app.logger.warning(
                    "Senha periódica atualizada, mas a notificação não pôde ser enviada."
                )
            flash("Senha Atualizada com sucesso.", "success")
            return _proximo_passo(cliente)

    return render_template(
        "autenticacao/senha_expirada.html",
        dias=_config_int("PASSWORD_MAX_AGE_DAYS", 180),
    )


@seguranca_conta.route("/validar-dispositivo", methods=["GET", "POST"])
@limitador.limit("8 per 10 minutes", methods=["POST"])
def validar_dispositivo():
    """Aprova por código de e-mail um navegador antes de autenticar o cliente."""
    cliente = _cliente_em_fluxo()
    if cliente is None:
        return redirect(url_for("autenticacao.login"))
    if senha_precisa_ser_trocada(cliente):
        return redirect(url_for("seguranca_conta.senha_expirada"))
    if dispositivo_esta_validado(cliente):
        return _proximo_passo(cliente)

    if request.method == "GET" and not _desafio_dispositivo_ativo(cliente):
        try:
            _iniciar_desafio_dispositivo(cliente)
            flash(f"Enviamos um código de 6 dígitos para {cliente.email}.", "info")
        except ErroEnvioEmail:
            flash(
                "Não foi Possível enviar o código agora. Tente reenviar em alguns instantes.",
                "danger",
            )

    if request.method == "POST":
        codigo = re.sub(r"\D", "", request.form.get("codigo", ""))
        if not PADRAO_CODIGO_DISPOSITIVO.fullmatch(codigo):
            flash("Informe o código de 6 dígitos enviado por e-mail.", "danger")
        elif not _desafio_dispositivo_ativo(cliente):
            flash("O código expirou. Solicite um novo código.", "warning")
        elif not _codigo_dispositivo_valido(cliente, codigo):
            flash("Código inválido.", "danger")
        else:
            token, dias = _registrar_dispositivo_confiavel(cliente)
            destino = (
                _finalizar_login_pendente(cliente)
                if _fluxo_pendente_do_cliente(cliente)
                else _destino_final()
            )
            flash("Dispositivo Validado com Sucesso", "success")
            resposta = make_response(redirect(destino))
            return _aplicar_cookie_dispositivo(resposta, token, dias)

    return render_template(
        "autenticacao/validar_dispositivo.html",
        email=cliente.email,
        minutos=max(1, _config_int("DEVICE_CODE_TTL", 600) // 60),
        dias=_config_int("DEVICE_TRUST_DAYS", 30),
    )


@seguranca_conta.post("/validar-dispositivo/reenviar")
@limitador.limit("5 per 10 minutes")
def reenviar_codigo_dispositivo():
    """Reenvia o código sem autenticar o cliente antes da confirmação."""
    cliente = _cliente_em_fluxo()
    if cliente is None:
        return redirect(url_for("autenticacao.login"))
    if senha_precisa_ser_trocada(cliente):
        return redirect(url_for("seguranca_conta.senha_expirada"))
    if dispositivo_esta_validado(cliente):
        return _proximo_passo(cliente)

    desafio_anterior = session.get(CHAVE_DESAFIO_DISPOSITIVO)
    try:
        _iniciar_desafio_dispositivo(cliente, forcar=True)
    except ErroEnvioEmail:
        if desafio_anterior:
            session[CHAVE_DESAFIO_DISPOSITIVO] = desafio_anterior
        flash(
            "Não foi Possível reenviar o código agora. Tente novamente em alguns instantes.",
            "danger",
        )
    else:
        flash(f"Um novo código foi enviado para {cliente.email}.", "success")
    return redirect(url_for("seguranca_conta.validar_dispositivo"))
