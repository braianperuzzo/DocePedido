# Arquitetura e Código

## Tecnologias

- Python 3 e Flask;
- Jinja, HTML, CSS, JavaScript e Bootstrap;
- SQLAlchemy e SQLite;
- Flask-Login, Flask-WTF e Flask-Limiter;
- Pytest e Playwright para verificação;
- Ruff, Bandit e pip-audit para qualidade e segurança.

## Organização

```text
aplicacao/
├── controladores/   rotas e coordenação dos fluxos HTTP
├── modelos/         entidades e persistência SQLAlchemy
├── servicos/        regras compartilhadas e integrações
├── templates/       páginas renderizadas com Jinja
└── static/          estilos, JavaScript, imagens e recursos do PWA
```

## Separação de Responsabilidades

Os controladores recebem as requisições e coordenam as ações. Os modelos representam os dados persistidos. Os serviços concentram regras reutilizáveis, como cupom, e-mail e tokens. Os templates formam a camada de apresentação e os recursos estáticos tratam comportamento visual, tema, responsividade e PWA.

## Serviços Externos

A solução utiliza transporte SMTP para mensagens transacionais e serviços de localidades para apoio ao cadastro de endereços. Falhas externas são tratadas sem exposição de dados sensíveis ou detalhes internos.

## Regras Centralizadas

Regras como elegibilidade do cupom, autenticação, confirmação de conta, segurança de dispositivo, persistência de pedido e envio de mensagens permanecem no back-end, evitando dependência exclusiva do JavaScript do navegador.
