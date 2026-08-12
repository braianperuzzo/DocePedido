"""Valida os artefatos UML formais usados na entrega acadêmica atual."""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PLANEJAMENTO = RAIZ / "documentacao" / "01-PLANEJAMENTO-E-MODELAGEM"
PASTA = PLANEJAMENTO / "diagramas"

DIAGRAMAS: dict[str, tuple[str, ...]] = {
    "01-casos-de-uso.puml": (
        "@startuml",
        "@enduml",
        "actor Visitante",
        "actor Cliente",
        'rectangle "Doce Pedido"',
        "usecase",
        "<<include>>",
        "<<extend>>",
        "--|>",
    ),
    "02-classes.puml": (
        "@startuml",
        "@enduml",
        "class Cliente",
        "class Categoria",
        "class Produto",
        "class Endereco",
        "class Favorito",
        "class Pedido",
        "class ItemPedido",
        "class DetalhePedido",
        "class AlteracaoConta",
        "class SegurancaConta",
        "class DispositivoConfiavel",
        '"1" -- "0..*"',
        "*--",
    ),
    "03-sequencia-finalizacao-pedido.puml": (
        "@startuml",
        "@enduml",
        "actor Cliente",
        "boundary",
        "control",
        "database",
        "alt",
        "opt",
        "POST /pedidos/confirmar",
    ),
    "04-atividade-compra.puml": (
        "@startuml",
        "@enduml",
        "start",
        "if (",
        "while (",
        "stop",
    ),
    "05-componentes-mvc.puml": (
        "@startuml",
        "@enduml",
        "component",
        "database",
        "cloud",
        "Modelos SQLAlchemy",
        "Controladores / Blueprints",
        "Templates Jinja",
    ),
}

MODELOS_ESPERADOS = {
    "AlteracaoConta": "alteracao_conta.py",
    "Categoria": "categoria.py",
    "Cliente": "cliente.py",
    "DetalhePedido": "detalhe_pedido.py",
    "Endereco": "endereco.py",
    "Favorito": "favorito.py",
    "ItemPedido": "item_pedido.py",
    "Pedido": "pedido.py",
    "Produto": "produto.py",
    "SegurancaConta": "seguranca.py",
    "DispositivoConfiavel": "seguranca.py",
}


def main() -> int:
    erros: list[str] = []

    for arquivo, tokens in DIAGRAMAS.items():
        caminho = PASTA / arquivo
        if not caminho.exists():
            erros.append(f"diagrama ausente: {caminho.relative_to(RAIZ)}")
            continue

        texto = caminho.read_text(encoding="utf-8")
        if texto.count("@startuml") != 1 or texto.count("@enduml") != 1:
            erros.append(f"{arquivo}: deve possuir um único @startuml/@enduml")

        for token in tokens:
            if token not in texto:
                erros.append(f"{arquivo}: elemento UML esperado ausente: {token}")

    diagrama_classes = PASTA / "02-classes.puml"
    if diagrama_classes.exists():
        texto_classes = diagrama_classes.read_text(encoding="utf-8")
        pasta_modelos = RAIZ / "aplicacao" / "modelos"
        for classe, arquivo_modelo in MODELOS_ESPERADOS.items():
            if f"class {classe}" not in texto_classes:
                erros.append(f"classe persistente não representada na UML: {classe}")
            if not (pasta_modelos / arquivo_modelo).exists():
                erros.append(f"arquivo do modelo não encontrado: aplicacao/modelos/{arquivo_modelo}")

    referencias = [
        PLANEJAMENTO / "MODELAGEM_UML.md",
        PASTA / "README.md",
    ]
    for referencia in referencias:
        if not referencia.exists():
            erros.append(f"documentação UML ausente: {referencia.relative_to(RAIZ)}")

    if erros:
        print(f"Validação UML falhou com {len(erros)} problema(s):")
        for item in erros:
            print(f"- {item}")
        return 1

    print("Validação UML aprovada.")
    print(f"- {len(DIAGRAMAS)} diagramas PlantUML formais: OK")
    print("- casos de uso com atores/include/extend/generalização: OK")
    print("- classes persistentes e multiplicidades: OK")
    print("- sequência com alternativas e opções: OK")
    print("- atividade com decisões e repetição: OK")
    print("- componentes/MVC: OK")
    print("- documentação MODELAGEM_UML.md e índice de diagramas: OK")
    print("- rastreabilidade mínima com modelos reais: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
