# Escopo e Requisitos

## Objetivo

O Doce Pedido representa uma loja virtual de cupcakes voltada à navegação de produtos e ao registro de pedidos. A solução foi construída como aplicação web responsiva e reúne os fluxos necessários para consulta, autenticação, compra e acompanhamento pelo cliente.

## Atores

- **Visitante:** consulta conteúdos públicos, produtos, busca e informações institucionais.
- **Cliente:** utiliza conta autenticada, endereços, favoritos, carrinho, pedidos e recursos de segurança.
- **Serviços externos:** participam de consultas de endereço e do envio de mensagens transacionais.

## Requisitos Funcionais

| Código | Requisito |
| --- | --- |
| RF01 | apresentar Home, catálogo, busca, filtros e detalhes de produtos |
| RF02 | permitir cadastro de cliente com CPF, e-mail e senha |
| RF03 | confirmar cadastro e alterações sensíveis por e-mail |
| RF04 | permitir login, logout e recuperação de senha |
| RF05 | disponibilizar edição de dados pessoais, preservando o CPF cadastrado |
| RF06 | permitir cadastro, edição, exclusão e seleção de endereços |
| RF07 | permitir inclusão e remoção de produtos favoritos |
| RF08 | permitir inclusão de produtos no carrinho e alteração de quantidades |
| RF09 | aplicar o cupom `BEMVINDO` conforme a regra de primeira compra |
| RF10 | revisar pedido com entrega ou retirada e endereço quando aplicável |
| RF11 | registrar Pagamento Presencial como forma ativa |
| RF12 | confirmar e persistir o pedido, seus itens, valores e dados de recebimento |
| RF13 | apresentar histórico e detalhes em Meus Pedidos |
| RF14 | enviar mensagens transacionais dos fluxos previstos |
| RF15 | permitir exclusão da conta com tratamento dos dados vinculados |

## Requisitos Não Funcionais

- interface responsiva para desktop, tablet e celular;
- funcionamento nos modos claro e escuro;
- validações no cliente e no servidor;
- proteção CSRF, controle de acesso e limitação de requisições em pontos sensíveis;
- armazenamento de senhas por hash;
- cookies e cabeçalhos de segurança compatíveis com o ambiente publicado;
- PWA com manifesto, Service Worker e fallback offline para conteúdo público;
- mensagens de erro sem exposição de credenciais ou detalhes internos;
- persistência relacional com SQLAlchemy e SQLite;
- rastreabilidade entre requisitos, implementação, testes e evidências.

## Regras de Negócio Relevantes

- o CPF é obrigatório no cadastro e não é editável depois da criação da conta;
- o cupom `BEMVINDO` concede 10% na primeira compra elegível, associada ao CPF;
- a quantidade do carrinho respeita disponibilidade e limites da aplicação;
- a revisão do pedido revalida os dados antes da persistência;
- entrega utiliza endereço salvo; retirada na loja não exige endereço de entrega;
- Pix e cartão on-line aparecem como opções indisponíveis, sem processamento financeiro;
- o pedido confirmado permanece registrado mesmo quando uma mensagem transacional posterior apresenta falha de transporte.

## Limites do Escopo

Não integram a versão final pagamento on-line, cálculo dinâmico de frete, painel administrativo, integração com transportadora ou notificações push.
