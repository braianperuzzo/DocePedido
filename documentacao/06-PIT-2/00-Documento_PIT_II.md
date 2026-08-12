# PIT II - Doce Pedido

Olá, estudante.

A seguir, você dará continuidade ao desenvolvimento da sua solução através dos campos específicos para a resolução dos 3 desafios propostos, lembrando que eles se complementam.

**Nome:** Braian Peruzzo  
**RGM:** 34602933

## Documentação

Revisite a documentação do projeto desenvolvido na PIT I, faça as atualizações e melhorias necessárias de acordo com os pontos explicitados no material teórico. Ao terminar os ajustes, suba a documentação em um repositório GIT.

**Link do repositório:**  
https://github.com/braianperuzzo/DocePedido/tree/main/documentacao/05-PIT-I

---

## Codificação

Na tabela a seguir estão as informações referentes ao desenvolvimento do código do front-end e back-end.

| Campo | Informação |
| --- | --- |
| **Linguagem do Back-end** | Python com Flask |
| **Banco de Dados** | SQLite, utilizando SQLAlchemy como ORM |
| **Hospedagem** | PythonAnywhere |
| **Plataforma** | Web, aplicação web responsiva |
| **Modo de Codificação** | **( X ) Tradicional**<br>( ) Low-code<br>( ) No-code |
| **Link do repositório no GitHub com os códigos abertos** | https://github.com/braianperuzzo/DocePedido |
| **Link da solução em funcionamento** | https://docepedido.pythonanywhere.com/ |
| **Link do vídeo narrado (no mínimo 5 min)** | https://youtu.be/PMrJzQXpWuE |

---

# Testes da Solução

Escolha 5 colegas para testar sua aplicação e preencha a tabela a seguir com as informações obtidas.

## Reberson Faria Gomes

| Campo | Informação |
| --- | --- |
| **Nome** | Reberson Faria Gomes |
| **Data do teste** | 10/08/2026 |
| **O que testou e funcionou** | Avaliou o funcionamento em modo offline, a instalação e utilização como PWA, o Modo Escuro e a experiência em dispositivos móveis. O PWA funcionou conforme esperado durante a avaliação. |
| **O que testou e não funcionou - O que deve ser corrigido** | No modo offline, apontou excesso de informações na tela e dificuldade para retomar a navegação quando a conexão retornava. No Modo Escuro, identificou áreas em que o tema não era aplicado corretamente e elementos com baixa visibilidade. Na experiência mobile, encontrou campos quebrados, elementos que não apareciam ou não respondiam corretamente, baixa responsividade em alguns tamanhos de tela e sensação de página pesada. A tela offline foi simplificada, recebeu uma ação clara de nova tentativa, o fallback offline foi reforçado, os componentes mobile foram reorganizados e o Modo Escuro foi revisado. |
| **Funcionalidade não testada (faltou ou não foi implementada)** | A avaliação foi concentrada em offline, PWA, Modo Escuro e responsividade/mobile. As demais funcionalidades não fizeram parte do foco deste teste. |

## Fernanda de Souza

| Campo | Informação |
| --- | --- |
| **Nome** | Fernanda de Souza |
| **Data do teste** | 11/08/2026 |
| **O que testou e funcionou** | Avaliou a estrutura geral do site, a organização das informações, os textos apresentados, as páginas disponíveis e a navegação entre as áreas. Não foram apontadas falhas funcionais relevantes na navegação ou na estrutura principal. |
| **O que testou e não funcionou - O que deve ser corrigido** | Identificou que o site apresentava poucas informações de contato, conteúdo limitado sobre a loja e poucas informações relacionadas à segurança e ao tratamento de dados. O conteúdo institucional foi ampliado, o rodapé foi preparado para dados reais quando configurados e foram adicionados aviso de cookies, preferências, privacidade e segurança. |
| **Funcionalidade não testada (faltou ou não foi implementada)** | O teste teve foco na estrutura, conteúdo e navegação, sem aprofundamento nos fluxos transacionais e técnicos da aplicação. |

## Matheus Moreira

| Campo | Informação |
| --- | --- |
| **Nome** | Matheus Moreira |
| **Data do teste** | 12/08/2026 |
| **O que testou e funcionou** | Percorreu cadastro, login, logout, Minha Conta, mensagens e processo de compra. Conseguiu utilizar as funções básicas existentes, mas identificou pontos relacionados à autonomia da conta, segurança percebida e continuidade da compra. |
| **O que testou e não funcionou - O que deve ser corrigido** | Relatou falta de recursos para Editar Dados, excluir a conta e manter favoritos. Também apontou necessidade de confirmação adicional em ações sensíveis e de uma etapa mais completa antes de finalizar a compra. Foram implementados edição de dados, exclusão de conta, favoritos, gerenciamento de endereços, validações por e-mail, validação de novos dispositivos e uma tela de revisão do pedido com endereço, entrega ou retirada, pagamento, cupom, resumo, confirmação e registro em Meus Pedidos. |
| **Funcionalidade não testada (faltou ou não foi implementada)** | A autenticação em duas etapas permanente não foi implementada. O pagamento on-line também não faz parte do escopo final. Pix e cartão permanecem indisponíveis, com Pagamento Presencial como opção ativa. |

## Gustavo Coelho

| Campo | Informação |
| --- | --- |
| **Nome** | Gustavo Coelho |
| **Data do teste** | 13/08/2026 |
| **O que testou e funcionou** | Realizou navegação ampla pela Home, FAQ, catálogo, produtos, carrinho e fluxo de compra. A estrutura geral permitia percorrer a aplicação, mas havia pontos de usabilidade e proporção visual. |
| **O que testou e não funcionou - O que deve ser corrigido** | Identificou quebra visual na FAQ, falta de filtros, Home e cards excessivamente grandes e continuidade incompleta ao abrir produtos em etapas posteriores. O FAQ foi reestruturado, o catálogo recebeu filtros e ordenação, os cards e páginas de produto foram compactados e a navegação para detalhes do produto foi ampliada. |
| **Funcionalidade não testada (faltou ou não foi implementada)** | O teste teve foco na navegação e experiência visual, sem aprofundamento específico nas regras técnicas de segurança da conta. |

## Gabriela de Lima

| Campo | Informação |
| --- | --- |
| **Nome** | Gabriela de Lima |
| **Data do teste** | 13/08/2026 |
| **O que testou e funcionou** | Realizou uma avaliação geral de ponta a ponta, incluindo navegação institucional, catálogo, busca, produto, cadastro, autenticação, Minha Conta, favoritos, carrinho, revisão e finalização, Meus Pedidos, Modo Escuro e uso geral da interface. Não foram apontadas falhas funcionais relevantes. |
| **O que testou e não funcionou - O que deve ser corrigido** | O principal apontamento foi falta de padronização em alguns textos, com diferenças de termos, capitalização e apresentação entre páginas e mensagens. Foi realizada uma conferência textual geral. |
| **Funcionalidade não testada (faltou ou não foi implementada)** | Não foi indicada funcionalidade relevante como não testada dentro do escopo disponível. |

---

# Laudo de Qualidade

Insira a seguir o laudo de qualidade do sistema, apontando os erros e as correções. Não esqueça de coletar as evidências para inseri-las no laudo.

A qualidade da solução Doce Pedido foi avaliada por cinco participantes entre 10/08/2026 e 13/08/2026, contemplando diferentes áreas da aplicação, como navegação, responsividade, Modo Escuro, PWA e funcionamento offline, cadastro e autenticação, área do cliente, catálogo, carrinho e processo de finalização de pedidos.

Durante as avaliações foram identificados pontos de melhoria relacionados principalmente à interface, responsividade, conteúdo institucional, autonomia da conta do cliente, segurança percebida e fluxo de compra. Os apontamentos considerados pertinentes foram corrigidos e posteriormente submetidos a novo teste.

Além dos registros individuais apresentados anteriormente, o quadro complementar abaixo consolida o foco de cada avaliação, os principais resultados, as correções associadas e a relação com os IDs detalhados neste laudo.

## Consolidação das Avaliações Externas

| Avaliador / Data | Consolidação da Avaliação |
| --- | --- |
| **Reberson Faria Gomes**<br>10/08/2026 | **Foco:** Offline, PWA, Modo Escuro e responsividade/mobile.<br><br>**O que funcionou:** A instalação e a utilização como PWA funcionaram conforme esperado.<br><br>**Problemas/sugestões:** Excesso de informações e retomada pouco clara no offline; inconsistências de contraste no Modo Escuro; campos e componentes com problemas em telas menores.<br><br>**Correções:** Tela offline simplificada, nova tentativa destacada, fallback reforçado, componentes mobile reorganizados e Modo Escuro revisado.<br><br>**IDs relacionados:** 01, 02 e 03.<br><br>**Não testado / fora do escopo:** As demais funcionalidades não fizeram parte do foco deste teste. |
| **Fernanda de Souza**<br>11/08/2026 | **Foco:** Estrutura geral do site, organização das informações, textos, páginas e navegação.<br><br>**O que funcionou:** Não foram apontadas falhas funcionais relevantes na navegação ou na estrutura principal.<br><br>**Problemas/sugestões:** Poucas informações de contato, conteúdo institucional limitado e poucas informações sobre segurança e tratamento de dados.<br><br>**Correções:** Ampliação da página Sobre, rodapé, cookies, privacidade e conteúdo de segurança.<br><br>**ID relacionado:** 04.<br><br>**Não testado / fora do escopo:** Fluxos transacionais e aspectos técnicos da aplicação não foram aprofundados. |
| **Matheus Moreira**<br>12/08/2026 | **Foco:** Cadastro, login, logout, Minha Conta, mensagens e processo de compra.<br><br>**O que funcionou:** As funções básicas existentes puderam ser utilizadas durante a avaliação.<br><br>**Problemas/sugestões:** Faltavam Editar Dados, exclusão de conta, favoritos, confirmações adicionais em ações sensíveis e uma etapa mais completa antes da finalização.<br><br>**Correções:** Edição de dados, exclusão de conta, favoritos, endereços, validações por e-mail, validação de novos dispositivos e revisão completa do pedido.<br><br>**IDs relacionados:** 05, 06 e 07.<br><br>**Não testado / fora do escopo:** Autenticação em duas etapas permanente não foi implementada. Pagamento on-line permanece fora do escopo; Pagamento Presencial é a opção ativa. |
| **Gustavo Coelho**<br>13/08/2026 | **Foco:** Home, FAQ, catálogo, produtos, carrinho e fluxo de compra.<br><br>**O que funcionou:** A estrutura geral permitia percorrer a aplicação.<br><br>**Problemas/sugestões:** Quebra visual na FAQ, falta de filtros, Home e cards excessivamente grandes e continuidade incompleta ao abrir produtos em etapas posteriores.<br><br>**Correções:** FAQ reestruturada, catálogo com filtros e ordenação, cards e páginas de produto compactados e navegação para detalhes ampliada.<br><br>**IDs relacionados:** 08 e 09.<br><br>**Não testado / fora do escopo:** O teste não aprofundou especificamente as regras técnicas de segurança da conta. |
| **Gabriela de Lima**<br>13/08/2026 | **Foco:** Avaliação geral de ponta a ponta: navegação institucional, catálogo, busca, produto, cadastro, autenticação, Minha Conta, favoritos, carrinho, revisão, finalização, Meus Pedidos, Modo Escuro e interface.<br><br>**O que funcionou:** Não foram apontadas falhas funcionais relevantes nos fluxos avaliados.<br><br>**Problemas/sugestões:** Diferenças de terminologia, títulos, capitalização e apresentação entre páginas e mensagens.<br><br>**Correções:** Revisão textual geral de títulos, rótulos, mensagens e conteúdos apresentados ao usuário.<br><br>**ID relacionado:** 10.<br><br>**Não testado / fora do escopo:** Não foi indicada funcionalidade relevante como não testada dentro do escopo disponível. |

Na sequência, cada apontamento é detalhado individualmente, mantendo o problema identificado, a correção realizada, o resultado do reteste e as evidências disponíveis.

Para manter esta versão Markdown visualmente alinhada ao documento oficial em Word, as capturas inseridas no DOCX são reaproveitadas diretamente do conjunto de evidências ou extraídas sem alteração para `../01-PLANEJAMENTO-E-MODELAGEM/evidencias/documento-oficial/`.

---

## ID 01 - Tela Offline

| Campo | Informação |
| --- | --- |
| **Problema identificado** | Tela offline com excesso de informações e retomada pouco clara. |
| **Correção realizada** | Conteúdo simplificado, reorganização da tela e inclusão de uma ação clara para tentar novamente. |
| **Resultado** | Aprovado no reteste |

| Antes | Depois |
| --- | --- |
| ![Tela offline antes](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/historico/01-offline-antes.png) | ![Tela offline depois](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/12-offline.png) |

---

## ID 02 - Modo Escuro

| Campo | Informação |
| --- | --- |
| **Problema identificado** | Algumas áreas apresentavam contraste e visibilidade inadequados no Modo Escuro. |
| **Correção realizada** | Revisão das superfícies, componentes e contraste do tema escuro. |
| **Resultado** | Aprovado no reteste |

| Antes | Depois |
| --- | --- |
| ![Modo Escuro antes](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/historico/04-faq-antes.png) | ![Modo Escuro depois](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/13-faq-dark.png) |

---

## ID 03 - Responsividade em Dispositivos Móveis

| Campo | Informação |
| --- | --- |
| **Problema identificado** | Quebras de layout e baixa responsividade em dispositivos móveis. |
| **Correção realizada** | Menu, grids, formulários, espaçamentos e tamanhos foram reorganizados para telas menores. |
| **Resultado** | Aprovado no reteste |

| Antes | Depois |
| --- | --- |
| ![Responsividade antes](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/historico/05-home-mobile-antes.png) | ![Responsividade depois](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/02-home-mobile.png) |

---

## ID 04 - Conteúdo Institucional, Privacidade e Segurança

| Campo | Informação |
| --- | --- |
| **Problema identificado** | Poucas informações institucionais, de privacidade e segurança. |
| **Correção realizada** | Ampliação da página Sobre, rodapé, Política de Privacidade, Cookies e conteúdo de segurança. |
| **Resultado** | Aprovado no reteste |

| Antes | Depois |
| --- | --- |
| ![Rodapé antes](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/historico/06-rodape-antes.png) | ![Sobre e rodapé depois](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/14-sobre-rodape.png) |

---

## ID 05 - Autonomia da Área do Cliente

| Campo | Informação |
| --- | --- |
| **Problema identificado** | Área do cliente com pouca autonomia. |
| **Correção realizada** | Foram adicionados edição de dados, gerenciamento de endereços, favoritos e exclusão da conta. |
| **Resultado** | Aprovado no reteste |

| Antes | Depois |
| --- | --- |
| **Não havia tela equivalente na versão anterior para registro comparativo.** | ![Minha Conta - captura do documento oficial](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/documento-oficial/03-id05-minha-conta-depois.jpeg) |

Evidência complementar: [Favoritos](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/15-favoritos.png).

---

## ID 06 - Confirmações em Ações Sensíveis

| Campo | Informação |
| --- | --- |
| **Problema identificado** | Ações sensíveis possuíam poucas confirmações adicionais. |
| **Correção realizada** | Foram implementadas confirmações por e-mail, validação de dispositivo e mensagens integradas ao site. |
| **Resultado** | Aprovado no reteste |

| Antes | Depois |
| --- | --- |
| **Não havia tela equivalente na versão anterior para registro comparativo.** | ![Validação de dispositivo por e-mail](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/17-validacao-dispositivo-email.jpeg) |

Evidências complementares: [Validação de formulário](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/11-validacao-formulario.png) e [Segurança](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/16-seguranca.png).

---

## ID 07 - Revisão e Finalização do Pedido

| Campo | Informação |
| --- | --- |
| **Problema identificado** | Processo de compra possuía finalização muito direta. |
| **Correção realizada** | Foi criada uma etapa completa de revisão do pedido, com recebimento, endereço, pagamento, cupom, resumo e confirmação. |
| **Resultado** | Aprovado no reteste |

| Antes | Depois |
| --- | --- |
| ![Fluxo anterior de finalização](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/historico/07-finalizacao-direta-antes.jpeg) | ![Revisar Pedido](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/18-revisar-pedido.jpeg) |

**Antes:** o fluxo seguia diretamente para a confirmação do pedido.  
**Depois:** foi incluída a etapa **Revisar Pedido** antes da confirmação.

---

## ID 08 - Perguntas Frequentes (FAQ)

| Campo | Informação |
| --- | --- |
| **Problema identificado** | FAQ apresentava problemas visuais, principalmente em determinadas resoluções e no tema escuro. |
| **Correção realizada** | FAQ reestruturada e revisada para desktop, mobile, teclado e Modo Escuro. |
| **Resultado** | Aprovado no reteste |

| Antes | Depois |
| --- | --- |
| ![FAQ antes](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/historico/04-faq-antes.png) | ![FAQ depois](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/13-faq-dark.png) |

---

## ID 09 - Catálogo e Página de Produto

| Campo | Informação |
| --- | --- |
| **Problema identificado** | Catálogo e página de produto apresentavam elementos grandes e pouca facilidade de filtragem. |
| **Correção realizada** | Foram adicionados filtros e ordenação, além da compactação de cards, revisão das páginas de produto e ampliação da navegação para detalhes. |
| **Resultado** | Aprovado no reteste |

### Catálogo

| Antes | Depois |
| --- | --- |
| ![Catálogo antes](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/documento-oficial/05-id09-catalogo-antes.png) | ![Catálogo depois](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/documento-oficial/06-id09-catalogo-depois.png) |

### Página de Produto

| Antes | Depois |
| --- | --- |
| ![Produto antes](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/documento-oficial/07-id09-produto-antes.png) | ![Produto depois](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/documento-oficial/08-id09-produto-depois.png) |

---

## ID 10 - Padronização Textual

| Campo | Informação |
| --- | --- |
| **Problema identificado** | Existiam diferenças de terminologia, títulos e capitalização entre páginas e mensagens. |
| **Correção realizada** | Foi realizada revisão textual geral, com padronização de títulos, rótulos, mensagens e conteúdos apresentados ao usuário. |
| **Resultado** | Aprovado no reteste |

| Antes | Depois |
| --- | --- |
| ![Padronização textual antes](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/historico/08-padronizacao-textual-antes.png) | ![Padronização textual depois](../01-PLANEJAMENTO-E-MODELAGEM/evidencias/19-padronizacao-textual.png) |

**Antes:** “Perguntas Frequentes” e “Um Cookie para Acompanhar seu Cupcake?”.  
**Depois:** “Perguntas frequentes” e “Preferências de cookies”.

A evidência do ID 10 utiliza uma captura histórica real já preservada no documento, sem simulação. O comparativo demonstra a padronização de capitalização e terminologia em títulos e no aviso de cookies.

---

Após a aplicação das correções, os cinco participantes realizaram um novo ciclo de avaliação dos fluxos testados. No reteste não foram relatados novos problemas funcionais ou sugestões adicionais relevantes. A consolidação das avaliações, os IDs do laudo e as evidências visuais foram mantidos alinhados à documentação de Testes e Qualidade do repositório.

Como verificação complementar, a versão final também foi submetida à bateria automatizada de testes e às verificações técnicas do projeto. Foram executados **261 testes automatizados, todos aprovados**, além de verificações de dependências, segurança, código Python, JavaScript e inicialização da aplicação.

Dessa forma, considerando os testes externos, as correções realizadas, o reteste e as verificações técnicas, a versão final da solução foi considerada aprovada para a entrega acadêmica.

---

# Vídeo da Solução Atualizada

Após levantar os feedbacks e executar as correções necessárias e pertinentes, grave um vídeo de até 5 minutos apresentando as modificações realizadas no sistema.

| Campo | Link |
| --- | --- |
| **Link para o vídeo** | https://youtu.be/jcKkAdVNfS0 |
