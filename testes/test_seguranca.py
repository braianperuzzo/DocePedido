"""Testes dos controles de segurança da aplicação."""

import re
from pathlib import Path

import pytest
from flask import abort

from aplicacao import criar_aplicacao


def test_producao_exige_secret_key(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        criar_aplicacao({"TESTING": True, "INICIALIZAR_DADOS": False})


def test_configuracoes_de_seguranca_podem_vir_do_ambiente(tmp_path, monkeypatch):
    monkeypatch.setenv("PASSWORD_ROTATION_ENABLED", "false")
    monkeypatch.setenv("PASSWORD_MAX_AGE_DAYS", "90")
    monkeypatch.setenv("DEVICE_VALIDATION_ENABLED", "false")
    monkeypatch.setenv("DEVICE_CODE_TTL", "900")
    monkeypatch.setenv("DEVICE_TRUST_DAYS", "15")
    monkeypatch.setenv("DEVICE_COOKIE_NAME", "dispositivo_teste")
    monkeypatch.setenv("ACCOUNT_CHANGE_TOKEN_TTL", "7200")

    app = criar_aplicacao(
        {
            "TESTING": True,
            "SECRET_KEY": "segredo-de-teste",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'configuracao.db'}",
            "INICIALIZAR_DADOS": False,
        }
    )

    assert app.config["PASSWORD_ROTATION_ENABLED"] is False
    assert app.config["PASSWORD_MAX_AGE_DAYS"] == 90
    assert app.config["DEVICE_VALIDATION_ENABLED"] is False
    assert app.config["DEVICE_CODE_TTL"] == 900
    assert app.config["DEVICE_TRUST_DAYS"] == 15
    assert app.config["DEVICE_COOKIE_NAME"] == "dispositivo_teste"
    assert app.config["ACCOUNT_CHANGE_TOKEN_TTL"] == 7200


def test_csrf_recusa_post_sem_token(tmp_path):
    app = criar_aplicacao(
        {
            "TESTING": True,
            "SECRET_KEY": "segredo-de-teste",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'csrf.db'}",
            "INICIALIZAR_DADOS": False,
            "WTF_CSRF_ENABLED": True,
            "RATELIMIT_ENABLED": False,
        }
    )
    cliente = app.test_client()

    resposta = cliente.post("/login", data={"email": "a@b.com", "senha": "12345678"})
    assert resposta.status_code == 400
    assert "Não foi Possível Validar o Formulário" in resposta.text

    pagina = cliente.get("/login").text
    token = re.search(r'name="csrf_token" value="([^"]+)"', pagina).group(1)
    resposta = cliente.post(
        "/login",
        data={"email": "a@b.com", "senha": "12345678", "csrf_token": token},
    )
    assert resposta.status_code == 200
    assert "E-mail ou senha inválidos" in resposta.text


def test_rate_limit_restringe_somente_tentativas_de_login(tmp_path):
    app = criar_aplicacao(
        {
            "TESTING": True,
            "SECRET_KEY": "segredo-de-teste",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'limite.db'}",
            "INICIALIZAR_DADOS": False,
            "WTF_CSRF_ENABLED": False,
            "RATELIMIT_ENABLED": True,
        }
    )
    cliente = app.test_client()

    for _ in range(5):
        assert (
            cliente.post(
                "/login", data={"email": "a@b.com", "senha": "invalida"}
            ).status_code
            == 200
        )
    resposta = cliente.post("/login", data={"email": "a@b.com", "senha": "invalida"})
    assert resposta.status_code == 429
    assert "Muitas Tentativas" in resposta.text
    assert cliente.get("/produtos").status_code == 200


def test_headers_cookies_cache_e_erros_amigaveis(aplicacao):
    @aplicacao.get("/erro-teste")
    def erro_teste():
        abort(500)

    cliente = aplicacao.test_client()
    resposta = cliente.get("/")
    assert resposta.headers["X-Content-Type-Options"] == "nosniff"
    assert resposta.headers["X-Frame-Options"] == "DENY"
    assert resposta.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in resposta.headers["Permissions-Policy"]
    assert "default-src 'self'" in resposta.headers["Content-Security-Policy"]
    assert (
        "font-src 'self' https://fonts.gstatic.com"
        in resposta.headers["Content-Security-Policy"]
    )
    assert "img-src 'self' data:" in resposta.headers["Content-Security-Policy"]
    assert "*" not in resposta.headers["Content-Security-Policy"]
    assert "fonts.googleapis.com" not in resposta.headers["Content-Security-Policy"]
    assert "unsafe-inline" not in resposta.headers["Content-Security-Policy"]
    assert "unsafe-eval" not in resposta.headers["Content-Security-Policy"]
    assert "Strict-Transport-Security" not in resposta.headers

    privado = cliente.get("/carrinho")
    assert privado.headers["Cache-Control"] == "no-store, private"

    erro = cliente.get("/erro-teste")
    assert erro.status_code == 500
    assert "Algo Não Saiu como Esperado" in erro.text
    assert "Traceback" not in erro.text


def test_paginas_e_css_nao_dependem_de_fontes_google(cliente_http):
    """Protege a independência tipográfica e o funcionamento offline."""
    rotas = (
        "/",
        "/produtos",
        "/produtos/1",
        "/carrinho",
        "/login",
        "/cadastro",
        "/sobre",
        "/faq",
        "/offline",
    )
    origens_proibidas = ("fonts.googleapis.com", "fonts.gstatic.com")

    for rota in rotas:
        resposta = cliente_http.get(rota)
        assert resposta.status_code == 200
        assert all(origem not in resposta.text for origem in origens_proibidas)

    raiz = Path(__file__).parents[1] / "aplicacao"
    arquivos_runtime = (
        *raiz.glob("templates/**/*.html"),
        *raiz.glob("static/css/**/*.css"),
    )
    for caminho in arquivos_runtime:
        conteudo = caminho.read_text(encoding="utf-8").lower()
        assert all(origem not in conteudo for origem in origens_proibidas)
        assert not re.search(
            r"@import\s+(?:url\()?[^;]*(?:googleapis|gstatic)", conteudo
        )


def test_cookies_e_hsts_somente_em_producao_https(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "uma-chave-forte-apenas-para-o-teste")
    monkeypatch.setenv("SITE_URL", "https://loja.exemplo")
    app = criar_aplicacao(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'producao.db'}",
            "INICIALIZAR_DADOS": False,
            "WTF_CSRF_ENABLED": False,
            "RATELIMIT_ENABLED": False,
        }
    )
    cliente = app.test_client()

    resposta = cliente.post(
        "/login",
        data={"email": "inexistente@example.com", "senha": "12345678"},
        base_url="https://loja.exemplo",
    )
    cookie = resposta.headers.get("Set-Cookie", "")
    assert "Secure" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert resposta.headers["Strict-Transport-Security"].startswith("max-age=")


def test_paginas_institucionais_sao_publicas(cliente_http):
    for rota in ("/privacidade", "/termos", "/seguranca"):
        resposta = cliente_http.get(rota)
        assert resposta.status_code == 200
        assert 'content="index, follow"' in resposta.text
        assert 'rel="canonical"' in resposta.text
