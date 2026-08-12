# Segurança e Privacidade

## Conta e Autenticação

- senhas armazenadas por hash;
- validação de credenciais no servidor;
- recuperação de senha por fluxo com token temporário;
- confirmação por e-mail em ações sensíveis;
- validação de novo dispositivo conforme a política da conta;
- proteção das rotas autenticadas;
- controle de duração e renovação de sessão conforme configuração da aplicação.

## Proteções da Aplicação

- CSRF em formulários e ações de alteração;
- rate limiting em pontos sensíveis;
- cookies com atributos adequados ao ambiente HTTPS;
- cabeçalhos de segurança, incluindo política de conteúdo;
- validação de entrada no servidor;
- mensagens de erro sem stack trace ou credenciais;
- segredos mantidos fora do repositório.

## Privacidade

A aplicação dispõe de Política de Privacidade, Política de Cookies, Termos de Uso e página de Segurança. Cookies essenciais sustentam o funcionamento do site. Recursos de análise dependem de consentimento quando configurados.

## Dados do Cliente

O sistema mantém apenas os dados necessários aos fluxos implementados. CPF, e-mail, telefone, endereços e dados de pedidos são tratados como informações vinculadas à conta e às regras da solução. A exclusão de conta possui fluxo próprio e confirmação adicional.
