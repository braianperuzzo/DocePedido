"""Ponto de entrada para executar a aplicação Doce Pedido."""

from dotenv import load_dotenv

from aplicacao import criar_aplicacao

load_dotenv()

aplicacao = criar_aplicacao()

if __name__ == "__main__":
    aplicacao.run(debug=aplicacao.debug)
