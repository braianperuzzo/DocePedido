"""Envio de e-mails transacionais da Doce Pedido."""

import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from flask import current_app


class ErroEnvioEmail(RuntimeError):
    """Sinaliza uma falha controlada no envio de e-mail."""


def _configuracao_obrigatoria(nome):
    """Lê uma configuração necessária e falha com mensagem controlada se estiver vazia."""
    valor = current_app.config.get(nome)
    if valor is None or str(valor).strip() == "":
        raise ErroEnvioEmail(f"Configuração de e-mail ausente: {nome}.")
    return valor


def enviar_email(destinatario, assunto, html, texto):
    """Envia uma mensagem multipart usando a configuração SMTP da aplicação."""
    if current_app.config.get("MAIL_SUPPRESS_SEND", False):
        return

    servidor = str(_configuracao_obrigatoria("MAIL_SERVER"))
    porta = int(_configuracao_obrigatoria("MAIL_PORT"))
    usuario = str(_configuracao_obrigatoria("MAIL_USERNAME"))
    senha = str(_configuracao_obrigatoria("MAIL_PASSWORD"))
    remetente = str(current_app.config.get("MAIL_SENDER") or usuario)
    nome_remetente = str(current_app.config.get("MAIL_SENDER_NAME") or "Doce Pedido")
    timeout = float(current_app.config.get("MAIL_TIMEOUT", 10))

    mensagem = EmailMessage()
    mensagem["From"] = formataddr((nome_remetente, remetente))
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.set_content(texto)
    mensagem.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(servidor, porta, timeout=timeout) as smtp:
            smtp.ehlo()
            if current_app.config.get("MAIL_USE_TLS", True):
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
            smtp.login(usuario, senha)
            smtp.send_message(mensagem)
    except (OSError, smtplib.SMTPException) as erro:
        current_app.logger.error(
            "Falha no envio de e-mail transacional (%s).", erro.__class__.__name__
        )
        raise ErroEnvioEmail("Não foi Possível enviar o e-mail.") from erro
