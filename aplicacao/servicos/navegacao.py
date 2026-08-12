"""Validação de destinos usados em redirecionamentos da aplicação."""

from urllib.parse import urlsplit


def caminho_interno_seguro(valor):
    """Aceita somente caminhos locais iniciados por uma única barra."""
    if not valor:
        return None

    caminho = str(valor).strip()
    partes = urlsplit(caminho)
    if partes.scheme or partes.netloc:
        return None
    if not caminho.startswith("/") or caminho.startswith("//"):
        return None
    return caminho


def caminho_de_referencia_seguro(referencia, origem):
    """Converte uma URL de referência da mesma origem em um caminho local seguro."""
    if not referencia:
        return None

    referencia_partes = urlsplit(str(referencia))
    origem_partes = urlsplit(str(origem))
    if (
        referencia_partes.scheme != origem_partes.scheme
        or referencia_partes.netloc != origem_partes.netloc
    ):
        return None

    caminho = referencia_partes.path or "/"
    if referencia_partes.query:
        caminho = f"{caminho}?{referencia_partes.query}"
    return caminho_interno_seguro(caminho)
