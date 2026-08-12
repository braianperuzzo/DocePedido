"""Modelo de dados de categoria da Doce Pedido."""

from aplicacao import banco


class Categoria(banco.Model):
    """Representa uma categoria usada para agrupar produtos."""
    id = banco.Column(banco.Integer, primary_key=True)
    nome = banco.Column(banco.String(80), unique=True, nullable=False)
    descricao = banco.Column(banco.Text)
    ativo = banco.Column(banco.Boolean, nullable=False, default=True)
    produtos = banco.relationship("Produto", back_populates="categoria", lazy=True)
