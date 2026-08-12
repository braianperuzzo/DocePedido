"""Tokens assinados e temporários usados pela autenticação."""

from hashlib import sha256

from flask import current_app
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SALT_REDEFINICAO_SENHA = "doce-pedido-redefinicao-senha-v1"
SALT_CONFIRMACAO_EMAIL = "doce-pedido-confirmacao-email-v1"


class TokenInvalido(ValueError):
    """Indica token ausente, adulterado ou incompatível com o estado atual."""


class TokenExpirado(TokenInvalido):
    """Indica token válido cuja janela de uso já terminou."""


def _serializador():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def fingerprint_senha(cliente):
    """Cria impressão curta do hash atual sem expô-lo no token."""
    return sha256(cliente.senha_hash.encode("utf-8")).hexdigest()[:24]


def gerar_token_redefinicao(cliente):
    """Assina um token vinculado ao cliente e ao hash de Senha Atual."""
    payload = {
        "cliente_id": cliente.id,
        "email": cliente.email,
        "senha": fingerprint_senha(cliente),
    }
    return _serializador().dumps(payload, salt=SALT_REDEFINICAO_SENHA)


def carregar_token_redefinicao(token):
    """Valida assinatura e expiração e devolve o payload mínimo."""
    try:
        return _serializador().loads(
            token,
            salt=SALT_REDEFINICAO_SENHA,
            max_age=int(current_app.config["PASSWORD_RESET_TOKEN_TTL"]),
        )
    except SignatureExpired as erro:
        raise TokenExpirado("Token de redefinição expirado.") from erro
    except (BadSignature, TypeError, ValueError) as erro:
        raise TokenInvalido("Token de redefinição inválido.") from erro


def gerar_token_confirmacao_email(cliente):
    """Assina um token mínimo e específico para confirmar o e-mail cadastrado."""
    payload = {"cliente_id": cliente.id, "email": cliente.email}
    return _serializador().dumps(payload, salt=SALT_CONFIRMACAO_EMAIL)


def carregar_token_confirmacao_email(token):
    """Valida assinatura e prazo do token de confirmação de cadastro."""
    try:
        return _serializador().loads(
            token,
            salt=SALT_CONFIRMACAO_EMAIL,
            max_age=int(current_app.config["EMAIL_CONFIRMATION_TOKEN_TTL"]),
        )
    except SignatureExpired as erro:
        raise TokenExpirado("Token de confirmação expirado.") from erro
    except (BadSignature, TypeError, ValueError) as erro:
        raise TokenInvalido("Token de confirmação inválido.") from erro
