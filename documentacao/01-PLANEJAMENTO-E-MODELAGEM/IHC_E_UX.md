# IHC e Experiência do Usuário

A interface final prioriza clareza, consistência, feedback e funcionamento previsível em diferentes tamanhos de tela.

## Organização da Navegação

- Home como ponto de entrada para catálogo e conteúdos institucionais;
- catálogo com busca, categoria, disponibilidade e ordenação;
- detalhe do produto com preço, disponibilidade, quantidade, favorito e carrinho;
- carrinho com resumo, quantidade, cupom e acesso à revisão;
- área autenticada com Minha Conta, endereços, favoritos e pedidos;
- revisão do pedido antes da confirmação;
- páginas institucionais de ajuda, privacidade, cookies e segurança.

## Mapa Conceitual de Navegação

O fluxo conceitual abaixo resume a relação entre as principais áreas da interface e os caminhos esperados do usuário:

```text
Usuário
├── Home
│   ├── Catálogo
│   │   └── Produto
│   │       └── Carrinho
│   │           └── Revisar Pedido
│   │               └── Confirmação
│   │                   └── Meus Pedidos
│   └── Conteúdo Institucional
│       ├── Sobre
│       ├── Perguntas Frequentes
│       ├── Privacidade
│       ├── Cookies
│       └── Segurança
└── Cadastro / Login
    └── Minha Conta
        ├── Editar Dados
        ├── Endereços
        ├── Favoritos
        └── Pedidos
```

Esse mapa representa a organização lógica da experiência e complementa os diagramas UML da solução.

## Critérios de IHC Aplicados

### Consistência

Cabeçalho, rodapé, botões, formulários, cartões, mensagens e títulos seguem padrões comuns entre as páginas. A redação final foi padronizada para reduzir variações de capitalização e termos equivalentes.

### Feedback

A aplicação apresenta retorno visual para ações como inclusão no carrinho, validação de formulário, confirmação de alterações, estoque insuficiente, pedido confirmado e indisponibilidade de conexão.

### Prevenção de Erro

A revisão do pedido apresenta itens, valores, recebimento, endereço e pagamento antes do fechamento. Quantidades e estoque são revalidados, opções financeiras indisponíveis permanecem desabilitadas e ações sensíveis possuem confirmação adicional.

### Responsividade e Tema

A interface se reorganiza em desktop, tablet e celular. O tema claro e o tema escuro utilizam superfícies e contrastes próprios, preservando legibilidade e estados de interação.

### Acessibilidade Presente

- estrutura semântica de títulos e regiões;
- rótulos e estados acessíveis em controles interativos;
- foco visível;
- navegação por teclado nos componentes aplicáveis;
- textos alternativos em imagens informativas;
- suporte a redução de movimento quando relevante.

## Protótipo e Evolução da Interface

A versão implementada corresponde à evolução do protótipo planejado na PIT I. Durante o desenvolvimento e a validação externa, a interface foi refinada com base no comportamento real da aplicação e no retorno dos avaliadores.

As principais evoluções incluem reorganização de componentes mobile, melhoria do Modo Escuro, simplificação do offline, ampliação da área do cliente, inclusão da etapa Revisar Pedido, revisão da FAQ, filtros e ordenação no catálogo, compactação de cards e padronização textual.

Os comparativos Antes × Depois preservados nas evidências documentam essa evolução sem reconstruir telas históricas inexistentes.

## Evolução Após Validação Externa

Os principais pontos revisados foram densidade da tela offline, contraste em Modo Escuro, comportamento mobile, conteúdo institucional, autonomia da área do cliente, revisão do pedido, FAQ, dimensão de cards e padronização textual.

## Evidências

O conjunto atual possui **19 evidências finais/complementares** em [`evidencias/`](evidencias/README.md) e **8 evidências históricas** em [`evidencias/historico/`](evidencias/historico/README.md). Capturas adicionais utilizadas no documento oficial permanecem organizadas em `evidencias/documento-oficial/`.
