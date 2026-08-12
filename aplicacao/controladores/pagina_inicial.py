"""Rotas da página inicial da Doce Pedido."""

from flask import Blueprint, render_template
from sqlalchemy.orm import selectinload

from aplicacao import banco
from aplicacao.modelos import Produto

pagina_inicial = Blueprint("pagina_inicial", __name__)


@pagina_inicial.get("/")
def inicio():
    """Exibe a página inicial com produtos ativos em uma ordem estável."""
    consulta = (
        banco.select(Produto)
        .options(selectinload(Produto.categoria))
        .where(Produto.ativo.is_(True))
        .order_by(Produto.id.asc())
        .limit(8)
    )
    destaques = banco.session.scalars(consulta).all()
    kit = banco.session.scalar(
        banco.select(Produto).where(
            Produto.ativo.is_(True), Produto.nome == "Kit com 6 Cupcakes"
        )
    )
    return render_template("pagina_inicial/index.html", destaques=destaques, kit=kit)
