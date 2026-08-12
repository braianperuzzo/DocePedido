"""Modelo de dados de pedido da Doce Pedido."""

from datetime import datetime, timezone
from decimal import Decimal

from aplicacao import banco


class Pedido(banco.Model):
    """Representa uma compra confirmada por um cliente."""

    id = banco.Column(banco.Integer, primary_key=True)
    cliente_id = banco.Column(
        banco.Integer, banco.ForeignKey("cliente.id"), nullable=False
    )
    data_pedido = banco.Column(
        banco.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    status = banco.Column(banco.String(30), nullable=False, default="Recebido")
    valor_total = banco.Column(
        banco.Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    cliente = banco.relationship("Cliente", back_populates="pedidos")
    itens = banco.relationship(
        "ItemPedido",
        back_populates="pedido",
        cascade="all, delete-orphan",
        lazy=True,
    )
    detalhes_checkout = banco.relationship(
        "DetalhePedido",
        back_populates="pedido",
        uselist=False,
        cascade="all, delete-orphan",
        lazy=True,
    )
