"""Testes do serviço de e-mail transacional."""

import importlib

modulo_email = importlib.import_module("aplicacao.servicos.email")


def test_senha_smtp_e_usada_exatamente_como_configurada(aplicacao, monkeypatch):
    """Evita alterar silenciosamente credenciais SMTP válidas."""
    chamadas = {}

    class SmtpFalso:
        def __init__(self, servidor, porta, timeout):
            chamadas["conexao"] = (servidor, porta, timeout)

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def ehlo(self):
            return None

        def login(self, usuario, senha):
            chamadas["login"] = (usuario, senha)

        def send_message(self, mensagem):
            chamadas["destinatario"] = mensagem["To"]

    monkeypatch.setattr(modulo_email.smtplib, "SMTP", SmtpFalso)
    aplicacao.config.update(
        MAIL_SUPPRESS_SEND=False,
        MAIL_SERVER="smtp.example.com",
        MAIL_PORT=587,
        MAIL_USERNAME="usuario@example.com",
        MAIL_PASSWORD="senha com espacos",
        MAIL_USE_TLS=False,
        MAIL_TIMEOUT=5,
    )

    with aplicacao.app_context():
        modulo_email.enviar_email(
            destinatario="destino@example.com",
            assunto="Teste",
            html="<p>Teste</p>",
            texto="Teste",
        )

    assert chamadas["login"] == ("usuario@example.com", "senha com espacos")
    assert chamadas["destinatario"] == "destino@example.com"
