document.addEventListener("DOMContentLoaded", () => {
  const area = document.querySelector("[data-profile-account]");
  if (!area) return;

  const formatarCelular = (valor) => {
    const numeros = valor.replace(/\D/g, "").slice(0, 11);
    if (numeros.length <= 2) return numeros ? `(${numeros}` : "";
    if (numeros.length <= 7) {
      return `(${numeros.slice(0, 2)}) ${numeros.slice(2)}`;
    }
    return `(${numeros.slice(0, 2)}) ${numeros.slice(2, 7)}.${numeros.slice(7)}`;
  };

  document.querySelectorAll("[data-cellphone-input]").forEach((campo) => {
    campo.value = formatarCelular(campo.value);
    campo.addEventListener("input", () => {
      campo.value = formatarCelular(campo.value);
    });
  });

  document.querySelectorAll("[data-profile-password-toggle]").forEach((botao) => {
    botao.addEventListener("click", () => {
      const campo = document.getElementById(botao.dataset.profilePasswordToggle);
      if (!campo) return;

      const mostrar = campo.type === "password";
      campo.type = mostrar ? "text" : "password";
      botao.setAttribute("aria-label", mostrar ? "Ocultar Senha" : "Mostrar Senha");
      const aberto = botao.querySelector("[data-profile-eye-open]");
      const fechado = botao.querySelector("[data-profile-eye-closed]");
      if (aberto) aberto.hidden = mostrar;
      if (fechado) fechado.hidden = !mostrar;
    });
  });

  const novaSenha = document.querySelector("#nova-senha");
  const confirmacaoNovaSenha = document.querySelector("#confirmacao-nova-senha");
  const criterios = document.querySelector("[data-profile-password-criteria]");
  const mensagemConfirmacao = document.querySelector("[data-profile-password-match]");
  const regras = {
    length: {
      teste: (valor) => valor.length >= 8,
      texto: "Mínimo de 8 Caracteres",
    },
    upper: {
      teste: (valor) => /[A-Z]/.test(valor),
      texto: "Uma Letra Maiúscula",
    },
    lower: {
      teste: (valor) => /[a-z]/.test(valor),
      texto: "Uma Letra Minúscula",
    },
    number: {
      teste: (valor) => /\d/.test(valor),
      texto: "Um Número",
    },
    special: {
      teste: (valor) => /[^A-Za-z0-9]/.test(valor),
      texto: "Um Caractere Especial",
    },
  };

  function atualizarCriteriosSenha() {
    if (!novaSenha || !criterios) return;
    const valor = novaSenha.value;
    criterios.hidden = valor.length === 0;

    Object.entries(regras).forEach(([nome, regra]) => {
      const item = criterios.querySelector(
        `[data-profile-password-rule="${nome}"]`,
      );
      if (!item) return;
      const valido = regra.teste(valor);
      item.textContent = `${valido ? "✓" : "✕"} ${regra.texto}`;
      item.dataset.valid = String(valido);
    });

    if (!confirmacaoNovaSenha || !mensagemConfirmacao) return;
    const preenchida = confirmacaoNovaSenha.value.length > 0;
    if (!preenchida) {
      mensagemConfirmacao.textContent = "";
      return;
    }
    const coincide = valor === confirmacaoNovaSenha.value;
    mensagemConfirmacao.textContent = coincide
      ? "✓ As Senhas Coincidem."
      : "✕ As Senhas Não Coincidem.";
  }

  novaSenha?.addEventListener("input", atualizarCriteriosSenha);
  confirmacaoNovaSenha?.addEventListener("input", atualizarCriteriosSenha);
  atualizarCriteriosSenha();

  document.querySelectorAll(".profile-account-modal").forEach((modal) => {
    modal.closest(".modal")?.addEventListener("hidden.bs.modal", () => {
      modal.querySelectorAll("[data-profile-password-toggle]").forEach((botao) => {
        const campo = document.getElementById(botao.dataset.profilePasswordToggle);
        if (campo?.type === "text") {
          campo.type = "password";
        }
        botao.setAttribute("aria-label", "Mostrar Senha");
        const aberto = botao.querySelector("[data-profile-eye-open]");
        const fechado = botao.querySelector("[data-profile-eye-closed]");
        if (aberto) aberto.hidden = false;
        if (fechado) fechado.hidden = true;
      });

      if (modal.closest("#modal-alterar-senha")) {
        modal.querySelector("form")?.reset();
        atualizarCriteriosSenha();
      }
    });
  });
});