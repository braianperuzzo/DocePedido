document.addEventListener("DOMContentLoaded", () => {
  const checkout = document.querySelector("[data-checkout]");
  if (!checkout) return;

  const opcoesRecebimento = checkout.querySelectorAll("[data-receipt-option]");
  const enderecoEntrega = checkout.querySelector("[data-delivery-address]");
  const retirada = checkout.querySelector("[data-pickup-address]");
  const resumoRecebimento = checkout.querySelector("[data-receipt-label]");
  const seletorEndereco = checkout.querySelector("[data-checkout-address-select]");
  const nomeEndereco = checkout.querySelector("[data-selected-address-name]");
  const detalhesEndereco = checkout.querySelectorAll(
    "[data-checkout-address-detail]",
  );

  const atualizarEndereco = () => {
    if (!seletorEndereco) return;
    const id = seletorEndereco.value;
    const opcao = seletorEndereco.selectedOptions[0];

    detalhesEndereco.forEach((detalhe) => {
      detalhe.hidden = detalhe.dataset.checkoutAddressDetail !== id;
    });

    if (nomeEndereco && opcao) {
      nomeEndereco.textContent = opcao.dataset.addressName || opcao.textContent.trim();
    }
  };

  const atualizarRecebimento = () => {
    const selecionada = checkout.querySelector(
      '[data-receipt-option]:checked',
    );
    const entregaSelecionada = selecionada?.value === "entrega";

    if (enderecoEntrega) enderecoEntrega.hidden = !entregaSelecionada;
    if (retirada) retirada.hidden = entregaSelecionada;
    if (seletorEndereco) seletorEndereco.disabled = !entregaSelecionada;
    if (resumoRecebimento) {
      resumoRecebimento.textContent = entregaSelecionada
        ? "Entrega"
        : "Retirada na Loja";
    }
  };

  opcoesRecebimento.forEach((opcao) => {
    opcao.addEventListener("change", atualizarRecebimento);
  });

  seletorEndereco?.addEventListener("change", atualizarEndereco);

  atualizarEndereco();
  atualizarRecebimento();
});