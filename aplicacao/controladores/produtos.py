"""Rotas e regras de produtos da Doce Pedido."""

from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import selectinload

from aplicacao import banco
from aplicacao.modelos import Categoria, Produto

produtos = Blueprint("produtos", __name__)


@produtos.get("/produtos")
def catalogo():
    """Lista produtos ativos com filtros e ordenação."""
    categoria = request.args.get("categoria", "").strip().lower()[:80]
    disponibilidade = request.args.get("disponibilidade", "").strip().lower()
    ordem = request.args.get("ordem", "").strip().lower()
    termo = request.args.get("q", "").strip()[:100]
    consulta = (
        banco.select(Produto)
        .options(selectinload(Produto.categoria))
        .join(Produto.categoria)
        .where(Produto.ativo.is_(True))
    )
    if categoria:
        consulta = consulta.where(Categoria.nome.ilike(categoria))
    if disponibilidade == "disponivel":
        consulta = consulta.where(Produto.estoque > 0)
    if termo:
        padrao = f"%{termo}%"
        consulta = consulta.where(
            or_(
                Produto.nome.ilike(padrao),
                Produto.descricao.ilike(padrao),
                Categoria.nome.ilike(padrao),
            )
        )
    ordenacoes = {
        "nome_asc": asc(Produto.nome),
        "nome_desc": desc(Produto.nome),
        "preco_asc": asc(Produto.preco),
        "preco_desc": desc(Produto.preco),
    }
    consulta = consulta.order_by(ordenacoes.get(ordem, asc(Produto.id)))
    produtos_disponiveis = banco.session.scalars(consulta).all()
    return render_template(
        "produtos/catalogo.html",
        produtos=produtos_disponiveis,
        filtros={
            "categoria": categoria,
            "disponibilidade": disponibilidade,
            "ordem": ordem,
            "q": termo,
        },
    )


@produtos.get("/produtos/<int:produto_id>")
def detalhes(produto_id):
    """Exibe um recurso solicitado quando acessível ao cliente."""
    produto = banco.get_or_404(Produto, produto_id)
    if not produto.ativo:
        return render_template("erros/produto_indisponivel.html"), 404

    return render_template("produtos/detalhes.html", produto=produto)


@produtos.get("/buscar")
def buscar():
    """Busca produtos ativos pelo termo informado."""
    termo = request.args.get("q", "").strip()
    if not termo:
        return redirect(url_for("produtos.catalogo"))

    padrao = f"%{termo[:100]}%"
    consulta = (
        banco.select(Produto)
        .options(selectinload(Produto.categoria))
        .join(Produto.categoria)
        .where(
            Produto.ativo.is_(True),
            or_(
                Produto.nome.ilike(padrao),
                Produto.descricao.ilike(padrao),
                Categoria.nome.ilike(padrao),
            ),
        )
        .order_by(Produto.nome)
    )
    resultados = banco.session.scalars(consulta).unique().all()
    return render_template(
        "produtos/busca.html", produtos=resultados, termo=termo[:100]
    )
