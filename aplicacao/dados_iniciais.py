"""Carga idempotente dos dados iniciais usados pelo catálogo."""

from decimal import Decimal

from aplicacao import banco
from aplicacao.modelos import Categoria, Produto

CATEGORIAS_INICIAIS = {
    "Tradicionais": "Sabores clássicos para todos os momentos.",
    "Especiais": "Receitas especiais com acabamentos caprichados.",
    "Kits": "Seleções para compartilhar e presentear.",
}

PRODUTOS_INICIAIS = {
    "Cupcake de Chocolate": {
        "categoria": "Tradicionais",
        "descricao": "Massa de chocolate e cobertura cremosa de brigadeiro.",
        "preco": Decimal("8.50"),
        "estoque": 30,
        "imagem": "imagens/cupcake_chocolate.webp",
    },
    "Cupcake de Baunilha": {
        "categoria": "Tradicionais",
        "descricao": "Massa leve de baunilha com cobertura suave.",
        "preco": Decimal("8.00"),
        "estoque": 25,
        "imagem": "imagens/cupcake_baunilha.webp",
    },
    "Cupcake Red Velvet": {
        "categoria": "Especiais",
        "descricao": "Massa aveludada com cobertura de cream cheese.",
        "preco": Decimal("10.50"),
        "estoque": 20,
        "imagem": "imagens/cupcake_red_velvet.webp",
    },
    "Cupcake de Morango": {
        "categoria": "Especiais",
        "descricao": "Massa de baunilha, recheio de morango e cobertura delicada.",
        "preco": Decimal("9.50"),
        "estoque": 20,
        "imagem": "imagens/cupcake_morango.webp",
    },
    "Kit com 6 Cupcakes": {
        "categoria": "Kits",
        "descricao": "Caixa com seis cupcakes de sabores variados.",
        "preco": Decimal("48.00"),
        "estoque": 12,
        "imagem": "imagens/cupcake_kit_6.webp",
    },
}


def criar_dados_iniciais():
    """Completa somente registros ausentes e corrige caminhos conhecidos de imagens."""
    categorias = {
        categoria.nome: categoria
        for categoria in banco.session.scalars(banco.select(Categoria)).all()
    }
    alterado = False

    for nome, descricao in CATEGORIAS_INICIAIS.items():
        if nome in categorias:
            continue
        categoria = Categoria(nome=nome, descricao=descricao)
        banco.session.add(categoria)
        categorias[nome] = categoria
        alterado = True

    if alterado:
        banco.session.flush()

    produtos = {
        produto.nome: produto
        for produto in banco.session.scalars(banco.select(Produto)).all()
    }
    for nome, dados in PRODUTOS_INICIAIS.items():
        existente = produtos.get(nome)
        if existente:
            if existente.imagem != dados["imagem"]:
                existente.imagem = dados["imagem"]
                alterado = True
            continue

        banco.session.add(
            Produto(
                categoria=categorias[dados["categoria"]],
                nome=nome,
                descricao=dados["descricao"],
                preco=dados["preco"],
                estoque=dados["estoque"],
                imagem=dados["imagem"],
            )
        )
        alterado = True

    if alterado:
        banco.session.commit()
