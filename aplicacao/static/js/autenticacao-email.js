(() => {
  const area = document.querySelector("[data-account-area]");
  const formulario = area?.querySelector("[data-password-recovery]");
  if (!area || !formulario) return;

  formulario.addEventListener(
    "submit",
    async (evento) => {
      evento.preventDefault();
      evento.stopImmediatePropagation();

      const email = formulario.querySelector("input[type=email]");
      const mensagem = area.querySelector("#recuperar-mensagem");
      const botao = formulario.querySelector("button[type=submit]");
      const csrf = area.querySelector('input[name="csrf_token"]')?.value;
      const valido = Boolean(email?.value.trim()) && email.checkValidity();

      email?.setAttribute("aria-invalid", String(!valido));
      if (!valido) {
        mensagem.textContent = "Informe um e-mail válido.";
        return;
      }
      if (!botao || botao.disabled) return;

      const textoOriginal = botao.textContent;
      botao.disabled = true;
      botao.textContent = "Enviando...";
      mensagem.textContent = "";

      const dadosFormulario = new FormData();
      dadosFormulario.append("email", email.value.trim());
      if (csrf) dadosFormulario.append("csrf_token", csrf);

      try {
        const resposta = await fetch("/esqueci-senha", {
          method: "POST",
          body: dadosFormulario,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const dados = await resposta.json();
        if (!resposta.ok || !dados.ok) {
          throw new Error(
            dados.mensagem || "Não foi Possível processar a solicitação agora.",
          );
        }
        mensagem.textContent = dados.mensagem;
        email.value = "";
        if (typeof window.exibirPopup === "function") {
          window.exibirPopup(dados.mensagem);
        }
      } catch (erro) {
        mensagem.textContent = erro.message;
        if (typeof window.exibirPopup === "function") {
          window.exibirPopup(erro.message);
        }
      } finally {
        botao.disabled = false;
        botao.textContent = textoOriginal;
      }
    },
    { capture: true },
  );
})();
