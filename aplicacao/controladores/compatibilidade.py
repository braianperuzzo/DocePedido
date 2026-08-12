"""Ajustes mínimos de compatibilidade para bancos SQLite criados por versões antigas."""

from flask import Blueprint, current_app
from sqlalchemy import inspect, text

from aplicacao import banco

compatibilidade = Blueprint("compatibilidade", __name__)
MARCADOR_SCHEMA = "doce_pedido_schema_local_verificado"


def _garantir_cpf_cliente(inspetor):
    """Inclui o CPF em bases antigas sem apagar clientes existentes."""
    if "cliente" not in inspetor.get_table_names():
        return

    colunas = {coluna["name"] for coluna in inspetor.get_columns("cliente")}
    if "cpf" in colunas:
        return

    with banco.engine.begin() as conexao:
        conexao.execute(text("ALTER TABLE cliente ADD COLUMN cpf VARCHAR(11)"))
        conexao.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_cliente_cpf_compat "
                "ON cliente (cpf) WHERE cpf IS NOT NULL"
            )
        )
    current_app.logger.info(
        "Schema local atualizado: coluna CPF adicionada sem remover clientes existentes."
    )


def _garantir_campos_cupom(inspetor):
    """Inclui os campos de cupom em pedidos criados antes dessa funcionalidade."""
    if "detalhe_pedido" not in inspetor.get_table_names():
        return

    colunas = {
        coluna["name"] for coluna in inspetor.get_columns("detalhe_pedido")
    }
    comandos = []
    if "cupom_codigo" not in colunas:
        comandos.append(
            "ALTER TABLE detalhe_pedido ADD COLUMN cupom_codigo VARCHAR(30)"
        )
    if "valor_desconto" not in colunas:
        comandos.append(
            "ALTER TABLE detalhe_pedido ADD COLUMN "
            "valor_desconto NUMERIC(10, 2) NOT NULL DEFAULT 0"
        )
    if not comandos:
        return

    with banco.engine.begin() as conexao:
        for comando in comandos:
            conexao.execute(text(comando))
    current_app.logger.info(
        "Schema local atualizado: campos de cupom adicionados aos detalhes do pedido."
    )


@compatibilidade.before_app_request
def garantir_schema_local():
    """Aplica somente ajustes aditivos necessários em bancos SQLite antigos."""
    if current_app.extensions.get(MARCADOR_SCHEMA):
        return

    if banco.engine.dialect.name != "sqlite":
        current_app.extensions[MARCADOR_SCHEMA] = True
        return

    inspetor = inspect(banco.engine)
    _garantir_cpf_cliente(inspetor)
    inspetor = inspect(banco.engine)
    _garantir_campos_cupom(inspetor)
    current_app.extensions[MARCADOR_SCHEMA] = True
