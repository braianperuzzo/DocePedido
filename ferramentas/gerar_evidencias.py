"""Gera capturas finais da interface em um ambiente temporário e controlado.

O script é usado para produzir evidências reais da versão executada. Todos os
dados exibidos são sintéticos e existem somente durante a execução do processo
de captura.
"""

from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path
from threading import Thread

from flask import redirect, session
from flask_login import login_user
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server

from aplicacao import banco, criar_aplicacao
from aplicacao.controladores.carrinho import CHAVE_CARRINHO, CHAVE_CUPOM
from aplicacao.modelos import (
    Cliente,
    DetalhePedido,
    Endereco,
    Favorito,
    ItemPedido,
    Pedido,
    Produto,
)

RAIZ = Path(__file__).resolve().parents[1]
PASTA_EVIDENCIAS = (
    RAIZ
    / "documentacao"
    / "01-PLANEJAMENTO-E-MODELAGEM"
    / "evidencias"
)
BANCO_TEMPORARIO = Path("/tmp/doce-pedido-evidencias.db")

ARQUIVOS_GERADOS = [
    "01-home-desktop.png",
    "02-home-mobile.png",
    "03-catalogo-filtros.png",
    "04-produto.png",
    "05-carrinho-cupom.png",
    "06-login-cadastro.png",
    "07-minha-conta.png",
    "08-checkout.png",
    "09-pedido-confirmado.png",
    "10-meus-pedidos.png",
    "11-validacao-formulario.png",
    "12-offline.png",
    "13-faq-dark.png",
    "14-sobre-rodape.png",
    "15-favoritos.png",
    "16-seguranca.png",
]


@contextmanager
def servidor_evidencias():
    """Sobe a aplicação localmente com dados sintéticos para as capturas."""
    BANCO_TEMPORARIO.unlink(missing_ok=True)
    aplicacao = criar_aplicacao(
        {
            "TESTING": True,
            "SECRET_KEY": "evidencias-academicas-doce-pedido",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{BANCO_TEMPORARIO}",
            "INICIALIZAR_DADOS": True,
            "MAIL_SUPPRESS_SEND": True,
            "PASSWORD_ROTATION_ENABLED": False,
            "DEVICE_VALIDATION_ENABLED": False,
        }
    )

    with aplicacao.app_context():
        produtos = banco.session.scalars(
            banco.select(Produto).order_by(Produto.id)
        ).all()
        if len(produtos) < 2:
            raise RuntimeError("A carga inicial precisa possuir ao menos dois produtos.")

        cliente_novo = Cliente(
            nome="Cliente Demonstração",
            email="cliente.demonstracao@example.com",
            cpf="11144477735",
            telefone="54999999999",
        )
        cliente_novo.definir_senha("Demo#12345")
        banco.session.add(cliente_novo)
        banco.session.flush()

        banco.session.add(
            Endereco(
                cliente_id=cliente_novo.id,
                nome="Casa",
                cep="95000000",
                logradouro="Rua de Demonstração",
                numero="100",
                complemento="Apto 10",
                bairro="Centro",
                cidade="Caxias do Sul",
                uf="RS",
                referencia="Próximo à praça central",
                principal=True,
            )
        )
        banco.session.add(
            Favorito(cliente_id=cliente_novo.id, produto_id=produtos[0].id)
        )

        cliente_historico = Cliente(
            nome="Cliente Histórico",
            email="cliente.historico@example.com",
            cpf="12345678909",
            telefone="54988888888",
        )
        cliente_historico.definir_senha("Demo#12345")
        banco.session.add(cliente_historico)
        banco.session.flush()

        pedido = Pedido(
            cliente_id=cliente_historico.id,
            status="Recebido",
            valor_total=Decimal("15.30"),
        )
        pedido.itens.append(
            ItemPedido(
                produto=produtos[0],
                quantidade=2,
                valor_unitario=Decimal("8.50"),
                subtotal=Decimal("17.00"),
            )
        )
        pedido.detalhes_checkout = DetalhePedido(
            tipo_entrega="Entrega",
            forma_pagamento="Presencial",
            valor_frete=Decimal("0.00"),
            cupom_codigo="BEMVINDO",
            valor_desconto=Decimal("1.70"),
            endereco_entrega=(
                "Rua de Demonstração, 100 - Apto 10\n"
                "Centro - Caxias do Sul/RS\nCEP 95000-000"
            ),
        )
        banco.session.add(pedido)
        banco.session.commit()

        cliente_novo_id = cliente_novo.id
        cliente_historico_id = cliente_historico.id
        produto_id = produtos[0].id
        pedido_id = pedido.id

    @aplicacao.get("/_evidencias/preparar/<perfil>")
    def preparar_perfil(perfil):
        """Cria sessão de demonstração sem expor uma rota no aplicativo real."""
        session.clear()
        if perfil == "novo":
            cliente_id = cliente_novo_id
        elif perfil == "historico":
            cliente_id = cliente_historico_id
        else:
            return "Perfil de evidência inválido.", 404

        cliente = banco.session.get(Cliente, cliente_id)
        login_user(cliente)
        if perfil == "novo":
            session[CHAVE_CARRINHO] = {str(produto_id): 2}
            session[CHAVE_CUPOM] = "BEMVINDO"
        return redirect("/")

    servidor = make_server("127.0.0.1", 0, aplicacao)
    thread = Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{servidor.server_port}", pedido_id
    finally:
        servidor.shutdown()
        thread.join(timeout=5)
        BANCO_TEMPORARIO.unlink(missing_ok=True)


def fechar_banner_cookies(pagina):
    """Evita que o banner cubra o conteúdo principal das evidências."""
    botao = pagina.locator("[data-cookie-reject]")
    if botao.count() and botao.first.is_visible():
        botao.first.click()
        pagina.wait_for_timeout(150)


def capturar(
    navegador,
    base_url,
    arquivo,
    rota,
    viewport,
    *,
    perfil=None,
    tema="light",
    pagina_inteira=False,
    preparar=None,
):
    """Abre uma rota, estabiliza a interface e grava a captura em PNG."""
    contexto = navegador.new_context(
        viewport=viewport,
        reduced_motion="reduce",
        service_workers="allow",
    )
    contexto.add_init_script(
        f"localStorage.setItem('doce_pedido_tema', {tema!r});"
    )
    pagina = contexto.new_page()
    pagina.set_default_timeout(15000)
    try:
        if perfil:
            pagina.goto(
                f"{base_url}/_evidencias/preparar/{perfil}",
                wait_until="networkidle",
            )
        pagina.goto(f"{base_url}{rota}", wait_until="networkidle")
        fechar_banner_cookies(pagina)
        if preparar:
            preparar(pagina)
        pagina.wait_for_timeout(250)
        pagina.screenshot(
            path=str(PASTA_EVIDENCIAS / arquivo),
            full_page=pagina_inteira,
        )
    finally:
        contexto.close()


def expandir_primeira_pergunta(pagina):
    """Expande uma pergunta para evidenciar o comportamento corrigido da FAQ."""
    botao = pagina.locator(".faq-accordion .accordion-button").first
    if botao.count():
        botao.click()
        pagina.wait_for_timeout(150)


def provocar_mensagem_login(pagina):
    """Gera uma mensagem real do site sem usar dados pessoais."""
    pagina.locator("#login-email").fill("nao.existe@example.com")
    pagina.locator("#login-senha").fill("Senha#Invalida123")
    pagina.locator("form[action$='/login'] button[type='submit']").click()
    pagina.wait_for_load_state("networkidle")
    fechar_banner_cookies(pagina)


def gerar_evidencias():
    """Produz as 16 capturas principais da versão final."""
    PASTA_EVIDENCIAS.mkdir(parents=True, exist_ok=True)

    # Remove somente as evidências que este script recria. Os arquivos 17 a 19
    # são complementares do laudo e não devem ser apagados por esta rotina.
    for nome in ARQUIVOS_GERADOS:
        (PASTA_EVIDENCIAS / nome).unlink(missing_ok=True)

    desktop = {"width": 1440, "height": 900}
    mobile = {"width": 390, "height": 844}

    with (
        servidor_evidencias() as (base_url, pedido_id),
        sync_playwright() as playwright,
    ):
        navegador = playwright.chromium.launch()
        try:
            capturar(navegador, base_url, "01-home-desktop.png", "/", desktop)
            capturar(navegador, base_url, "02-home-mobile.png", "/", mobile)
            capturar(
                navegador,
                base_url,
                "03-catalogo-filtros.png",
                "/produtos?categoria=Especiais&disponibilidade=disponivel&ordem=preco_asc",
                desktop,
            )
            capturar(navegador, base_url, "04-produto.png", "/produtos/1", desktop)
            capturar(
                navegador,
                base_url,
                "05-carrinho-cupom.png",
                "/carrinho",
                desktop,
                perfil="novo",
            )
            capturar(navegador, base_url, "06-login-cadastro.png", "/login", desktop)
            capturar(
                navegador,
                base_url,
                "07-minha-conta.png",
                "/minha-conta",
                desktop,
                perfil="novo",
            )
            capturar(
                navegador,
                base_url,
                "08-checkout.png",
                "/pedidos/revisar",
                desktop,
                perfil="novo",
            )
            capturar(
                navegador,
                base_url,
                "09-pedido-confirmado.png",
                f"/pedidos/confirmacao/{pedido_id}",
                desktop,
                perfil="historico",
            )
            capturar(
                navegador,
                base_url,
                "10-meus-pedidos.png",
                "/pedidos",
                desktop,
                perfil="historico",
            )
            capturar(
                navegador,
                base_url,
                "11-validacao-formulario.png",
                "/login",
                desktop,
                preparar=provocar_mensagem_login,
            )
            capturar(
                navegador,
                base_url,
                "12-offline.png",
                "/offline",
                mobile,
                tema="dark",
            )
            capturar(
                navegador,
                base_url,
                "13-faq-dark.png",
                "/faq",
                mobile,
                tema="dark",
                preparar=expandir_primeira_pergunta,
            )
            capturar(
                navegador,
                base_url,
                "14-sobre-rodape.png",
                "/sobre",
                desktop,
                pagina_inteira=True,
            )
            capturar(
                navegador,
                base_url,
                "15-favoritos.png",
                "/minha-conta/favoritos",
                desktop,
                perfil="novo",
            )
            capturar(
                navegador,
                base_url,
                "16-seguranca.png",
                "/seguranca",
                desktop,
                pagina_inteira=True,
            )
        finally:
            navegador.close()

    print(f"Evidências geradas em: {PASTA_EVIDENCIAS}")


if __name__ == "__main__":
    gerar_evidencias()
