# Funcionalidades e Manual de Uso

## Visão Geral

O Doce Pedido é uma aplicação web responsiva voltada à navegação de produtos e ao registro de pedidos de uma confeitaria. A solução reúne catálogo, autenticação, conta do cliente, favoritos, endereços, carrinho, cupom, revisão de pedido, histórico de compras e recursos complementares de segurança, privacidade, responsividade e PWA.

A aplicação está disponível em:

https://docepedido.pythonanywhere.com/

---

## Funcionalidades

### Área Pública

A Home apresenta a identidade da loja, produtos em destaque, kits e acesso às áreas principais.

O catálogo disponibiliza:

- busca de produtos;
- filtros;
- ordenação;
- indicação de disponibilidade;
- acesso aos detalhes de cada produto.

A página de produto apresenta imagem, descrição, preço, disponibilidade, seleção de quantidade, opção de favorito e inclusão no carrinho.

### Cadastro e Autenticação

O cadastro do cliente utiliza:

- nome;
- CPF;
- e-mail;
- celular;
- senha.

Após o cadastro, o sistema utiliza confirmação por e-mail nos fluxos previstos.

A aplicação também contempla:

- login;
- logout;
- recuperação de senha;
- validação de novos dispositivos;
- controles adicionais de segurança da conta.

### Minha Conta

Após a autenticação, a área Minha Conta permite acessar e gerenciar:

- dados pessoais;
- senha;
- endereços;
- produtos favoritos;
- pedidos realizados;
- exclusão da conta.

O CPF cadastrado é utilizado como informação de identificação e não pode ser alterado posteriormente.

### Carrinho e Cupom

O carrinho permite:

- adicionar produtos;
- alterar quantidades;
- remover itens;
- consultar subtotal;
- aplicar desconto;
- consultar o total do pedido.

O cupom `BEMVINDO` concede 10% de desconto na primeira compra elegível, conforme as regras da aplicação.

### Revisão e Finalização do Pedido

Antes da confirmação, o cliente passa por uma etapa de revisão do pedido.

É possível selecionar:

- entrega em um endereço cadastrado; ou
- retirada na loja.

Quando a opção de entrega é selecionada, o cliente pode escolher um de seus endereços salvos.

A forma de pagamento disponível na versão final é **Pagamento Presencial**.

Pix e cartão on-line podem aparecer na interface como indisponíveis, mas não realizam processamento financeiro.

A revisão apresenta os itens, quantidades, valores, desconto, forma de recebimento, endereço quando aplicável, forma de pagamento e total antes da confirmação.

### Pedidos

Após a finalização, o pedido é registrado no banco de dados com os itens e informações necessárias para preservar o histórico da compra.

A aplicação apresenta uma confirmação ao cliente e disponibiliza posteriormente o pedido na área **Meus Pedidos**.

Em Meus Pedidos, o cliente pode consultar seu histórico e acessar os detalhes das compras realizadas.

### Recursos Complementares

A solução também inclui:

- Modo Claro e Modo Escuro;
- interface responsiva para desktop e dispositivos móveis;
- PWA;
- funcionamento offline para conteúdos previstos;
- preferências de cookies;
- Política de Privacidade;
- Termos e Condições;
- página de Segurança;
- FAQ;
- informações sobre entrega;
- informações institucionais;
- recursos de SEO.

---

# Manual de Uso

## 1. Acessar a Aplicação

Acesse:

https://docepedido.pythonanywhere.com/

A página inicial permite navegar pelos produtos, acessar o catálogo, consultar informações da loja ou entrar na conta do cliente.

---

## 2. Criar uma Conta

1. Acesse a opção de cadastro.
2. Informe os dados solicitados.
3. Preencha nome, CPF, e-mail, celular e senha.
4. Confira os dados informados.
5. Envie o cadastro.
6. Quando solicitado, realize a confirmação pelo e-mail recebido.

Após a confirmação, a conta estará disponível para autenticação.

---

## 3. Fazer Login

1. Acesse a página de login.
2. Informe o e-mail e a senha cadastrados.
3. Selecione a opção para entrar.
4. Caso o dispositivo utilizado ainda não esteja reconhecido, siga o processo de validação apresentado pelo sistema.

Após a autenticação, serão disponibilizados os recursos da área do cliente.

---

## 4. Recuperar a Senha

Caso não se lembre da senha:

1. Acesse a opção de recuperação de senha na página de login.
2. Informe o e-mail da conta.
3. Siga as orientações enviadas pelo sistema.
4. Defina uma nova senha respeitando os requisitos apresentados.
5. Conclua o processo de recuperação.

---

## 5. Consultar Produtos

1. Acesse a opção **Produtos**.
2. Utilize a busca para localizar um produto pelo nome ou sabor.
3. Utilize os filtros disponíveis quando necessário.
4. Utilize a ordenação para reorganizar os resultados.
5. Clique em um produto para abrir seus detalhes.

Na página do produto são exibidos preço, descrição, disponibilidade e opções relacionadas à compra.

---

## 6. Adicionar um Produto aos Favoritos

Quando autenticado:

1. Localize o produto desejado.
2. Utilize a opção de favorito.
3. O produto ficará disponível na área de favoritos da conta.

Para remover um favorito, utilize novamente a ação correspondente.

---

## 7. Adicionar Produtos ao Carrinho

1. Abra o produto desejado.
2. Defina a quantidade.
3. Adicione o produto ao carrinho.
4. Repita o procedimento para outros produtos, se necessário.
5. Abra o carrinho para revisar os itens.

No carrinho é possível alterar quantidades ou remover produtos antes de continuar.

---

## 8. Utilizar o Cupom BEMVINDO

Quando a compra atender aos critérios da promoção:

1. Acesse o carrinho.
2. Informe o cupom `BEMVINDO`.
3. Solicite a aplicação do cupom.
4. Confira o desconto apresentado no resumo.

O cupom concede 10% de desconto na primeira compra elegível, conforme as regras do sistema.

---

## 9. Cadastrar e Gerenciar Endereços

Após entrar na conta:

1. Acesse **Minha Conta**.
2. Abra a área de endereços.
3. Cadastre um novo endereço informando os dados solicitados.
4. Selecione UF e cidade nos campos disponíveis.
5. Salve o endereço.

A área também permite editar, excluir e definir o endereço principal conforme as opções apresentadas.

---

## 10. Finalizar um Pedido

Após revisar o carrinho:

1. Continue para a etapa de revisão do pedido.
2. Escolha como deseja receber a compra:
   - entrega em um endereço cadastrado; ou
   - retirada na loja.
3. Caso escolha entrega, selecione o endereço desejado.
4. Confira os produtos, quantidades e valores.
5. Confira o desconto, caso exista.
6. Verifique a forma de pagamento.
7. Confira o total do pedido.
8. Selecione **Finalizar Pedido**.

Na versão final, a forma de pagamento ativa é **Pagamento Presencial**.

---

## 11. Consultar Pedidos Realizados

1. Faça login.
2. Acesse **Minha Conta**.
3. Abra **Meus Pedidos**.
4. Consulte os pedidos já realizados.
5. Utilize a opção de detalhes para visualizar as informações disponíveis de uma compra.

---

## 12. Editar os Dados da Conta

1. Acesse **Minha Conta**.
2. Abra a área de dados pessoais.
3. Selecione **Editar Dados**.
4. Atualize as informações permitidas.
5. Confirme a alteração conforme o procedimento apresentado pelo sistema.

O CPF cadastrado não pode ser alterado.

---

## 13. Alterar a Senha

1. Acesse **Minha Conta**.
2. Localize a área de segurança ou alteração de senha.
3. Selecione **Alterar Senha**.
4. Informe os dados solicitados.
5. Defina uma nova senha respeitando os requisitos exibidos.
6. Conclua a confirmação solicitada pelo sistema.

---

## 14. Excluir a Conta

1. Acesse **Minha Conta**.
2. Localize a opção **Excluir Conta**.
3. Solicite a exclusão.
4. Siga o procedimento de confirmação apresentado pelo sistema.

A exclusão é tratada como uma ação sensível e possui confirmação adicional.

---

## 15. Alterar o Tema

A aplicação disponibiliza Modo Claro e Modo Escuro.

Utilize o controle de tema presente na interface para alternar entre os modos disponíveis.

A preferência visual é aplicada às páginas compatíveis da aplicação.

---

## 16. Utilizar como PWA

Em navegadores e dispositivos compatíveis, o Doce Pedido pode ser utilizado como PWA.

Quando a instalação estiver disponível:

1. utilize a opção de instalação apresentada pelo navegador;
2. confirme a instalação;
3. abra o Doce Pedido pelo atalho criado no dispositivo.

A aplicação também possui comportamento offline para os conteúdos previstos no projeto.

---

## 17. Preferências de Cookies

Ao acessar a aplicação, o usuário pode visualizar o aviso de cookies.

É possível:

- aceitar as preferências apresentadas; ou
- acessar **Gerenciar Preferências** para revisar as opções disponíveis.

As informações complementares estão disponíveis nas páginas de Cookies e Política de Privacidade.

---

## Observações

A versão acadêmica do Doce Pedido não contempla processamento de pagamento on-line, cálculo dinâmico de frete, painel administrativo, integração com transportadora ou notificações push.

Esses recursos não fazem parte do escopo final implementado.
