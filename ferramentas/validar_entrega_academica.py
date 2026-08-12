"""Valida a estrutura e a consistência documental da entrega acadêmica atual.

O script não recria evidências nem altera arquivos. Ele verifica a árvore vigente do
repositório, links Markdown, evidências esperadas e artefatos finais de submissão.
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "documentacao"
PLANEJAMENTO = DOCS / "01-PLANEJAMENTO-E-MODELAGEM"
DESENVOLVIMENTO = DOCS / "02-DESENVOLVIMENTO-E-PUBLICACAO"
QUALIDADE = DOCS / "03-TESTES-E-QUALIDADE"
CONSOLIDADA = DOCS / "04-DOCUMENTACAO-CONSOLIDADA"
PIT_I = DOCS / "05-PIT-I"
PIT_II = DOCS / "06-PIT-2"
EVIDENCIAS = PLANEJAMENTO / "evidencias"
HISTORICO = EVIDENCIAS / "historico"
DIAGRAMAS = PLANEJAMENTO / "diagramas"

PASTAS_DOCUMENTACAO = {
    "01-PLANEJAMENTO-E-MODELAGEM",
    "02-DESENVOLVIMENTO-E-PUBLICACAO",
    "03-TESTES-E-QUALIDADE",
    "04-DOCUMENTACAO-CONSOLIDADA",
    "05-PIT-I",
    "06-PIT-2",
}

OBRIGATORIOS = [
    RAIZ / "README.md",
    DOCS / "README.md",
    PLANEJAMENTO / "README.md",
    PLANEJAMENTO / "ESCOPO_E_REQUISITOS.md",
    PLANEJAMENTO / "MODELAGEM_UML.md",
    PLANEJAMENTO / "IHC_E_UX.md",
    PLANEJAMENTO / "BANCO_DE_DADOS.md",
    DIAGRAMAS / "01-casos-de-uso.puml",
    DIAGRAMAS / "02-classes.puml",
    DIAGRAMAS / "03-sequencia-finalizacao-pedido.puml",
    DIAGRAMAS / "04-atividade-compra.puml",
    DIAGRAMAS / "05-componentes-mvc.puml",
    EVIDENCIAS / "README.md",
    HISTORICO / "README.md",
    DESENVOLVIMENTO / "README.md",
    DESENVOLVIMENTO / "ARQUITETURA_E_CODIGO.md",
    DESENVOLVIMENTO / "FUNCIONALIDADES_E_USO.md",
    DESENVOLVIMENTO / "PUBLICACAO_PWA_SEO.md",
    DESENVOLVIMENTO / "SEGURANCA_E_PRIVACIDADE.md",
    QUALIDADE / "README.md",
    QUALIDADE / "RESULTADOS_TECNICOS.md",
    QUALIDADE / "MODELO_AVALIACAO_EXTERNA.md",
    QUALIDADE / "AVALIACOES_EXTERNAS.md",
    QUALIDADE / "LAUDO_QUALIDADE.md",
    QUALIDADE / "EVIDENCIAS_ANTES_DEPOIS.md",
    CONSOLIDADA / "README.md",
    CONSOLIDADA / "ENTREGA_PIT_II.md",
    CONSOLIDADA / "ENTREGA_PIT_II.pdf",
    CONSOLIDADA / "FORMULARIO_ENTREGA.md",
    CONSOLIDADA / "MATRIZ_RASTREABILIDADE.md",
    PIT_I / "README.md",
    PIT_I / "00-DocumentoOriginal.pdf",
    PIT_I / "01-DocumentoMelhorado.md",
    PIT_I / "01-DocumentoMelhorado.pdf",
    PIT_I / "02-ESCOPO-E-REQUISITOS.md",
    PIT_I / "03-UML-E-ARQUITETURA.md",
    PIT_I / "04-IHC-E-UX.md",
    PIT_I / "05-BANCO-DE-DADOS.md",
    PIT_I / "06-RASTREABILIDADE-E-EVOLUCAO.md",
    PIT_II / "00-Documento_PIT_II.docx",
    PIT_II / "00-Documento_PIT_II.md",
    PIT_II / "00-Documento_PIT_II.pdf",
    PIT_II / "01-Video-1-Apresentação.mp4",
    PIT_II / "02-Video-2-Erros.mp4",
    PIT_II / "03-Material.pdf",
]

FINAIS = [
    "01-home-desktop.png",
    "02-home-mobile.png",
    "03-catalogo-filtros.png",
    "04-produto.png",
    "05-carrinho-cupom.png",
    "06-login-cadastro.png",
    "07-minha-conta.png",
    "08-checkout.png",
    "09-pedido-confirmado.png",
    "10-meus-pedidos.png",
    "11-validacao-formulario.png",
    "12-offline.png",
    "13-faq-dark.png",
    "14-sobre-rodape.png",
    "15-favoritos.png",
    "16-seguranca.png",
    "17-validacao-dispositivo-email.jpeg",
    "18-revisar-pedido.jpeg",
    "19-padronizacao-textual.png",
]

HISTORICAS = [
    "01-offline-antes.png",
    "02-catalogo-antes.png",
    "03-produto-antes.png",
    "04-faq-antes.png",
    "05-home-mobile-antes.png",
    "06-rodape-antes.png",
    "07-finalizacao-direta-antes.jpeg",
    "08-padronizacao-textual-antes.png",
]

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
VIDEO_RE = re.compile(r"https://youtu\.be/[A-Za-z0-9_-]+")


def normalizar_destino(destino: str) -> str:
    destino = destino.strip()
    if ' "' in destino or " '" in destino:
        destino = destino.split(maxsplit=1)[0]
    return unquote(destino)


def validar_estrutura(erros: list[str]) -> None:
    if not DOCS.exists():
        erros.append("pasta documentacao/ ausente")
        return

    atuais = {p.name for p in DOCS.iterdir() if p.is_dir()}
    extras = sorted(atuais - PASTAS_DOCUMENTACAO)
    ausentes = sorted(PASTAS_DOCUMENTACAO - atuais)
    for item in ausentes:
        erros.append(f"pasta obrigatória ausente: documentacao/{item}")
    for item in extras:
        erros.append(f"pasta inesperada em documentacao/: {item}")

    for caminho in OBRIGATORIOS:
        if not caminho.exists():
            erros.append(f"arquivo obrigatório ausente: {caminho.relative_to(RAIZ)}")


def validar_evidencias(erros: list[str]) -> None:
    for nome in FINAIS:
        if not (EVIDENCIAS / nome).exists():
            erros.append(f"evidência final/complementar ausente: {nome}")
    for nome in HISTORICAS:
        if not (HISTORICO / nome).exists():
            erros.append(f"evidência histórica ausente: historico/{nome}")


def validar_links(erros: list[str]) -> None:
    quebrados: set[str] = set()
    arquivos = [RAIZ / "README.md", *DOCS.rglob("*.md")]
    for arquivo in arquivos:
        if not arquivo.exists():
            continue
        texto = arquivo.read_text(encoding="utf-8")
        for bruto in LINK_RE.findall(texto):
            destino = normalizar_destino(bruto)
            if not destino or destino.startswith(("http://", "https://", "mailto:", "#")):
                continue
            caminho_sem_ancora = destino.split("#", 1)[0]
            if not caminho_sem_ancora:
                continue
            alvo = (arquivo.parent / caminho_sem_ancora).resolve()
            if not alvo.exists():
                quebrados.add(f"{arquivo.relative_to(RAIZ)} -> {destino}")
    erros.extend(f"link local quebrado: {item}" for item in sorted(quebrados))


def validar_navegacao(erros: list[str]) -> None:
    arquivos = [RAIZ / "README.md", DOCS / "README.md"]
    referencias = [
        "01-PLANEJAMENTO-E-MODELAGEM",
        "02-DESENVOLVIMENTO-E-PUBLICACAO",
        "03-TESTES-E-QUALIDADE",
        "04-DOCUMENTACAO-CONSOLIDADA",
        "05-PIT-I",
        "06-PIT-2",
    ]
    for arquivo in arquivos:
        if not arquivo.exists():
            continue
        texto = arquivo.read_text(encoding="utf-8")
        for ref in referencias:
            if ref not in texto:
                erros.append(f"{arquivo.relative_to(RAIZ)} não referencia {ref}")


def pendencias_finais() -> list[str]:
    pendencias: list[str] = []

    md = PIT_II / "00-Documento_PIT_II.md"
    if md.exists():
        links = VIDEO_RE.findall(md.read_text(encoding="utf-8"))
        if len(set(links)) < 2:
            pendencias.append("o documento oficial Markdown deve conter os dois links de vídeo")

    formulario = CONSOLIDADA / "FORMULARIO_ENTREGA.md"
    if formulario.exists():
        links = VIDEO_RE.findall(formulario.read_text(encoding="utf-8"))
        if len(set(links)) < 2:
            pendencias.append("o formulário consolidado deve conter os dois links de vídeo")

    return pendencias


def main() -> int:
    erros: list[str] = []
    validar_estrutura(erros)
    validar_evidencias(erros)
    validar_links(erros)
    validar_navegacao(erros)

    if erros:
        print(f"Validação estrutural falhou com {len(erros)} problema(s):")
        for item in erros:
            print(f"- {item}")
        return 1

    print("Validação estrutural aprovada.")
    print("- estrutura atual de documentacao/: OK")
    print("- arquivos acadêmicos essenciais: OK")
    print("- artefatos finais da PIT II: OK")
    print("- 19 evidências finais/complementares: OK")
    print("- 8 evidências históricas: OK")
    print("- links Markdown locais: OK")
    print("- navegação principal: OK")

    pendencias = pendencias_finais()
    if pendencias:
        print("\nPendências finais de submissão:")
        for item in pendencias:
            print(f"- {item}")
    else:
        print("- documento oficial, PDF e links dos vídeos: OK")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
