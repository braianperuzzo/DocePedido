# 6 - Rastreabilidade e Evolução do PIT I

## 6.1 Principais mudanças entre o planejamento e a versão final

| Aspecto | Planejamento anterior | Documentação revisada / solução final |
| --- | --- | --- |
| Objetivo central | Venda de cupcakes com catálogo, carrinho, pagamento e acompanhamento. | Mantido: aplicação web de e-commerce para cupcakes com catálogo, carrinho, conta e pedidos. |
| Plataforma | Planejamento inicialmente orientado a aplicativo/protótipo móvel. | Aplicação Web responsiva e PWA, acessível por navegador e instalável. |
| Back-end | Ainda não definido na documentação inicial. | Python com Flask. |
| Banco de dados | Modelo físico de referência preparado para MySQL. | SQLite com SQLAlchemy, adequado ao escopo acadêmico e à hospedagem atual. |
| Pagamento | Previsão de gateway e aprovação de pagamento on-line. | Pagamento Presencial é a única opção ativa; Pix e cartão ficam visíveis e desabilitados. |
| Entrega | Previsão de serviço de entrega e acompanhamento mais amplo. | Entrega em endereço salvo ou Retirada na Loja, com frete grátis no fluxo atual. |
| Administração | Planejamento previa administração básica de produtos, estoque e status. | Painel administrativo não integra o escopo final publicado. |
| Conta do cliente | Cadastro, autenticação e atualização básica. | CPF, confirmação por e-mail, recuperação de senha, edição de dados, endereços, favoritos, exclusão e segurança adicional. |
| UX | Protótipos do fluxo mínimo de compra. | Interface revisada para desktop/mobile, Modo Escuro, acessibilidade, feedback, FAQ, filtros e padronização textual. |
| Recursos adicionais | Não detalhados no PIT I. | Cupom de primeira compra, PWA, offline, cookies, privacidade, segurança e e-mails transacionais. |

## 6.2 Rastreabilidade funcional

| Funcionalidade | Implementação principal | Verificação |
| --- | --- | --- |
| Home e navegação | Página inicial, templates e recursos estáticos | Interface e responsividade |
| Catálogo e busca | Controlador e templates de produtos | Produtos, busca e interface |
| Carrinho | Controlador do carrinho | Carrinho, estoque e quantidades |
| Cupom BEMVINDO | Serviço de cupons, carrinho e pedidos | Cupons e pedidos |
| Cadastro e login | Autenticação e modelos de segurança | Autenticação, confirmação e sessão |
| Minha Conta | Conta, endereços, favoritos e alterações | Conta e recursos do cliente |
| Checkout | Pedidos, Pedido, ItemPedido e DetalhePedido | Pedidos e interface |
| Confirmação e histórico | Pedidos e e-mail | Pedidos, e-mail e Meus Pedidos |
| PWA e offline | Manifesto, Service Worker e página offline | PWA, mobile e fallback |
| Segurança | Autenticação, tokens e dispositivo confiável | Segurança e fluxos sensíveis |

## 6.3 Relação com a atividade da PIT II

A atividade solicita revisitar a documentação desenvolvida na PIT I, realizar atualizações e melhorias conforme o material teórico e manter o resultado em um repositório Git. Esta pasta atende diretamente a essa solicitação porque consolida:

- escopo e requisitos revisados;
- UML coerente com o sistema final;
- IHC e UX atualizadas;
- projeto conceitual, lógico e físico do banco;
- dicionário de dados;
- rastreabilidade entre planejamento e implementação.

## 6.4 Referências do projeto

- Repositório: https://github.com/braianperuzzo/DocePedido
- Aplicação publicada: https://docepedido.pythonanywhere.com/
- Material da disciplina: Projeto Integrador Transdisciplinar em Engenharia de Software II, Cruzeiro do Sul Virtual, 2026.
- Documento de intervenção da PIT II: revisão do aplicativo de venda de cupcakes definido no PIT I, 2026.

## 6.5 Conclusão

A revisão manteve a finalidade do projeto original, mas atualizou decisões de escopo, plataforma, banco de dados, pagamento, segurança e interface para refletir o Doce Pedido efetivamente entregue. O resultado é uma documentação consistente com a implementação, verificável pelo código e adequada para ser mantida no GitHub junto da solução.
