"""Testes de autenticação da aplicação."""

import pytest

from aplicacao import banco, criar_aplicacao
from aplicacao.controladores.autenticacao import validar_cpf
from aplicacao.modelos import Cliente

CPF_VALIDO = "529.982.247-25"
SENHA_VALIDA = "Doce@123"


def dados_cadastro(**alteracoes):
    """Monta um cadastro válido permitindo substituir o cenário sob teste."""
    dados = {
        "nome": "Carlos",
        "cpf": CPF_VALIDO,
        "email": "carlos@example.com",
        "senha": SENHA_VALIDA,
        "confirmacao_senha": SENHA_VALIDA,
    }
    dados.update(alteracoes)
    return dados


def test_paginas_da_area_do_cliente_abrem_com_estado_correto(cliente_http):
    """Mantém as rotas públicas e sinaliza o painel inicial no componente comum."""
    login = cliente_http.get("/login")
    cadastro = cliente_http.get("/cadastro")

    assert login.status_code == 200
    assert cadastro.status_code == 200
    assert 'data-initial-panel="entrar"' in login.text
    assert 'data-initial-panel="cadastrar"' in cadastro.text
    assert "Minha Conta" in login.text
    assert "Minha Conta" in cadastro.text


def test_cadastro_valido_normaliza_cpf_e_protege_senha(cliente_http, aplicacao):
    resposta = cliente_http.post(
        "/cadastro", data=dados_cadastro(), follow_redirects=True
    )
    assert "Cadastro Realizado com Sucesso" in resposta.text
    with aplicacao.app_context():
        cliente = banco.session.scalar(
            banco.select(Cliente).where(Cliente.email == "carlos@example.com")
        )
        assert cliente.cpf == "52998224725"
        assert cliente.senha_hash != SENHA_VALIDA
        assert cliente.verificar_senha(SENHA_VALIDA)


@pytest.mark.parametrize(
    ("senha", "mensagem"),
    (
        ("doce@123", "uma letra maiúscula"),
        ("DOCE@123", "uma letra minúscula"),
        ("Doce@abc", "um número"),
        ("Doce1234", "um caractere especial"),
        ("Dc@123", "8 caracteres"),
    ),
)
def test_cadastro_recusa_senha_sem_criterio(cliente_http, senha, mensagem):
    resposta = cliente_http.post(
        "/cadastro",
        data=dados_cadastro(senha=senha, confirmacao_senha=senha),
    )
    assert mensagem in resposta.text


def test_cadastro_recusa_confirmacao_diferente(cliente_http):
    resposta = cliente_http.post(
        "/cadastro", data=dados_cadastro(confirmacao_senha="Outra@123")
    )
    assert "As senhas informadas não coincidem" in resposta.text


@pytest.mark.parametrize(
    "cpf",
    ("", "123", "111.111.111-11", "529.982.247-24", "529982247250"),
)
def test_cadastro_recusa_cpf_invalido(cliente_http, cpf):
    resposta = cliente_http.post("/cadastro", data=dados_cadastro(cpf=cpf))
    assert "Informe um CPF válido" in resposta.text


def test_validar_cpf_aceita_formatado_e_normalizado():
    assert validar_cpf(CPF_VALIDO)
    assert validar_cpf("52998224725")


def test_cadastro_recusa_cpf_repetido_sem_expor_o_dado(cliente_http):
    primeira = cliente_http.post("/cadastro", data=dados_cadastro())
    segunda = cliente_http.post(
        "/cadastro",
        data=dados_cadastro(email="outro@example.com"),
    )
    assert primeira.status_code == 302
    assert "Não foi Possível concluir o cadastro com estes dados" in segunda.text


def test_cadastro_recusa_email_duplicado(cliente_http):
    resposta = cliente_http.post(
        "/cadastro", data=dados_cadastro(email="ana@example.com")
    )
    assert "Não foi Possível concluir o cadastro" in resposta.text


def test_cadastro_recusa_email_invalido(cliente_http):
    resposta = cliente_http.post(
        "/cadastro", data=dados_cadastro(email="email-invalido")
    )
    assert "Informe um e-mail válido" in resposta.text


def test_erro_de_cadastro_mantem_dados_seguros_e_painel(cliente_http):
    resposta = cliente_http.post(
        "/cadastro",
        data=dados_cadastro(
            nome="Carlos Silva",
            cpf=CPF_VALIDO,
            email="invalido",
            senha="Segredo@1",
            confirmacao_senha="Segredo@2",
        ),
    )
    assert 'data-initial-panel="cadastrar"' in resposta.text
    assert 'value="Carlos Silva"' in resposta.text
    assert f'value="{CPF_VALIDO}"' in resposta.text
    assert 'value="invalido"' in resposta.text
    assert "Segredo@1" not in resposta.text
    assert "Segredo@2" not in resposta.text


def test_login_valido(login):
    resposta = login()
    assert "Bem-vindo, Ana" in resposta.text
    assert "Meus Pedidos" in resposta.text


def test_login_invalido_permanece_em_entrar(login):
    resposta = login(senha="incorreta")
    assert "E-mail ou senha inválidos" in resposta.text
    assert 'data-initial-panel="entrar"' in resposta.text


def test_login_retorna_ao_destino_interno_solicitado(cliente_http):
    resposta = cliente_http.post(
        "/login?next=/carrinho",
        data={"email": "ana@example.com", "senha": "segredo12"},
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/carrinho")


def test_login_preserva_destino_entre_get_e_post_do_formulario(cliente_http):
    pagina = cliente_http.get("/login?next=/carrinho")
    assert pagina.status_code == 200

    resposta = cliente_http.post(
        "/login",
        data={"email": "ana@example.com", "senha": "segredo12"},
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/carrinho")


def test_login_nao_redireciona_para_destino_externo(cliente_http):
    resposta = cliente_http.post(
        "/login?next=https://example.com",
        data={"email": "ana@example.com", "senha": "segredo12"},
    )
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/")
    assert "example.com" not in resposta.headers["Location"]


@pytest.mark.parametrize(("lembrar", "presente"), (("on", True), (None, False)))
def test_login_controla_cookie_lembrar(cliente_http, lembrar, presente):
    dados = {"email": "ana@example.com", "senha": "segredo12"}
    if lembrar:
        dados["lembrar"] = lembrar
    resposta = cliente_http.post("/login", data=dados)
    cookies = resposta.headers.getlist("Set-Cookie")
    assert any(cookie.startswith("remember_token=") for cookie in cookies) is presente


def test_login_preserva_carrinho(cliente_http):
    with cliente_http.session_transaction() as sessao:
        sessao["carrinho"] = {"1": 2}
    cliente_http.post(
        "/login", data={"email": "ana@example.com", "senha": "segredo12"}
    )
    with cliente_http.session_transaction() as sessao:
        assert sessao["carrinho"] == {"1": 2}


def test_rate_limit_de_login_permanece_ativo(tmp_path):
    aplicacao = criar_aplicacao(
        {
            "TESTING": True,
            "SECRET_KEY": "segredo-limite",
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'limite.db'}",
            "INICIALIZAR_DADOS": False,
            "RATELIMIT_ENABLED": True,
            "WTF_CSRF_ENABLED": False,
        }
    )
    cliente_http = aplicacao.test_client()
    for _ in range(5):
        resposta = cliente_http.post(
            "/login", data={"email": "invalido@example.com", "senha": "incorreta"}
        )
        assert resposta.status_code == 200
    resposta = cliente_http.post(
        "/login", data={"email": "invalido@example.com", "senha": "incorreta"}
    )
    assert resposta.status_code == 429


def test_logout(cliente_http, login):
    login()
    resposta = cliente_http.post("/logout", follow_redirects=True)
    assert "Você saiu da sua conta" in resposta.text
    assert "Criar Conta" in resposta.text
