"""Endereços salvos pelo cliente para uso atual e futuro no checkout."""

from datetime import datetime, timezone

from aplicacao import banco


class Endereco(banco.Model):
    """Representa um endereço nomeado pertencente a uma conta de cliente."""

    __tablename__ = "endereco"
    __table_args__ = (
        banco.UniqueConstraint("cliente_id", "nome", name="uq_endereco_cliente_nome"),
    )

    id = banco.Column(banco.Integer, primary_key=True)
    cliente_id = banco.Column(
        banco.Integer,
        banco.ForeignKey("cliente.id"),
        nullable=False,
        index=True,
    )
    nome = banco.Column(banco.String(60), nullable=False)
    cep = banco.Column(banco.String(8), nullable=False)
    logradouro = banco.Column(banco.String(160), nullable=False)
    numero = banco.Column(banco.String(20), nullable=False)
    complemento = banco.Column(banco.String(100))
    bairro = banco.Column(banco.String(100), nullable=False)
    cidade = banco.Column(banco.String(100), nullable=False)
    uf = banco.Column(banco.String(2), nullable=False)
    referencia = banco.Column(banco.String(180))
    principal = banco.Column(banco.Boolean, nullable=False, default=False, index=True)
    criado_em = banco.Column(
        banco.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    cliente = banco.relationship("Cliente")

    @property
    def cep_formatado(self):
        """Apresenta o CEP no padrão brasileiro sem alterar o valor persistido."""
        if len(self.cep or "") != 8:
            return self.cep or ""
        return f"{self.cep[:5]}-{self.cep[5:]}"
