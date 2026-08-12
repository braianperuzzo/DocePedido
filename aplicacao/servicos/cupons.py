"""Regras de cupons disponíveis na Doce Pedido."""

from decimal import ROUND_HALF_UP, Decimal

from aplicacao import banco
from aplicacao.modelos import Cliente, Pedido

CODIGO_BEMVINDO = "BEMVINDO"
PERCENTUAL_BEMVINDO = Decimal("0.10")


def normalizar_codigo(codigo):
    """Normaliza o código informado antes da validação."""
    return (codigo or "").strip().upper()


def cpf_ja_realizou_compra(cpf):
    """Informa se existe pedido de uma conta que utiliza o CPF informado."""
    if not cpf:
        return True

    pedido_id = banco.session.scalar(
        banco.select(Pedido.id)
        .join(Cliente, Pedido.cliente_id == Cliente.id)
        .where(Cliente.cpf == cpf)
        .limit(1)
    )
    return pedido_id is not None


def validar_cupom(codigo, cliente):
    """Valida o código e a elegibilidade do cliente sem alterar a sessão."""
    codigo = normalizar_codigo(codigo)
    if codigo != CODIGO_BEMVINDO:
        return False, "Cupom não encontrado."
    if not cliente:
        return False, "Entre na sua conta para validar o cupom."
    if not getattr(cliente, "cpf", None):
        return False, "Sua conta precisa ter CPF cadastrado para usar o cupom."
    if cpf_ja_realizou_compra(cliente.cpf):
        return (
            False,
            "O cupom BEMVINDO é válido somente na primeira compra deste CPF.",
        )
    return True, None


def calcular_resumo(subtotal, codigo, cliente):
    """Calcula desconto e total somente quando o cupom continua válido."""
    subtotal = Decimal(subtotal or 0).quantize(Decimal("0.01"))
    valido, _ = validar_cupom(codigo, cliente)
    if not valido:
        return {
            "subtotal": subtotal,
            "desconto": Decimal("0.00"),
            "total": subtotal,
            "cupom": None,
        }

    desconto = (subtotal * PERCENTUAL_BEMVINDO).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return {
        "subtotal": subtotal,
        "desconto": desconto,
        "total": subtotal - desconto,
        "cupom": CODIGO_BEMVINDO,
    }
