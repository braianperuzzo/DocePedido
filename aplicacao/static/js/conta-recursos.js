(() => {
  const CAMINHOS_CONTA = [
    ["/minha-conta", "Meus Dados", "dados"],
    ["/minha-conta/enderecos", "Endereços", "enderecos"],
    ["/minha-conta/favoritos", "Cupcakes Favoritos", "favoritos"],
    ["/pedidos", "Meus Pedidos", "pedidos"],
  ];

  const UFS_BRASIL = [
    ["AC", "Acre"],
    ["AL", "Alagoas"],
    ["AP", "Amapá"],
    ["AM", "Amazonas"],
    ["BA", "Bahia"],
    ["CE", "Ceará"],
    ["DF", "Distrito Federal"],
    ["ES", "Espírito Santo"],
    ["GO", "Goiás"],
    ["MA", "Maranhão"],
    ["MT", "Mato Grosso"],
    ["MS", "Mato Grosso do Sul"],
    ["MG", "Minas Gerais"],
    ["PA", "Pará"],
    ["PB", "Paraíba"],
    ["PR", "Paraná"],
    ["PE", "Pernambuco"],
    ["PI", "Piauí"],
    ["RJ", "Rio de Janeiro"],
    ["RN", "Rio Grande do Norte"],
    ["RS", "Rio Grande do Sul"],
    ["RO", "Rondônia"],
    ["RR", "Roraima"],
    ["SC", "Santa Catarina"],
    ["SP", "São Paulo"],
    ["SE", "Sergipe"],
    ["TO", "Tocantins"],
  ].map(([sigla, nome]) => ({ sigla, nome }));

  function paginaContaAtual() {
    const caminho = window.location.pathname;
    if (caminho.startsWith("/minha-conta/enderecos")) return "enderecos";
    if (caminho.startsWith("/minha-conta/favoritos")) return "favoritos";
    if (caminho.startsWith("/pedidos")) return "pedidos";
    if (caminho === "/minha-conta") return "dados";
    return "";
  }

  function configurarNavegacaoConta() {
    const atual = paginaContaAtual();
    document.querySelectorAll(".profile-account-nav").forEach((nav) => {
      nav.dataset.accountNav = "true";
      nav.replaceChildren();
      CAMINHOS_CONTA.forEach(([href, texto, chave]) => {
        const link = document.createElement("a");
        link.href = href;
        link.textContent = texto;
        if (chave === atual) {
          link.classList.add("active");
          link.setAttribute("aria-current", "page");
        }
        nav.append(link);
      });
    });
  }

  function formatarCep(valor) {
    const numeros = valor.replace(/\D/g, "").slice(0, 8);
    return numeros.length > 5
      ? `${numeros.slice(0, 5)}-${numeros.slice(5)}`
      : numeros;
  }

  async function obterUfs() {
    return UFS_BRASIL;
  }

  function selecionarOpcao(select, valor) {
    if (!select || !valor) return;
    const existe = Array.from(select.options).some(
      (opcao) => opcao.value === valor,
    );
    if (!existe) {
      select.add(new Option(valor, valor));
    }
    select.value = valor;
  }

  async function carregarUfs(select, selecionada = "") {
    const ufs = await obterUfs();
    const valorAtual = selecionada || select.value;
    select.replaceChildren(new Option("Selecione", ""));
    ufs.forEach((uf) => {
      select.add(new Option(`${uf.sigla} - ${uf.nome}`, uf.sigla));
    });
    selecionarOpcao(select, valorAtual);
  }

  async function carregarCidades(form, uf, selecionada = "") {
    const cidade = form.querySelector("[data-address-city]");
    const campoCidade = form.querySelector("[data-address-city-field]");
    if (!cidade || !campoCidade) return;

    if (!uf) {
      cidade.replaceChildren(new Option("Selecione a cidade", ""));
      cidade.disabled = true;
      campoCidade.hidden = true;
      return;
    }

    campoCidade.hidden = false;

    if (selecionada) {
      cidade.replaceChildren(new Option("Selecione a cidade", ""));
      selecionarOpcao(cidade, selecionada);
      cidade.disabled = false;
      return;
    }

    cidade.disabled = true;
    cidade.replaceChildren(new Option("Carregando cidades...", ""));

    try {
      const resposta = await fetch(
        `/api/localidades/ufs/${encodeURIComponent(uf)}/municipios`,
        {
          headers: { Accept: "application/json" },
          credentials: "same-origin",
        },
      );
      const dados = await resposta.json();
      if (!resposta.ok || !Array.isArray(dados) || !dados.length) {
        throw new Error("Localidades indisponíveis");
      }

      cidade.replaceChildren(new Option("Selecione a cidade", ""));
      dados.forEach((nome) => cidade.add(new Option(nome, nome)));
      cidade.disabled = false;
    } catch {
      cidade.replaceChildren(new Option("Use o CEP para preencher a cidade", ""));
      cidade.disabled = true;
    }
  }

  function configurarExclusaoEndereco(pagina) {
    const modal = document.querySelector("[data-address-delete-modal]");
    const mensagem = modal?.querySelector("[data-address-delete-message]");
    const confirmar = modal?.querySelector("[data-address-delete-confirm]");
    if (!modal || !mensagem || !confirmar || !window.bootstrap?.Modal) return;

    const instancia = window.bootstrap.Modal.getOrCreateInstance(modal);
    let formularioPendente = null;

    pagina.querySelectorAll("[data-address-delete]").forEach((form) => {
      form.addEventListener("submit", (evento) => {
        evento.preventDefault();
        formularioPendente = form;
        const nome = form.dataset.addressName || "este endereço";
        mensagem.textContent = `Excluir ${nome}? Esta ação não pode ser desfeita.`;
        instancia.show();
      });
    });

    confirmar.addEventListener("click", () => {
      if (!formularioPendente) return;
      const formulario = formularioPendente;
      formularioPendente = null;
      instancia.hide();
      formulario.submit();
    });

    modal.addEventListener("hidden.bs.modal", () => {
      formularioPendente = null;
    });
  }

  function configurarEnderecos() {
    const pagina = document.querySelector("[data-address-page]");
    if (!pagina) return;

    pagina.querySelectorAll("[data-address-form]").forEach((form) => {
      const cep = form.querySelector("[data-cep-input]");
      const botao = form.querySelector("[data-cep-lookup]");
      const retorno = form.querySelector("[data-cep-feedback]");
      const uf = form.querySelector("[data-address-uf]");
      const cidade = form.querySelector("[data-address-city]");
      if (!cep || !botao || !retorno || !uf || !cidade) return;

      const ufInicial = uf.dataset.selectedValue || uf.value;
      const cidadeInicial = cidade.dataset.selectedValue || cidade.value;

      carregarUfs(uf, ufInicial).then(() =>
        carregarCidades(form, ufInicial, cidadeInicial),
      );

      cep.addEventListener("input", () => {
        cep.value = formatarCep(cep.value);
      });

      uf.addEventListener("change", () => {
        cidade.dataset.selectedValue = "";
        retorno.textContent = "";
        retorno.className = "address-cep-feedback";
        carregarCidades(form, uf.value);
      });

      const consultar = async () => {
        const numeros = cep.value.replace(/\D/g, "");
        retorno.className = "address-cep-feedback";
        if (numeros.length !== 8) {
          retorno.textContent = "Informe os 8 dígitos do CEP.";
          retorno.classList.add("is-error");
          return;
        }

        botao.disabled = true;
        botao.textContent = "Buscando...";
        retorno.textContent = "Consultando CEP...";
        try {
          const resposta = await fetch(`/api/cep/${numeros}`, {
            headers: { Accept: "application/json" },
            credentials: "same-origin",
          });
          const dados = await resposta.json();
          if (!resposta.ok) throw new Error(dados.erro || "CEP não encontrado.");

          const campos = {
            logradouro: dados.logradouro,
            bairro: dados.bairro,
          };
          Object.entries(campos).forEach(([nome, valor]) => {
            const campo = form.querySelector(`[name="${nome}"]`);
            if (campo && valor) campo.value = valor;
          });

          if (dados.uf) {
            await carregarUfs(uf, dados.uf);
            await carregarCidades(form, dados.uf, dados.cidade || "");
          }

          cep.value = formatarCep(dados.cep || numeros);
          retorno.textContent = "CEP encontrado. Informe o número e confira os dados.";
          retorno.classList.add("is-success");
          form.querySelector('[name="numero"]')?.focus();
        } catch (erro) {
          retorno.textContent =
            erro.message || "Não foi Possível Consultar o CEP Agora.";
          retorno.classList.add("is-error");
        } finally {
          botao.disabled = false;
          botao.textContent = "Buscar CEP";
        }
      };

      botao.addEventListener("click", consultar);
      cep.addEventListener("blur", () => {
        if (cep.value.replace(/\D/g, "").length === 8) consultar();
      });
    });

    configurarExclusaoEndereco(pagina);
  }

  function idProdutoDoHref(href) {
    if (!href) return null;
    try {
      const url = new URL(href, window.location.origin);
      const resultado = url.pathname.match(/^\/produtos\/(\d+)\/?$/);
      return resultado ? Number(resultado[1]) : null;
    } catch {
      return null;
    }
  }

  function criarIconeCoracao() {
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("width", "20");
    svg.setAttribute("height", "20");
    svg.setAttribute("fill", "none");
    svg.setAttribute("aria-hidden", "true");
    const path = document.createElementNS(ns, "path");
    path.setAttribute(
      "d",
      "M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06" +
        "a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78Z",
    );
    path.setAttribute("stroke", "currentColor");
    path.setAttribute("stroke-width", "2");
    path.setAttribute("stroke-linecap", "round");
    path.setAttribute("stroke-linejoin", "round");
    svg.append(path);
    return svg;
  }

  function rotuloFavorito(favoritado, detalhado = false) {
    if (detalhado) {
      return favoritado ? "Desfavoritar" : "Favoritar";
    }
    return favoritado ? "Remover dos Favoritos" : "Adicionar aos Favoritos";
  }

  function atualizarControleFavorito(controle, favoritado) {
    const detalhado =
      controle.classList.contains("favorite-detail-toggle") ||
      controle.classList.contains("favorite-kit-toggle");
    controle.classList.toggle("is-favorite", favoritado);
    controle.setAttribute("aria-pressed", favoritado ? "true" : "false");
    controle.setAttribute("aria-label", rotuloFavorito(favoritado));
    controle.title = rotuloFavorito(favoritado);
    const caminho = controle.querySelector("svg path");
    if (caminho) caminho.style.fill = favoritado ? "currentColor" : "none";
    const texto = controle.querySelector("[data-favorite-label]");
    if (texto && detalhado) {
      texto.textContent = rotuloFavorito(favoritado, true);
    }
  }

  function feedbackFavorito(mensagem) {
    let toast = document.querySelector("[data-favorite-feedback]");
    if (!toast) {
      toast = document.createElement("div");
      toast.className = "favorite-feedback-toast";
      toast.dataset.favoriteFeedback = "true";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      document.body.append(toast);
    }
    toast.textContent = mensagem;
    toast.classList.add("is-visible");
    window.clearTimeout(feedbackFavorito.timeout);
    feedbackFavorito.timeout = window.setTimeout(
      () => toast.classList.remove("is-visible"),
      2200,
    );
  }

  function botaoFavorito(produtoId, favoritado, classe, comTexto, autenticado) {
    const controle = document.createElement(autenticado ? "button" : "a");
    controle.className = `favorite-toggle ${classe}`;
    if (classe === "favorite-detail-toggle") {
      controle.classList.add("btn", "btn-outline-secondary");
    }
    controle.dataset.favoriteId = String(produtoId);
    if (autenticado) controle.type = "button";
    else controle.href = "/login";
    controle.append(criarIconeCoracao());

    if (comTexto) {
      const texto = document.createElement("span");
      texto.dataset.favoriteLabel = "true";
      controle.append(texto);
    }

    if (!autenticado) {
      controle.setAttribute("aria-label", "Entre na sua Conta para Favoritar");
      controle.title = "Entre na sua Conta para Favoritar";
      if (comTexto) controle.querySelector("span").textContent = "Favoritar";
    } else {
      atualizarControleFavorito(controle, favoritado);
    }
    return controle;
  }

  function produtosDaPagina() {
    const encontrados = [];
    document.querySelectorAll(".product-card").forEach((card) => {
      const link = card.querySelector('a[href*="/produtos/"]');
      const id = idProdutoDoHref(link?.href);
      if (id) encontrados.push({ id, card, tipo: "card" });
    });

    const detalhe = document.querySelector(".product-detail-content");
    const idDetalhe = Number(document.body.dataset.analyticsItemId || 0);
    if (detalhe && idDetalhe) {
      encontrados.push({ id: idDetalhe, card: detalhe, tipo: "detalhe" });
    }

    const kit = document.querySelector(".kit-panel .kit-copy");
    const linkKit = kit?.querySelector('a[href*="/produtos/"]');
    const idKit = idProdutoDoHref(linkKit?.href);
    if (kit && idKit) encontrados.push({ id: idKit, card: kit, tipo: "kit" });
    return encontrados;
  }

  async function configurarFavoritos() {
    const produtos = produtosDaPagina();
    if (!produtos.length) return;

    let estado;
    try {
      const resposta = await fetch("/favoritos/status", {
        headers: { Accept: "application/json" },
        credentials: "same-origin",
      });
      if (!resposta.ok) return;
      estado = await resposta.json();
    } catch {
      return;
    }

    const idsFavoritos = new Set((estado.favoritos || []).map(Number));
    produtos.forEach(({ id, card, tipo }) => {
      if (card.querySelector(`[data-favorite-id="${id}"]`)) return;
      const favoritado = idsFavoritos.has(id);
      if (tipo === "card") {
        card.prepend(
          botaoFavorito(
            id,
            favoritado,
            "favorite-card-toggle",
            false,
            estado.autenticado,
          ),
        );
      } else if (tipo === "detalhe") {
        const controle = botaoFavorito(
          id,
          favoritado,
          "favorite-detail-toggle",
          true,
          estado.autenticado,
        );
        const formularioCompra = card.querySelector(".purchase-form");
        const botaoCarrinho = formularioCompra?.querySelector(".purchase-cta");
        if (formularioCompra && botaoCarrinho) {
          botaoCarrinho.after(controle);
        } else {
          const disponibilidade = card.querySelector(".availability");
          if (disponibilidade) disponibilidade.after(controle);
          else card.prepend(controle);
        }
      } else if (tipo === "kit") {
        const controle = botaoFavorito(
          id,
          favoritado,
          "favorite-kit-toggle",
          true,
          estado.autenticado,
        );
        const destino = card.querySelector("div:last-child") || card;
        destino.append(controle);
      }
    });

    if (!estado.autenticado) return;
    const csrf = document.querySelector('input[name="csrf_token"]')?.value;
    if (!csrf) return;

    document.querySelectorAll("button[data-favorite-id]").forEach((controle) => {
      controle.addEventListener("click", async () => {
        if (controle.disabled) return;
        const produtoId = Number(controle.dataset.favoriteId);
        controle.disabled = true;
        try {
          const corpo = new URLSearchParams({ csrf_token: csrf });
          const resposta = await fetch(`/favoritos/${produtoId}/alternar`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
              Accept: "application/json",
              "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
              "X-Requested-With": "fetch",
            },
            body: corpo,
          });
          const dados = await resposta.json();
          if (!resposta.ok) {
            throw new Error(dados.erro || "Não foi Possível Atualizar.");
          }

          document
            .querySelectorAll(`[data-favorite-id="${produtoId}"]`)
            .forEach((item) => {
              atualizarControleFavorito(item, dados.favoritado);
            });
          feedbackFavorito(dados.mensagem);

          if (
            !dados.favoritado &&
            document.querySelector("[data-favorites-page]")
          ) {
            controle.closest(".product-card-wrap")?.remove();
            const grade = document.querySelector("[data-favorites-grid]");
            if (grade && !grade.querySelector(".product-card")) {
              grade.hidden = true;
              const vazio = document.querySelector("[data-favorites-empty]");
              if (vazio) vazio.hidden = false;
            }
          }
        } catch (erro) {
          feedbackFavorito(
            erro.message || "Não foi Possível Atualizar seus Favoritos.",
          );
        } finally {
          controle.disabled = false;
        }
      });
    });
  }

  function iniciar() {
    configurarNavegacaoConta();
    configurarEnderecos();
    configurarFavoritos();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar, { once: true });
  } else {
    iniciar();
  }
})();