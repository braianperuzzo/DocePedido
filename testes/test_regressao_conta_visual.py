"""Regressões simples da Área do Cliente e do acesso direto no cabeçalho."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def test_template_conta_mantem_icones_placeholders_e_estados_de_senha():
    conteudo = (RAIZ / "aplicacao/templates/autenticacao/conta.html").read_text(
        encoding="utf-8"
    )

    assert 'transform="translate(-8 -21.1)"' in conteudo
    assert 'transform="translate(-4 -2)"' in conteudo
    assert 'stroke="currentColor"' in conteudo
    assert 'class="conta-olho-estado olho-aberto"' in conteudo
    assert 'class="conta-olho-estado olho-fechado"' in conteudo
    assert "exemplo@exemplo.com.br" in conteudo
    assert "Digite sua Senha" in conteudo
    assert "Crie uma Senha" in conteudo
    assert "Repita sua Senha" in conteudo
    assert "data-password-criteria" in conteudo


def test_cabecalho_prepara_acesso_compacto_para_visitante_e_cliente_logado():
    conteudo = (RAIZ / "aplicacao/static/js/tema-inicial.js").read_text(
        encoding="utf-8"
    )

    assert 'acesso.className = "nav-item account-access"' in conteudo
    assert 'titulo.className = "account-access-title"' in conteudo
    assert "if (!autenticado) titulo.href = destinoConta" in conteudo
    assert 'titulo.textContent = autenticado ? `Olá, ${primeiroNome}` : "Minha Conta"' in conteudo
    assert 'acao.textContent = "Cadastrar"' in conteudo
    assert 'linkConta.href = "/minha-conta"' in conteudo
    assert 'linkConta.textContent = "Conta"' in conteudo
    assert 'linkPedidos.textContent = "Pedidos"' in conteudo
    assert 'separador.textContent = "|"' in conteudo


def test_minha_conta_reaproveita_componentes_e_confirmacao_por_email():
    conteudo = (RAIZ / "aplicacao/templates/conta/perfil.html").read_text(
        encoding="utf-8"
    )

    assert "Meus Dados" in conteudo
    assert "Editar Dados" in conteudo
    assert "Alterar Senha" in conteudo
    assert "Confirmar" in conteudo
    assert "modal-editar-dados" in conteudo
    assert "modal-alterar-senha" in conteudo
    assert "data-profile-password-toggle" in conteudo


def test_meus_pedidos_mantem_resumo_e_expansao_no_proprio_card():
    conteudo = (RAIZ / "aplicacao/templates/pedidos/lista.html").read_text(
        encoding="utf-8"
    )

    assert "Meus Pedidos" in conteudo
    assert 'data-bs-toggle="collapse"' in conteudo
    assert 'aria-controls="pedido-{{ pedido.id }}"' in conteudo
    assert "pedido.data_pedido" in conteudo
    assert "pedido.valor_total|moeda" in conteudo
    assert "pedido.status" in conteudo
    assert "item.produto.nome" in conteudo
    assert "Ver Detalhes" in conteudo


def test_css_da_conta_esconde_criterios_ate_haver_digitacao():
    conteudo = (RAIZ / "aplicacao/static/css/conta.css").read_text(encoding="utf-8")

    assert ".conta-criterios {\n  display: none;\n}" in conteudo
    assert ".conta-formulario:has(#cadastro-senha:not(:placeholder-shown))" in conteudo
    assert ".conta-olho-estado[hidden]" in conteudo
    assert ".account-access" in conteudo
    assert ".profile-account-grid" in conteudo
    assert ".orders-history-card" in conteudo


def test_estado_enviando_mantem_a_paleta_da_area_do_cliente():
    conteudo = (RAIZ / "aplicacao/static/css/conta.css").read_text(encoding="utf-8")

    assert ".conta-botao:disabled" in conteudo
    assert "border-color: var(--cor-rosa-escuro);" in conteudo
    assert "background: var(--cor-rosa-escuro);" in conteudo
    assert "cursor: wait;" in conteudo


def test_redefinicao_reutiliza_janela_de_requisitos_da_senha():
    conteudo = (
        RAIZ / "aplicacao/templates/autenticacao/redefinir_senha.html"
    ).read_text(encoding="utf-8")

    assert "data-password-criteria" in conteudo
    assert 'data-password-rule="length"' in conteudo
    assert 'data-password-rule="upper"' in conteudo
    assert 'data-password-rule="lower"' in conteudo
    assert 'data-password-rule="number"' in conteudo
    assert 'data-password-rule="special"' in conteudo


def test_menu_mobile_mantem_itens_e_acoes_centralizados():
    conteudo = (RAIZ / "aplicacao/static/css/conta.css").read_text(encoding="utf-8")

    assert "#menu .navbar-nav {" in conteudo
    assert "align-items: center !important;" in conteudo
    assert "text-align: center;" in conteudo
    assert "#menu .navbar-nav > .nav-item" in conteudo
    assert "#menu .theme-toggle" in conteudo
    assert "justify-content: center;" in conteudo
    assert "margin: 0.15rem auto 0;" in conteudo


def test_service_worker_evitar_rede_quando_offline():
    conteudo = (RAIZ / "aplicacao/static/js/service-worker.js").read_text(
        encoding="utf-8"
    )

    assert 'const CACHE_NAME = "doce-pedido-static-v9";' in conteudo
    assert "if (!self.navigator.onLine) {" in conteudo
    assert "event.respondWith(caches.match(OFFLINE_URL));" in conteudo

