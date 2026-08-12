# 3 - UML e Arquitetura Revisadas

## 3.1 Perspectivas da modelagem

A modelagem foi atualizada para representar a solução final em quatro perspectivas:

1. funcional, por atores e casos de uso;
3. estrutural, por classes e relacionamentos persistidos;
3. comportamental, pelos fluxos de autenticação e compra;
4. arquitetural, pela separação de modelos, controladores, serviços, templates e recursos estáticos.

## 3.2 Casos de uso principais

```mermaid
flowchart LR
    V((Visitante))
    C((Cliente))
    E[[Serviço de e-mail]]
    L[[CEP / localidades]]

    UC1([Consultar catálogo])
    UC2([Pesquisar produtos])
    UC3([Montar carrinho])
    UC4([Criar conta])
    UC5([Entrar na conta])
    UC6([Gerenciar dados e senha])
    UC7([Gerenciar endereços])
    UC8([Gerenciar favoritos])
    UC9([Finalizar pedido])
    UC10([Acompanhar pedidos])
    UC11([Excluir conta])

    V --> UC1
    V --> UC2
    V --> UC3
    V --> UC4
    V --> UC5
    C --> UC1
    C --> UC2
    C --> UC3
    C --> UC6
    C --> UC7
    C --> UC8
    C --> UC9
    C --> UC10
    C --> UC11
    UC4 -. confirmação .-> E
    UC6 -. confirmação .-> E
    UC9 -. confirmação .-> E
    UC11 -. confirmação .-> E
    UC7 -. consulta .-> L
```

## 3.3 Classes do domínio

| Classe | Responsabilidade |
| --- | --- |
| Cliente | Conta, autenticação e vínculo com pedidos e dados pessoais |
| Categoria | Organização do catálogo |
| Produto | Item comercializado, preço, estoque e imagem |
| Endereco | Endereço salvo do cliente |
| Favorito | Associação entre cliente e produto favorito |
| Pedido | Compra confirmada e valor final |
| ItemPedido | Produto, quantidade e valores históricos do pedido |
| DetalhePedido | Recebimento, pagamento, frete, cupom, desconto e endereço usado |
| AlteracaoConta | Solicitação temporária de alteração ou exclusão |
| SegurancaConta | Referência de troca periódica de senha |
| DispositivoConfiavel | Navegador aprovado para a conta |

```mermaid
classDiagram
    Categoria "1" --> "0..*" Produto : agrupa
    Cliente "1" --> "0..*" Endereco : possui
    Cliente "1" --> "0..*" Favorito : marca
    Produto "1" --> "0..*" Favorito : recebe
    Cliente "1" --> "0..*" Pedido : realiza
    Pedido "1" --> "1..*" ItemPedido : contem
    Produto "1" --> "0..*" ItemPedido : referencia
    Pedido "1" --> "0..1" DetalhePedido : registra
    Cliente "1" --> "0..*" AlteracaoConta : solicita
    Cliente "1" --> "0..1" SegurancaConta : possui
    Cliente "1" --> "0..*" DispositivoConfiavel : aprova
```

## 3.4 Sequência da finalização do pedido

```mermaid
sequenceDiagram
    actor Cliente
    participant Web as Interface Web
    participant Pedidos as Controlador de Pedidos
    participant Cupom as Serviço de Cupons
    participant Banco as SQLite / SQLAlchemy
    participant Email as Serviço de E-mail

    Cliente->>Web: abre Revisar Pedido
    Web->>Pedidos: solicita resumo
    Pedidos->>Banco: lê carrinho e endereços
    Pedidos->>Cupom: valida cupom, quando houver
    Cupom->>Banco: consulta histórico do CPF
    Pedidos-->>Web: exibe subtotal, desconto e total
    Cliente->>Web: confirma recebimento e pagamento
    Web->>Pedidos: envia confirmação
    Pedidos->>Banco: revalida produtos e estoque
    Pedidos->>Cupom: revalida elegibilidade
    Pedidos->>Banco: grava pedido, itens e detalhes
    Pedidos->>Banco: reduz estoque e confirma transação
    Pedidos->>Email: envia confirmação
    Pedidos-->>Web: mostra pedido confirmado
```

## 3.5 Atividade principal de compra

```mermaid
flowchart TD
    A[Adicionar produtos ao carrinho] --> B[Abrir Revisar Pedido]
    B --> C{Autenticado?}
    C -- Não --> D[Login ou cadastro]
    D --> B
    C -- Sim --> E[Selecionar entrega ou retirada]
    E --> F{Entrega?}
    F -- Sim --> G[Selecionar endereço salvo]
    F -- Não --> H[Seguir sem endereço de entrega]
    G --> I[Selecionar pagamento presencial]
    H --> I
    I --> J[Conferir itens, desconto e total]
    J --> K{Dados válidos e estoque disponível?}
    K -- Não --> L[Exibir mensagem e manter revisão]
    L --> J
    K -- Sim --> M[Gravar pedido e reduzir estoque]
    M --> N[Enviar e-mail]
    N --> O[Exibir confirmação]
    O --> P[Disponibilizar em Meus Pedidos]
```

## 3.6 Arquitetura

```mermaid
flowchart LR
    Browser[Navegador] --> Controller[Controladores / Blueprints]
    Controller --> Service[Serviços]
    Controller --> Model[Modelos SQLAlchemy]
    Service --> Model
    Model --> DB[(SQLite)]
    Controller --> View[Templates Jinja]
    View --> Browser
    Service --> Mail[SMTP]
    Service --> External[CEP / localidades]
```

| Camada | Local no projeto | Responsabilidade |
| --- | --- | --- |
| Model | `aplicacao/modelos/` | entidades e relacionamentos persistidos |
| Controller | `aplicacao/controladores/` | rotas, validações HTTP e coordenação dos fluxos |
| View | `aplicacao/templates/` | páginas Jinja apresentadas ao usuário |
| Service | `aplicacao/servicos/` | e-mail, tokens, cupom e operações compartilhadas |
| Static | `aplicacao/static/` | CSS, JavaScript, imagens, manifesto e Service Worker |
