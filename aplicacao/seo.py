"""Utilitários de SEO e metadados compartilhados pelas páginas."""

from pathlib import Path
from urllib.parse import urljoin

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from aplicacao import banco
from aplicacao.modelos import Produto

seo = Blueprint("seo", __name__)

INFORMACOES_SITE = {
    "nome": "Doce Pedido",
    "descricao": (
        "Loja de cupcakes artesanais, sabores especiais e kits para "
        "diferentes momentos."
    ),
    "idioma": "pt-BR",
    "locale": "pt_BR",
}


def url_publica(caminho="/"):
    """Monta uma URL absoluta usando a origem pública configurada."""

    base = current_app.config.get("SITE_URL") or request.url_root
    return urljoin(f"{base.rstrip('/')}/", caminho.lstrip("/"))


def url_publica_para(endpoint, **valores):
    """Monta uma URL pública absoluta para um endpoint Flask."""

    return url_publica(url_for(endpoint, **valores))


def arquivo_estatico_existe(nome):
    """Confirma que o caminho aponta para um arquivo dentro do diretório static."""
    if not nome:
        return False
    raiz = Path(current_app.static_folder).resolve()
    candidato = (raiz / nome).resolve()
    return candidato.is_relative_to(raiz) and candidato.is_file()


def contexto_seo():
    """Disponibiliza metadados básicos e dados comerciais opcionais."""

    informacoes_site = {
        **INFORMACOES_SITE,
        "email": current_app.config.get("SITE_EMAIL", ""),
        "telefone": current_app.config.get("SITE_TELEPHONE", ""),
        "telefone_exibicao": current_app.config.get("SITE_TELEPHONE_DISPLAY", ""),
        "horarios": current_app.config.get("SITE_BUSINESS_HOURS", ""),
        "redes": {
            "facebook": current_app.config.get("SITE_FACEBOOK_URL", ""),
            "instagram": current_app.config.get("SITE_INSTAGRAM_URL", ""),
            "tiktok": current_app.config.get("SITE_TIKTOK_URL", ""),
            "whatsapp": current_app.config.get("SITE_WHATSAPP_URL", ""),
        },
        "endereco": {
            "logradouro": current_app.config.get("SITE_ADDRESS_STREET", ""),
            "cidade": current_app.config.get("SITE_ADDRESS_LOCALITY", ""),
            "estado": current_app.config.get("SITE_ADDRESS_REGION", ""),
            "pais": current_app.config.get("SITE_ADDRESS_COUNTRY", ""),
            "completo": current_app.config.get("SITE_ADDRESS_DISPLAY", ""),
            "maps": current_app.config.get("SITE_MAPS_URL", ""),
        },
    }
    return {
        "informacoes_site": informacoes_site,
        "url_publica": url_publica,
        "url_publica_para": url_publica_para,
        "google_site_verification": current_app.config.get("GOOGLE_SITE_VERIFICATION"),
        "bing_site_verification": current_app.config.get("BING_SITE_VERIFICATION"),
        "ga_measurement_id": current_app.config.get("GA_MEASUREMENT_ID"),
        "arquivo_estatico_existe": arquivo_estatico_existe,
        "imagem_produto_existe": arquivo_estatico_existe,
    }


@seo.get("/api/site-footer")
def dados_rodape():
    """Expõe somente os dados públicos necessários para completar o rodapé."""

    return jsonify(
        {
            "endereco": current_app.config.get("SITE_ADDRESS_DISPLAY", ""),
            "maps": current_app.config.get("SITE_MAPS_URL", ""),
        }
    )


@seo.get("/robots.txt")
def robots():
    """Publica regras de indexação e a URL do sitemap."""

    conteudo = render_template(
        "seo/robots.txt", sitemap_url=url_publica("/sitemap.xml")
    )
    return Response(conteudo, content_type="text/plain; charset=utf-8")


@seo.get("/sitemap.xml")
def sitemap():
    """Lista rotas públicas e produtos ativos para indexação."""

    produtos = banco.session.scalars(
        banco.select(Produto).where(Produto.ativo.is_(True)).order_by(Produto.id)
    ).all()
    urls = [
        url_publica_para("pagina_inicial.inicio"),
        url_publica_para("produtos.catalogo"),
        url_publica_para("institucional.sobre"),
        url_publica_para("institucional.faq"),
        url_publica_para("institucional.entrega"),
        url_publica_para("institucional.trocas_cancelamentos"),
        url_publica_para("institucional.privacidade"),
        url_publica_para("institucional.cookies"),
        url_publica_para("institucional.termos"),
        url_publica_para("institucional.seguranca"),
        *[
            url_publica_para("produtos.detalhes", produto_id=produto.id)
            for produto in produtos
        ],
    ]
    conteudo = render_template("seo/sitemap.xml", urls=urls)
    return Response(conteudo, content_type="application/xml; charset=utf-8")


@seo.get("/manifest.webmanifest")
@seo.get("/site.webmanifest")
def manifesto():
    """Gera o manifesto PWA apenas com ícones existentes."""

    candidatos = [
        ("imagens/icone-192.png", "192x192", "any"),
        ("imagens/icone-512.png", "512x512", "any"),
        ("imagens/icone-maskable-192.png", "192x192", "maskable"),
        ("imagens/icone-maskable-512.png", "512x512", "maskable"),
    ]
    icons = [
        {
            "src": url_for("static", filename=nome),
            "sizes": tamanho,
            "type": "image/png",
            "purpose": finalidade,
        }
        for nome, tamanho, finalidade in candidatos
        if arquivo_estatico_existe(nome)
    ]
    resposta = jsonify(
        {
            "name": INFORMACOES_SITE["nome"],
            "short_name": INFORMACOES_SITE["nome"],
            "description": INFORMACOES_SITE["descricao"],
            "lang": INFORMACOES_SITE["idioma"],
            "icons": icons,
            "theme_color": "#b85f7d",
            "background_color": "#fffdf9",
            "display": "standalone",
            "start_url": url_for("pagina_inicial.inicio"),
            "scope": "/",
            "shortcuts": [
                {"name": "Produtos", "url": url_for("produtos.catalogo")},
                {"name": "Carrinho", "url": url_for("carrinho.visualizar")},
            ],
        }
    )
    resposta.content_type = "application/manifest+json"
    return resposta


@seo.get("/service-worker.js")
def service_worker():
    """Serve o Service Worker na raiz com cache HTTP desabilitado."""

    resposta = send_from_directory(
        Path(current_app.static_folder) / "js", "service-worker.js"
    )
    resposta.headers["Service-Worker-Allowed"] = "/"
    resposta.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resposta.headers["Expires"] = "0"
    return resposta
