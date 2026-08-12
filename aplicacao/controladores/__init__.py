"""Exporta os blueprints que compõem as rotas da aplicação."""

from aplicacao.controladores.autenticacao import autenticacao
from aplicacao.controladores.carrinho import carrinho
from aplicacao.controladores.compatibilidade import compatibilidade
from aplicacao.controladores.conta import conta
from aplicacao.controladores.pagina_inicial import pagina_inicial
from aplicacao.controladores.pedidos import pedidos
from aplicacao.controladores.produtos import produtos
from aplicacao.controladores.recursos_conta import recursos_conta
from aplicacao.controladores.seguranca_conta import seguranca_conta

controladores = (
    compatibilidade,
    pagina_inicial,
    autenticacao,
    seguranca_conta,
    conta,
    recursos_conta,
    produtos,
    carrinho,
    pedidos,
)

__all__ = ["controladores"]
