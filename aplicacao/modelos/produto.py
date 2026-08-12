"""Modelo de dados de produto da Doce Pedido."""

from aplicacao import banco


class Produto(banco.Model):
    """Representa um item comercializado no catálogo."""
    id = banco.Column(banco.Integer, primary_key=True)
    categoria_id = banco.Column(
        banco.Integer, banco.ForeignKey("categoria.id"), nullable=False
    )
    nome = banco.Column(banco.String(120), nullable=False)
    descricao = banco.Column(banco.Text)
    preco = banco.Column(banco.Numeric(10, 2), nullable=False)
    estoque = banco.Column(banco.Integer, nullable=False, default=0)
    ativo = banco.Column(banco.Boolean, nullable=False, default=True)
    imagem = banco.Column(banco.String(255))
    categoria = banco.relationship("Categoria", back_populates="produtos")
    itens_pedido = banco.relationship("ItemPedido", back_populates="produto", lazy=True)

    @property
    def preco_formatado(self):
        return f"R$ {self.preco:.2f}".replace(".", ",")
