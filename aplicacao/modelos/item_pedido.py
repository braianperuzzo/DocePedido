"""Modelo de dados de item pedido da Doce Pedido."""

from aplicacao import banco


class ItemPedido(banco.Model):
    """Registra um produto e seus valores dentro de um pedido."""
    __tablename__ = "item_pedido"

    id = banco.Column(banco.Integer, primary_key=True)
    pedido_id = banco.Column(
        banco.Integer, banco.ForeignKey("pedido.id"), nullable=False
    )
    produto_id = banco.Column(
        banco.Integer, banco.ForeignKey("produto.id"), nullable=False
    )
    quantidade = banco.Column(banco.Integer, nullable=False)
    valor_unitario = banco.Column(banco.Numeric(10, 2), nullable=False)
    subtotal = banco.Column(banco.Numeric(10, 2), nullable=False)
    pedido = banco.relationship("Pedido", back_populates="itens")
    produto = banco.relationship("Produto", back_populates="itens_pedido")
