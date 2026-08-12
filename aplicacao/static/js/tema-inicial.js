(() => {
  const urlScriptAtual = document.currentScript?.src || "";
  let salvo = null;
  try {
    salvo = localStorage.getItem("doce_pedido_tema");
  } catch {
    salvo = null;
  }
  const tema = salvo === "dark" || salvo === "light" ? salvo : "light";
  document.documentElement.dataset.theme = tema;

  const redesRodape = [
    {
      nome: "Facebook",
      url: "https://www.facebook.com/",
      svg: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path fill-rule="evenodd" clip-rule="evenodd" d="M20 1C21.6569 1 23 2.34315 23 4V20C23 21.6569 21.6569 23 20 23H4C2.34315 23 1 21.6569 1 20V4C1 2.34315 2.34315 1 4 1H20ZM20 3C20.5523 3 21 3.44772 21 4V20C21 20.5523 20.5523 21 20 21H15V14H17.1L18 11H15V9C15 8.4 15.4 8 16 8H18V5.4C17.4 5.3 16.7 5.2 16 5.2C13.5 5.2 12 6.8 12 9V11H10V14H12V21H4C3.44772 21 3 20.5523 3 20V4C3 3.44772 3.44772 3 4 3H20Z" fill="currentColor"/></svg>`,
    },
    {
      nome: "Instagram",
      url: "https://www.instagram.com/",
      svg: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>`,
    },
    {
      nome: "TikTok",
      url: "https://www.tiktok.com/",
      svg: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M14 4v10.2a4.2 4.2 0 1 1-3.5-4.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 4c.7 2.2 2.1 3.5 4.5 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>`,
    },
    {
      nome: "WhatsApp",
      url: "https://www.whatsapp.com/",
      svg: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M20.5 11.7a8.5 8.5 0 0 1-12.6 7.4L3 20.5l1.3-4.7A8.5 8.5 0 1 1 20.5 11.7Zm-8-6.2a6.2 6.2 0 0 0-5.3 9.4l.3.5-.7 2.1 2.2-.6.5.3a6.2 6.2 0 1 0 3-11.7Zm-3 3.1c.2 0 .3 0 .4.3l.6 1.4c.1.2.1.3 0 .5l-.5.7c-.1.1-.2.3 0 .5.5 1 1.3 1.8 2.3 2.3.2.1.4.1.5-.1l.7-.9c.1-.2.3-.2.5-.1l1.5.7c.2.1.3.2.3.4 0 .5-.2 1.4-.7 1.8-.5.4-1.1.6-1.8.4-1.1-.3-2.5-.8-4-2.1-1.2-1.1-2.1-2.4-2.3-3.5-.2-.8.1-1.7.6-2.2.3-.3.6-.4.9-.4Z" fill="currentColor"/></svg>`,
    },
    {
      nome: "iFood",
      url: "https://www.ifood.com.br/",
      svg: `<svg width="30" height="18" viewBox="0 0 60 24" fill="none" aria-hidden="true"><text x="30" y="17" text-anchor="middle" fill="currentColor" font-family="Arial, sans-serif" font-size="18" font-weight="800" letter-spacing="-1">iFood</text></svg>`,
    },
  ];

  const palavrasDeLigacao = new Set([
    "a",
    "as",
    "o",
    "os",
    "e",
    "de",
    "da",
    "das",
    "do",
    "dos",
    "em",
    "no",
    "na",
    "nos",
    "nas",
    "por",
    "para",
    "ao",
    "aos",
    "com",
    "um",
    "uma",
  ]);

  function capitalizarTrechoDeMensagem(texto) {
    let primeiraPalavra = true;
    return texto.replace(/\p{L}+(?:-\p{L}+)?/gu, (palavra) => {
      const minuscula = palavra.toLocaleLowerCase("pt-BR");
      if (
        palavra.length > 1 &&
        palavra === palavra.toLocaleUpperCase("pt-BR")
      ) {
        primeiraPalavra = false;
        return palavra;
      }
      if (!primeiraPalavra && palavrasDeLigacao.has(minuscula)) {
        return minuscula;
      }
      primeiraPalavra = false;
      return `${minuscula.charAt(0).toLocaleUpperCase("pt-BR")}${minuscula.slice(1)}`;
    });
  }

  function formatarMensagemNaoFoiPossivel(texto) {
    return texto.replace(
      /Não foi [Pp]ossível([^.!?]*)([.!?]?)/g,
      (_frase, restante, pontuacao) => {
        const conteudo = restante.trim();
        const complemento = conteudo
          ? ` ${capitalizarTrechoDeMensagem(conteudo)}`
          : "";
        return `Não foi Possível${complemento}${pontuacao}`;
      },
    );
  }

  function padronizarMensagensNaoFoiPossivel(raiz) {
    if (!raiz) return;
    const atualizarTexto = (no) => {
      const atual = no.nodeValue || "";
      if (!/Não foi [Pp]ossível/.test(atual)) return;
      const formatado = formatarMensagemNaoFoiPossivel(atual);
      if (formatado !== atual) no.nodeValue = formatado;
    };

    if (raiz.nodeType === Node.TEXT_NODE) {
      atualizarTexto(raiz);
      return;
    }
    if (raiz.nodeType !== Node.ELEMENT_NODE) return;

    const walker = document.createTreeWalker(raiz, NodeFilter.SHOW_TEXT);
    let no = walker.nextNode();
    while (no) {
      atualizarTexto(no);
      no = walker.nextNode();
    }
  }

  function configurarPadronizacaoDeMensagens() {
    padronizarMensagensNaoFoiPossivel(document.body);
    const observador = new MutationObserver((mutacoes) => {
      mutacoes.forEach((mutacao) => {
        if (mutacao.type === "characterData") {
          padronizarMensagensNaoFoiPossivel(mutacao.target);
          return;
        }
        mutacao.addedNodes.forEach((no) =>
          padronizarMensagensNaoFoiPossivel(no),
        );
      });
    });
    observador.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
    });
  }

  function carregarAjustesInterface() {
    if (document.querySelector('link[data-interface-adjustments]')) return;
    const href = urlScriptAtual
      ? new URL("../css/ajustes-interface.css", urlScriptAtual).href
      : "/static/css/ajustes-interface.css";
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    link.dataset.interfaceAdjustments = "true";
    document.head.append(link);
  }

  function carregarEstilosConta() {
    if (document.querySelector('link[data-conta-styles]')) return;
    const href = urlScriptAtual
      ? new URL("../css/conta.css", urlScriptAtual).href
      : "/static/css/conta.css";
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = href;
    link.dataset.contaStyles = "true";
    document.head.append(link);
  }

  function carregarRecursosConta() {
    if (!document.querySelector('link[data-conta-recursos-styles]')) {
      const href = urlScriptAtual
        ? new URL("../css/conta-recursos.css", urlScriptAtual).href
        : "/static/css/conta-recursos.css";
      const link = document.createElement("link");
      link.rel = "stylesheet";
      link.href = href;
      link.dataset.contaRecursosStyles = "true";
      document.head.append(link);
    }
    if (!document.querySelector("script[data-conta-recursos-script]")) {
      const src = urlScriptAtual
        ? new URL("conta-recursos.js", urlScriptAtual).href
        : "/static/js/conta-recursos.js";
      const script = document.createElement("script");
      script.src = src;
      script.dataset.contaRecursosScript = "true";
      document.body.append(script);
    }
  }

  function carregarInteracoesEmailConta() {
    if (
      !document.querySelector("[data-account-area]") ||
      document.querySelector("script[data-account-email-script]")
    )
      return;
    const src = urlScriptAtual
      ? new URL("autenticacao-email.js", urlScriptAtual).href
      : "/static/js/autenticacao-email.js";
    const script = document.createElement("script");
    script.src = src;
    script.dataset.accountEmailScript = "true";
    document.body.append(script);
  }

  function configurarAcessoDiretoConta() {
    const componente = document.querySelector(
      ".account-dropdown[data-header-dropdown]",
    );
    if (!componente) return;

    const acesso = componente.cloneNode(true);
    const tituloAtual = acesso.querySelector("[data-dropdown-trigger]");
    const menu = acesso.querySelector("[data-dropdown-menu]");
    if (!tituloAtual || !menu) return;

    const saudacaoAtual = menu.querySelector(".account-name")?.textContent.trim() || "";
    const nomeCompleto = saudacaoAtual.replace(/^Olá,\s*/i, "").trim();
    const primeiroNome = nomeCompleto.split(/\s+/)[0] || "";
    const autenticado = Boolean(primeiroNome);
    const linkEntrar = [...menu.querySelectorAll("a")].find(
      (link) =>
        link.textContent.trim() === "Entrar" ||
        link.getAttribute("href")?.includes("/login"),
    );
    const destinoConta = linkEntrar?.getAttribute("href") || "/login";

    acesso.className = "nav-item account-access";
    acesso.removeAttribute("data-header-dropdown");

    const titulo = document.createElement(autenticado ? "span" : "a");
    titulo.className = "account-access-title";
    if (!autenticado) titulo.href = destinoConta;
    titulo.textContent = autenticado ? `Olá, ${primeiroNome}` : "Minha Conta";
    tituloAtual.replaceWith(titulo);

    menu.className = "account-access-actions";
    menu.removeAttribute("id");
    menu.removeAttribute("data-dropdown-menu");
    menu.querySelector(".account-name")?.remove();

    if (autenticado) {
      const linkPedidos = [...menu.querySelectorAll(":scope > a")].find(
        (link) =>
          link.textContent.trim().toLowerCase() === "meus pedidos" ||
          link.getAttribute("href")?.includes("/pedidos"),
      );
      if (linkPedidos) {
        const linkConta = linkPedidos.cloneNode(true);
        linkConta.href = "/minha-conta";
        linkConta.textContent = "Conta";
        linkConta.setAttribute("aria-label", "Minha Conta");
        linkPedidos.textContent = "Pedidos";
        linkPedidos.setAttribute("aria-label", "Meus Pedidos");
        linkPedidos.before(linkConta);
      }
    }

    const acoes = [...menu.querySelectorAll(":scope > a, :scope > form")];
    acoes.forEach((acao, indice) => {
      if (acao.matches("a")) {
        acao.className = "account-access-action";
        if (
          acao.getAttribute("href")?.includes("/cadastro") ||
          acao.textContent.trim().toLowerCase() === "criar conta"
        ) {
          acao.textContent = "Cadastrar";
          acao.setAttribute("aria-label", "Cadastrar");
        }
      } else {
        acao.className = "account-access-form";
        const botao = acao.querySelector("button");
        if (botao) botao.className = "account-access-button";
      }

      if (indice < acoes.length - 1) {
        const separador = document.createElement("span");
        separador.className = "account-access-separator";
        separador.setAttribute("aria-hidden", "true");
        separador.textContent = "|";
        acao.after(separador);
      }
    });

    componente.replaceWith(acesso);
  }

  function padronizarRotulosDeControles() {
    const textos = (
      [
        ["[data-cookie-manage]", "Gerenciar Preferências"],
        ["#cookie-dialog-title", "Preferências de Cookies"],
        [".essential-status", "Sempre Ativos"],
        ["[data-cookie-reject]", "Recusar Não Essenciais"],
        ["[data-cookie-accept-all]", "Aceitar Todos"],
        ["[data-cookie-save]", "Salvar Preferências"],
      ]
    );
    textos.forEach(([seletor, texto]) => {
      const elemento = document.querySelector(seletor);
      if (elemento) elemento.textContent = texto;
    });
  }

  function configurarCupomCarrinho() {
    const formulario = document.querySelector("[data-coupon-form]");
    const campo = formulario?.querySelector("#cupom");
    const feedback = formulario?.querySelector("[data-coupon-feedback]");
    document
      .querySelector(".coupon-summary-title")
      ?.classList.add("h6", "mb-2");
    if (!formulario || !campo || !feedback) return;

    formulario.addEventListener("submit", (evento) => {
      const codigo = campo.value.trim().toUpperCase();
      if (codigo === "BEMVINDO") {
        feedback.textContent = "";
        return;
      }

      evento.preventDefault();
      feedback.textContent = codigo ? "Cupom não Encontrado." : "Digite um Cupom.";
    });
  }

  function criarLinkExterno(nome, url, svg, classe = "") {
    const link = document.createElement("a");
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.setAttribute("aria-label", nome);
    link.title = nome;
    if (classe) link.className = classe;
    link.innerHTML = svg;
    return link;
  }

  async function configurarRodape() {
    const rodape = document.querySelector(".site-footer");
    const grade = rodape?.querySelector(".footer-grid");
    const marca = rodape?.querySelector(".footer-brand")?.parentElement;
    if (!rodape || !grade || !marca) return;

    let tituloRedes = marca.querySelector(".social-title");
    if (!tituloRedes) {
      tituloRedes = document.createElement("h3");
      tituloRedes.className = "social-title";
      tituloRedes.textContent = "Siga a Doce Pedido";
      marca.append(tituloRedes);
    }

    let links = marca.querySelector(".social-links");
    if (!links) {
      links = document.createElement("div");
      links.className = "social-links";
      marca.append(links);
    }
    links.replaceChildren(
      ...redesRodape.map((rede) =>
        criarLinkExterno(rede.nome, rede.url, rede.svg),
      ),
    );

    let dados;
    try {
      const resposta = await fetch("/api/site-footer", {
        headers: { Accept: "application/json" },
        credentials: "same-origin",
      });
      if (!resposta.ok) return;
      dados = await resposta.json();
    } catch {
      return;
    }
    if (!dados.endereco) return;

    let atendimento = [...grade.children].find(
      (coluna) => coluna.querySelector(":scope > h2")?.textContent.trim() === "Atendimento",
    );
    if (!atendimento) {
      atendimento = document.createElement("div");
      const titulo = document.createElement("h2");
      titulo.textContent = "Atendimento";
      atendimento.append(titulo);
      const institucional = [...grade.children].find(
        (coluna) => coluna.querySelector(":scope > h2")?.textContent.trim() === "Institucional e Ajuda",
      );
      grade.insertBefore(atendimento, institucional || null);
    }

    let endereco = atendimento.querySelector("[data-site-address]");
    if (!endereco) {
      endereco = document.createElement("p");
      endereco.dataset.siteAddress = "true";
      atendimento.append(endereco);
    }
    endereco.replaceChildren();
    if (dados.maps) {
      const link = document.createElement("a");
      link.href = dados.maps;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = dados.endereco;
      link.setAttribute("aria-label", `Abrir endereço no mapa: ${dados.endereco}`);
      endereco.append(link);
    } else {
      endereco.textContent = dados.endereco;
    }
  }

  function organizarAcoesProduto() {
    const conteudo = document.querySelector(".product-detail-content");
    if (!conteudo) return;

    const ajustar = () => {
      const favorito = conteudo.querySelector(".favorite-detail-toggle");
      if (!favorito) return false;
      favorito.classList.remove("favorite-detail-icon-only");
      const formulario = conteudo.querySelector(".purchase-form");
      const carrinho = formulario?.querySelector(".purchase-cta");
      if (formulario && carrinho && favorito.previousElementSibling !== carrinho) {
        carrinho.after(favorito);
      }
      return true;
    };

    if (ajustar()) return;
    const observador = new MutationObserver(() => {
      if (ajustar()) observador.disconnect();
    });
    observador.observe(conteudo, { childList: true, subtree: true });
  }

  function garantirAtalhosFlutuantes() {
    if (document.body.classList.contains("offline-body")) return;

    let grupo = document.querySelector(".contact-fab-group");
    if (!grupo) {
      grupo = document.createElement("div");
      grupo.className = "contact-fab-group";
      grupo.setAttribute("aria-label", "Canais Externos");
      document.body.append(grupo);
    }

    grupo.querySelector(".whatsapp-fab")?.remove();
    grupo.querySelector(".ifood-fab")?.remove();

    const whatsapp = redesRodape.find((rede) => rede.nome === "WhatsApp");
    const ifood = redesRodape.find((rede) => rede.nome === "iFood");
    if (whatsapp) {
      grupo.append(
        criarLinkExterno(
          whatsapp.nome,
          whatsapp.url,
          whatsapp.svg,
          "contact-fab whatsapp-fab",
        ),
      );
    }
    if (ifood) {
      grupo.append(
        criarLinkExterno(
          ifood.nome,
          ifood.url,
          ifood.svg,
          "contact-fab ifood-fab",
        ),
      );
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    carregarAjustesInterface();
    carregarEstilosConta();
    carregarRecursosConta();
    configurarAcessoDiretoConta();
    carregarInteracoesEmailConta();
    padronizarRotulosDeControles();
    configurarCupomCarrinho();
    configurarPadronizacaoDeMensagens();
    configurarRodape();
    organizarAcoesProduto();
    garantirAtalhosFlutuantes();
  });
})();
