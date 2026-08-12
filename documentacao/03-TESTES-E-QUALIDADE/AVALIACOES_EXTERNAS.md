# Avaliações Externas

As avaliações externas da solução Doce Pedido foram realizadas por cinco participantes, distribuindo os testes entre diferentes áreas da aplicação.

O objetivo foi validar o funcionamento da solução sob diferentes perspectivas de uso, registrar problemas e sugestões, realizar as correções pertinentes e posteriormente repetir os fluxos avaliados.

As informações abaixo correspondem às avaliações registradas no documento oficial da PIT II e estão alinhadas aos IDs do Laudo de Qualidade.

## Quadro de Consolidação

| Avaliador / Data | Foco | O que Funcionou | Principais Apontamentos | IDs | Não Testado / Fora do Escopo |
| --- | --- | --- | --- | --- | --- |
| Reberson Faria Gomes - 10/08/2026 | Offline, PWA, Modo Escuro e mobile | PWA funcionou conforme esperado | Offline denso, retomada pouco clara, inconsistências no tema escuro e problemas mobile | 01, 02 e 03 | Demais funcionalidades fora do foco |
| Fernanda de Souza - 11/08/2026 | Estrutura, conteúdo e navegação | Estrutura principal sem falhas funcionais relevantes | Pouco conteúdo institucional, contato, segurança e tratamento de dados | 04 | Fluxos transacionais e técnicos não aprofundados |
| Matheus Moreira - 12/08/2026 | Cadastro, autenticação, Minha Conta, mensagens e compra | Funções básicas existentes utilizáveis | Baixa autonomia da conta, poucas confirmações e finalização direta | 05, 06 e 07 | 2FA permanente não implementado e pagamento on-line fora do escopo |
| Gustavo Coelho - 13/08/2026 | Home, FAQ, catálogo, produtos, carrinho e compra | Navegação geral possível | FAQ quebrada, ausência de filtros, elementos grandes e continuidade incompleta | 08 e 09 | Segurança técnica da conta não aprofundada |
| Gabriela de Lima - 13/08/2026 | Avaliação ponta a ponta | Sem falhas funcionais relevantes | Inconsistências de terminologia, títulos e capitalização | 10 | Nenhuma funcionalidade relevante indicada como não testada |

---

## 1. Reberson Faria Gomes

**Data do teste:** 10/08/2026

### O que testou e funcionou

Avaliou o funcionamento em modo offline, a instalação e utilização como PWA, o Modo Escuro e a experiência em dispositivos móveis. O PWA funcionou conforme esperado durante a avaliação.

### O que testou e não funcionou - O que deve ser corrigido

No modo offline, apontou excesso de informações na tela e dificuldade para retomar a navegação quando a conexão retornava. No Modo Escuro, identificou áreas em que o tema não era aplicado corretamente e elementos com baixa visibilidade. Na experiência mobile, encontrou campos quebrados, elementos que não apareciam ou não respondiam corretamente, baixa responsividade em alguns tamanhos de tela e sensação de página pesada.

Como resultado da avaliação:

- a tela offline foi simplificada;
- foi incluída uma ação clara de nova tentativa;
- o fallback offline foi reforçado;
- os componentes mobile foram reorganizados;
- o Modo Escuro foi revisado.

### Funcionalidade não testada

A avaliação foi concentrada em offline, PWA, Modo Escuro e responsividade/mobile. As demais funcionalidades não fizeram parte do foco deste teste.

### Relação com o Laudo de Qualidade

Apontamentos relacionados aos IDs **01, 02 e 03**. **Reteste:** aprovado após as correções.

---

## 2. Fernanda de Souza

**Data do teste:** 11/08/2026

### O que testou e funcionou

Avaliou a estrutura geral do site, a organização das informações, os textos apresentados, as páginas disponíveis e a navegação entre as áreas. Não foram apontadas falhas funcionais relevantes na navegação ou na estrutura principal.

### O que testou e não funcionou - O que deve ser corrigido

Identificou que o site apresentava poucas informações de contato, conteúdo limitado sobre a loja e poucas informações relacionadas à segurança e ao tratamento de dados.

Como resultado da avaliação:

- o conteúdo institucional foi ampliado;
- o rodapé foi preparado para apresentação das informações da loja;
- foram adicionados aviso e preferências de cookies;
- foram ampliados os conteúdos de privacidade e segurança.

### Funcionalidade não testada

O teste teve foco na estrutura, conteúdo e navegação, sem aprofundamento nos fluxos transacionais e técnicos da aplicação.

### Relação com o Laudo de Qualidade

Apontamento relacionado ao ID **04**. **Reteste:** aprovado após as correções.

---

## 3. Matheus Moreira

**Data do teste:** 12/08/2026

### O que testou e funcionou

Percorreu cadastro, login, logout, Minha Conta, mensagens e processo de compra. Conseguiu utilizar as funções básicas existentes, mas identificou pontos relacionados à autonomia da conta, segurança percebida e continuidade da compra.

### O que testou e não funcionou - O que deve ser corrigido

Relatou falta de recursos para Editar Dados, excluir a conta e manter favoritos. Também apontou necessidade de confirmação adicional em ações sensíveis e de uma etapa mais completa antes de finalizar a compra.

Como resultado da avaliação foram implementados:

- edição de dados;
- exclusão de conta;
- favoritos;
- gerenciamento de endereços;
- validações por e-mail;
- validação de novos dispositivos;
- tela de revisão do pedido;
- seleção de endereço;
- entrega ou retirada;
- apresentação da forma de pagamento;
- cupom;
- resumo e confirmação do pedido;
- registro em Meus Pedidos.

### Funcionalidade não testada, faltou ou não foi implementada

A autenticação em duas etapas permanente não foi implementada. O pagamento on-line também não faz parte do escopo final. Pix e cartão permanecem indisponíveis, com Pagamento Presencial como opção ativa.

### Relação com o Laudo de Qualidade

Apontamentos relacionados aos IDs **05, 06 e 07**. **Reteste:** aprovado após as correções.

---

## 4. Gustavo Coelho

**Data do teste:** 13/08/2026

### O que testou e funcionou

Realizou navegação ampla pela Home, FAQ, catálogo, produtos, carrinho e fluxo de compra. A estrutura geral permitia percorrer a aplicação, mas havia pontos de usabilidade e proporção visual.

### O que testou e não funcionou - O que deve ser corrigido

Identificou quebra visual na FAQ, falta de filtros, Home e cards excessivamente grandes e continuidade incompleta ao abrir produtos em etapas posteriores.

Como resultado da avaliação:

- a FAQ foi reestruturada;
- o catálogo recebeu filtros e ordenação;
- os cards foram compactados;
- as páginas de produto foram reorganizadas;
- a navegação para detalhes do produto foi ampliada.

### Funcionalidade não testada

O teste teve foco na navegação e experiência visual, sem aprofundamento específico nas regras técnicas de segurança da conta.

### Relação com o Laudo de Qualidade

Apontamentos relacionados aos IDs **08 e 09**. **Reteste:** aprovado após as correções.

---

## 5. Gabriela de Lima

**Data do teste:** 13/08/2026

### O que testou e funcionou

Realizou uma avaliação geral de ponta a ponta, incluindo navegação institucional, catálogo, busca, produto, cadastro, autenticação, Minha Conta, favoritos, carrinho, revisão e finalização, Meus Pedidos, Modo Escuro e uso geral da interface. Não foram apontadas falhas funcionais relevantes.

### O que testou e não funcionou - O que deve ser corrigido

O principal apontamento foi falta de padronização em alguns textos, com diferenças de termos, capitalização e apresentação entre páginas e mensagens.

Foi realizada uma conferência textual geral da aplicação, incluindo títulos, rótulos, mensagens e conteúdos apresentados ao usuário.

### Funcionalidade não testada

Não foi indicada funcionalidade relevante como não testada dentro do escopo disponível.

### Relação com o Laudo de Qualidade

Apontamento relacionado ao ID **10**. **Reteste:** aprovado após a revisão.

---

# Reteste

Após a aplicação das correções, os cinco participantes realizaram um novo ciclo de avaliação dos fluxos testados. No reteste não foram relatados novos problemas funcionais ou sugestões adicionais relevantes.

Como verificação complementar, a versão final também foi submetida à bateria automatizada de testes e às verificações técnicas do projeto. Foram executados **261 testes automatizados, todos aprovados**, além das verificações de dependências, segurança, código Python, JavaScript e inicialização da aplicação.

# Evidências

As evidências visuais estão documentadas em [`EVIDENCIAS_ANTES_DEPOIS.md`](EVIDENCIAS_ANTES_DEPOIS.md).
