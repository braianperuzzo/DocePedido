"""Testes de pwa mobile da aplicação."""

import json
from pathlib import Path

from PIL import Image

from testes.conftest import normalizar_html


def test_manifesto_pwa_e_alias(cliente_http):
    for caminho in ("/manifest.webmanifest", "/site.webmanifest"):
        resposta = cliente_http.get(caminho)
        dados = json.loads(resposta.data)
        assert resposta.status_code == 200
        assert resposta.mimetype == "application/manifest+json"
        assert dados["name"] == dados["short_name"] == "Doce Pedido"
        assert dados["start_url"] == dados["scope"] == "/"
        assert dados["display"] == "standalone"
        assert dados["lang"] == "pt-BR"
        assert all(
            cliente_http.get(icone["src"]).status_code == 200
            for icone in dados["icons"]
        )


def test_icones_pwa_correspondem_as_dimensoes_declaradas(cliente_http):
    manifesto = cliente_http.get("/manifest.webmanifest").get_json()
    raiz_static = Path(__file__).parents[1] / "aplicacao" / "static"
    esperados = {
        ("192x192", "any"),
        ("512x512", "any"),
        ("192x192", "maskable"),
        ("512x512", "maskable"),
    }

    assert {
        (icone["sizes"], icone["purpose"]) for icone in manifesto["icons"]
    } == esperados
    for icone in manifesto["icons"]:
        caminho = raiz_static / icone["src"].removeprefix("/static/")
        largura, altura = map(int, icone["sizes"].split("x"))
        assert caminho.is_file()
        with Image.open(caminho) as imagem:
            assert imagem.format == "PNG"
            assert imagem.size == (largura, altura)

    for nome, dimensoes in (
        ("favicon-32.png", (32, 32)),
        ("apple-touch-icon.png", (180, 180)),
    ):
        with Image.open(raiz_static / "imagens" / nome) as imagem:
            assert imagem.size == dimensoes


def test_bootstrap_e_servido_localmente_e_csp_nao_libera_cdn(cliente_http):
    resposta = cliente_http.get("/")
    pagina = resposta.get_data(as_text=True)
    assert "/static/vendor/bootstrap/bootstrap.min.css" in pagina
    assert "/static/vendor/bootstrap/bootstrap.bundle.min.js" in pagina
    assert "cdn.jsdelivr.net" not in pagina
    assert "cdn.jsdelivr.net" not in resposta.headers["Content-Security-Policy"]


def test_service_worker_atualiza_codigo_e_cacheia_apenas_assets(cliente_http):
    resposta = cliente_http.get("/service-worker.js")
    assert resposta.status_code == 200
    assert resposta.headers["Service-Worker-Allowed"] == "/"
    assert resposta.headers["Cache-Control"] == "no-cache, no-store, must-revalidate"
    assert resposta.headers["Expires"] == "0"
    assert 'CACHE_NAME = "doce-pedido-static-v9"' in resposta.text
    assert 'request.method !== "GET"' in resposta.text
    assert 'url.pathname.startsWith("/static/")' in resposta.text
    assert 'request.destination === "style"' in resposta.text
    assert 'request.destination === "script"' in resposta.text
    assert "fetch(request).then((response)" in resposta.text
    assert ".catch(() => caches.match(request))" in resposta.text
    assert "caches.match(OFFLINE_URL)" in resposta.text
    assert "self.skipWaiting()" in resposta.text
    assert "self.clients.claim()" in resposta.text
    for essencial in (
        "/offline",
        "/static/css/principal.css",
        "/static/css/offline.css",
        "/static/js/tema-inicial.js",
        "/static/js/offline.js",
        "/static/imagens/favicon-32.png",
        "/static/imagens/apple-touch-icon.png",
        "/manifest.webmanifest",
    ):
        assert f'"{essencial}"' in resposta.text
    for privada in ("/login", "/cadastro", "/carrinho", "/pedidos"):
        assert privada not in resposta.text


def test_registro_do_service_worker_ignora_cache_http(cliente_http):
    javascript = cliente_http.get("/static/js/principal.js").text
    assert 'updateViaCache: "none"' in javascript
    assert "await registro.update()" in javascript
    assert 'addEventListener("controllerchange"' in javascript


def test_offline_neutro_e_controles_mobile(cliente_http):
    offline = cliente_http.get("/offline")
    html = normalizar_html(offline.text)
    assert offline.status_code == 200
    assert "Sem Conexão" in offline.text
    assert "Não foi Possível acessar a Doce Pedido" in offline.text
    assert "current_user" not in offline.text
    assert "data-retry" in offline.text
    assert 'rel="icon" type="image/png" sizes="32x32"' in html
    assert 'rel="apple-touch-icon" sizes="180x180"' in html
    assert 'rel="manifest"' in html
    assert 'class="offline-wifi"' in html
    assert 'class="offline-retry-icon"' in html
    assert 'role="status" aria-live="polite"' in html
    assert "Aguardando Conexão" in offline.text

    javascript_offline = cliente_http.get("/static/js/offline.js").text
    assert 'window.addEventListener("online"' in javascript_offline
    assert "Conexão Restabelecida" in javascript_offline
    assert "window.location.reload()" in javascript_offline

    javascript = cliente_http.get("/static/js/principal.js").text
    assert "if (!banner || !dialogo || !analise)" in javascript
    assert "window.bootstrap?.Alert" in javascript
    assert "configurarRecarregamento" in javascript

    pagina = cliente_http.get("/produtos/1").text
    assert "data-quantity-decrease" in pagina
    assert 'inputmode="numeric"' in pagina
    inicio = cliente_http.get("/").text
    assert "mobile-header-actions" in inicio
    assert "data-install-app" not in inicio
    assert "serviceWorker.register" in javascript
    assert (
        "cookie-banner-visible .contact-fab-group"
        in cliente_http.get("/static/css/principal.css").text
    )



