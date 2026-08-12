// -----------------------------------------------------------------------------
// Rolagem da página e retorno ao topo
// -----------------------------------------------------------------------------

const cabecalho = document.querySelector("[data-site-header]");
const botaoVoltarAoTopo = document.querySelector("[data-back-to-top]");
const prefereMovimentoReduzido = window.matchMedia(
  "(prefers-reduced-motion: reduce)",
).matches;

function atualizarElementosDaRolagem() {
  const paginaRolada = window.scrollY > 80;
  cabecalho?.classList.toggle("is-scrolled", paginaRolada);
  botaoVoltarAoTopo?.classList.toggle("is-visible", paginaRolada);
}

window.addEventListener("scroll", atualizarElementosDaRolagem, {
  passive: true,
});
atualizarElementosDaRolagem();

botaoVoltarAoTopo?.addEventListener("click", () => {
  window.scrollTo({
    top: 0,
    behavior: prefereMovimentoReduzido ? "auto" : "smooth",
  });
});

// -----------------------------------------------------------------------------
// Persistência e alternância do tema
// -----------------------------------------------------------------------------

function configurarTema() {
  const botao = document.querySelector("[data-theme-toggle]");
  function atualizarBotao() {
    const escuro = document.documentElement.dataset.theme === "dark";
    const descricao = escuro ? "Modo Claro" : "Modo Escuro";
    botao?.setAttribute("aria-label", descricao);
    botao?.setAttribute("title", descricao);
  }

  botao?.addEventListener("click", () => {
    const novoTema =
      document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = novoTema;
    try {
      localStorage.setItem("doce_pedido_tema", novoTema);
    } catch {
      // A indisponibilidade do armazenamento não deve impedir a troca na página atual.
    }
    atualizarBotao();
  });
  atualizarBotao();
}

// -----------------------------------------------------------------------------
// Consentimento de cookies e carregamento condicional do Analytics
// -----------------------------------------------------------------------------

const NOME_COOKIE = "doce_pedido_consentimento";
let analyticsCarregado = false;
let eventoPaginaEnviado = false;
let consentimentoInicializado = false;

function lerConsentimento() {
  const registro = document.cookie
    .split("; ")
    .find((item) => item.startsWith(`${NOME_COOKIE}=`));
  if (!registro) {
    return null;
  }
  try {
    const valor = JSON.parse(
      decodeURIComponent(registro.split("=").slice(1).join("=")),
    );
    return valor?.version === 1 && typeof valor.analytics === "boolean"
      ? valor
      : null;
  } catch {
    return null;
  }
}

function salvarConsentimento(analytics) {
  const valor = encodeURIComponent(JSON.stringify({ version: 1, analytics }));
  const seguro = location.protocol === "https:" ? "; Secure" : "";
  document.cookie = `${NOME_COOKIE}=${valor}; Max-Age=15552000; Path=/; SameSite=Lax${seguro}`;
}

function configurarConsentMode(analytics) {
  window.dataLayer = window.dataLayer || [];
  window.gtag =
    window.gtag ||
    function gtag() {
      window.dataLayer.push(arguments);
    };
  window.gtag("consent", consentimentoInicializado ? "update" : "default", {
    analytics_storage: analytics ? "granted" : "denied",
  });
  consentimentoInicializado = true;
}

function enviarEventoDaPagina() {
  if (
    !analyticsCarregado ||
    eventoPaginaEnviado ||
    !document.body.dataset.analyticsEvent
  )
    return;
  const parametros = {};
  const dados = document.body.dataset;
  if (dados.analyticsItemId) parametros.item_id = dados.analyticsItemId;
  if (dados.analyticsItemName) parametros.item_name = dados.analyticsItemName;
  if (dados.analyticsItemCount)
    parametros.item_count = Number(dados.analyticsItemCount);
  if (dados.analyticsResultCount)
    parametros.result_count = Number(dados.analyticsResultCount);
  if (dados.analyticsValue) parametros.value = Number(dados.analyticsValue);
  window.gtag("event", dados.analyticsEvent, parametros);
  eventoPaginaEnviado = true;
}

function carregarAnalytics() {
  const measurementId = document.body.dataset.gaMeasurementId;
  if (!measurementId || analyticsCarregado) {
    return;
  }

  configurarConsentMode(true);
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`;
  script.addEventListener("load", () => {
    window.gtag("js", new Date());
    window.gtag("config", measurementId, {
      anonymize_ip: true,
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
    });
    analyticsCarregado = true;
    enviarEventoDaPagina();
  });
  document.head.appendChild(script);
}

function removerCookiesAnalytics() {
  document.cookie.split("; ").forEach((item) => {
    const nome = item.split("=")[0];
    if (nome === "_ga" || nome.startsWith("_ga_")) {
      document.cookie = `${nome}=; Max-Age=0; Path=/; SameSite=Lax`;
    }
  });
}

function configurarCookies() {
  const banner = document.querySelector("[data-cookie-banner]");
  const dialogo = document.querySelector("[data-cookie-dialog]");
  const analise = document.querySelector("[data-cookie-analytics]");
  if (!banner || !dialogo || !analise) {
    return;
  }
  const consentimento = lerConsentimento();
  let ultimoAcionador = null;

  function aplicar(escolha) {
    salvarConsentimento(escolha);
    configurarConsentMode(escolha);
    banner.hidden = true;
    document.body.classList.remove("cookie-banner-visible");
    if (dialogo.open && typeof dialogo.close === "function") {
      dialogo.close();
    }
    if (escolha) {
      carregarAnalytics();
    } else {
      removerCookiesAnalytics();
    }
  }

  document
    .querySelector("[data-cookie-accept]")
    ?.addEventListener("click", () => aplicar(true));
  document
    .querySelector("[data-cookie-accept-all]")
    ?.addEventListener("click", () => aplicar(true));
  document
    .querySelector("[data-cookie-reject]")
    ?.addEventListener("click", () => aplicar(false));
  document
    .querySelector("[data-cookie-save]")
    ?.addEventListener("click", () => aplicar(analise.checked));
  document
    .querySelectorAll("[data-cookie-manage], [data-cookie-settings]")
    .forEach((botao) => {
      botao.addEventListener("click", () => {
        ultimoAcionador = botao;
        analise.checked = Boolean(lerConsentimento()?.analytics);
        if (typeof dialogo.showModal === "function") dialogo.showModal();
      });
    });
  dialogo.addEventListener("close", () => {
    // Após uma decisão, o acionador do banner fica oculto; nesse caso o foco
    // segue para a marca em vez de permanecer preso em um elemento invisível.
    const destino = ultimoAcionador?.offsetParent
      ? ultimoAcionador
      : document.querySelector(".navbar-brand");
    destino?.focus();
    ultimoAcionador = null;
  });

  configurarConsentMode(Boolean(consentimento?.analytics));
  if (consentimento === null) {
    banner.hidden = false;
    document.body.classList.add("cookie-banner-visible");
  } else if (consentimento.analytics) {
    carregarAnalytics();
  }
}

// -----------------------------------------------------------------------------
// Animações progressivas e carrossel de produtos
// -----------------------------------------------------------------------------

function configurarAnimacoes() {
  const secoes = document.querySelectorAll(
    "[data-reveal], .favorites, .kit-section, .about-section, .benefits",
  );
  if (prefereMovimentoReduzido || !("IntersectionObserver" in window)) return;
  secoes.forEach((secao) => secao.classList.add("reveal-ready"));
  const observador = new IntersectionObserver(
    (entradas) => {
      entradas.forEach((entrada) => {
        if (entrada.isIntersecting) {
          entrada.target.classList.add("is-visible");
          observador.unobserve(entrada.target);
        }
      });
    },
    { threshold: 0.12 },
  );
  secoes.forEach((secao) => observador.observe(secao));
}

function configurarCarrossel() {
  const carrossel = document.querySelector("[data-product-carousel]");
  const viewport = carrossel?.closest("[data-product-carousel-viewport]");
  const anterior = document.querySelector("[data-carousel-previous]");
  const proximo = document.querySelector("[data-carousel-next]");
  if (!carrossel || !viewport || !anterior || !proximo) return;

  const atualizarControles = () => {
    const limite = Math.max(0, carrossel.scrollWidth - carrossel.clientWidth);
    const tolerancia = 4;
    anterior.disabled = carrossel.scrollLeft <= tolerancia;
    proximo.disabled = carrossel.scrollLeft >= limite - tolerancia;
    anterior.hidden = limite <= tolerancia;
    proximo.hidden = limite <= tolerancia;
  };
  const alinharControlesComImagem = () => {
    const imagem = carrossel.querySelector(
      ".product-image, .image-placeholder",
    );
    if (!imagem) return;
    const caixaImagem = imagem.getBoundingClientRect();
    const caixaViewport = viewport.getBoundingClientRect();
    const topo =
      caixaImagem.top -
      caixaViewport.top +
      (caixaImagem.height - anterior.offsetHeight) / 2;
    anterior.style.top = `${topo}px`;
    proximo.style.top = `${topo}px`;
  };
  const atualizarGeometria = () => {
    atualizarControles();
    alinharControlesComImagem();
  };
  const mover = (direcao) => {
    const card = carrossel.querySelector(".product-card-wrap");
    const estilo = window.getComputedStyle(carrossel);
    const distancia = card
      ? card.getBoundingClientRect().width +
        Number.parseFloat(estilo.columnGap || estilo.gap || "0")
      : carrossel.clientWidth;
    carrossel.scrollBy({
      left: direcao * distancia,
      behavior: prefereMovimentoReduzido ? "auto" : "smooth",
    });
  };

  anterior.addEventListener("click", () => mover(-1));
  proximo.addEventListener("click", () => mover(1));
  carrossel.addEventListener(
    "scroll",
    () => window.requestAnimationFrame(atualizarControles),
    { passive: true },
  );
  window.addEventListener("resize", atualizarGeometria);
  if ("ResizeObserver" in window) {
    const observadorGeometria = new ResizeObserver(alinharControlesComImagem);
    observadorGeometria.observe(carrossel);
  }
  atualizarGeometria();
}

function configurarAlertas() {
  const Alert = window.bootstrap?.Alert;
  if (!Alert) return;
  document.querySelectorAll(".alert").forEach((alerta) => {
    window.setTimeout(() => Alert.getOrCreateInstance(alerta)?.close(), 10000);
  });
}

function exibirPopup(mensagem) {
  const Toast = window.bootstrap?.Toast;
  if (!Toast) return;
  let container = document.querySelector(".interface-toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "interface-toast-container";
    container.setAttribute("aria-live", "polite");
    container.setAttribute("aria-atomic", "true");
    document.body.append(container);
  }
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.setAttribute("role", "status");
  toast.innerHTML = `
    <div class="toast-body d-flex align-items-center justify-content-between gap-3">
      <span></span>
      <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Fechar"></button>
    </div>`;
  toast.querySelector("span").textContent = mensagem;
  container.append(toast);
  toast.addEventListener("hidden.bs.toast", () => toast.remove());
  Toast.getOrCreateInstance(toast, { delay: 4000 }).show();
}

// -----------------------------------------------------------------------------
// Adição assíncrona ao carrinho
// -----------------------------------------------------------------------------
function configurarAdicaoAoCarrinho() {
  document.querySelectorAll("[data-add-to-cart]").forEach((formulario) => {
    formulario.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      const botao = formulario.querySelector("button[type=submit]");
      if (!botao || botao.disabled) return;

      const conteudoOriginal = botao.innerHTML;
      const exibeTexto = Boolean(botao.textContent.trim());
      botao.disabled = true;
      if (exibeTexto) botao.textContent = "Adicionando...";
      try {
        const resposta = await fetch(formulario.action, {
          method: "POST",
          body: new FormData(formulario),
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const dados = await resposta.json();
        if (!resposta.ok || !dados.ok) {
          throw new Error(dados.mensagem || "Não foi Possível Carrinho.");
        }
        document.querySelectorAll("[data-cart-count]").forEach((elemento) => {
          elemento.textContent = dados.quantidade_carrinho;
        });
        exibirPopup(dados.mensagem);
      } catch (erro) {
        exibirPopup(erro.message);
      } finally {
        if (exibeTexto) botao.innerHTML = conteudoOriginal;
        botao.disabled = false;
      }
    });
  });
}

// -----------------------------------------------------------------------------
// Dropdowns acessíveis do cabeçalho
// -----------------------------------------------------------------------------
function configurarDropdownsDoCabecalho() {
  const componentes = [...document.querySelectorAll("[data-header-dropdown]")];
  const atrasosDeFechamento = new WeakMap();
  const cancelarFechamento = (componente) => {
    window.clearTimeout(atrasosDeFechamento.get(componente));
    atrasosDeFechamento.delete(componente);
  };
  const fechar = (componente, devolverFoco = false) => {
    cancelarFechamento(componente);
    const gatilho = componente.querySelector("[data-dropdown-trigger]");
    componente.classList.remove("is-open");
    gatilho?.setAttribute("aria-expanded", "false");
    if (devolverFoco) gatilho?.focus();
  };
  const abrir = (componente) => {
    cancelarFechamento(componente);
    componentes.forEach((outro) => {
      if (outro !== componente) fechar(outro);
    });
    componente.classList.add("is-open");
    componente
      .querySelector("[data-dropdown-trigger]")
      ?.setAttribute("aria-expanded", "true");
  };

  componentes.forEach((componente) => {
    const gatilho = componente.querySelector("[data-dropdown-trigger]");
    gatilho?.addEventListener("click", () => {
      if (!componente.classList.contains("is-open")) abrir(componente);
      else fechar(componente);
    });
    componente.addEventListener("pointerenter", () => {
      if (window.matchMedia("(min-width: 1200px)").matches) abrir(componente);
    });
    componente.addEventListener("pointerleave", () => {
      if (!window.matchMedia("(min-width: 1200px)").matches) return;
      // Uma tolerância curta evita fechamentos acidentais sem atrasar a abertura.
      cancelarFechamento(componente);
      atrasosDeFechamento.set(
        componente,
        window.setTimeout(() => fechar(componente), 120),
      );
    });
    componente.addEventListener("focusin", () => {
      // No mobile o clique controla o accordion; abrir antes no focusin faria
      // o mesmo clique alterná-lo imediatamente para fechado.
      if (window.matchMedia("(min-width: 1200px)").matches) abrir(componente);
    });
    componente.addEventListener("focusout", (evento) => {
      if (!componente.contains(evento.relatedTarget)) fechar(componente);
    });
  });

  document.addEventListener("click", (evento) =>
    componentes.forEach((componente) => {
      if (!componente.contains(evento.target)) fechar(componente);
    }),
  );
  document.addEventListener("keydown", (evento) => {
    if (evento.key !== "Escape") return;
    const aberto = componentes.find((componente) =>
      componente.classList.contains("is-open"),
    );
    if (aberto) fechar(aberto, true);
  });
}

// -----------------------------------------------------------------------------
// Busca expansível no cabeçalho
// -----------------------------------------------------------------------------
function configurarBuscaDoCabecalho() {
  const formulario = document.querySelector("[data-header-search]");
  const gatilho = formulario?.querySelector("[data-search-toggle]");
  const campo = formulario?.querySelector("input[type='search']");
  if (!formulario || !gatilho || !campo) return;

  const expandir = () => {
    formulario.classList.add("is-expanded");
    gatilho.setAttribute("aria-expanded", "true");
    window.requestAnimationFrame(() => campo.focus());
  };
  const recolher = () => {
    formulario.classList.remove("is-expanded");
    gatilho.setAttribute("aria-expanded", "false");
    campo.blur();
  };
  gatilho.addEventListener("click", () =>
    formulario.classList.contains("is-expanded") ? recolher() : expandir(),
  );
  formulario.addEventListener("keydown", (evento) => {
    if (evento.key === "Escape") {
      evento.preventDefault();
      recolher();
      gatilho.focus();
    }
  });
  document.addEventListener("click", (evento) => {
    if (!formulario.contains(evento.target)) recolher();
  });
}

function configurarMenuMobile() {
  const menu = document.querySelector("#menu");
  const Collapse = window.bootstrap?.Collapse;
  if (!menu || !Collapse) return;
  menu.querySelectorAll("a").forEach((link) =>
    link.addEventListener("click", () => {
      if (
        window.matchMedia("(max-width: 1199.98px)").matches &&
        menu.classList.contains("show")
      ) {
        Collapse.getOrCreateInstance(menu)?.hide();
      }
    }),
  );
}

function configurarQuantidades() {
  document.querySelectorAll("[data-quantity-control]").forEach((controle) => {
    const input = controle.querySelector("input[type=number]");
    const diminuir = controle.querySelector("[data-quantity-decrease]");
    const aumentar = controle.querySelector("[data-quantity-increase]");
    if (!input || !diminuir || !aumentar) return;
    const atualizarLimites = () => {
      const valor = Number(input.value);
      const minimo = Number(input.min);
      const maximo = Number(input.max);
      diminuir.disabled = Number.isFinite(valor) && valor <= minimo;
      aumentar.disabled = Number.isFinite(valor) && valor >= maximo;
    };
    diminuir.addEventListener("click", () => {
      input.stepDown();
      atualizarLimites();
    });
    aumentar.addEventListener("click", () => {
      input.stepUp();
      atualizarLimites();
    });
    input.addEventListener("input", atualizarLimites);
    atualizarLimites();
  });
}

// -----------------------------------------------------------------------------
// Atualização assíncrona do carrinho
// -----------------------------------------------------------------------------
function configurarCarrinho() {
  document.querySelectorAll("[data-cart-item]").forEach((item) => {
    const formulario = item.querySelector(".cart-quantity");
    const input = formulario?.querySelector("input[name=quantidade]");
    const subtotal = item.querySelector("[data-cart-subtotal]");
    const feedback = item.querySelector(".cart-feedback");
    if (!formulario || !input || !subtotal || !feedback) return;

    let valorConfirmado = input.value;
    let temporizador;
    let requisicaoAtual = 0;

    const atualizar = async () => {
      const numeroRequisicao = ++requisicaoAtual;
      window.clearTimeout(temporizador);
      item.classList.add("is-updating");
      feedback.textContent = "Atualizando quantidade…";
      try {
        const resposta = await fetch(formulario.action, {
          method: "POST",
          body: new FormData(formulario),
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const dados = await resposta.json();
        if (!resposta.ok || !dados.ok) {
          throw new Error(dados.mensagem || "Não foi Possível Atualizar o Carrinho.");
        }
        if (numeroRequisicao !== requisicaoAtual) return;
        input.value = dados.quantidade;
        valorConfirmado = input.value;
        subtotal.textContent = dados.subtotal;
        document.querySelectorAll("[data-cart-total]").forEach((elemento) => {
          elemento.textContent = dados.total;
        });
        document.querySelectorAll("[data-cart-count]").forEach((elemento) => {
          elemento.textContent = dados.quantidade_carrinho;
        });
        feedback.textContent = "";
      } catch (erro) {
        if (numeroRequisicao !== requisicaoAtual) return;
        input.value = valorConfirmado;
        input.dispatchEvent(new Event("input"));
        feedback.textContent = erro.message;
      } finally {
        if (numeroRequisicao === requisicaoAtual) {
          item.classList.remove("is-updating");
        }
      }
    };

    formulario.addEventListener("submit", (evento) => {
      evento.preventDefault();
      atualizar();
    });
    formulario
      .querySelectorAll("[data-quantity-decrease], [data-quantity-increase]")
      .forEach((botao) => botao.addEventListener("click", atualizar));
    input.addEventListener("input", (evento) => {
      if (!evento.isTrusted) return;
      window.clearTimeout(temporizador);
      temporizador = window.setTimeout(atualizar, 300);
    });
  });
}

function configurarServiceWorker() {
  if (
    !("serviceWorker" in navigator) ||
    (!window.isSecureContext && location.hostname !== "localhost")
  )
    return;
  const paginaJaControlada = Boolean(
    // O registro preserva a navegação normal quando o navegador não oferece PWA.
    navigator.serviceWorker.controller,
  );
  let paginaRecarregada = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (paginaJaControlada && !paginaRecarregada) {
      paginaRecarregada = true;
      window.location.reload();
    }
  });
  window.addEventListener("load", async () => {
    try {
      const registro = await navigator.serviceWorker.register(
        "/service-worker.js",
        {
          scope: "/",
          updateViaCache: "none",
        },
      );
      await registro.update();
    } catch {
      /* A interface continua funcional sem o Service Worker. */
    }
  });
}

function configurarRecarregamento() {
  const botao = document.querySelector("[data-retry]");
  if (!botao) return;
  botao.addEventListener("click", () => window.location.reload());
}

// -----------------------------------------------------------------------------
// Minha conta
// -----------------------------------------------------------------------------

function configurarAreaCliente() {
  const area = document.querySelector("[data-account-area]");
  if (!area) return;
  const tabs = [...area.querySelectorAll("[data-account-tab]")];
  const paineis = [...area.querySelectorAll("[data-account-panel]")];

  function mostrarPainel(nome) {
    paineis.forEach((painel) => {
      painel.hidden = painel.dataset.accountPanel !== nome;
    });
    tabs.forEach((tab) => {
      const selecionada = tab.dataset.accountTab === nome;
      tab.setAttribute("aria-selected", String(selecionada));
      tab.tabIndex = selecionada ? 0 : -1;
    });
  }

  tabs.forEach((tab, indice) => {
    tab.addEventListener("click", () => mostrarPainel(tab.dataset.accountTab));
    tab.addEventListener("keydown", (evento) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(evento.key)) return;
      evento.preventDefault();
      let destino = evento.key === "Home" ? 0 : tabs.length - 1;
      if (evento.key === "ArrowLeft") destino = (indice - 1 + tabs.length) % tabs.length;
      if (evento.key === "ArrowRight") destino = (indice + 1) % tabs.length;
      tabs[destino].focus();
      tabs[destino].click();
    });
  });
  area.querySelector("[data-forgot-password]")?.addEventListener("click", () =>
    mostrarPainel("recuperar"),
  );
  area.querySelector("[data-back-to-login]")?.addEventListener("click", () => {
    mostrarPainel("entrar");
    area.querySelector("#tab-entrar")?.focus();
  });
  mostrarPainel(area.dataset.initialPanel || "entrar");
}

function configurarAlternanciaSenha() {
  document.querySelectorAll("[data-password-toggle]").forEach((botao) => {
    botao.addEventListener("click", () => {
      const campo = document.getElementById(botao.dataset.passwordToggle);
      if (!campo) return;
      const mostrar = campo.type === "password";
      campo.type = mostrar ? "text" : "password";
      botao.setAttribute("aria-label", mostrar ? "Ocultar senha" : "Mostrar senha");
      botao.querySelector(".olho-aberto").hidden = mostrar;
      botao.querySelector(".olho-fechado").hidden = !mostrar;
    });
  });
}

function configurarMascaraCpf() {
  const campo = document.querySelector("#cadastro-cpf");
  campo?.setAttribute("inputmode", "numeric");
  campo?.setAttribute("placeholder", "000.000.000-00");
  campo?.setAttribute("maxlength", "14");
  campo?.addEventListener("input", () => {
    const numeros = campo.value.replace(/\D/g, "").slice(0, 11);
    campo.value = numeros
      .replace(/^(\d{3})(\d)/, "$1.$2")
      .replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3")
      .replace(/\.(\d{3})(\d)/, ".$1-$2");
  });
}

function configurarCriteriosSenha() {
  const senha = document.querySelector("#cadastro-senha");
  const confirmacao = document.querySelector("#cadastro-confirmacao");
  const mensagem = document.querySelector("#confirmacao-mensagem");
  if (!senha || !confirmacao || !mensagem) return;
  const regras = {
    length: { teste: (valor) => valor.length >= 8, texto: "Mínimo de 8 caracteres" },
    upper: { teste: (valor) => /[A-Z]/.test(valor), texto: "Uma letra maiúscula" },
    lower: { teste: (valor) => /[a-z]/.test(valor), texto: "Uma letra minúscula" },
    number: { teste: (valor) => /\d/.test(valor), texto: "Um número" },
    special: { teste: (valor) => /[^A-Za-z0-9]/.test(valor), texto: "Um caractere especial" },
  };

  function atualizar() {
    Object.entries(regras).forEach(([nome, regra]) => {
      const item = document.querySelector(`[data-password-rule="${nome}"]`);
      const valido = regra.teste(senha.value);
      item?.classList.toggle("is-valid", valido);
      if (item) item.textContent = `${valido ? "✓" : "✕"} ${regra.texto}`;
    });
    const preenchida = confirmacao.value.length > 0;
    const coincide = preenchida && senha.value === confirmacao.value;
    confirmacao.setAttribute("aria-invalid", String(preenchida && !coincide));
    mensagem.classList.toggle("is-valid", coincide);
    mensagem.textContent = preenchida
      ? coincide
        ? "✓ As senhas coincidem."
        : "✕ As senhas não coincidem."
      : "";
  }
  senha.addEventListener("input", atualizar);
  confirmacao.addEventListener("input", atualizar);
  atualizar();
}

function iniciarModulo(configurar) {
  try {
    configurar();
  } catch (erro) {
    console.error("Falha ao iniciar módulo de interface.", erro);
  }
}

[
  configurarRecarregamento,
  configurarTema,
  configurarDropdownsDoCabecalho,
  configurarBuscaDoCabecalho,
  configurarCookies,
  configurarAnimacoes,
  configurarCarrossel,
  configurarAlertas,
  configurarMenuMobile,
  configurarQuantidades,
  configurarAdicaoAoCarrinho,
  configurarCarrinho,
  configurarAreaCliente,
  configurarAlternanciaSenha,
  configurarMascaraCpf,
  configurarCriteriosSenha,
  configurarServiceWorker,
].forEach(iniciarModulo);
