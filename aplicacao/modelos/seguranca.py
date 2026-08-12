"""Modelos auxiliares das políticas de segurança de conta."""

from datetime import datetime, timezone

from aplicacao import banco


class SegurancaConta(banco.Model):
    """Guarda a referência da rotação de senha sem alterar o cadastro comercial."""

    cliente_id = banco.Column(
        banco.Integer,
        banco.ForeignKey("cliente.id"),
        primary_key=True,
    )
    senha_alterada_em = banco.Column(
        banco.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    senha_fingerprint = banco.Column(banco.String(64), nullable=True)


class DispositivoConfiavel(banco.Model):
    """Representa um navegador aprovado por token opaco e temporário."""

    id = banco.Column(banco.Integer, primary_key=True)
    cliente_id = banco.Column(
        banco.Integer,
        banco.ForeignKey("cliente.id"),
        nullable=False,
        index=True,
    )
    token_hash = banco.Column(banco.String(64), unique=True, nullable=False, index=True)
    user_agent = banco.Column(banco.String(255))
    criado_em = banco.Column(
        banco.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    expira_em = banco.Column(banco.DateTime, nullable=False, index=True)
