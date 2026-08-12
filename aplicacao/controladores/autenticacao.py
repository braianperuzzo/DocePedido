"""Rotas e regras de autenticação da Doce Pedido."""

import re
import time

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_user, logout_user

from aplicacao import banco, limitador
from aplicacao.modelos import Cliente
from aplicacao.servicos.email import ErroEnvioEmail, enviar_email
from aplicacao.servicos.navegacao import caminho_interno_seguro
from aplicacao.servicos.tokens import (
    TokenExpirado,
    TokenInvalido,
    carregar_token_confirmacao_email,
    carregar_token_redefinicao,
    fingerprint_senha,
    gerar_token_confirmacao_email,
    gerar_token_redefinicao,
)

autenticacao = Blueprint("autenticacao", __name__)
CHAVE_INICIO_AUTENTICACAO = "autenticacao_iniciada_em"
CHAVE_DESTINO_LOGIN = "autenticacao_destino"
PADRAO_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PADRAO_MAIUSCULA = re.compile(r"[A-Z]")
PADRAO_MINUSCULA = re.compile(r"[a-z]")
PADRAO_NUMERO = re.compile(r"\d")
PADRAO_ESPECIAL = re.compile(r"[^A-Za-z0-9]")
MENSAGEM_RECUPERACAO = (
    "Se houver uma conta cadastrada com este e-mail, enviaremos as instruções "
    "para redefinir sua senha."
)
MENSAGEM_REENVIO_CONFIRMACAO = (
    "Se este cadastro estiver aguardando confirmação, enviaremos um novo link "
    "para o e-mail informado."
)


@autenticacao.route("/cadastro", methods=["GET", "POST"])
@limitador.limit("5 per hour", methods=["POST"])
def cadastro():
    """Cria uma conta pendente e solicita a confirmação do e-mail."""
    if current_user.is_authenticated:
        return redirect(url_for("pagina_inicial.inicio"))

    if request.method == "POST":
        email_informado = request.form.get("email", "").strip().lower()
        existente = cliente_por_email(email_informado) if email_informado else None
        if existente and not existente.ativo:
            try:
                enviar_email_confirmacao(existente)
            except ErroEnvioEmail:
                flash(
                    "Não foi Possível reenviar a confirmação agora. "
                    "Tente novamente em alguns instantes.",
                    "danger",
                )
            else:
                flash(MENSAGEM_REENVIO_CONFIRMACAO, "success")
            return redirect(url_for("autenticacao.cadastro"))

        erros, dados = validar_cadastro()
        if erros:
            for erro in erros:
                flash(erro, "danger")
        else:
            cliente = cadastrar_cliente(dados, ativo=False)
            try:
                banco.session.flush()
                enviar_email_confirmacao(cliente)
                banco.session.commit()
            except ErroEnvioEmail:
                banco.session.rollback()
                flash(
                    "Não foi Possível enviar a confirmação agora. "
                    "Tente novamente em alguns instantes.",
                    "danger",
                )
            else:
                flash(
                    "Cadastro Realizado com Sucesso. Confira seu E-mail para "
                    "Confirmar sua Conta.",
                    "success",
                )
                return redirect(url_for("autenticacao.login"))

    return render_template("autenticacao/cadastro.html")


def validar_regras_senha(senha, confirmacao_senha=None):
    """Aplica em um único lugar os critérios obrigatórios de senha."""
    erros = []
    if not senha:
        erros.append("Informe uma senha.")
        return erros
    if len(senha) < 8:
        erros.append("A senha deve conter pelo menos 8 caracteres.")
    if not PADRAO_MAIUSCULA.search(senha):
        erros.append("A senha deve conter pelo menos uma letra maiúscula.")
    if not PADRAO_MINUSCULA.search(senha):
        erros.append("A senha deve conter pelo menos uma letra minúscula.")
    if not PADRAO_NUMERO.search(senha):
        erros.append("A senha deve conter pelo menos um número.")
    if not PADRAO_ESPECIAL.search(senha):
        erros.append("A senha deve conter pelo menos um caractere especial.")
    if confirmacao_senha is not None and senha != confirmacao_senha:
        erros.append("As senhas informadas não coincidem.")
    return erros


def validar_cadastro():
    """Normaliza o cadastro e retorna os erros de validação encontrados."""
    dados = {
        "nome": request.form.get("nome", "").strip(),
        "cpf": re.sub(r"\D", "", request.form.get("cpf", "")),
        "email": request.form.get("email", "").strip().lower(),
        "senha": request.form.get("senha", ""),
        "confirmacao_senha": request.form.get("confirmacao_senha", ""),
    }
    erros = []

    if not dados["nome"]:
        erros.append("Informe seu nome.")
    elif len(dados["nome"]) > 120:
        erros.append("O nome deve possuir no máximo 120 caracteres.")
    if not validar_cpf(dados["cpf"]):
        erros.append("Informe um CPF válido.")
    elif cliente_por_cpf(dados["cpf"]):
        erros.append("Não foi Possível concluir o cadastro com estes dados.")
    if not dados["email"]:
        erros.append("Informe seu e-mail.")
    elif not PADRAO_EMAIL.match(dados["email"]):
        erros.append("Informe um e-mail válido.")
    elif len(dados["email"]) > 255:
        erros.append("O e-mail informado é muito longo.")
    elif cliente_por_email(dados["email"]):
        erros.append("Não foi Possível concluir o cadastro com estes dados.")
    erros.extend(
        validar_regras_senha(dados["senha"], dados["confirmacao_senha"])
    )

    return erros, dados


def cadastrar_cliente(dados, ativo=True):
    """Prepara um cliente com a senha protegida e o adiciona à transação atual."""
    cliente = Cliente(
        nome=dados["nome"],
        cpf=dados["cpf"],
        email=dados["email"],
        ativo=ativo,
    )
    cliente.definir_senha(dados["senha"])
    banco.session.add(cliente)
    return cliente


def cliente_por_email(email):
    """Localiza um cliente pelo e-mail normalizado."""
    return banco.session.scalar(banco.select(Cliente).where(Cliente.email == email))


def cliente_por_cpf(cpf):
    """Localiza um cliente pelo CPF normalizado."""
    return banco.session.scalar(banco.select(Cliente).where(Cliente.cpf == cpf))


def validar_cpf(cpf):
    """Valida tamanho, repetição e dígitos verificadores de um CPF."""
    numeros = re.sub(r"\D", "", cpf or "")
    if len(numeros) != 11 or numeros == numeros[0] * 11:
        return False

    def calcular_digito(parcial, peso_inicial):
        pesos = range(peso_inicial, 1, -1)
        soma = sum(int(numero) * peso for numero, peso in zip(parcial, pesos))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    primeiro = calcular_digito(numeros[:9], 10)
    segundo = calcular_digito(numeros[:9] + primeiro, 11)
    return numeros[-2:] == primeiro + segundo


def autenticar_cliente(cliente, lembrar=False):
    """Inicia uma sessão limpa sem reiniciar o prazo absoluto da autenticação."""
    carrinho_atual = session.get("carrinho")
    inicio_autenticacao = session.get(CHAVE_INICIO_AUTENTICACAO)
    try:
        inicio_autenticacao = int(inicio_autenticacao)
    except (TypeError, ValueError):
        inicio_autenticacao = int(time.time())

    session.clear()
    login_user(cliente, remember=lembrar)
    session[CHAVE_INICIO_AUTENTICACAO] = inicio_autenticacao
    session.permanent = bool(lembrar)
    if carrinho_atual:
        session["carrinho"] = carrinho_atual


def _url_externa(endpoint, **valores):
    """Monta um link absoluto para os e-mails de autenticação."""
    caminho = url_for(endpoint, **valores)
    site_url = current_app.config.get("SITE_URL", "").rstrip("/")
    if site_url:
        return f"{site_url}{caminho}"
    return url_for(endpoint, _external=True, **valores)


def enviar_email_redefinicao(cliente):
    """Monta e envia o e-mail de redefinição sem registrar o token em logs."""
    token = gerar_token_redefinicao(cliente)
    link = _url_externa("autenticacao.redefinir_senha", token=token)
    html = render_template(
        "emails/recuperacao_senha.html", nome=cliente.nome, link=link
    )
    texto = (
        f"Olá, {cliente.nome}.\n\n"
        "Recebemos uma solicitação para redefinir a senha da sua conta na "
        "Doce Pedido.\n\n"
        f"Acesse: {link}\n\n"
        "Se você não solicitou a alteração, ignore este e-mail."
    )
    enviar_email(
        destinatario=cliente.email,
        assunto="Redefinição de Senha - Doce Pedido",
        html=html,
        texto=texto,
    )


def enviar_email_confirmacao(cliente):
    """Monta e envia a confirmação do cadastro por e-mail."""
    token = gerar_token_confirmacao_email(cliente)
    link = _url_externa("autenticacao.confirmar_email", token=token)
    html = render_template(
        "emails/confirmacao_cadastro.html", nome=cliente.nome, link=link
    )
    texto = (
        f"Olá, {cliente.nome}.\n\n"
        "Para concluir seu cadastro na Doce Pedido, confirme sua conta "
        f"acessando:\n\n{link}\n\n"
        "Se você não realizou este cadastro, ignore esta mensagem."
    )
    enviar_email(
        destinatario=cliente.email,
        assunto="Confirme seu Cadastro na Doce Pedido",
        html=html,
        texto=texto,
    )


@autenticacao.post("/esqueci-senha")
@limitador.limit("5 per hour")
def esqueci_senha():
    """Solicita recuperação sem revelar se o e-mail pertence a uma conta."""
    email = request.form.get("email", "").strip().lower()
    if not email or not PADRAO_EMAIL.match(email) or len(email) > 255:
        return jsonify(ok=False, mensagem="Informe um e-mail válido."), 400
    cliente = cliente_por_email(email)
    if cliente and cliente.ativo:
        try:
            enviar_email_redefinicao(cliente)
        except ErroEnvioEmail:
            return (
                jsonify(
                    ok=False,
                    mensagem=(
                        "Não foi Possível enviar as instruções agora. "
                        "Tente novamente em alguns instantes."
                    ),
                ),
                503,
            )

    return jsonify(ok=True, mensagem=MENSAGEM_RECUPERACAO)


def _cliente_do_token_redefinicao(token):
    """Resolve o cliente somente quando o token ainda corresponde à conta atual."""
    payload = carregar_token_redefinicao(token)
    if not isinstance(payload, dict):
        raise TokenInvalido("Payload inválido.")
    cliente = banco.session.get(Cliente, payload.get("cliente_id"))
    if (
        not cliente
        or not cliente.ativo
        or cliente.email != payload.get("email")
        or fingerprint_senha(cliente) != payload.get("senha")
    ):
        raise TokenInvalido("Token incompatível com a conta.")
    return cliente


@autenticacao.route("/redefinir-senha/<token>", methods=["GET", "POST"])
@limitador.limit("10 per hour", methods=["POST"])
def redefinir_senha(token):
    """Valida o link, altera a senha e conclui a segurança antes do login."""
    try:
        cliente = _cliente_do_token_redefinicao(token)
    except TokenExpirado:
        return (
            render_template(
                "autenticacao/redefinir_senha.html",
                estado_token="expirado",  # nosec B106 - estado visual do link
            ),
            410,
        )
    except TokenInvalido:
        return (
            render_template(
                "autenticacao/redefinir_senha.html",
                estado_token="invalido",  # nosec B106 - estado visual do link
            ),
            400,
        )

    if request.method == "POST":
        senha = request.form.get("senha", "")
        confirmacao = request.form.get("confirmacao_senha", "")
        erros = validar_regras_senha(senha, confirmacao)
        if not erros and cliente.verificar_senha(senha):
            erros.append("Escolha uma senha diferente da atual.")
        if erros:
            for erro in erros:
                flash(erro, "danger")
            return render_template(
                "autenticacao/redefinir_senha.html",
                estado_token="valido",  # nosec B106 - estado visual do link
            )

        cliente.definir_senha(senha)
        from aplicacao.controladores.seguranca_conta import (
            iniciar_login_seguro,
            registrar_alteracao_senha,
        )

        registrar_alteracao_senha(cliente)
        banco.session.commit()
        resposta_seguranca = iniciar_login_seguro(cliente)
        flash("Senha redefinida com sucesso.", "success")
        if resposta_seguranca is not None:
            return resposta_seguranca

        autenticar_cliente(cliente)
        return redirect(url_for("pagina_inicial.inicio"))

    return render_template(
        "autenticacao/redefinir_senha.html",
        estado_token="valido",  # nosec B106 - estado visual do link
    )


@autenticacao.get("/confirmar-email/<token>")
def confirmar_email(token):
    """Ativa o cadastro e conclui a segurança antes de iniciar a sessão."""
    try:
        payload = carregar_token_confirmacao_email(token)
    except TokenExpirado:
        flash(
            "Este link de confirmação expirou. Faça o cadastro novamente para "
            "receber um novo link.",
            "warning",
        )
        return redirect(url_for("autenticacao.cadastro"))
    except TokenInvalido:
        flash("Este link de confirmação não é válido.", "danger")
        return redirect(url_for("autenticacao.login"))

    if not isinstance(payload, dict):
        flash("Este link de confirmação não é válido.", "danger")
        return redirect(url_for("autenticacao.login"))
    cliente = banco.session.get(Cliente, payload.get("cliente_id"))
    if not cliente or cliente.email != payload.get("email"):
        flash("Este link de confirmação não é válido.", "danger")
        return redirect(url_for("autenticacao.login"))

    if not cliente.ativo:
        cliente.ativo = True
        banco.session.commit()

    from aplicacao.controladores.seguranca_conta import iniciar_login_seguro

    resposta_seguranca = iniciar_login_seguro(cliente)
    flash("Conta confirmada com sucesso.", "success")
    if resposta_seguranca is not None:
        return resposta_seguranca

    autenticar_cliente(cliente)
    flash("Bem-vindo à Doce Pedido!", "success")
    return redirect(url_for("pagina_inicial.inicio"))


@autenticacao.route("/login", methods=["GET", "POST"])
@limitador.limit("5 per minute", methods=["POST"])
def login():
    """Valida credenciais e só autentica após as etapas de segurança exigidas."""
    destino_argumento = caminho_interno_seguro(request.args.get("next"))
    if current_user.is_authenticated:
        return redirect(destino_argumento or url_for("pagina_inicial.inicio"))

    if request.method == "GET":
        if destino_argumento:
            session[CHAVE_DESTINO_LOGIN] = destino_argumento
        else:
            session.pop(CHAVE_DESTINO_LOGIN, None)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        lembrar = request.form.get("lembrar") == "on"
        cliente = cliente_por_email(email)

        if cliente and cliente.verificar_senha(senha):
            if not cliente.ativo:
                flash("Confirme seu e-mail antes de acessar sua conta.", "warning")
            else:
                destino = destino_argumento or caminho_interno_seguro(
                    session.get(CHAVE_DESTINO_LOGIN)
                )
                from aplicacao.controladores.seguranca_conta import iniciar_login_seguro

                resposta_seguranca = iniciar_login_seguro(
                    cliente,
                    lembrar=lembrar,
                    destino=destino,
                )
                if resposta_seguranca is not None:
                    return resposta_seguranca

                autenticar_cliente(cliente, lembrar=lembrar)
                flash(f"Bem-vindo, {cliente.nome}!", "success")
                return redirect(destino or url_for("pagina_inicial.inicio"))
        else:
            flash("E-mail ou senha inválidos.", "danger")

    return render_template("autenticacao/login.html")


@autenticacao.post("/logout")
def logout():
    """Encerra a sessão autenticada do cliente."""
    logout_user()
    session.pop(CHAVE_INICIO_AUTENTICACAO, None)
    session.pop(CHAVE_DESTINO_LOGIN, None)
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("pagina_inicial.inicio"))
