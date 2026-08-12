"""Testes da rotação periódica de senha e da validação de dispositivos."""

import importlib
import time
from datetime import datetime, timedelta, timezone

from aplicacao import banco
from aplicacao.modelos import Cliente, SegurancaConta
from aplicacao.servicos.tokens import gerar_token_redefinicao

CHAVE_CLIENTE_PENDENTE = "seguranca_cliente_pendente"
CHAVE_INICIO_AUTENTICACAO = "autenticacao_iniciada_em"


def _habilitar(aplicacao, senha=False, dispositivo=False):
    aplicacao.config.update(
        AUTH_SESSION_MAX_AGE_DAYS=7,
        PASSWORD_ROTATION_ENABLED=senha,
        PASSWORD_MAX_AGE_DAYS=180,
        DEVICE_VALIDATION_ENABLED=dispositivo,
        DEVICE_TRUST_DAYS=30,
        DEVICE_CODE_TTL=600,
        DEVICE_COOKIE_NAME="doce_pedido_dispositivo",
    )


def _expirar_senha(aplicacao, email="ana@example.com"):
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == email)
        )
        estado = banco.session.get(SegurancaConta, cliente.id)
        if estado is None:
            estado = SegurancaConta(cliente_id=cliente.id)
            banco.session.add(estado)
        estado.senha_alterada_em = datetime.now(timezone.utc) - timedelta(days=181)
        estado.senha_fingerprint = None
        banco.session.commit()


def _fixar_codigo(monkeypatch):
    modulo = importlib.import_module("aplicacao.controladores.seguranca_conta")
    monkeypatch.setattr(modulo, "_gerar_codigo_dispositivo", lambda: "123456")


def _assert_login_pendente(cliente_http):
    with cliente_http.session_transaction() as sessao:
        assert "_user_id" not in sessao
        assert sessao.get(CHAVE_CLIENTE_PENDENTE) == 1


def test_apenas_reset_autentica_somente_depois_da_troca(aplicacao, cliente_http):
    _habilitar(aplicacao, senha=True, dispositivo=False)
    _expirar_senha(aplicacao)

    resposta = cliente_http.post(
        "/login",
        data={"email": "ana@example.com", "senha": "segredo12"},
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/senha-expirada")
    _assert_login_pendente(cliente_http)

    resposta = cliente_http.get("/senha-expirada")
    assert resposta.status_code == 200
    _assert_login_pendente(cliente_http)

    resposta = cliente_http.post(
        "/senha-expirada",
        data={"senha": "NovaSenha1!", "confirmacao_senha": "NovaSenha1!"},
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/")

    with cliente_http.session_transaction() as sessao:
        assert sessao.get("_user_id") == "1"
        assert CHAVE_CLIENTE_PENDENTE not in sessao


def test_apenas_validacao_autentica_somente_depois_do_codigo(
    aplicacao, cliente_http, monkeypatch
):
    _habilitar(aplicacao, senha=False, dispositivo=True)
    _fixar_codigo(monkeypatch)

    resposta = cliente_http.post(
        "/login",
        data={"email": "ana@example.com", "senha": "segredo12"},
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/validar-dispositivo")
    _assert_login_pendente(cliente_http)

    pagina_codigo = cliente_http.get("/validar-dispositivo")
    assert pagina_codigo.status_code == 200
    with cliente_http.session_transaction() as sessao:
        assert "_user_id" not in sessao
        assert sessao.get("desafio_dispositivo")

    resposta = cliente_http.post("/validar-dispositivo", data={"codigo": "123456"})
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/")
    assert "doce_pedido_dispositivo=" in resposta.headers.get("Set-Cookie", "")

    with cliente_http.session_transaction() as sessao:
        assert sessao.get("_user_id") == "1"
        assert CHAVE_CLIENTE_PENDENTE not in sessao
        assert "desafio_dispositivo" not in sessao


def test_reset_e_validacao_autenticam_somente_apos_as_duas_etapas(
    aplicacao, cliente_http, monkeypatch
):
    _habilitar(aplicacao, senha=True, dispositivo=True)
    _expirar_senha(aplicacao)
    _fixar_codigo(monkeypatch)

    resposta = cliente_http.post(
        "/login",
        data={"email": "ana@example.com", "senha": "segredo12"},
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/senha-expirada")
    _assert_login_pendente(cliente_http)

    resposta = cliente_http.post(
        "/senha-expirada",
        data={"senha": "NovaSenha1!", "confirmacao_senha": "NovaSenha1!"},
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/validar-dispositivo")
    _assert_login_pendente(cliente_http)

    pagina_codigo = cliente_http.get("/validar-dispositivo")
    assert pagina_codigo.status_code == 200
    _assert_login_pendente(cliente_http)

    resposta = cliente_http.post("/validar-dispositivo", data={"codigo": "123456"})
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/")
    with cliente_http.session_transaction() as sessao:
        assert sessao.get("_user_id") == "1"
        assert CHAVE_CLIENTE_PENDENTE not in sessao


def test_service_worker_nao_vira_destino_apos_validacao(
    aplicacao, cliente_http, monkeypatch
):
    _habilitar(aplicacao, senha=False, dispositivo=True)
    _fixar_codigo(monkeypatch)

    resposta = cliente_http.post(
        "/login",
        data={"email": "ana@example.com", "senha": "segredo12"},
    )
    assert resposta.headers["Location"].endswith("/validar-dispositivo")
    cliente_http.get("/validar-dispositivo")

    resposta_sw = cliente_http.get("/service-worker.js")
    assert resposta_sw.status_code == 200
    _assert_login_pendente(cliente_http)

    resposta = cliente_http.post("/validar-dispositivo", data={"codigo": "123456"})
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/")
    assert not resposta.headers["Location"].endswith("/service-worker.js")


def test_dispositivo_validado_nao_pede_codigo_a_cada_login(
    aplicacao, cliente_http, monkeypatch
):
    _habilitar(aplicacao, senha=False, dispositivo=True)
    _fixar_codigo(monkeypatch)

    resposta = cliente_http.post(
        "/login", data={"email": "ana@example.com", "senha": "segredo12"}
    )
    assert resposta.headers["Location"].endswith("/validar-dispositivo")
    cliente_http.get("/validar-dispositivo")
    cliente_http.post("/validar-dispositivo", data={"codigo": "123456"})
    cliente_http.post("/logout")

    resposta = cliente_http.post(
        "/login", data={"email": "ana@example.com", "senha": "segredo12"}
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/")
    with cliente_http.session_transaction() as sessao:
        assert sessao.get("_user_id") == "1"
        assert CHAVE_CLIENTE_PENDENTE not in sessao


def test_reset_por_link_atualiza_rotacao_sem_forcar_segunda_troca(
    aplicacao, cliente_http
):
    _habilitar(aplicacao, senha=True, dispositivo=False)
    _expirar_senha(aplicacao)

    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "ana@example.com")
        )
        token = gerar_token_redefinicao(cliente)

    resposta = cliente_http.post(
        f"/redefinir-senha/{token}",
        data={"senha": "NovaSenha1!", "confirmacao_senha": "NovaSenha1!"},
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/")
    with cliente_http.session_transaction() as sessao:
        assert sessao.get("_user_id") == "1"


def test_reset_por_link_exige_dispositivo_antes_do_login(
    aplicacao, cliente_http, monkeypatch
):
    _habilitar(aplicacao, senha=True, dispositivo=True)
    _expirar_senha(aplicacao)
    _fixar_codigo(monkeypatch)

    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "ana@example.com")
        )
        token = gerar_token_redefinicao(cliente)

    resposta = cliente_http.post(
        f"/redefinir-senha/{token}",
        data={"senha": "NovaSenha1!", "confirmacao_senha": "NovaSenha1!"},
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/validar-dispositivo")
    _assert_login_pendente(cliente_http)


def test_login_registra_inicio_absoluto_da_autenticacao(aplicacao, cliente_http):
    _habilitar(aplicacao, senha=False, dispositivo=False)
    antes = int(time.time())

    resposta = cliente_http.post(
        "/login", data={"email": "ana@example.com", "senha": "segredo12"}
    )

    assert resposta.status_code == 302
    depois = int(time.time())
    with cliente_http.session_transaction() as sessao:
        assert sessao.get("_user_id") == "1"
        assert antes <= sessao[CHAVE_INICIO_AUTENTICACAO] <= depois
        assert sessao.permanent is False

    assert aplicacao.config["AUTH_SESSION_MAX_AGE_DAYS"] == 7
    assert aplicacao.config["PERMANENT_SESSION_LIFETIME"] == timedelta(days=7)
    assert aplicacao.config["REMEMBER_COOKIE_DURATION"] == timedelta(days=7)


def test_lembrar_nao_ultrapassa_limite_de_sete_dias(aplicacao, cliente_http):
    _habilitar(aplicacao, senha=False, dispositivo=False)

    resposta = cliente_http.post(
        "/login",
        data={
            "email": "ana@example.com",
            "senha": "segredo12",
            "lembrar": "on",
        },
    )

    assert resposta.status_code == 302
    assert "remember_token=" in resposta.headers.get("Set-Cookie", "")
    with cliente_http.session_transaction() as sessao:
        assert sessao.get("_user_id") == "1"
        assert sessao.permanent is True
        assert CHAVE_INICIO_AUTENTICACAO in sessao


def test_sessao_expira_apos_sete_dias_e_preserva_carrinho(aplicacao, cliente_http):
    _habilitar(aplicacao, senha=False, dispositivo=False)
    cliente_http.post(
        "/login", data={"email": "ana@example.com", "senha": "segredo12"}
    )

    with cliente_http.session_transaction() as sessao:
        sessao[CHAVE_INICIO_AUTENTICACAO] = int(time.time()) - (7 * 86400)
        sessao["carrinho"] = {"1": 2}

    resposta = cliente_http.get("/")

    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/login")
    with cliente_http.session_transaction() as sessao:
        assert "_user_id" not in sessao
        assert CHAVE_INICIO_AUTENTICACAO not in sessao
        assert sessao.get("carrinho") == {"1": 2}

    pagina_login = cliente_http.get(resposta.headers["Location"])
    assert "Sua sessão expirou por segurança. Faça login novamente." in pagina_login.text


def test_sessao_continua_valida_antes_de_sete_dias(aplicacao, cliente_http):
    _habilitar(aplicacao, senha=False, dispositivo=False)
    cliente_http.post(
        "/login", data={"email": "ana@example.com", "senha": "segredo12"}
    )

    with cliente_http.session_transaction() as sessao:
        sessao[CHAVE_INICIO_AUTENTICACAO] = int(time.time()) - (6 * 86400)

    resposta = cliente_http.get("/")

    assert resposta.status_code == 200
    with cliente_http.session_transaction() as sessao:
        assert sessao.get("_user_id") == "1"
        assert CHAVE_INICIO_AUTENTICACAO in sessao


def test_validacao_dispositivo_preserva_inicio_da_autenticacao(
    aplicacao, cliente_http, monkeypatch
):
    _habilitar(aplicacao, senha=False, dispositivo=True)
    _fixar_codigo(monkeypatch)

    resposta = cliente_http.post(
        "/login", data={"email": "ana@example.com", "senha": "segredo12"}
    )
    assert resposta.headers["Location"].endswith("/validar-dispositivo")
    with cliente_http.session_transaction() as sessao:
        inicio = sessao[CHAVE_INICIO_AUTENTICACAO]

    cliente_http.get("/validar-dispositivo")
    resposta = cliente_http.post("/validar-dispositivo", data={"codigo": "123456"})

    assert resposta.status_code == 302
    with cliente_http.session_transaction() as sessao:
        assert sessao.get("_user_id") == "1"
        assert sessao[CHAVE_INICIO_AUTENTICACAO] == inicio
