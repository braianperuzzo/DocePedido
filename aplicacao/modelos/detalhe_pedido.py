"""Detalhes de recebimento, pagamento e desconto registrados no pedido."""

from decimal import Decimal

from aplicacao import banco


class DetalhePedido(banco.Model):
    """Preserva como o cliente escolheu receber e pagar um pedido."""

    __tablename__ = "detalhe_pedido"

    id = banco.Column(banco.Integer, primary_key=True)
    pedido_id = banco.Column(
        banco.Integer,
        banco.ForeignKey("pedido.id"),
        nullable=False,
        unique=True,
        index=True,
    )
    tipo_entrega = banco.Column(banco.String(30), nullable=False)
    forma_pagamento = banco.Column(
        banco.String(30), nullable=False, default="Presencial"
    )
    valor_frete = banco.Column(
        banco.Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    cupom_codigo = banco.Column(banco.String(30))
    valor_desconto = banco.Column(
        banco.Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    endereco_entrega = banco.Column(banco.Text)

    pedido = banco.relationship("Pedido", back_populates="detalhes_checkout")
