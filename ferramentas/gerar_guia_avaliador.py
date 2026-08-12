"""Gera o PDF visual de apoio à avaliação usando a estrutura atual do repositório.

O PDF gerado é complementar. O documento oficial da PIT II permanece em
`documentacao/06-PIT-2/`, disponível em DOCX, Markdown e PDF.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "documentacao"
EVIDENCIAS = DOCS / "01-PLANEJAMENTO-E-MODELAGEM" / "evidencias"
HISTORICO = EVIDENCIAS / "historico"
QUALIDADE = DOCS / "03-TESTES-E-QUALIDADE"
PIT_II = DOCS / "06-PIT-2"
PDF_OFICIAL = PIT_II / "00-Documento_PIT_II.pdf"
OUT = DOCS / "04-DOCUMENTACAO-CONSOLIDADA" / "ENTREGA_PIT_II.pdf"
REPO = "https://github.com/braianperuzzo/DocePedido"
APP = "https://docepedido.pythonanywhere.com/"

DARK = colors.HexColor("#7E3E56")
LIGHT = colors.HexColor("#F8F2F5")
BORDER = colors.HexColor("#D9D9D9")
GRAY = colors.HexColor("#555555")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CapaDP", parent=styles["Title"], fontSize=23, leading=27, alignment=1, textColor=DARK, spaceAfter=8))
styles.add(ParagraphStyle(name="SubDP", parent=styles["Normal"], fontSize=10, leading=14, alignment=1, textColor=GRAY, spaceAfter=7))
styles.add(ParagraphStyle(name="H1DP", parent=styles["Heading1"], fontSize=16, leading=20, textColor=DARK, spaceAfter=8))
styles.add(ParagraphStyle(name="BodyDP", parent=styles["BodyText"], fontSize=9, leading=12, spaceAfter=5))
styles.add(ParagraphStyle(name="CapDP", parent=styles["BodyText"], fontSize=7.5, leading=9, alignment=1, textColor=GRAY))


def figura(path: Path, max_w: float, max_h: float) -> Image:
    if not path.exists():
        raise FileNotFoundError(path)
    with PILImage.open(path) as im:
        w, h = im.size
    escala = min(max_w / w, max_h / h)
    return Image(str(path), width=w * escala, height=h * escala)


def tabela(rows, widths):
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def par_imagens(antes: str, depois: str, titulo: str):
    t = Table([
        [figura(HISTORICO / antes, 7.5 * cm, 6.0 * cm), figura(EVIDENCIAS / depois, 7.5 * cm, 6.0 * cm)],
        [Paragraph("ANTES", styles["CapDP"]), Paragraph("DEPOIS", styles["CapDP"])],
    ], colWidths=[8.1 * cm, 8.1 * cm])
    t.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, 0), 0.3, BORDER),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    return [Paragraph(titulo, styles["H1DP"]), t, Spacer(1, 0.25 * cm)]


def gerar() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    story = [
        Spacer(1, 1.6 * cm),
        Paragraph("Doce Pedido", styles["CapaDP"]),
        Paragraph("Documentação Consolidada - apoio visual à PIT II", styles["SubDP"]),
        figura(EVIDENCIAS / "01-home-desktop.png", 16.2 * cm, 8.5 * cm),
        Spacer(1, 0.25 * cm),
        Paragraph(f"Aplicação publicada: {APP}", styles["SubDP"]),
        Paragraph(f"Repositório: {REPO}", styles["SubDP"]),
        PageBreak(),
        Paragraph("1. Situação Acadêmica", styles["H1DP"]),
        tabela([
            ["Componente", "Situação"],
            ["Escopo, requisitos, UML, IHC e banco", "Concluídos"],
            ["Front-end e back-end", "Implementados"],
            ["Testes automatizados", "261/261 aprovados"],
            ["Cinco avaliações externas", "Concluídas"],
            ["Correções e reteste", "Concluídos"],
            ["Evidências finais/complementares", "19 arquivos"],
            ["Evidências históricas", "8 arquivos"],
            ["Documento oficial em PDF", "Concluído"],
            ["Vídeos da entrega", "Concluídos"],
            ["Publicação", "Concluída"],
        ], [10.5 * cm, 5.5 * cm]),
        Spacer(1, 0.4 * cm),
        Paragraph("O documento oficial da PIT II está em documentacao/06-PIT-2/, inclusive em PDF. Este arquivo é apenas uma visão consolidada de apoio à avaliação.", styles["BodyDP"]),
        PageBreak(),
        Paragraph("2. Evidências da Versão Final", styles["H1DP"]),
        tabela([
            ["Área", "Arquivo"],
            ["Home mobile", "02-home-mobile.png"],
            ["Catálogo", "03-catalogo-filtros.png"],
            ["Produto", "04-produto.png"],
            ["Minha Conta", "07-minha-conta.png"],
            ["Revisão do pedido", "18-revisar-pedido.jpeg"],
            ["Offline", "12-offline.png"],
            ["FAQ / Modo Escuro", "13-faq-dark.png"],
            ["Segurança", "16-seguranca.png"],
            ["Padronização textual", "19-padronizacao-textual.png"],
        ], [8 * cm, 8 * cm]),
        PageBreak(),
    ]

    pares = [
        ("01-offline-antes.png", "12-offline.png", "3. Offline - Antes e Depois"),
        ("02-catalogo-antes.png", "03-catalogo-filtros.png", "4. Catálogo - Antes e Depois"),
        ("03-produto-antes.png", "04-produto.png", "5. Produto - Antes e Depois"),
        ("04-faq-antes.png", "13-faq-dark.png", "6. FAQ - Antes e Depois"),
        ("05-home-mobile-antes.png", "02-home-mobile.png", "7. Home Mobile - Antes e Depois"),
        ("07-finalizacao-direta-antes.jpeg", "18-revisar-pedido.jpeg", "8. Fluxo de Compra - Antes e Depois"),
        ("08-padronizacao-textual-antes.png", "19-padronizacao-textual.png", "9. Padronização Textual - Antes e Depois"),
    ]
    for antes, depois, titulo in pares:
        story.extend(par_imagens(antes, depois, titulo))
        story.append(PageBreak())

    story += [
        Paragraph("10. Qualidade", styles["H1DP"]),
        Paragraph("A documentação de testes e qualidade está em documentacao/03-TESTES-E-QUALIDADE/. O laudo relaciona os cinco participantes, os dez IDs de correção, o reteste e as evidências correspondentes.", styles["BodyDP"]),
        tabela([
            ["Verificação", "Resultado"],
            ["Pytest", "261/261 aprovados"],
            ["Ruff", "Aprovado"],
            ["Bandit", "Aprovado"],
            ["pip-audit", "Sem vulnerabilidades conhecidas"],
            ["pip check", "Sem dependências quebradas"],
        ], [8 * cm, 8 * cm]),
    ]

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=1.5 * cm, leftMargin=1.5 * cm, topMargin=1.4 * cm, bottomMargin=1.4 * cm)
    doc.build(story)
    return OUT


if __name__ == "__main__":
    print(gerar())
