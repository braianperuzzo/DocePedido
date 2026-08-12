"""Testes de conftest da aplicação."""

import re
from decimal import Decimal

import pytest

from aplicacao import banco, criar_aplicacao
from aplicacao.modelos import Categoria, Cliente, Produto


def normalizar_html(conteudo):
    """Remove espacos de formatacao sem mascarar o conteudo renderizado."""
    conteudo = re.sub(r"\s+", " ", conteudo)
    conteudo = re.sub(r">\s+", ">", conteudo)
    return re.sub(r"\s+<", "<", conteudo)


@pytest.fixture
def aplicacao(tmp_path):
    app = criar_aplicacao(
        {
            "TESTING": True,
            "SECRET_KEY": "segredo-de-teste",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'testes.db'}",
            "INICIALIZAR_DADOS": False,
            "SITE_URL": "",
        }
    )
    with app.app_context():
        categoria = Categoria(nome="Tradicionais")
        produtos = [
            Produto(
                nome="Chocolate",
                descricao="Cupcake",
                preco=Decimal("10.00"),
                estoque=10,
                ativo=True,
                categoria=categoria,
            ),
            Produto(
                nome="Morango",
                descricao="Cupcake",
                preco=Decimal("15.00"),
                estoque=5,
                ativo=True,
                categoria=categoria,
            ),
            Produto(
                nome="Inativo",
                descricao="Cupcake",
                preco=Decimal("8.00"),
                estoque=5,
                ativo=False,
                categoria=categoria,
            ),
        ]
        cliente = Cliente(
            nome="Ana",
            email="ana@example.com",
            cpf="11144477735",
        )
        cliente.definir_senha("segredo12")
        outro = Cliente(
            nome="Bia",
            email="bia@example.com",
            cpf="12345678909",
        )
        outro.definir_senha("segredo12")
        banco.session.add_all([*produtos, cliente, outro])
        banco.session.commit()
    yield app
    with app.app_context():
        banco.session.remove()
        banco.drop_all()


@pytest.fixture
def cliente_http(aplicacao):
    return aplicacao.test_client()


@pytest.fixture
def login(cliente_http):
    def fazer_login(email="ana@example.com", senha="segredo12"):
        return cliente_http.post(
            "/login", data={"email": email, "senha": senha}, follow_redirects=True
        )

    return fazer_login


@pytest.fixture
def adicionar(cliente_http):
    def adicionar_produto(produto_id=1, quantidade=1, seguir=True):
        return cliente_http.post(
            f"/carrinho/adicionar/{produto_id}",
            data={"quantidade": quantidade},
            follow_redirects=seguir,
        )

    return adicionar_produto
