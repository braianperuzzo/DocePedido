# 2 - Escopo e Requisitos Revisados

## 2.1 Objetivo revisado

O Doce Pedido é uma aplicação web acadêmica para uma loja demonstrativa de cupcakes. O sistema permite que visitantes consultem produtos e montem um carrinho e que clientes identificados possam gerenciar sua conta, concluir pedidos e consultar o histórico de compras.

A ideia central do PIT I foi mantida, mas o escopo foi atualizado para refletir a aplicação realmente construída. Funcionalidades previstas inicialmente, como gateway de pagamento on-line, integração com transportadora e painel administrativo, não são apresentadas como prontas quando não fazem parte da versão final.

## 2.2 Atores

- **Visitante:** consulta a loja, pesquisa produtos, monta o carrinho e pode criar uma conta.
- **Cliente:** gerencia conta, endereços e favoritos, finaliza pedidos e consulta o histórico.
- **Serviço de e-mail:** envia confirmações de cadastro, senha, alterações da conta, validação de dispositivo e pedidos.
- **Serviços públicos de localização:** apoiam consulta de CEP, estados e municípios.

## 2.3 Requisitos funcionais consolidados

| ID | Requisito | Situação |
| --- | --- | --- |
| RF01 | Exibir página inicial com produtos ativos em destaque | Implementado |
| RF02 | Listar, pesquisar e abrir detalhes de produtos ativos | Implementado |
| RF03 | Adicionar, atualizar, remover e esvaziar itens do carrinho | Implementado |
| RF04 | Criar conta com nome, CPF, e-mail e senha | Implementado |
| RF05 | Confirmar o cadastro por e-mail | Implementado |
| RF06 | Autenticar e encerrar a sessão do cliente | Implementado |
| RF07 | Recuperar e redefinir senha por e-mail | Implementado |
| RF08 | Editar nome, e-mail e celular com confirmação por e-mail | Implementado |
| RF09 | Manter o CPF sem possibilidade de alteração após o cadastro | Implementado |
| RF10 | Alterar senha com confirmação por e-mail | Implementado |
| RF11 | Excluir a conta somente após confirmação por e-mail | Implementado |
| RF12 | Cadastrar, editar, excluir e definir endereço principal | Implementado |
| RF13 | Consultar CEP e selecionar UF e município no cadastro de endereço | Implementado |
| RF14 | Marcar e remover produtos favoritos | Implementado |
| RF15 | Aplicar o cupom BEMVINDO com 10% de desconto na primeira compra do CPF | Implementado |
| RF16 | Revisar o pedido antes da confirmação | Implementado |
| RF17 | Escolher entrega em endereço salvo ou Retirada na Loja | Implementado |
| RF18 | Escolher outro endereço salvo diretamente na revisão | Implementado |
| RF19 | Trabalhar com frete grátis no fluxo atual | Implementado |
| RF20 | Aceitar somente Pagamento Presencial na entrega ou retirada | Implementado |
| RF21 | Exibir Pix e cartão on-line como opções indisponíveis | Implementado |
| RF22 | Registrar pedido, itens, total, desconto, recebimento, pagamento e endereço usado | Implementado |
| RF23 | Reduzir o estoque no fechamento do pedido | Implementado |
| RF24 | Enviar e-mail de confirmação do pedido | Implementado, depende de SMTP |
| RF25 | Listar pedidos do cliente e abrir seus detalhes | Implementado |
| RF26 | Permitir acesso ao produto a partir de um item do histórico, quando ativo | Implementado |

## 2.4 Requisitos não funcionais

| ID | Categoria | Especificação |
| --- | --- | --- |
| RNF01 | Usabilidade | Interface responsiva, linguagem direta, navegação consistente, feedback de ações e validação próxima ao contexto do usuário. |
| RNF02 | Segurança | Senhas armazenadas por hash, CSRF, rate limiting, confirmação por e-mail em ações sensíveis, validação opcional de dispositivo e páginas privadas sem cache. |
| RNF03 | Compatibilidade | Aplicação web responsiva para desktop, tablet e celular, com PWA e página offline. |
| RNF04 | Acessibilidade | Foco visível, navegação por teclado, atributos ARIA e respeito a redução de movimento quando aplicável. |
| RNF05 | Integridade | Validação de estoque, quantidades, propriedade dos dados, cupom e endereço antes de confirmar alterações ou pedidos. |
| RNF06 | Manutenibilidade | Separação entre modelos, controladores, serviços, templates e recursos estáticos, seguindo organização compatível com MVC. |
| RNF07 | Privacidade | Consentimento separado para análise de uso, páginas de privacidade, cookies, termos e segurança. |
| RNF08 | Testabilidade | Suíte automatizada com Pytest e verificações técnicas complementares registradas no repositório. |

## 2.5 Regras de negócio

- Produtos inativos não podem ser adicionados ao carrinho nem favoritados.
- Quantidades devem ser inteiras, positivas e não podem ultrapassar o estoque disponível.
- O CPF é obrigatório para novos cadastros, único e não pode ser alterado na área do cliente.
- O cupom BEMVINDO concede 10% de desconto somente quando não existe pedido anterior associado ao CPF.
- O cupom é validado novamente antes da confirmação do pedido.
- O pedido registra o código do cupom e o valor do desconto para preservar o histórico.
- O checkout revalida carrinho, produtos e estoque antes de criar o pedido.
- Um cliente só pode consultar os próprios pedidos e endereços.
- O endereço escolhido é copiado para o pedido, preservando o dado utilizado na compra.
- O pagamento on-line não é processado. Pix e cartão aparecem apenas como opções futuras desabilitadas.
- A exclusão da conta só ocorre depois da confirmação do link enviado por e-mail.

## 2.6 Fora do escopo atual

- pagamento on-line por Pix ou cartão;
- cálculo dinâmico de frete;
- painel administrativo para cadastro de produtos, estoque ou gestão de pedidos;
- integração com transportadora;
- integração funcional com WhatsApp ou iFood;
- notificações push;
- processamento de dados de cartão.

Essas limitações são intencionais e não devem ser descritas como funcionalidades prontas na apresentação acadêmica.
