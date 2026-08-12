"""Factory e configuração central da aplicação Flask Doce Pedido."""

import os
from datetime import timedelta
from pathlib import Path

from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix

banco = SQLAlchemy()
gerenciador_login = LoginManager()
protecao_csrf = CSRFProtect()
limitador = Limiter(key_func=get_remote_address, default_limits=[])


def _variavel_booleana(nome, padrao=False):
    """Converte uma variável de ambiente textual em booleano."""
    valor = os.environ.get(nome)
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "yes", "on"}


def criar_aplicacao(configuracao=None):
    """Cria e configura uma instância isolada da aplicação."""
    aplicacao = Flask(__name__, instance_relative_config=True)
    caminho_banco = Path(aplicacao.instance_path) / "doce_pedido.db"
    ambiente = os.environ.get("APP_ENV", "development").lower()
    producao = ambiente == "production"
    duracao_autenticacao_dias = max(
        1, int(os.environ.get("AUTH_SESSION_MAX_AGE_DAYS", "7"))
    )
    chave_secreta = os.environ.get("SECRET_KEY")
    if producao and not chave_secreta:
        raise RuntimeError("SECRET_KEY deve ser configurada no ambiente de produção.")
    site_url = os.environ.get("SITE_URL", "").rstrip("/")
    if producao and not site_url:
        raise RuntimeError("SITE_URL deve ser configurada no ambiente de produção.")

    aplicacao.config.from_mapping(
        SECRET_KEY=chave_secreta or "chave-exclusiva-para-desenvolvimento-local",
        DEBUG=False,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{caminho_banco}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        INICIALIZAR_DADOS=True,
        AMBIENTE_PRODUCAO=producao,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=producao,
        SESSION_COOKIE_SAMESITE="Lax",
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SECURE=producao,
        REMEMBER_COOKIE_SAMESITE="Lax",
        AUTH_SESSION_MAX_AGE_DAYS=duracao_autenticacao_dias,
        PERMANENT_SESSION_LIFETIME=timedelta(days=duracao_autenticacao_dias),
        REMEMBER_COOKIE_DURATION=timedelta(days=duracao_autenticacao_dias),
        PASSWORD_ROTATION_ENABLED=_variavel_booleana(
            "PASSWORD_ROTATION_ENABLED", True
        ),
        PASSWORD_MAX_AGE_DAYS=max(
            1, int(os.environ.get("PASSWORD_MAX_AGE_DAYS", "180"))
        ),
        DEVICE_VALIDATION_ENABLED=_variavel_booleana(
            "DEVICE_VALIDATION_ENABLED", True
        ),
        DEVICE_CODE_TTL=max(60, int(os.environ.get("DEVICE_CODE_TTL", "600"))),
        DEVICE_TRUST_DAYS=max(1, int(os.environ.get("DEVICE_TRUST_DAYS", "30"))),
        DEVICE_COOKIE_NAME=os.environ.get(
            "DEVICE_COOKIE_NAME", "doce_pedido_dispositivo"
        ).strip()
        or "doce_pedido_dispositivo",
        ACCOUNT_CHANGE_TOKEN_TTL=max(
            60, int(os.environ.get("ACCOUNT_CHANGE_TOKEN_TTL", "86400"))
        ),
        SITE_URL=site_url,
        GOOGLE_SITE_VERIFICATION=os.environ.get("GOOGLE_SITE_VERIFICATION"),
        BING_SITE_VERIFICATION=os.environ.get("BING_SITE_VERIFICATION"),
        GA_MEASUREMENT_ID=os.environ.get("GA_MEASUREMENT_ID", "").strip(),
        SITE_EMAIL=os.environ.get("SITE_EMAIL", "").strip(),
        SITE_TELEPHONE=os.environ.get("SITE_TELEPHONE", "").strip(),
        SITE_TELEPHONE_DISPLAY=os.environ.get("SITE_TELEPHONE_DISPLAY", "").strip(),
        SITE_ADDRESS_STREET=os.environ.get("SITE_ADDRESS_STREET", "").strip(),
        SITE_ADDRESS_LOCALITY=os.environ.get("SITE_ADDRESS_LOCALITY", "").strip(),
        SITE_ADDRESS_REGION=os.environ.get("SITE_ADDRESS_REGION", "").strip(),
        SITE_ADDRESS_COUNTRY=os.environ.get("SITE_ADDRESS_COUNTRY", "").strip(),
        SITE_ADDRESS_DISPLAY=os.environ.get("SITE_ADDRESS_DISPLAY", "").strip(),
        SITE_MAPS_URL=os.environ.get("SITE_MAPS_URL", "").strip(),
        SITE_BUSINESS_HOURS=os.environ.get("SITE_BUSINESS_HOURS", "").strip(),
        SITE_FACEBOOK_URL=os.environ.get("SITE_FACEBOOK_URL", "").strip(),
        SITE_INSTAGRAM_URL=os.environ.get("SITE_INSTAGRAM_URL", "").strip(),
        SITE_TIKTOK_URL=os.environ.get("SITE_TIKTOK_URL", "").strip(),
        SITE_WHATSAPP_URL=os.environ.get("SITE_WHATSAPP_URL", "").strip(),
        MAIL_SERVER=os.environ.get("MAIL_SERVER", "smtp.gmail.com").strip(),
        MAIL_PORT=int(os.environ.get("MAIL_PORT", "587")),
        MAIL_USE_TLS=_variavel_booleana("MAIL_USE_TLS", True),
        MAIL_USERNAME=os.environ.get(
            "MAIL_USERNAME", "docepedidosite@gmail.com"
        ).strip(),
        MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", ""),
        MAIL_SENDER=os.environ.get(
            "MAIL_SENDER", "docepedidosite@gmail.com"
        ).strip(),
        MAIL_SENDER_NAME=os.environ.get("MAIL_SENDER_NAME", "Doce Pedido").strip(),
        MAIL_TIMEOUT=float(os.environ.get("MAIL_TIMEOUT", "10")),
        MAIL_SUPPRESS_SEND=False,
        PASSWORD_RESET_TOKEN_TTL=max(
            60, int(os.environ.get("PASSWORD_RESET_TOKEN_TTL", "3600"))
        ),
        EMAIL_CONFIRMATION_TOKEN_TTL=max(
            60, int(os.environ.get("EMAIL_CONFIRMATION_TOKEN_TTL", "86400"))
        ),
        SEND_FILE_MAX_AGE_DEFAULT=timedelta(hours=1),
        RATELIMIT_STORAGE_URI=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
        TRUSTED_HOSTS=[
            host.strip()
            for host in os.environ.get("TRUSTED_HOSTS", "").split(",")
            if host.strip()
        ]
        or None,
    )
    if configuracao:
        aplicacao.config.update(configuracao)

    # Nos testes comuns, as etapas extras de segurança ficam desligadas para
    # não interferir em cenários que não estão validando essas políticas.
    if aplicacao.testing:
        configuracao = configuracao or {}
        if (
            "PASSWORD_ROTATION_ENABLED" not in configuracao
            and "PASSWORD_ROTATION_ENABLED" not in os.environ
        ):
            aplicacao.config["PASSWORD_ROTATION_ENABLED"] = False
        if (
            "DEVICE_VALIDATION_ENABLED" not in configuracao
            and "DEVICE_VALIDATION_ENABLED" not in os.environ
        ):
            aplicacao.config["DEVICE_VALIDATION_ENABLED"] = False

    if not configuracao or "WTF_CSRF_ENABLED" not in configuracao:
        aplicacao.config["WTF_CSRF_ENABLED"] = not aplicacao.testing
    if not configuracao or "RATELIMIT_ENABLED" not in configuracao:
        aplicacao.config["RATELIMIT_ENABLED"] = not aplicacao.testing
    if not configuracao or "MAIL_SUPPRESS_SEND" not in configuracao:
        aplicacao.config["MAIL_SUPPRESS_SEND"] = aplicacao.testing

    if _variavel_booleana("TRUST_PROXY", False):
        aplicacao.wsgi_app = ProxyFix(
            aplicacao.wsgi_app, x_for=1, x_proto=1, x_host=0, x_prefix=0
        )

    Path(aplicacao.instance_path).mkdir(parents=True, exist_ok=True)
    banco.init_app(aplicacao)
    protecao_csrf.init_app(aplicacao)
    limitador.init_app(aplicacao)
    configurar_login(aplicacao)
    registrar_controladores(aplicacao)

    with aplicacao.app_context():
        banco.create_all()

        from aplicacao.dados_iniciais import criar_dados_iniciais

        if aplicacao.config["INICIALIZAR_DADOS"]:
            criar_dados_iniciais()

    return aplicacao


def configurar_login(aplicacao):
    """Configura o carregamento de clientes e as mensagens de autenticação."""
    from aplicacao.modelos import Cliente

    gerenciador_login.init_app(aplicacao)
    gerenciador_login.login_view = "autenticacao.login"
    gerenciador_login.login_message = "Faça Login para Acessar."
    gerenciador_login.login_message_category = "warning"

    @gerenciador_login.user_loader
    def carregar_cliente(cliente_id):
        """Recupera o cliente associado ao identificador salvo na sessão."""
        try:
            identificador = int(cliente_id)
        except (TypeError, ValueError):
            return None
        return banco.session.get(Cliente, identificador)


def registrar_controladores(aplicacao):
    """Registra rotas, contexto de templates, filtros e respostas globais."""
    from aplicacao.controladores import controladores
    from aplicacao.institucional import institucional
    from aplicacao.seo import contexto_seo, seo

    for controlador in controladores:
        aplicacao.register_blueprint(controlador)
    aplicacao.register_blueprint(seo)
    aplicacao.register_blueprint(institucional)
    aplicacao.context_processor(contexto_seo)

    @aplicacao.template_filter("moeda")
    def formatar_moeda(valor):
        return f"R$ {valor:.2f}".replace(".", ",")

    @aplicacao.after_request
    def aplicar_headers_seguranca(resposta):
        """Acrescenta headers de segurança e cache adequados à resposta."""
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        resposta.headers["X-Frame-Options"] = "DENY"
        resposta.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        resposta.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )
        analytics_ativo = bool(aplicacao.config["GA_MEASUREMENT_ID"])
        origens_analytics = (
            " https://www.googletagmanager.com" if analytics_ativo else ""
        )
        conexoes_analytics = (
            " https://www.google-analytics.com https://region1.google-analytics.com"
            if analytics_ativo
            else ""
        )
        resposta.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"script-src 'self'{origens_analytics}; "
            "style-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self' https://fonts.gstatic.com; "
            f"connect-src 'self'{conexoes_analytics}; "
            "object-src 'none'; base-uri 'self'; "
            "form-action 'self'; frame-ancestors 'none'; "
            "worker-src 'self'; manifest-src 'self'"
        )
        caminho_privado = request.path.startswith(
            (
                "/carrinho",
                "/pedidos",
                "/login",
                "/cadastro",
                "/esqueci-senha",
                "/redefinir-senha",
                "/confirmar-email",
            )
        )
        if caminho_privado:
            resposta.headers["Cache-Control"] = "no-store, private"
            resposta.headers["Pragma"] = "no-cache"
        if request.path.startswith(("/redefinir-senha", "/confirmar-email")):
            resposta.headers["X-Robots-Tag"] = "noindex, nofollow"
        if aplicacao.config["AMBIENTE_PRODUCAO"] and request.is_secure:
            resposta.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return resposta

    @aplicacao.errorhandler(CSRFError)
    def erro_csrf(erro):
        return render_template(
            "erros/erro.html",
            codigo=400,
            titulo="Não foi Possível Validar o Formulário",
            mensagem="Atualize a página e tente novamente.",
        ), 400

    def resposta_erro(codigo, titulo, mensagem):
        """Renderiza a página de erro compartilhada com o status informado."""
        return render_template(
            "erros/erro.html",
            codigo=codigo,
            titulo=titulo,
            mensagem=mensagem,
        ), codigo

    @aplicacao.errorhandler(400)
    def requisicao_invalida(erro):
        from werkzeug.exceptions import SecurityError

        if isinstance(erro, SecurityError):
            return "Requisição inválida.", 400

        return resposta_erro(
            400,
            "Requisição Inválida",
            "Revise os dados enviados.",
        )

    @aplicacao.errorhandler(403)
    def acesso_negado(erro):
        return resposta_erro(
            403,
            "Acesso Não Permitido",
            "Você não pode acessar este conteúdo.",
        )

    @aplicacao.errorhandler(404)
    def pagina_nao_encontrada(erro):
        return resposta_erro(
            404,
            "Página Não Encontrada",
            "O endereço pode ter mudado ou não estar mais disponível.",
        )

    @aplicacao.errorhandler(429)
    def muitas_tentativas(erro):
        return resposta_erro(
            429,
            "Muitas Tentativas",
            "Aguarde um momento antes de tentar novamente.",
        )

    @aplicacao.errorhandler(500)
    def erro_interno(erro):
        banco.session.rollback()
        aplicacao.logger.error("Erro interno ao processar %s", request.path)
        return resposta_erro(
            500,
            "Algo Não Saiu como Esperado",
            "Tente novamente mais tarde.",
        )
