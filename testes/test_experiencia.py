"""Testes de experiência da aplicação."""

from pathlib import Path

from testes.conftest import normalizar_html


def test_analytics_nao_carrega_sem_configuracao(cliente_http):
    pagina = cliente_http.get("/")

    assert 'data-ga-measurement-id=""' in pagina.text
    assert "googletagmanager.com/gtag/js" not in pagina.text
    assert "www.googletagmanager.com" not in pagina.headers["Content-Security-Policy"]


def test_analytics_configurado_ainda_depende_do_javascript_de_consentimento(
    aplicacao,
):
    aplicacao.config["GA_MEASUREMENT_ID"] = "G-TESTE-LOCAL"

    resposta = aplicacao.test_client().get("/")

    assert 'data-ga-measurement-id="G-TESTE-LOCAL"' in resposta.text
    assert "googletagmanager.com/gtag/js" not in resposta.text
    assert (
        "https://www.googletagmanager.com"
        in resposta.headers["Content-Security-Policy"]
    )


def test_banner_paginas_e_links_de_cookies(cliente_http):
    pagina = normalizar_html(cliente_http.get("/").text)
    banner = pagina.split('<section class="cookie-banner"', 1)[1].split(
        "</section>", 1
    )[0]
    assert "Preferências de Cookies" in banner
    assert ">Aceitar</button>" in banner
    assert ">Gerenciar preferências</button>" in banner
    # A recusa permanece na camada detalhada para manter o banner compacto.
    assert "Recusar não essenciais" not in banner
    assert banner.count("<button") == 2
    assert "Recusar não essenciais" in pagina
    assert "Salvar preferências" in pagina
    assert cliente_http.get("/cookies").status_code == 200


def test_rodape_remove_dados_ficticios_e_mantem_credito(cliente_http):
    pagina = normalizar_html(cliente_http.get("/").text)

    assert "google.com/maps/search/" not in pagina
    assert "Desenvolvido por Braian Peruzzo" in pagina

    # Política de Cookies aparece no menu Sobre e no rodapé.
    assert pagina.count("Política de Cookies") == 2


def test_canais_flutuantes_e_rodape_apontam_para_paginas_principais():
    script = Path("aplicacao/static/js/tema-inicial.js").read_text(encoding="utf-8")

    for url in (
        "https://www.facebook.com/",
        "https://www.instagram.com/",
        "https://www.tiktok.com/",
        "https://www.whatsapp.com/",
        "https://www.ifood.com.br/",
    ):
        assert url in script
    assert '"contact-fab whatsapp-fab"' in script
    assert '"contact-fab ifood-fab"' in script
    assert 'document.createElement("a")' in script
    assert 'target = "_blank"' in script
    assert 'style.pointerEvents = "none"' not in script


def test_padronizacao_visual_de_nao_foi_possivel_e_observa_mensagens_dinamicas():
    script = Path("aplicacao/static/js/tema-inicial.js").read_text(encoding="utf-8")

    assert "formatarMensagemNaoFoiPossivel" in script
    assert "Não foi Possível" in script
    assert "palavrasDeLigacao" in script
    assert "MutationObserver" in script


def test_tema_tem_controle_acessivel_e_script_antecipado(cliente_http):
    pagina = normalizar_html(cliente_http.get("/").text)

    assert "data-theme-toggle" in pagina
    assert 'aria-label="Modo Escuro"' in pagina
    assert "js/tema-inicial.js" in pagina


def test_cabecalho_agrupa_navegacao_conta_e_busca(cliente_http):
    """Protege a navegação compacta contra a volta dos controles separados."""
    pagina = normalizar_html(cliente_http.get("/").text)

    assert 'class="brand-mark"' in pagina
    assert 'aria-controls="menu-sobre"' in pagina
    assert 'aria-controls="menu-conta"' in pagina
    assert pagina.count(">Minha Conta<") == 1
    assert "data-header-search" in pagina
    assert 'placeholder="Buscar Cupcakes"' in pagina
    assert 'stroke="currentColor"' in pagina


def test_menu_sobre_aponta_somente_para_rotas_institucionais_validas(
    cliente_http,
):
    rotas = (
        "/sobre",
        "/faq",
        "/entrega",
        "/trocas-e-cancelamentos",
        "/privacidade",
        "/cookies",
        "/termos",
        "/seguranca",
    )

    pagina = cliente_http.get("/").text

    assert all(f'href="{rota}"' in pagina for rota in rotas)
    assert all(cliente_http.get(rota).status_code == 200 for rota in rotas)


def test_tema_inicial_nao_depende_da_preferencia_do_sistema():
    """O primeiro acesso usa tema claro sem seguir o tema do sistema operacional."""
    script = Path("aplicacao/static/js/tema-inicial.js").read_text(encoding="utf-8")

    assert "prefers-color-scheme" not in script
