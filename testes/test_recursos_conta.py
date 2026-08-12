"""Testes de endereços e cupcakes favoritos da área do cliente."""

import importlib
from pathlib import Path

from aplicacao import banco
from aplicacao.modelos import Endereco, Favorito

recursos_conta = importlib.import_module("aplicacao.controladores.recursos_conta")


def dados_endereco(nome="Casa", **alteracoes):
    dados = {
        "nome": nome,
        "cep": "95010-000",
        "logradouro": "Rua Sinimbu",
        "numero": "100",
        "complemento": "Apto 10",
        "bairro": "Centro",
        "cidade": "Caxias do Sul",
        "uf": "RS",
        "referencia": "Próximo à praça",
    }
    dados.update(alteracoes)
    return dados


def test_enderecos_exigem_login(cliente_http):
    resposta = cliente_http.get("/minha-conta/enderecos")
    assert resposta.status_code == 302
    assert "/login" in resposta.headers["Location"]


def test_primeiro_endereco_vira_principal(cliente_http, login, aplicacao):
    login()
    resposta = cliente_http.post(
        "/minha-conta/enderecos/adicionar",
        data=dados_endereco(),
        follow_redirects=True,
    )
    assert "Endereço Casa adicionado" in resposta.text
    with aplicacao.app_context():
        endereco = banco.session.scalar(banco.select(Endereco))
        assert endereco.nome == "Casa"
        assert endereco.cep == "95010000"
        assert endereco.principal is True


def test_multiplos_enderecos_e_troca_de_principal(
    cliente_http, login, aplicacao
):
    login()
    cliente_http.post(
        "/minha-conta/enderecos/adicionar",
        data=dados_endereco("Casa"),
    )
    cliente_http.post(
        "/minha-conta/enderecos/adicionar",
        data=dados_endereco(
            "Trabalho",
            numero="200",
            complemento="",
            referencia="",
        ),
    )
    with aplicacao.app_context():
        trabalho = banco.session.scalar(
            banco.select(Endereco).where(Endereco.nome == "Trabalho")
        )
        trabalho_id = trabalho.id
    cliente_http.post(f"/minha-conta/enderecos/{trabalho_id}/principal")

    with aplicacao.app_context():
        enderecos = banco.session.scalars(
            banco.select(Endereco).order_by(Endereco.nome)
        ).all()
        principais = [endereco.nome for endereco in enderecos if endereco.principal]
        assert principais == ["Trabalho"]
        assert len(enderecos) == 2


def test_nome_de_endereco_nao_pode_repetir(cliente_http, login, aplicacao):
    login()
    cliente_http.post(
        "/minha-conta/enderecos/adicionar",
        data=dados_endereco("Casa"),
    )
    resposta = cliente_http.post(
        "/minha-conta/enderecos/adicionar",
        data=dados_endereco("casa", numero="500"),
        follow_redirects=True,
    )
    assert "já possui um endereço com este nome" in resposta.text
    with aplicacao.app_context():
        quantidade = banco.session.scalar(
            banco.select(banco.func.count(Endereco.id))
        )
        assert quantidade == 1


def test_endereco_recusa_uf_que_nao_existe(cliente_http, login, aplicacao):
    login()
    resposta = cliente_http.post(
        "/minha-conta/enderecos/adicionar",
        data=dados_endereco(uf="ZZ"),
        follow_redirects=True,
    )

    assert "Selecione uma UF válida" in resposta.text
    with aplicacao.app_context():
        assert banco.session.scalar(banco.select(Endereco)) is None


def test_consulta_cep_preenche_dados_normalizados(
    cliente_http, login, monkeypatch
):
    login()

    def consulta_simulada(cep):
        assert cep == "95010000"
        return {
            "cep": cep,
            "logradouro": "Rua Sinimbu",
            "bairro": "Centro",
            "cidade": "Caxias do Sul",
            "uf": "RS",
        }

    monkeypatch.setattr(
        recursos_conta,
        "consultar_cep_viacep",
        consulta_simulada,
    )
    resposta = cliente_http.get("/api/cep/95010-000")
    assert resposta.status_code == 200
    assert resposta.get_json() == {
        "cep": "95010000",
        "logradouro": "Rua Sinimbu",
        "bairro": "Centro",
        "cidade": "Caxias do Sul",
        "uf": "RS",
    }


def test_consulta_cep_recusa_formato_invalido(cliente_http, login, monkeypatch):
    login()
    chamado = False

    def consulta_nao_deve_ocorrer(_cep):
        nonlocal chamado
        chamado = True

    monkeypatch.setattr(
        recursos_conta,
        "consultar_cep_viacep",
        consulta_nao_deve_ocorrer,
    )
    resposta = cliente_http.get("/api/cep/123")
    assert resposta.status_code == 400
    assert chamado is False


def test_api_de_ufs_repassa_localidades_do_ibge(
    cliente_http, login, monkeypatch
):
    login()
    monkeypatch.setattr(
        recursos_conta,
        "consultar_ufs_ibge",
        lambda: [
            {"sigla": "RS", "nome": "Rio Grande do Sul"},
            {"sigla": "SC", "nome": "Santa Catarina"},
        ],
    )

    resposta = cliente_http.get("/api/localidades/ufs")
    assert resposta.status_code == 200
    assert resposta.get_json()[0] == {
        "sigla": "RS",
        "nome": "Rio Grande do Sul",
    }


def test_api_de_municipios_depende_da_uf(
    cliente_http, login, monkeypatch
):
    login()
    chamadas = []

    def municipios_simulados(uf):
        chamadas.append(uf)
        return ["Bento Gonçalves", "Caxias do Sul"]

    monkeypatch.setattr(
        recursos_conta,
        "consultar_municipios_ibge",
        municipios_simulados,
    )
    resposta = cliente_http.get("/api/localidades/ufs/rs/municipios")
    assert resposta.status_code == 200
    assert chamadas == ["RS"]
    assert resposta.get_json() == ["Bento Gonçalves", "Caxias do Sul"]

    invalida = cliente_http.get("/api/localidades/ufs/123/municipios")
    assert invalida.status_code == 400
    inexistente = cliente_http.get("/api/localidades/ufs/ZZ/municipios")
    assert inexistente.status_code == 400


def test_pagina_de_enderecos_exibe_seletores_e_modal_interno(cliente_http, login):
    login()
    pagina = cliente_http.get("/minha-conta/enderecos")
    assert pagina.status_code == 200
    assert "data-address-uf" in pagina.text
    assert "data-address-city" in pagina.text
    assert "modal-excluir-endereco" in pagina.text
    assert "conta-recursos.js" in pagina.text


def test_favoritar_e_remover_produto(cliente_http, login, aplicacao):
    login()
    resposta = cliente_http.post(
        "/favoritos/1/alternar",
        headers={"X-Requested-With": "fetch"},
    )
    assert resposta.status_code == 200
    assert resposta.get_json()["favoritado"] is True

    pagina = cliente_http.get("/minha-conta/favoritos")
    assert "Cupcakes Favoritos" in pagina.text
    assert "Chocolate" in pagina.text

    status = cliente_http.get("/favoritos/status").get_json()
    assert status["autenticado"] is True
    assert status["favoritos"] == [1]

    resposta = cliente_http.post(
        "/favoritos/1/alternar",
        headers={"X-Requested-With": "fetch"},
    )
    assert resposta.get_json()["favoritado"] is False
    with aplicacao.app_context():
        quantidade = banco.session.scalar(
            banco.select(banco.func.count(Favorito.id))
        )
        assert quantidade == 0


def test_favoritos_sao_isolados_por_cliente(cliente_http, login, aplicacao):
    login()
    cliente_http.post("/favoritos/1/alternar")
    cliente_http.post("/logout")
    login(email="bia@example.com")

    pagina = cliente_http.get("/minha-conta/favoritos")
    assert "Chocolate" not in pagina.text
    with aplicacao.app_context():
        favorito = banco.session.scalar(banco.select(Favorito))
        assert favorito.cliente_id == 1


def test_produto_inativo_nao_pode_ser_adicionado_aos_favoritos(
    cliente_http, login
):
    login()
    resposta = cliente_http.post(
        "/favoritos/3/alternar",
        headers={"X-Requested-With": "fetch"},
    )
    assert resposta.status_code == 404
    assert "indisponível" in resposta.get_json()["erro"]


def test_paginas_novas_exibem_navegacao_completa(cliente_http, login):
    login()
    for rota in ("/minha-conta/enderecos", "/minha-conta/favoritos"):
        resposta = cliente_http.get(rota)
        assert resposta.status_code == 200
        assert "Meus Dados" in resposta.text
        assert "Endereços" in resposta.text
        assert "Cupcakes Favoritos" in resposta.text
        assert "Meus Pedidos" in resposta.text


def test_script_global_prepara_favoritos_e_consulta_de_cep():
    raiz = Path(__file__).resolve().parents[1]
    conteudo = (
        raiz / "aplicacao/static/js/conta-recursos.js"
    ).read_text(encoding="utf-8")
    assert "/favoritos/status" in conteudo
    assert "favorite-card-toggle" in conteudo
    assert "/api/cep/" in conteudo
    assert "/api/localidades/ufs" in conteudo
    assert "data-address-form" in conteudo
    assert "window.confirm" not in conteudo
