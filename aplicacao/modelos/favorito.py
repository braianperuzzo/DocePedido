"""Produtos marcados como favoritos por cada cliente."""

from datetime import datetime, timezone

from aplicacao import banco


class Favorito(banco.Model):
    """Relaciona uma conta autenticada a um produto favoritado."""

    __tablename__ = "favorito"
    __table_args__ = (
        banco.UniqueConstraint(
            "cliente_id", "produto_id", name="uq_favorito_cliente_produto"
        ),
    )

    id = banco.Column(banco.Integer, primary_key=True)
    cliente_id = banco.Column(
        banco.Integer,
        banco.ForeignKey("cliente.id"),
        nullable=False,
        index=True,
    )
    produto_id = banco.Column(
        banco.Integer,
        banco.ForeignKey("produto.id"),
        nullable=False,
        index=True,
    )
    criado_em = banco.Column(
        banco.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    cliente = banco.relationship("Cliente")
    produto = banco.relationship("Produto")
