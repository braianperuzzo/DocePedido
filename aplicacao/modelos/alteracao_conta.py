"""Solicitações pendentes de alteração dos dados da conta."""

from datetime import datetime, timezone

from aplicacao import banco


def agora_utc():
    """Retorna UTC sem fuso para manter compatibilidade com o SQLite atual."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class AlteracaoConta(banco.Model):
    """Guarda uma alteração até a confirmação recebida por e-mail."""

    __tablename__ = "alteracao_conta"

    id = banco.Column(banco.Integer, primary_key=True)
    cliente_id = banco.Column(
        banco.Integer,
        banco.ForeignKey("cliente.id"),
        nullable=False,
        index=True,
    )
    tipo = banco.Column(banco.String(20), nullable=False)
    token_hash = banco.Column(banco.String(64), nullable=False, unique=True, index=True)
    senha_fingerprint = banco.Column(banco.String(64), nullable=False)
    dados_json = banco.Column(banco.Text, nullable=True)
    senha_hash_nova = banco.Column(banco.String(255), nullable=True)
    criado_em = banco.Column(banco.DateTime, nullable=False, default=agora_utc)
    expira_em = banco.Column(banco.DateTime, nullable=False)
    concluida_em = banco.Column(banco.DateTime, nullable=True)

    cliente = banco.relationship("Cliente")
