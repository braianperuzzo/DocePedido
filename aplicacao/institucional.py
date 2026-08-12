"""Rotas das páginas institucionais da Doce Pedido."""

from flask import Blueprint, render_template

institucional = Blueprint("institucional", __name__)


@institucional.get("/sobre")
def sobre():
    return render_template("institucional/sobre.html")


@institucional.get("/faq")
def faq():
    return render_template("institucional/faq.html")


@institucional.get("/entrega")
def entrega():
    return render_template("institucional/entrega.html")


@institucional.get("/trocas-e-cancelamentos")
def trocas_cancelamentos():
    return render_template("institucional/trocas_cancelamentos.html")


@institucional.get("/privacidade")
def privacidade():
    return render_template("institucional/privacidade.html")


@institucional.get("/cookies")
def cookies():
    return render_template("institucional/cookies.html")


@institucional.get("/termos")
def termos():
    return render_template("institucional/termos.html")


@institucional.get("/seguranca")
def seguranca():
    return render_template("institucional/seguranca.html")


@institucional.get("/offline")
def offline():
    return render_template("institucional/offline.html")
