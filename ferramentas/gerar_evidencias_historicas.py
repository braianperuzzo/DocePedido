"""Valida as evidências históricas reais e regenera o índice da pasta.

Este utilitário NÃO recria bugs nem fabrica imagens. As evidências históricas devem
ser capturas reais preservadas durante o desenvolvimento ou extratos de evidências
reais já presentes no documento oficial da PIT II.
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
HISTORICO = (
    RAIZ
    / "documentacao"
    / "01-PLANEJAMENTO-E-MODELAGEM"
    / "evidencias"
    / "historico"
)

EVIDENCIAS = [
    ("01-offline-antes.png", "tela offline antes da simplificação"),
    ("02-catalogo-antes.png", "catálogo antes da compactação e dos filtros"),
    ("03-produto-antes.png", "detalhe do produto antes da reorganização"),
    ("04-faq-antes.png", "FAQ antes da revisão de layout, contraste e texto"),
    ("05-home-mobile-antes.png", "Home mobile antes da reorganização responsiva"),
    ("06-rodape-antes.png", "rodapé/conteúdo institucional anterior"),
    ("07-finalizacao-direta-antes.jpeg", "fluxo anterior chegando diretamente à finalização"),
    ("08-padronizacao-textual-antes.png", "recorte real anterior à padronização textual"),
]


def main() -> int:
    HISTORICO.mkdir(parents=True, exist_ok=True)
    ausentes = [nome for nome, _ in EVIDENCIAS if not (HISTORICO / nome).exists()]
    if ausentes:
        print("Não é seguro recriar evidências históricas automaticamente.")
        print("Arquivos reais ainda ausentes:")
        for nome in ausentes:
            print(f"- {nome}")
        return 1

    linhas = [
        "# Evidências Anteriores",
        "",
        "As imagens desta pasta preservam estados anteriores reais da interface ou extratos de evidências históricas já presentes no documento oficial da PIT II.",
        "",
        "| Arquivo | Comparação |",
        "| --- | --- |",
    ]
    linhas.extend(f"| `{nome}` | {descricao} |" for nome, descricao in EVIDENCIAS)
    linhas += [
        "",
        "## Integridade",
        "",
        "Nenhuma imagem desta pasta é criada artificialmente para simular bugs. Os arquivos são mantidos apenas quando existe evidência real de origem.",
        "",
        "A matriz completa está em [`../../../03-TESTES-E-QUALIDADE/EVIDENCIAS_ANTES_DEPOIS.md`](../../../03-TESTES-E-QUALIDADE/EVIDENCIAS_ANTES_DEPOIS.md).",
        "",
    ]
    (HISTORICO / "README.md").write_text("\n".join(linhas), encoding="utf-8")
    print(f"Índice atualizado: {HISTORICO / 'README.md'}")
    print(f"Evidências históricas validadas: {len(EVIDENCIAS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
