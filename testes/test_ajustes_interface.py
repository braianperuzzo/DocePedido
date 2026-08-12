"""Regressões dos ajustes finais de interface solicitados na revisão visual."""

import importlib
from pathlib import Path

recursos_conta = importlib.import_module("aplicacao.controladores.recursos_conta")


def test_localidades_usam_fallback_sem_erro_502(cliente_http, login, monkeypatch):
    login()

    def falha_externa(*_args, **_kwargs):
        raise RuntimeError("serviço indisponível")

    monkeypatch.setattr(recursos_conta, "consultar_ufs_ibge", falha_externa)
    resposta_ufs = cliente_http.get("/api/localidades/ufs")
    assert resposta_ufs.status_code == 200
    assert len(resposta_ufs.get_json()) == 27

    monkeypatch.setattr(recursos_conta, "consultar_municipios_ibge", falha_externa)
    resposta_cidades = cliente_http.get("/api/localidades/ufs/RS/municipios")
    assert resposta_cidades.status_code == 200
    assert resposta_cidades.get_json() == []


def test_produto_exibe_textos_das_acoes(cliente_http):
    pagina = cliente_http.get("/produtos/1")
    assert pagina.status_code == 200
    assert ">Carrinho</span>" in pagina.text

    script = Path("aplicacao/static/js/conta-recursos.js").read_text(encoding="utf-8")
    assert 'return favoritado ? "Desfavoritar" : "Favoritar";' in script
    assert 'controle.classList.add("btn", "btn-outline-secondary")' in script
    assert "botaoCarrinho.after(controle)" in script


def test_area_da_conta_compartilha_navegacao_completa(cliente_http, login):
    login()
    pagina = cliente_http.get("/pedidos")
    assert pagina.status_code == 200
    assert 'account-resource-page orders-history-page' in pagina.text
    for rotulo in ("Meus Dados", "Endereços", "Cupcakes Favoritos", "Meus Pedidos"):
        assert rotulo in pagina.text


def test_favoritos_nao_exibe_card_de_contagem():
    template = Path("aplicacao/templates/conta/favoritos.html").read_text(encoding="utf-8")
    assert "favorite-account-summary" not in template
    assert "cupcake salvo" not in template


def test_cupom_usa_input_group_na_largura_total():
    template = Path("aplicacao/templates/carrinho/carrinho.html").read_text(encoding="utf-8")
    assert 'class="coupon-field-summary"' in template
    assert 'class="input-group"' in template
    assert "data-coupon-apply" in template

    css = Path("aplicacao/static/css/ajustes-interface.css").read_text(encoding="utf-8")
    assert ".coupon-field-summary .input-group" in css
    assert "flex-wrap: nowrap" in css


def test_novo_endereco_ocupa_largura_da_area_da_conta():
    css = Path("aplicacao/static/css/conta-recursos.css").read_text(encoding="utf-8")
    trecho = css.split(".address-new-card {", 1)[1].split("}", 1)[0]
    assert "width: 100%" in trecho
    assert "max-width: none" in trecho


def test_css_padroniza_produto_campos_e_cores():
    css = Path("aplicacao/static/css/ajustes-interface.css").read_text(encoding="utf-8")
    assert "max-height: 410px" in css
    assert ".form-control.is-valid" in css
    assert ".form-control.is-invalid" in css
    assert "border-color: var(--cor-borda) !important" in css
