# Laudo de Qualidade

- **Período da validação externa:** de 10/08/2026 a 13/08/2026
- **Solução:** Doce Pedido
- **Ambiente final:** https://docepedido.pythonanywhere.com/
- **Resultado:** aprovado após correções e reteste

A qualidade da solução Doce Pedido foi avaliada por cinco participantes, contemplando navegação, responsividade, Modo Escuro, PWA e funcionamento offline, cadastro e autenticação, área do cliente, catálogo, carrinho e processo de finalização de pedidos.

Durante as avaliações foram identificados pontos de melhoria relacionados principalmente à interface, responsividade, conteúdo institucional, autonomia da conta do cliente, segurança percebida, fluxo de compra e padronização textual. Os apontamentos considerados pertinentes foram corrigidos e posteriormente submetidos a novo teste.

## Consolidação das Avaliações Externas

| Avaliador / Data | Foco e o que funcionou | Problemas / Sugestões | Correções e IDs | Não testado / Fora do escopo |
| --- | --- | --- | --- | --- |
| Reberson Faria Gomes - 10/08/2026 | Offline, PWA, Modo Escuro e mobile. O PWA funcionou conforme esperado. | Excesso de informações e retomada pouco clara no offline; inconsistências de contraste no Modo Escuro; campos e componentes com problemas em telas menores. | Offline simplificado, nova tentativa destacada, fallback reforçado, mobile reorganizado e Modo Escuro revisado. **IDs 01, 02 e 03.** | Demais funcionalidades fora do foco do teste. |
| Fernanda de Souza - 11/08/2026 | Estrutura, conteúdo e navegação. Sem falhas funcionais relevantes na estrutura principal. | Poucas informações de contato, conteúdo institucional limitado e poucas informações de segurança e tratamento de dados. | Ampliação de Sobre, rodapé, cookies, privacidade e segurança. **ID 04.** | Fluxos transacionais e aspectos técnicos não aprofundados. |
| Matheus Moreira - 12/08/2026 | Cadastro, login, logout, Minha Conta, mensagens e compra. Funções básicas existentes puderam ser utilizadas. | Falta de Editar Dados, exclusão, favoritos, confirmações adicionais e etapa completa de revisão antes da compra. | Edição, exclusão, favoritos, endereços, validações por e-mail, validação de novos dispositivos e revisão completa do pedido. **IDs 05, 06 e 07.** | 2FA permanente não implementado; pagamento on-line fora do escopo; Pagamento Presencial ativo. |
| Gustavo Coelho - 13/08/2026 | Home, FAQ, catálogo, produtos, carrinho e compra. A estrutura geral permitia percorrer a aplicação. | Quebra visual na FAQ, falta de filtros, Home e cards grandes e continuidade incompleta para detalhes de produtos. | FAQ reestruturada, filtros, ordenação, compactação e navegação para detalhes ampliada. **IDs 08 e 09.** | Regras técnicas de segurança da conta não aprofundadas. |
| Gabriela de Lima - 13/08/2026 | Avaliação ponta a ponta dos principais fluxos. Não foram apontadas falhas funcionais relevantes. | Diferenças de terminologia, títulos, capitalização e apresentação entre páginas e mensagens. | Revisão textual geral de títulos, rótulos, mensagens e conteúdos. **ID 10.** | Nenhuma funcionalidade relevante indicada como não testada dentro do escopo disponível. |

## Problemas, Correções e Reteste

| ID | Problema Identificado | Correção Realizada | Resultado |
| --- | --- | --- | --- |
| 01 | Tela offline com excesso de informações e retomada pouco clara. | Conteúdo simplificado, reorganização da tela e inclusão de uma ação clara para tentar novamente. | Aprovado no reteste |
| 02 | Algumas áreas apresentavam contraste e visibilidade inadequados no Modo Escuro. | Revisão das superfícies, componentes e contraste do tema escuro. | Aprovado no reteste |
| 03 | Quebras de layout e baixa responsividade em dispositivos móveis. | Menu, grids, formulários, espaçamentos e tamanhos foram reorganizados para telas menores. | Aprovado no reteste |
| 04 | Poucas informações institucionais, de privacidade e segurança. | Ampliação da página Sobre, rodapé, Política de Privacidade, Cookies e conteúdo de segurança. | Aprovado no reteste |
| 05 | Área do cliente com pouca autonomia. | Foram adicionados edição de dados, gerenciamento de endereços, favoritos e exclusão da conta. | Aprovado no reteste |
| 06 | Ações sensíveis possuíam poucas confirmações adicionais. | Foram implementadas confirmações por e-mail, validação de dispositivo e mensagens integradas ao site. | Aprovado no reteste |
| 07 | Processo de compra possuía finalização muito direta. | Foi criada uma etapa completa de revisão do pedido, com recebimento, endereço, pagamento, cupom, resumo e confirmação. | Aprovado no reteste |
| 08 | FAQ apresentava problemas visuais, principalmente em determinadas resoluções e no tema escuro. | FAQ reestruturada e revisada para desktop, mobile, teclado e Modo Escuro. | Aprovado no reteste |
| 09 | Catálogo e página de produto apresentavam elementos grandes e pouca facilidade de filtragem. | Foram adicionados filtros e ordenação, além da compactação de cards, revisão das páginas de produto e ampliação da navegação para detalhes. | Aprovado no reteste |
| 10 | Existiam diferenças de terminologia, títulos e capitalização entre páginas e mensagens. | Foi realizada revisão textual geral, com padronização de títulos, rótulos, mensagens e conteúdos apresentados ao usuário. | Aprovado no reteste |

## Evidências do Laudo

As evidências estão organizadas em [`EVIDENCIAS_ANTES_DEPOIS.md`](EVIDENCIAS_ANTES_DEPOIS.md). O documento relaciona os IDs do laudo às capturas anteriores efetivamente preservadas e às evidências da versão corrigida.

Quando não existe uma captura histórica específica, essa condição é registrada explicitamente. Não foram produzidas imagens artificiais para simular bugs antigos.

O ID 10 utiliza um comparativo real extraído da captura histórica da FAQ e da versão revisada, demonstrando exemplos de padronização como **"Perguntas Frequentes" → "Perguntas frequentes"** e **"Um Cookie para Acompanhar seu Cupcake?" → "Preferências de cookies"**.

## Reteste

Após a aplicação das correções, os cinco participantes realizaram um novo ciclo de avaliação dos fluxos testados. No reteste não foram relatados novos problemas funcionais ou sugestões adicionais relevantes.

## Resultado Técnico

A versão final registrou **261 testes automatizados aprovados em 261 execuções**, além das verificações de dependências, segurança, código Python, JavaScript e inicialização da aplicação.

## Conclusão

Considerando as avaliações externas, as correções realizadas, o reteste e as verificações técnicas, a versão final da solução foi considerada aprovada para a entrega acadêmica.
