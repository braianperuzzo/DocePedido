/** Adiciona estados e reconexão progressivos à página, que permanece útil sem JS. */
(() => {
  const pagina = document.querySelector(".offline-page");
  const botao = document.querySelector("[data-retry]");
  const rotulo = document.querySelector("[data-retry-label]");
  const status = document.querySelector("[data-connection-status]");
  if (!pagina || !botao || !rotulo || !status) return;

  let verificacaoEmCurso = false;
  let retornoAgendado = false;
  const chaveTentativaAutomatica = "doce_pedido_retorno_offline";

  function definirEstado(textoStatus, textoBotao, carregando) {
    if (status.textContent !== textoStatus) status.textContent = textoStatus;
    rotulo.textContent = textoBotao;
    botao.disabled = carregando;
    botao.classList.toggle("is-loading", carregando);
  }

  function tentativaAutomaticaJaRealizada() {
    try {
      if (sessionStorage.getItem(chaveTentativaAutomatica)) return true;
      sessionStorage.setItem(chaveTentativaAutomatica, "1");
    } catch {
      // A flag em memória ainda evita repetição nesta renderização.
    }
    return false;
  }

  async function servidorEstaDisponivel() {
    const controlador = new AbortController();
    const limite = window.setTimeout(() => controlador.abort(), 2500);
    try {
      const resposta = await fetch(window.location.href, {
        cache: "no-store",
        credentials: "same-origin",
        headers: { "X-Offline-Check": "1" },
        signal: controlador.signal,
      });
      return resposta.ok;
    } catch {
      return false;
    } finally {
      window.clearTimeout(limite);
    }
  }

  function concluirReconexao() {
    if (retornoAgendado) return;
    retornoAgendado = true;
    pagina.classList.add("is-online");
    definirEstado("Conexão Restabelecida", "Atualizando...", true);
    window.setTimeout(() => window.location.reload(), 500);
  }

  async function verificarConexao() {
    if (verificacaoEmCurso || retornoAgendado) return;
    verificacaoEmCurso = true;
    const inicioVerificacao = Date.now();
    definirEstado("Verificando Conexão...", "Verificando...", true);

    if (!navigator.onLine) {
      await new Promise((resolver) => window.setTimeout(resolver, 600));
    }
    const disponivel = navigator.onLine && (await servidorEstaDisponivel());
    if (disponivel) {
      concluirReconexao();
      return;
    }

    const tempoRestante = Math.max(0, 600 - (Date.now() - inicioVerificacao));
    if (tempoRestante) {
      await new Promise((resolver) =>
        window.setTimeout(resolver, tempoRestante),
      );
    }

    verificacaoEmCurso = false;
    definirEstado("Aguardando Conexão", "Tentar Novamente", false);
  }

  botao.addEventListener("click", verificarConexao);
  window.addEventListener("online", verificarConexao);

  if (navigator.onLine && !tentativaAutomaticaJaRealizada()) {
    window.setTimeout(verificarConexao, 250);
  }
})();
