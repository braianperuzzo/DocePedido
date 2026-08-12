"""Testes de frontend playwright da aplicação."""

from contextlib import contextmanager
from threading import Thread

import pytest
from flask import flash, redirect
from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server

from aplicacao import criar_aplicacao

VIEWPORTS = (
    {"width": 320, "height": 568},
    {"width": 360, "height": 800},
    {"width": 375, "height": 667},
    {"width": 390, "height": 844},
    {"width": 414, "height": 896},
    {"width": 768, "height": 1024},
    {"width": 1024, "height": 768},
    {"width": 1280, "height": 720},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1920, "height": 1080},
)

HOME_VIEWPORTS = (
    {"width": 320, "height": 568},
    {"width": 360, "height": 800},
    {"width": 390, "height": 844},
    {"width": 414, "height": 896},
    {"width": 768, "height": 1024},
    {"width": 1024, "height": 768},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1920, "height": 1080},
)

CATALOG_VIEWPORTS = (
    {"width": 320, "height": 568},
    {"width": 360, "height": 800},
    {"width": 390, "height": 844},
    {"width": 768, "height": 1024},
    {"width": 1024, "height": 768},
    {"width": 1366, "height": 768},
    {"width": 1920, "height": 1080},
)

TOLERANCIA_GEOMETRICA = 4
ROTAS_INSTITUCIONAIS = ("/sobre", "/faq", "/entrega", "/privacidade")


@contextmanager
def servidor_frontend(tmp_path):
    aplicacao = criar_aplicacao(
        {
            "TESTING": True,
            "SECRET_KEY": "segredo-frontend",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'frontend.db'}",
            "INICIALIZAR_DADOS": True,
            "SITE_URL": "",
        }
    )

    @aplicacao.get("/_teste/alertas")
    def exibir_alertas_de_teste():
        """Disponibiliza mensagens globais para a verificação visual isolada."""
        flash("Operação concluída.", "success")
        flash("Confira os dados informados.", "warning")
        flash("Informação adicional.", "info")
        return redirect("/")

    servidor = make_server("127.0.0.1", 0, aplicacao)
    thread = Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{servidor.server_port}"
    finally:
        servidor.shutdown()
        thread.join(timeout=5)


def validar_pagina(page, url):
    erros_console = []
    erros_pagina = []
    recursos_404 = []
    page.on(
        "console",
        lambda mensagem: (
            erros_console.append(mensagem.text) if mensagem.type == "error" else None
        ),
    )
    page.on("pageerror", lambda erro: erros_pagina.append(str(erro)))
    page.on(
        "response",
        lambda resposta: (
            recursos_404.append(resposta.url)
            if resposta.url.startswith(url) and resposta.status == 404
            else None
        ),
    )

    page.goto(url, wait_until="networkidle")
    page.evaluate("scrollTo(0, document.documentElement.scrollHeight)")
    page.wait_for_timeout(250)

    assert page.locator("main").is_visible()
    assert not page.evaluate(
        "document.documentElement.scrollWidth > document.documentElement.clientWidth"
    )
    assert not erros_console
    assert not erros_pagina
    assert not recursos_404

    for svg in page.locator("svg").all():
        if not svg.is_visible():
            continue
        caixa = svg.bounding_box()
        assert caixa
        assert caixa["width"] > 0 and caixa["height"] > 0

    for imagem in page.locator("img").all():
        imagem.scroll_into_view_if_needed()
        page.wait_for_function(
            "elemento => elemento.complete && elemento.naturalWidth > 0",
            arg=imagem.element_handle(),
        )
        assert imagem.evaluate(
            "elemento => elemento.complete && elemento.naturalWidth > 0"
        )


def test_breadcrumbs_institucionais_permanecem_visiveis_no_tema_escuro(tmp_path):
    """Compara texto ativo e separador com o fundo das páginas institucionais."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        contexto = navegador.new_context(service_workers="block")
        contexto.add_init_script(
            "localStorage.setItem('doce_pedido_tema', 'dark')"
        )
        pagina = contexto.new_page()
        try:
            for rota in ROTAS_INSTITUCIONAIS:
                pagina.goto(f"{base_url}{rota}", wait_until="networkidle")
                cores = pagina.evaluate("""() => ({
                    fundo: getComputedStyle(document.body).backgroundColor,
                    ativo: getComputedStyle(document.querySelector('.breadcrumb-item.active')).color,
                    link: getComputedStyle(document.querySelector('.breadcrumb-item a')).color,
                    separador: getComputedStyle(
                        document.querySelector('.breadcrumb-item + .breadcrumb-item'),
                        '::before'
                    ).color
                })""")
                assert cores["ativo"] != cores["fundo"]
                assert cores["link"] != cores["fundo"]
                assert cores["separador"] != cores["fundo"]
        finally:
            contexto.close()
            navegador.close()


@pytest.mark.parametrize(
    "viewport",
    (
        {"width": 320, "height": 568},
        {"width": 360, "height": 800},
        {"width": 390, "height": 844},
        {"width": 414, "height": 896},
    ),
)
def test_faq_compacto_interativo_e_sem_overflow_no_tema_escuro(
    tmp_path, viewport
):
    """Valida accordion exclusivo, contraste, teclado e geometria no mobile."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        contexto = navegador.new_context(
            viewport=viewport, service_workers="block"
        )
        contexto.add_init_script(
            "localStorage.setItem('doce_pedido_tema', 'dark')"
        )
        pagina = contexto.new_page()
        try:
            pagina.goto(f"{base_url}/faq", wait_until="networkidle")
            pagina.locator("[data-cookie-accept]").click()
            perguntas = pagina.locator(".faq-accordion .accordion-button")
            respostas = pagina.locator(".faq-accordion .accordion-collapse")

            assert perguntas.count() == respostas.count() == 10
            assert all(
                estado == "false"
                for estado in perguntas.evaluate_all(
                    "elements => elements.map(element => element.getAttribute('aria-expanded'))"
                )
            )
            perguntas.first.focus()
            pagina.keyboard.press("Enter")
            expect(perguntas.first).to_have_attribute("aria-expanded", "true")
            expect(respostas.first).to_be_visible()

            perguntas.nth(1).click()
            expect(perguntas.first).to_have_attribute("aria-expanded", "false")
            expect(perguntas.nth(1)).to_have_attribute("aria-expanded", "true")
            expect(respostas.nth(1)).to_be_visible()

            estilos = pagina.evaluate("""() => {
                const item = document.querySelector('.faq-accordion .accordion-item');
                const button = document.querySelector('.faq-accordion .accordion-button:not(.collapsed)');
                const body = document.querySelector('.faq-accordion .accordion-body');
                return {
                    bodyBackground: getComputedStyle(document.body).backgroundColor,
                    itemBackground: getComputedStyle(item).backgroundColor,
                    itemBorder: getComputedStyle(item).borderColor,
                    buttonBackground: getComputedStyle(button).backgroundColor,
                    buttonColor: getComputedStyle(button).color,
                    answerColor: getComputedStyle(body).color
                };
            }""")
            assert estilos["itemBackground"] != estilos["bodyBackground"]
            assert estilos["itemBorder"] != estilos["itemBackground"]
            assert estilos["buttonBackground"] != estilos["bodyBackground"]
            assert estilos["buttonColor"] != estilos["buttonBackground"]
            assert estilos["answerColor"] != estilos["itemBackground"]
            assert not pagina.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
            assert all(
                caixa["width"] <= viewport["width"]
                for caixa in perguntas.evaluate_all(
                    "elements => elements.map(element => "
                    "element.getBoundingClientRect().toJSON())"
                )
            )
        finally:
            contexto.close()
            navegador.close()


@pytest.mark.parametrize("tema", ("light", "dark"))
@pytest.mark.parametrize("largura", (320, 1366))
def test_alertas_globais_flutuam_e_podem_ser_fechados(
    tmp_path, tema, largura
):
    """Valida empilhamento, temas e fechamento sem deslocar o conteúdo."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        contexto = navegador.new_context(
            viewport={"width": largura, "height": 800}, service_workers="block"
        )
        contexto.add_init_script(
            f"localStorage.setItem('doce_pedido_tema', '{tema}')"
        )
        pagina = contexto.new_page()
        try:
            pagina.goto(base_url, wait_until="networkidle")
            geometria_sem_alerta = pagina.locator(".hero").bounding_box()
            pagina.goto(f"{base_url}/_teste/alertas", wait_until="networkidle")

            area = pagina.locator(".flash-area")
            alertas = area.locator(".alert")
            geometria_com_alerta = pagina.locator(".hero").bounding_box()
            assert area.evaluate("el => getComputedStyle(el).position") == "fixed"
            assert geometria_sem_alerta == geometria_com_alerta
            assert alertas.count() == 3
            caixas = alertas.evaluate_all(
                "els => els.map(el => el.getBoundingClientRect()).map(r => "
                "({top: r.top, bottom: r.bottom, right: r.right}))"
            )
            assert all(
                caixas[indice]["bottom"] < caixas[indice + 1]["top"]
                for indice in range(len(caixas) - 1)
            )
            assert all(caixa["right"] <= largura for caixa in caixas)
            botoes_fechar = area.get_by_role("button", name="Fechar")
            assert botoes_fechar.count() == 3
            botoes_fechar.first.click()
            expect(alertas).to_have_count(2)
        finally:
            contexto.close()
            navegador.close()


def test_alerta_global_fecha_automaticamente_no_prazo_configurado(tmp_path):
    """Acelera somente o temporizador do alerta para manter a suíte rápida."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        contexto = navegador.new_context(service_workers="block")
        contexto.add_init_script("""(() => {
            const setTimeoutNativo = window.setTimeout.bind(window);
            window.setTimeout = (callback, atraso, ...argumentos) =>
                setTimeoutNativo(callback, atraso === 10000 ? 30 : atraso, ...argumentos);
        })();""")
        pagina = contexto.new_page()
        try:
            pagina.goto(f"{base_url}/_teste/alertas", wait_until="domcontentloaded")
            expect(pagina.locator(".flash-area .alert")).to_have_count(0, timeout=1000)
        finally:
            contexto.close()
            navegador.close()


@pytest.mark.parametrize("tema", ("light", "dark"))
def test_detalhe_produto_compacto_e_legivel_no_desktop(tmp_path, tema):
    """Valida geometria essencial e contraste temático do detalhe do produto."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        contexto = navegador.new_context(
            viewport={"width": 1366, "height": 768}, service_workers="block"
        )
        contexto.add_init_script(
            f"localStorage.setItem('doce_pedido_tema', '{tema}')"
        )
        pagina = contexto.new_page()
        try:
            pagina.goto(f"{base_url}/produtos/1", wait_until="networkidle")
            imagem = pagina.locator(".product-detail-image").bounding_box()
            informacoes = pagina.locator(".product-detail-content").bounding_box()
            quantidade = pagina.locator(".purchase-form .quantity-row").bounding_box()
            botao = pagina.get_by_role("button", name="Carrinho").bounding_box()
            container = pagina.locator(".product-detail").bounding_box()
            breadcrumb = pagina.locator(".product-breadcrumb").bounding_box()

            assert all((imagem, informacoes, quantidade, botao, container, breadcrumb))
            assert abs(imagem["y"] - informacoes["y"]) <= TOLERANCIA_GEOMETRICA
            assert imagem["height"] <= 420
            assert (
                informacoes["y"] + informacoes["height"]
                <= imagem["y"] + imagem["height"] + TOLERANCIA_GEOMETRICA
            )
            assert abs(quantidade["y"] - botao["y"]) <= TOLERANCIA_GEOMETRICA
            assert container["x"] >= 0
            assert container["x"] + container["width"] <= 1366
            assert breadcrumb["width"] <= container["width"]
            assert botao["y"] + botao["height"] <= 768
            assert not pagina.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )

            cores = pagina.evaluate("""() => ({
                fundo: getComputedStyle(document.body).backgroundColor,
                breadcrumb: getComputedStyle(document.querySelector('.breadcrumb')).backgroundColor,
                ativo: getComputedStyle(document.querySelector('.breadcrumb-item.active')).color,
                separador: getComputedStyle(document.querySelector('.breadcrumb-item + .breadcrumb-item'), '::before').color
            })""")
            assert cores["breadcrumb"] == "rgba(0, 0, 0, 0)"
            assert cores["ativo"] != cores["fundo"]
            assert cores["separador"] != cores["fundo"]
            for seletor in (
                ".product-detail-title",
                ".product-detail-description",
                ".detail-price",
                ".availability",
                ".quantity-input",
                ".purchase-cta",
            ):
                expect(pagina.locator(seletor)).to_be_visible()
        finally:
            contexto.close()
            navegador.close()


@pytest.mark.parametrize("largura, altura", ((320, 568), (390, 844)))
def test_detalhe_produto_mobile_sem_overflow(tmp_path, largura, altura):
    """Mantém imagem, breadcrumb e ações utilizáveis nos menores viewports."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        pagina = navegador.new_page(viewport={"width": largura, "height": altura})
        try:
            pagina.goto(f"{base_url}/produtos/1", wait_until="networkidle")
            imagem = pagina.locator(".product-detail-image").bounding_box()
            breadcrumb = pagina.locator(".product-breadcrumb").bounding_box()
            quantidade = pagina.locator(".purchase-form .quantity-row").bounding_box()
            botao = pagina.get_by_role("button", name="Carrinho")

            assert imagem and imagem["height"] <= 340
            assert breadcrumb and breadcrumb["width"] <= largura
            assert quantidade and quantidade["width"] < largura
            expect(botao).to_be_visible()
            assert botao.bounding_box()["width"] <= largura
            assert not pagina.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
        finally:
            navegador.close()


@pytest.mark.parametrize("tema", ("light", "dark"))
def test_home_nao_emite_erros_nem_requisita_fontes_externas(tmp_path, tema):
    """Valida console, recursos internos e fontes da Home em Chromium limpo."""
@pytest.mark.parametrize(
    "viewport",
    CATALOG_VIEWPORTS,
    ids=lambda viewport: f"catalogo-{viewport['width']}-{viewport['height']}",
)
def test_cards_compactos_do_catalogo_e_busca(tmp_path, viewport):
    """Valida proporção fluida, controles e ausência de clipping nos resultados."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            pagina = navegador.new_page(viewport=viewport)
            for caminho in ("/produtos", "/buscar?q=Cupcake"):
                pagina.goto(f"{base_url}{caminho}", wait_until="networkidle")
                cards = pagina.locator(".products-grid .product-card")
                assert cards.count() > 0
                for card in cards.all():
                    caixa = card.bounding_box()
                    assert caixa is not None
                    assert caixa["height"] / caixa["width"] <= 1.9
                    assert card.locator(".product-actions .btn").count() > 0
                    assert card.evaluate(
                        """elemento => {
                            const limite = elemento.getBoundingClientRect();
                            return [...elemento.querySelectorAll('.product-actions .btn')]
                                .every(botao => {
                                    const caixa = botao.getBoundingClientRect();
                                    return caixa.left >= limite.left && caixa.right <= limite.right
                                        && caixa.top >= limite.top && caixa.bottom <= limite.bottom;
                                });
                        }"""
                    )
                assert not pagina.evaluate(
                    "document.documentElement.scrollWidth > document.documentElement.clientWidth"
                )

            pagina.goto(f"{base_url}/produtos", wait_until="networkidle")
            pagina.evaluate("document.documentElement.dataset.theme = 'dark'")
            placeholder = pagina.locator(".catalog-filters .form-control").evaluate(
                "elemento => getComputedStyle(elemento, '::placeholder').color"
            )
            texto_secundario = pagina.evaluate(
                """() => {
                    const referencia = document.createElement('span');
                    referencia.style.color = 'var(--cor-texto-secundario)';
                    document.body.append(referencia);
                    const cor = getComputedStyle(referencia).color;
                    referencia.remove();
                    return cor;
                }"""
            )
            assert placeholder == texto_secundario
        finally:
            navegador.close()


@pytest.mark.parametrize("tema", ["light", "dark"])
def test_home_nao_requisita_fontes_externas_nem_viola_csp(tmp_path, tema):
    """Captura a regressão que fazia o navegador solicitar fontes do Google."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            contexto = navegador.new_context(service_workers="block")
            contexto.add_init_script(
                f"localStorage.setItem('doce_pedido_tema', '{tema}')"
            )
            pagina = contexto.new_page()
            requisicoes = []
            erros = []
            recursos_404 = []
            pagina.on("request", lambda requisicao: requisicoes.append(requisicao.url))
            pagina.on(
                "console",
                lambda mensagem: (
                    erros.append(mensagem.text) if mensagem.type == "error" else None
                ),
            )
            pagina.on("pageerror", lambda erro: erros.append(str(erro)))
            pagina.on(
                "response",
                lambda resposta: (
                    recursos_404.append(resposta.url)
                    if resposta.url.startswith(base_url) and resposta.status == 404
                    else None
                ),
            )

            resposta = pagina.goto(base_url, wait_until="networkidle")

            assert resposta.ok
            assert pagina.locator("html").get_attribute("data-theme") == tema
            assert not erros
            assert not recursos_404
            assert not any(
                origem in url
                for url in requisicoes
                for origem in ("fonts.googleapis.com", "fonts.gstatic.com")
            )
        finally:
            navegador.close()


@pytest.mark.parametrize(
    "viewport",
    VIEWPORTS,
    ids=lambda viewport: f"{viewport['width']}-{viewport['height']}",
)
def test_interface_nos_viewports_de_regressao(tmp_path, viewport):
    """Identifica isoladamente a resolução que apresentar uma regressão."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            contexto = navegador.new_context(
                viewport=viewport,
                service_workers="block",
            )
            pagina = contexto.new_page()
            pagina.goto(base_url, wait_until="networkidle")
            pagina.locator("[data-cookie-accept]").click()

            validar_pagina(pagina, f"{base_url}/")
            validar_pagina(pagina, f"{base_url}/produtos")
            validar_pagina(pagina, f"{base_url}/produtos/1")

            if viewport["width"] >= 768:
                assert pagina.goto(f"{base_url}/produtos").ok
                assert pagina.locator("#catalog-filters").is_visible()

            if viewport["width"] < 1200:
                pagina.goto(base_url, wait_until="networkidle")
                pagina.locator(".navbar-toggler").click()
                assert pagina.locator("#menu").is_visible()
                assert pagina.locator(".header-search").is_visible()

            validar_pagina(pagina, f"{base_url}/offline")
            titulo_offline = pagina.get_by_role(
                "heading",
                name="Sem Conexão",
            )
            assert titulo_offline.is_visible()
            assert pagina.locator("html").get_attribute("data-theme") == "light"
            assert pagina.get_by_role(
                "button",
                name="Tentar Novamente",
            ).is_visible()
            favicon = pagina.locator('link[rel="icon"]').get_attribute("href")
            assert favicon.endswith("favicon-32.png")
            assert pagina.locator(".offline-wifi").evaluate(
                "elemento => elemento.getBoundingClientRect().width <= 48"
            )
            assert pagina.locator(".offline-retry-icon").evaluate(
                "elemento => elemento.getBoundingClientRect().width <= 20"
            )
            assert pagina.evaluate(
                "document.documentElement.scrollWidth "
                "<= document.documentElement.clientWidth"
            )
            pagina.locator("[data-retry]").click()
            assert pagina.locator("[data-retry-label]").text_content() in (
                "Verificando...",
                "Atualizando...",
            )
            pagina.wait_for_load_state("networkidle")
            assert pagina.url == f"{base_url}/offline"
            contexto.close()
        finally:
            navegador.close()


def test_dropdown_sobre_permanece_aberto_ate_o_clique_no_item(tmp_path):
    """Protege a travessia que antes cruzava uma lacuna e fechava o dropdown."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            pagina = navegador.new_page(viewport={"width": 1440, "height": 900})
            pagina.goto(base_url, wait_until="networkidle")
            gatilho = pagina.get_by_role("button", name="Sobre")
            opcao = pagina.get_by_role("link", name="Sobre a Doce Pedido").first

            gatilho.hover()
            expect(gatilho).to_have_attribute("aria-expanded", "true")
            expect(opcao).to_be_visible()
            opcao.hover()
            expect(opcao).to_be_visible()
            opcao.click()

            assert pagina.url == f"{base_url}/sobre"
            assert pagina.get_by_role(
                "heading", name="Sobre a Doce Pedido"
            ).is_visible()
        finally:
            navegador.close()


@pytest.mark.parametrize(
    "viewport",
    tuple(viewport for viewport in HOME_VIEWPORTS if viewport["width"] >= 1200),
    ids=lambda viewport: f"{viewport['width']}-{viewport['height']}",
)
def test_cabecalho_desktop_preserva_alinhamento_e_busca_expansivel(tmp_path, viewport):
    """Protege a Minha Conta compacta, clicável e a busca recolhível do desktop."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            pagina = navegador.new_page(viewport=viewport)
            pagina.goto(base_url, wait_until="networkidle")

            sobre = pagina.get_by_role("button", name="Sobre")
            conta = pagina.get_by_role("link", name="Minha Conta")
            bloco_conta = conta.locator("xpath=..")
            entrar = bloco_conta.get_by_role("link", name="Entrar")
            cadastrar = bloco_conta.get_by_role("link", name="Cadastrar")
            busca = pagina.locator("[data-header-search]")
            botao_busca = busca.locator("[data-search-toggle]")
            campo = busca.locator("input")

            expect(conta).to_be_visible()
            expect(entrar).to_be_visible()
            expect(cadastrar).to_be_visible()
            assert bloco_conta.get_attribute("data-header-dropdown") is None

            caixa_bloco = bloco_conta.bounding_box()
            caixa_titulo = conta.bounding_box()
            caixa_entrar = entrar.bounding_box()
            caixa_sobre = sobre.bounding_box()
            assert caixa_bloco and caixa_titulo and caixa_entrar and caixa_sobre

            assert (
                caixa_titulo["y"] + caixa_titulo["height"]
                <= caixa_entrar["y"] + TOLERANCIA_GEOMETRICA
            )
            centro_sobre = caixa_sobre["y"] + caixa_sobre["height"] / 2
            assert (
                caixa_bloco["y"] - TOLERANCIA_GEOMETRICA
                <= centro_sobre
                <= caixa_bloco["y"] + caixa_bloco["height"] + TOLERANCIA_GEOMETRICA
            )

            caixa_chevron = sobre.locator(".dropdown-chevron").bounding_box()
            assert caixa_chevron
            assert caixa_chevron["x"] >= caixa_sobre["x"] - TOLERANCIA_GEOMETRICA
            assert caixa_chevron["x"] + caixa_chevron["width"] <= (
                caixa_sobre["x"] + caixa_sobre["width"] + TOLERANCIA_GEOMETRICA
            )

            linhas = pagina.locator("#menu > ul > li").evaluate_all(
                "items => items.filter(item => getComputedStyle(item).display !== 'none').map(item => item.getBoundingClientRect().top)"
            )
            assert max(linhas) - min(linhas) <= TOLERANCIA_GEOMETRICA
            expect(botao_busca).to_have_attribute("aria-expanded", "false")
            expect(campo).not_to_be_visible()
            botao_busca.click()
            expect(botao_busca).to_have_attribute("aria-expanded", "true")
            expect(campo).to_be_focused()
            campo.press("Escape")
            expect(botao_busca).to_have_attribute("aria-expanded", "false")
            expect(campo).not_to_be_visible()

            conta.click()
            assert pagina.url == f"{base_url}/login"
        finally:
            navegador.close()


@pytest.mark.parametrize(
    "viewport",
    (
        {"width": 320, "height": 568},
        {"width": 360, "height": 800},
        {"width": 390, "height": 844},
        {"width": 414, "height": 896},
        {"width": 768, "height": 1024},
        {"width": 1024, "height": 768},
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
        {"width": 1920, "height": 1080},
    ),
    ids=lambda viewport: f"carrossel-{viewport['width']}-{viewport['height']}",
)
def test_geometria_e_legibilidade_do_carrossel_da_home(tmp_path, viewport):
    """Valida a geometria que evita setas desalinhadas e cards comprimidos."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            contexto = navegador.new_context(viewport=viewport, service_workers="block")
            pagina = contexto.new_page()
            pagina.goto(base_url, wait_until="networkidle")
            viewport_carrossel = pagina.locator("[data-product-carousel-viewport]")
            setas = pagina.locator(".carousel-arrow")
            card = pagina.locator(".product-carousel .product-card-wrap").first

            geometria = pagina.evaluate("""() => {
                const viewportRect = document.querySelector('[data-product-carousel-viewport]').getBoundingClientRect();
                const leftArrowRect = document.querySelector('[data-carousel-previous]').getBoundingClientRect();
                const rightArrowRect = document.querySelector('[data-carousel-next]').getBoundingClientRect();
                const arrows = [leftArrowRect, rightArrowRect];
                const card = document.querySelector('.product-carousel .product-card-wrap').getBoundingClientRect();
                const image = document.querySelector('.product-carousel .product-image').getBoundingClientRect();
                const buttons = [...document.querySelectorAll('.home-product-card .icon-action')];
                return {
                    viewport: {left: viewportRect.left, right: viewportRect.right},
                    arrows: arrows.map(arrowRect => ({left: arrowRect.left, right: arrowRect.right, centerX: arrowRect.left + arrowRect.width / 2, centroSeta: arrowRect.top + arrowRect.height / 2, width: arrowRect.width, height: arrowRect.height})),
                    image: {centroImagem: image.top + image.height / 2},
                    card: {left: card.left, right: card.right, width: card.width},
                    buttonsFit: buttons.every(button => {
                        const buttonBox = button.getBoundingClientRect();
                        const cardBox = button.closest('.product-card').getBoundingClientRect();
                        return buttonBox.left >= cardBox.left - 3
                            && buttonBox.right <= cardBox.right + 3
                            && button.scrollWidth <= button.clientWidth
                            && button.scrollHeight <= button.clientHeight;
                    }),
                    actionTextsVisible: [...document.querySelectorAll('.home-product-card .icon-action span')]
                        .every(text => text.getClientRects().length > 0 && getComputedStyle(text).visibility === 'visible'),
                    pageFits: document.documentElement.scrollWidth <= document.documentElement.clientWidth,
                };
            }""")

            assert viewport_carrossel.is_visible() and card.is_visible()
            assert setas.count() == 2
            assert all(
                abs(seta["centroSeta"] - geometria["image"]["centroImagem"]) <= 2
                for seta in geometria["arrows"]
            )
            assert (
                abs(geometria["arrows"][0]["width"] - geometria["arrows"][1]["width"])
                <= TOLERANCIA_GEOMETRICA
            )
            assert (
                abs(geometria["arrows"][0]["height"] - geometria["arrows"][1]["height"])
                <= TOLERANCIA_GEOMETRICA
            )
            assert all(
                geometria["viewport"]["left"] - TOLERANCIA_GEOMETRICA <= seta["left"]
                and seta["right"]
                <= geometria["viewport"]["right"] + TOLERANCIA_GEOMETRICA
                for seta in geometria["arrows"]
            )
            inset_esquerdo = (
                geometria["arrows"][0]["centerX"] - geometria["viewport"]["left"]
            )
            inset_direito = (
                geometria["viewport"]["right"] - geometria["arrows"][1]["centerX"]
            )
            assert abs(inset_esquerdo - inset_direito) <= TOLERANCIA_GEOMETRICA

            setas.nth(1).hover(force=True)
            pagina.wait_for_timeout(250)
            insets_no_hover = pagina.evaluate("""() => {
                const viewportRect = document.querySelector('[data-product-carousel-viewport]').getBoundingClientRect();
                const leftArrowRect = document.querySelector('[data-carousel-previous]').getBoundingClientRect();
                const rightArrowRect = document.querySelector('[data-carousel-next]').getBoundingClientRect();
                return {
                    left: leftArrowRect.left + leftArrowRect.width / 2 - viewportRect.left,
                    right: viewportRect.right - (rightArrowRect.left + rightArrowRect.width / 2),
                };
            }""")
            assert (
                abs(insets_no_hover["left"] - insets_no_hover["right"])
                <= TOLERANCIA_GEOMETRICA
            )
            assert (
                geometria["card"]["left"]
                >= geometria["viewport"]["left"] - TOLERANCIA_GEOMETRICA
            )
            assert (
                geometria["card"]["right"]
                <= geometria["viewport"]["right"] + TOLERANCIA_GEOMETRICA
            )
            assert geometria["card"]["width"] >= 240
            assert geometria["buttonsFit"] and geometria["actionTextsVisible"]
            assert geometria["pageFits"]
        finally:
            navegador.close()


@pytest.mark.parametrize(
    "viewport",
    (
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900},
        {"width": 1920, "height": 1080},
    ),
    ids=lambda viewport: f"header-dark-{viewport['width']}-{viewport['height']}",
)
def test_header_dark_permanece_uma_superficie_ao_rolar(tmp_path, viewport):
    """Impede que o menu desktop desenhe uma segunda superfície no cabeçalho."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            contexto = navegador.new_context(viewport=viewport, service_workers="block")
            contexto.add_init_script(
                "localStorage.setItem('doce_pedido_tema', 'dark')"
            )
            pagina = contexto.new_page()
            pagina.goto(base_url, wait_until="networkidle")

            for posicao in (0, 100, 500):
                pagina.evaluate("posicao => scrollTo(0, posicao)", posicao)
                pagina.wait_for_function(
                    "posicao => Math.round(scrollY) === posicao", arg=posicao
                )
                superficies = pagina.evaluate("""() => {
                    const header = getComputedStyle(document.querySelector('.site-header'));
                    const menu = getComputedStyle(document.querySelector('.navbar-collapse'));
                    return {
                        header: header.backgroundColor,
                        menu: menu.backgroundColor,
                    };
                }""")

                assert superficies["header"] != "rgba(0, 0, 0, 0)"
                assert superficies["menu"] == "rgba(0, 0, 0, 0)"
        finally:
            contexto.close()
            navegador.close()


@pytest.mark.parametrize(
    "viewport",
    HOME_VIEWPORTS,
    ids=lambda viewport: f"dark-home-{viewport['width']}-{viewport['height']}",
)
def test_dark_mode_da_home_usa_superficies_quentes_e_estaveis(tmp_path, viewport):
    """Smoke visual estrutural do tema escuro sem depender de comparação por pixel."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            contexto = navegador.new_context(viewport=viewport, service_workers="block")
            contexto.add_init_script("localStorage.setItem('doce_pedido_tema', 'dark')")
            pagina = contexto.new_page()
            erros = []
            pagina.on(
                "console",
                lambda mensagem: (
                    erros.append(mensagem.text) if mensagem.type == "error" else None
                ),
            )
            pagina.on("pageerror", lambda erro: erros.append(str(erro)))
            pagina.goto(base_url, wait_until="networkidle")
            pagina.locator("[data-cookie-accept]").click()

            if viewport["width"] < 1200:
                pagina.locator(".navbar-toggler").click()
            busca = pagina.locator(".header-search")
            if busca.get_attribute(
                "class"
            ) and "is-expanded" not in busca.get_attribute("class"):
                pagina.locator("[data-search-toggle]").click()

            cores = pagina.evaluate("""() => {
                const color = selector => getComputedStyle(document.querySelector(selector)).backgroundColor;
                const text = selector => getComputedStyle(document.querySelector(selector)).color;
                return {
                    body: color('body'), header: color('.site-header'), search: color('.header-search'),
                    kit: color('.kit-panel'), about: color('.about-section'), benefits: color('.benefits'),
                    benefitCards: [...document.querySelectorAll('.benefit')].map(item => getComputedStyle(item).backgroundColor),
                    benefitBorders: [...document.querySelectorAll('.benefit')].map(item => getComputedStyle(item).borderColor),
                    icon: text('.benefit-icon'), placeholder: getComputedStyle(document.querySelector('.header-search input'), '::placeholder').color,
                    overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                };
            }""")
            preto_puro = {"rgb(0, 0, 0)", "rgba(0, 0, 0, 1)"}

            assert pagina.locator("html").get_attribute("data-theme") == "dark"
            assert cores["header"] != cores["body"]
            assert cores["about"] == cores["benefits"] == cores["body"]
            assert (
                len(set(cores["benefitCards"]))
                == len(set(cores["benefitBorders"]))
                == 1
            )
            assert all(
                cor not in preto_puro
                for cor in (
                    cores["body"],
                    cores["header"],
                    cores["search"],
                    cores["kit"],
                    cores["placeholder"],
                    cores["icon"],
                )
            )
            assert not cores["overflow"] and not erros

            for caminho in ("/produtos", "/login"):
                pagina.goto(f"{base_url}{caminho}", wait_until="networkidle")
                assert pagina.locator("html").get_attribute("data-theme") == "dark"
                assert not pagina.evaluate(
                    "document.documentElement.scrollWidth > document.documentElement.clientWidth"
                )
            assert not erros
        finally:
            navegador.close()


@pytest.mark.parametrize(
    ("tema_salvo", "tema_esperado"),
    ((None, "light"), ("dark", "dark"), ("light", "light")),
    ids=("sem-preferencia-light", "restaura-dark", "restaura-light"),
)
def test_tema_inicial_e_ultima_selecao_persistem_na_home(
    tmp_path, tema_salvo, tema_esperado
):
    """Distingue o padrão claro da restauração explícita feita pelo usuário."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            contexto = navegador.new_context(
                viewport={"width": 1366, "height": 768},
                color_scheme="dark",
                service_workers="block",
            )
            if tema_salvo:
                contexto.add_init_script(
                    f"localStorage.setItem('doce_pedido_tema', '{tema_salvo}')"
                )
            pagina = contexto.new_page()
            pagina.goto(base_url, wait_until="networkidle")
            expect(pagina.locator("html")).to_have_attribute(
                "data-theme", tema_esperado
            )

            if tema_salvo is None:
                pagina.get_by_role("button", name="Modo Escuro").click()
                expect(pagina.locator("html")).to_have_attribute("data-theme", "dark")
                tema_esperado = "dark"

            pagina.reload(wait_until="networkidle")
            expect(pagina.locator("html")).to_have_attribute(
                "data-theme", tema_esperado
            )
            pagina.evaluate("scrollTo(0, document.documentElement.scrollHeight)")
            voltar = pagina.get_by_role("button", name="Voltar ao Topo")
            expect(voltar).to_be_visible()
            assert voltar.locator("svg").bounding_box()
            assert not pagina.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
        finally:
            navegador.close()


@pytest.mark.parametrize(
    "viewport",
    (
        {"width": 320, "height": 568},
        {"width": 360, "height": 800},
        {"width": 390, "height": 844},
        {"width": 414, "height": 896},
    ),
    ids=lambda viewport: f"{viewport['width']}-{viewport['height']}",
)
def test_menu_mobile_executa_navegacao_conta_busca_e_tema(tmp_path, viewport):
    """Exercita as ações do menu compacto, inclusive em telas de pouca altura."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            contexto = navegador.new_context(viewport=viewport, service_workers="block")
            pagina = contexto.new_page()
            pagina.goto(base_url, wait_until="networkidle")
            pagina.locator("[data-cookie-accept]").click()
            menu = pagina.locator("#menu")
            alternador = pagina.locator(".navbar-toggler")

            alternador.click()
            expect(alternador).to_have_attribute("aria-expanded", "true")
            for nome in ("Início", "Produtos", "Sobre", "Minha Conta"):
                expect(menu.get_by_text(nome, exact=True).first).to_be_visible()
            expect(menu.locator("[data-search-toggle]")).to_be_visible()
            expect(menu.locator("[data-theme-toggle]")).to_be_visible()
            geometria_tema = pagina.evaluate("""() => {
                const button = document.querySelector('[data-theme-toggle]');
                const stack = button.querySelector('.theme-icon-stack');
                const icons = [...stack.querySelectorAll('.theme-icon')];
                const label = button.querySelector('.theme-label');
                const buttonBox = button.getBoundingClientRect();
                const stackBox = stack.getBoundingClientRect();
                const labelBox = label.getBoundingClientRect();
                return {
                    buttonFits: button.scrollWidth <= button.clientWidth && button.scrollHeight <= button.clientHeight,
                    labelVisible: labelBox.width > 0 && labelBox.height > 0,
                    noOverlap: stackBox.right <= labelBox.left,
                    iconsSized: icons.every(icon => {
                        const style = getComputedStyle(icon);
                        return style.width === '22px' && style.height === '22px';
                    }),
                    iconsInside: icons.every(icon => {
                        const box = icon.getBoundingClientRect();
                        return box.left >= buttonBox.left && box.right <= buttonBox.right;
                    }),
                };
            }""")
            assert all(geometria_tema.values())
            assert pagina.locator("header .cart-icon-link").count() == 2
            assert pagina.get_by_role("link", name="Abrir carrinho").count() == 1
            menu.get_by_role("button", name="Sobre").click()
            expect(menu.get_by_role("link", name="Sobre a Doce Pedido")).to_be_visible()
            item_sobre = menu.get_by_role("link", name="Perguntas Frequentes")
            item_sobre.scroll_into_view_if_needed()
            item_sobre.click()
            assert pagina.url == f"{base_url}/faq"

            alternador.click()
            expect(alternador).to_have_attribute("aria-expanded", "true")
            pagina.wait_for_function(
                "menu => menu.classList.contains('show') && !menu.classList.contains('collapsing')",
                arg=menu.element_handle(),
            )
            conta = menu.get_by_role("link", name="Minha Conta")
            expect(conta).to_be_visible()
            expect(menu.get_by_role("link", name="Entrar")).to_be_visible()
            expect(menu.get_by_role("link", name="Cadastrar")).to_be_visible()
            conta.click()
            assert pagina.url == f"{base_url}/login"

            menu = pagina.locator("#menu")
            alternador = pagina.locator(".navbar-toggler")
            alternador.click()
            expect(alternador).to_have_attribute("aria-expanded", "true")
            campo_busca = menu.get_by_role("searchbox", name="Buscar Cupcakes")
            campo_busca.fill("chocolate")
            campo_busca.press("Enter")
            assert "/buscar?q=chocolate" in pagina.url

            alternador.click()
            expect(alternador).to_have_attribute("aria-expanded", "true")
            expect(menu).to_be_visible()
            pagina.wait_for_function(
                "menu => menu.classList.contains('show') && !menu.classList.contains('collapsing')",
                arg=menu.element_handle(),
            )
            botao_tema = menu.get_by_role("button", name="Modo Escuro")
            botao_tema.scroll_into_view_if_needed()
            botao_tema.click()
            expect(pagina.locator("html")).to_have_attribute("data-theme", "dark")
            expect(menu.get_by_role("button", name="Modo Claro")).to_be_visible()
            expect(menu.locator(".theme-icon-sun")).to_have_css("opacity", "0")
            expect(menu.locator(".theme-icon-moon")).to_have_css("opacity", "1")
            assert pagina.evaluate(
                "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
            )
        finally:
            contexto.close()
            navegador.close()


def test_fallback_realmente_offline_mantem_estilo_e_retorna_a_url(tmp_path):
    """Protege a regressão em que o HTML surgia sem o CSS específico cacheado."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        contexto = navegador.new_context(viewport={"width": 390, "height": 844})
        pagina = contexto.new_page()
        erros_reais = []
        erros_offline_esperados = []
        contexto_offline = {"ativo": False}
        requisicoes_remotas = []

        def registrar_erro_console(mensagem):
            if mensagem.type != "error":
                return
            erro_rede_offline = (
                contexto_offline["ativo"]
                and mensagem.text
                == "Failed to load resource: net::ERR_INTERNET_DISCONNECTED"
            )
            if erro_rede_offline:
                erros_offline_esperados.append(mensagem.text)
            else:
                erros_reais.append(mensagem.text)

        pagina.on("pageerror", lambda erro: erros_reais.append(str(erro)))
        pagina.on("console", registrar_erro_console)
        pagina.on(
            "request",
            lambda requisicao: (
                requisicoes_remotas.append(requisicao.url)
                if not requisicao.url.startswith(base_url)
                else None
            ),
        )
        try:
            pagina.goto(base_url, wait_until="networkidle")
            pagina.wait_for_function("'serviceWorker' in navigator")
            pagina.wait_for_function("navigator.serviceWorker.ready")
            if not pagina.evaluate("Boolean(navigator.serviceWorker.controller)"):
                pagina.reload(wait_until="networkidle")
            assert pagina.evaluate("Boolean(navigator.serviceWorker.controller)")

            contexto_offline["ativo"] = True
            contexto.set_offline(True)
            pagina.goto(f"{base_url}/produtos/1", wait_until="domcontentloaded")
            assert pagina.get_by_role("heading", name="Sem Conexão").is_visible()
            expect(pagina.locator("[data-connection-status]")).to_have_text(
                "Aguardando Conexão"
            )

            card = pagina.locator(".offline-page")
            botao = pagina.locator("[data-retry]")
            wifi = pagina.locator(".offline-wifi")
            assert (
                float(card.evaluate("el => parseFloat(getComputedStyle(el).borderRadius)"))
                > 0
            )
            assert (
                botao.evaluate("el => getComputedStyle(el).backgroundColor")
                != "rgba(0, 0, 0, 0)"
            )
            assert 38 <= wifi.evaluate("el => el.getBoundingClientRect().width") <= 48
            assert pagina.locator(".offline-body").evaluate(
                "el => getComputedStyle(el).display"
            ) == "grid"
            assert not pagina.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
            botao.dispatch_event("click")
            assert "is-loading" in (botao.get_attribute("class") or "")
            expect(pagina.locator("[data-retry-label]")).to_have_text("Verificando...")
            pagina.wait_for_function(
                "elemento => elemento.textContent === 'Tentar Novamente'",
                arg=pagina.locator("[data-retry-label]").element_handle(),
            )
            assert not botao.is_disabled()

            contexto.set_offline(False)
            contexto_offline["ativo"] = False
            pagina.evaluate("window.dispatchEvent(new Event('online'))")
            produto = pagina.locator(".product-detail h1")
            produto.wait_for(state="visible")
            assert pagina.url == f"{base_url}/produtos/1"
            assert not erros_reais
            assert not requisicoes_remotas
        finally:
            contexto.close()
            navegador.close()


def test_offline_respeita_movimento_reduzido(tmp_path):
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        contexto = navegador.new_context(
            viewport={"width": 320, "height": 568},
            reduced_motion="reduce",
            service_workers="block",
        )
        pagina = contexto.new_page()
        try:
            pagina.goto(f"{base_url}/offline", wait_until="networkidle")
            for seletor in (
                ".offline-visual",
                ".offline-signal-ring",
                ".offline-wifi path",
            ):
                assert (
                    pagina.locator(seletor).first.evaluate(
                        "el => getComputedStyle(el).animationName"
                    )
                    == "none"
                )
            assert pagina.get_by_role("button", name="Tentar Novamente").is_visible()
            assert not pagina.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
        finally:
            contexto.close()
            navegador.close()


@pytest.mark.parametrize(
    "viewport",
    (
        {"width": 320, "height": 568},
        {"width": 360, "height": 800},
        {"width": 390, "height": 844},
        {"width": 768, "height": 1024},
        {"width": 1366, "height": 768},
    ),
    ids=lambda viewport: f"cookies-{viewport['width']}-{viewport['height']}",
)
def test_fluxo_acessivel_e_persistente_das_preferencias_de_cookies(tmp_path, viewport):
    """Exercita todas as decisões sem confundir banner e diálogo no mesmo DOM."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        try:
            contexto = navegador.new_context(viewport=viewport, service_workers="block")
            pagina = contexto.new_page()
            erros = []
            pagina.on(
                "console",
                lambda mensagem: (
                    erros.append(mensagem.text) if mensagem.type == "error" else None
                ),
            )
            pagina.on("pageerror", lambda erro: erros.append(str(erro)))
            pagina.goto(base_url, wait_until="networkidle")

            banner = pagina.locator("[data-cookie-banner]")
            assert banner.is_visible()
            assert banner.locator("button").count() == 2
            assert banner.get_by_role("button", name="Aceitar", exact=True).is_visible()
            assert banner.get_by_role(
                "button", name="Gerenciar Preferências", exact=True
            ).is_visible()
            assert not banner.get_by_role(
                "button", name="Recusar Não Essenciais"
            ).is_visible()
            assert banner.evaluate(
                "element => [...element.querySelectorAll('button')].every(button => button.scrollWidth <= button.clientWidth)"
            )
            assert not pagina.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )

            gerenciar = pagina.locator("[data-cookie-manage]")
            gerenciar.click()
            dialogo = pagina.locator("[data-cookie-dialog]")
            assert dialogo.is_visible()
            assert dialogo.get_by_role(
                "heading", name="Preferências de Cookies", exact=True
            ).is_visible()
            assert dialogo.get_by_text("Sempre Ativos", exact=True).is_visible()
            analise = pagina.locator("[data-cookie-analytics]")
            assert not analise.is_checked()
            analise.check()
            assert analise.is_checked()
            pagina.locator("[data-cookie-accept-all]").click()
            assert '"analytics":true' in pagina.evaluate(
                "decodeURIComponent(document.cookie)"
            )

            pagina.goto(f"{base_url}/cookies", wait_until="networkidle")
            pagina.locator("[data-cookie-settings]").click()
            assert analise.is_checked()
            pagina.locator("[data-cookie-reject]").click()
            assert not banner.is_visible()
            assert '"analytics":false' in pagina.evaluate(
                "decodeURIComponent(document.cookie)"
            )

            pagina.locator("[data-cookie-settings]").click()
            assert not analise.is_checked()
            analise.check()
            pagina.locator("[data-cookie-save]").click()
            assert '"analytics":true' in pagina.evaluate(
                "decodeURIComponent(document.cookie)"
            )
            pagina.reload(wait_until="networkidle")
            assert not banner.is_visible()

            pagina.locator("[data-cookie-settings]").click()
            pagina.keyboard.press("Escape")
            assert not dialogo.is_visible()
            assert pagina.locator("[data-cookie-settings]").evaluate(
                "element => element === document.activeElement"
            )

            pagina.evaluate("localStorage.setItem('doce_pedido_tema', 'dark')")
            pagina.reload(wait_until="networkidle")
            pagina.locator("[data-cookie-settings]").click()
            assert (
                dialogo.evaluate("element => getComputedStyle(element).backgroundColor")
                != "rgb(0, 0, 0)"
            )
            assert not pagina.evaluate(
                "document.documentElement.scrollWidth > document.documentElement.clientWidth"
            )
            assert not erros
            contexto.close()
        finally:
            navegador.close()


def test_carrinho_atualiza_quantidades_sem_recarregar(tmp_path):
    """Valida botões, digitação, totais e remoção na interação real do carrinho."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        pagina = navegador.new_page()
        try:
            pagina.goto(f"{base_url}/produtos/1", wait_until="networkidle")
            pagina.get_by_role("button", name="Carrinho").click()
            pagina.goto(f"{base_url}/carrinho", wait_until="networkidle")

            item = pagina.locator("[data-cart-item]")
            input_quantidade = item.locator("input[name=quantidade]")
            subtotal = item.locator("[data-cart-subtotal]")
            total = pagina.locator("[data-cart-total]")

            item.locator("[data-quantity-increase]").click()
            expect(subtotal).to_have_text("R$ 17,00")
            expect(total).to_have_text("R$ 17,00")
            expect(pagina.locator("[data-cart-count]").first).to_have_text("2")
            assert pagina.url == f"{base_url}/carrinho"

            item.locator("[data-quantity-decrease]").click()
            expect(subtotal).to_have_text("R$ 8,50")

            input_quantidade.fill("3")
            expect(subtotal).to_have_text("R$ 25,50", timeout=2_000)
            expect(total).to_have_text("R$ 25,50")
            expect(pagina.locator("[data-cart-count]").first).to_have_text("3")

            item.locator(".cart-remove-button").click()
            expect(pagina.get_by_text("Seu Carrinho Ainda Está Vazio")).to_be_visible()
        finally:
            navegador.close()


def test_carrinho_alinha_itens_e_mantem_cupom_demonstrativo(tmp_path):
    """Valida geometria dos itens e o cupom local em desktop e mobile."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        pagina = navegador.new_page(viewport={"width": 1366, "height": 768})
        requisicoes_cupom = []
        pagina.on(
            "request",
            lambda requisicao: (
                requisicoes_cupom.append(requisicao.url)
                if "cupom" in requisicao.url.lower()
                else None
            ),
        )
        try:
            for produto_id in (1, 2):
                pagina.goto(
                    f"{base_url}/produtos/{produto_id}", wait_until="networkidle"
                )
                pagina.get_by_role("button", name="Carrinho").click()
            pagina.goto(f"{base_url}/carrinho", wait_until="networkidle")

            quantidades = pagina.locator(".cart-quantity").evaluate_all(
                "elements => elements.map(element => element.getBoundingClientRect().toJSON())"
            )
            subtotais = pagina.locator(".cart-subtotal").evaluate_all(
                "elements => elements.map(element => element.getBoundingClientRect().toJSON())"
            )
            assert len(quantidades) == len(subtotais) == 2
            assert abs(quantidades[0]["x"] - quantidades[1]["x"]) <= 2
            assert abs(subtotais[0]["x"] - subtotais[1]["x"]) <= 2

            cupom = pagina.locator("#cupom")
            aplicar = pagina.locator("[data-coupon-apply]")
            total_inicial = pagina.locator("[data-cart-total]").inner_text()
            assert cupom.is_enabled()
            assert aplicar.is_enabled()
            aplicar.click()
            expect(pagina.get_by_text("Digite um Cupom.")).to_be_visible()
            cupom.fill("DOCE10")
            aplicar.click()
            expect(pagina.get_by_text("Cupom não Encontrado.")).to_be_visible()
            expect(pagina.locator("[data-cart-total]")).to_have_text(total_inicial)
            assert aplicar.evaluate(
                "element => getComputedStyle(element).whiteSpace === 'nowrap'"
            )
            assert not requisicoes_cupom

            for viewport in ({"width": 320, "height": 568}, {"width": 390, "height": 844}):
                pagina.set_viewport_size(viewport)
                pagina.reload(wait_until="networkidle")
                assert not pagina.evaluate(
                    "document.documentElement.scrollWidth > document.documentElement.clientWidth"
                )
                expect(pagina.locator(".cart-info h2").first).to_be_visible()
                expect(pagina.locator(".cart-remove-button").first).to_be_visible()
                expect(pagina.locator(".quantity-row").first).to_be_visible()
                expect(pagina.locator("[data-cart-subtotal]").first).to_be_visible()
                expect(cupom).to_be_enabled()
                expect(aplicar).to_be_visible()
                expect(pagina.get_by_role("link", name="Revisar o Pedido")).to_be_visible()
                assert aplicar.inner_text() == "Aplicar"
        finally:
            navegador.close()


@pytest.mark.parametrize("caminho", ("/", "/produtos/1"))
def test_adicao_ao_carrinho_preserva_pagina_e_scroll(tmp_path, caminho):
    """Adiciona pela Home e pelo detalhe sem navegação ou deslocamento."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        pagina = navegador.new_page(
            viewport={"width": 390, "height": 844}, service_workers="block"
        )
        try:
            url = f"{base_url}{caminho}"
            pagina.goto(url, wait_until="networkidle")
            formulario = pagina.locator("[data-add-to-cart]").first
            botao_adicionar = formulario.locator("button[type=submit]")
            botao_adicionar.evaluate(
                "el => el.scrollIntoView({block: 'center', behavior: 'instant'})"
            )
            scroll_inicial = pagina.evaluate("window.scrollY")

            botao_adicionar.click()

            popup = pagina.locator(".interface-toast-container .toast")
            expect(popup).to_be_visible()
            expect(pagina.locator("[data-cart-count]").first).to_have_text("1")
            assert pagina.url == url
            assert abs(pagina.evaluate("window.scrollY") - scroll_inicial) <= 2
            caixa = popup.bounding_box()
            assert caixa is not None
            assert abs((caixa["x"] + caixa["width"] / 2) - 195) <= 2
            assert popup.evaluate("el => getComputedStyle(el).position") == "static"
            assert popup.locator("xpath=..").evaluate(
                "el => getComputedStyle(el).position"
            ) == "fixed"

            popup.get_by_role("button", name="Fechar").click()
            expect(popup).to_have_count(0)
        finally:
            navegador.close()


def test_popup_fecha_automaticamente_e_cupom_dark_tem_contraste(tmp_path):
    """Valida fechamento do toast e placeholder opaco no tema escuro."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        contexto = navegador.new_context(service_workers="block")
        contexto.add_init_script(
            "localStorage.setItem('doce_pedido_tema', 'dark')"
        )
        pagina = contexto.new_page()
        try:
            pagina.goto(f"{base_url}/produtos/1", wait_until="networkidle")
            pagina.locator("[data-add-to-cart] button[type=submit]").click()
            popup = pagina.locator(".interface-toast-container .toast")
            expect(popup).to_be_visible()
            expect(popup).to_have_count(0, timeout=5_000)

            pagina.goto(f"{base_url}/carrinho", wait_until="networkidle")
            cupom = pagina.locator("#cupom")
            estilo = cupom.evaluate(
                "el => { const s = getComputedStyle(el, '::placeholder'); "
                "return { color: s.color, opacity: s.opacity }; }"
            )
            assert estilo["opacity"] == "1"
            assert estilo["color"] not in ("rgba(0, 0, 0, 0)", "transparent")
            cupom.focus()
            pagina.wait_for_timeout(250)
            assert cupom.evaluate(
                "el => { const probe = document.createElement('span'); "
                "probe.style.color = 'var(--cor-rosa-principal)'; "
                "document.body.append(probe); "
                "const esperado = getComputedStyle(probe).color; probe.remove(); "
                "return getComputedStyle(el).borderColor === esperado; }"
            )
        finally:
            contexto.close()
            navegador.close()


def test_area_cliente_interacoes_e_responsividade(tmp_path):
    """Valida estados locais, placeholders, olhos e geometria da Minha Conta."""
    with servidor_frontend(tmp_path) as base_url, sync_playwright() as playwright:
        navegador = playwright.chromium.launch()
        contexto = navegador.new_context(service_workers="block")
        pagina = contexto.new_page()
        try:
            for rota, painel in (("/login", "entrar"), ("/cadastro", "cadastrar")):
                pagina.goto(f"{base_url}{rota}", wait_until="networkidle")
                expect(pagina.locator(f'[data-account-panel="{painel}"]')).to_be_visible()

            url = pagina.url
            pagina.get_by_role("tab", name="Entrar").click()
            expect(pagina.locator('[data-account-panel="entrar"]')).to_be_visible()
            assert pagina.locator("#login-email").get_attribute("placeholder") == "exemplo@exemplo.com.br"
            assert pagina.locator("#login-senha").get_attribute("placeholder") == "Digite sua Senha"
            assert pagina.url == url
            pagina.get_by_role("button", name="Esqueceu a senha?").click()
            expect(pagina.locator('[data-account-panel="recuperar"]')).to_be_visible()
            assert pagina.locator("#recuperar-email").get_attribute("placeholder") == "exemplo@exemplo.com.br"
            assert pagina.url == url
            pagina.locator("[data-back-to-login]").click()
            expect(pagina.locator('[data-account-panel="entrar"]')).to_be_visible()
            assert pagina.url == url

            pagina.get_by_role("tab", name="Cadastrar").click()
            assert pagina.url == url
            senha = pagina.locator("#cadastro-senha")
            criterios = pagina.locator("#criterios-senha")
            expect(criterios).not_to_be_visible()
            senha.fill("D")
            expect(criterios).to_be_visible()
            senha.fill("Doce@123")
            botao_olho = pagina.locator('[data-password-toggle="cadastro-senha"]')
            expect(botao_olho.locator(".olho-aberto")).to_be_visible()
            expect(botao_olho.locator(".olho-fechado")).not_to_be_visible()
            botao_olho.click()
            assert senha.get_attribute("type") == "text"
            expect(botao_olho.locator(".olho-aberto")).not_to_be_visible()
            expect(botao_olho.locator(".olho-fechado")).to_be_visible()
            expect(pagina.locator(".conta-criterios .is-valid")).to_have_count(5)
            pagina.locator("#cadastro-cpf").fill("12345678901")
            assert pagina.locator("#cadastro-cpf").input_value() == "123.456.789-01"
            pagina.locator("#cadastro-confirmacao").fill("diferente")
            expect(pagina.locator("#confirmacao-mensagem")).to_contain_text(
                "não coincidem"
            )
            pagina.locator("#cadastro-confirmacao").fill("Doce@123")
            expect(pagina.locator("#confirmacao-mensagem")).to_contain_text("coincidem")

            for tema in ("light", "dark"):
                pagina.evaluate("tema => document.documentElement.dataset.theme = tema", tema)
                for viewport in VIEWPORTS:
                    pagina.set_viewport_size(viewport)
                    assert not pagina.evaluate(
                        "document.documentElement.scrollWidth > "
                        "document.documentElement.clientWidth"
                    )
        finally:
            contexto.close()
            navegador.close()
