# Resultados Técnicos

## Suíte Automatizada

| Métrica | Resultado |
| --- | --- |
| Testes executados | 261 |
| Testes aprovados | 261 |
| Falhas | 0 |
| Erros | 0 |
| Testes ignorados | 0 |
| Avisos externos | 2 avisos de depreciação do Flask-Login |

## Qualidade e Segurança

| Verificação | Resultado |
| --- | --- |
| Ruff | Aprovado |
| Bandit | Aprovado |
| pip-audit | Sem vulnerabilidades conhecidas |
| pip check | Sem dependências quebradas |
| Compilação Python | Aprovada |
| Sintaxe JavaScript | Aprovada |
| Inicialização HTTP | Aprovada |
| Evidências principais da versão final | 16 capturas |
| Evidências complementares do laudo | 3 arquivos (17 a 19) |
| Evidências históricas antes/depois | 8 arquivos |

## Cobertura Funcional

A suíte inclui cenários de criação da aplicação, autenticação, cadastro, CPF, e-mail, recuperação de senha, segurança de conta, catálogo, busca, carrinho, estoque, cupom, endereços, favoritos, pedidos, cookies, SEO, PWA, offline, mobile, Modo Escuro e regressões de interface.

## Evidências

O conjunto documental utiliza **19 arquivos de evidência final/complementar** e **8 evidências históricas**, organizados em `documentacao/01-PLANEJAMENTO-E-MODELAGEM/evidencias/` e relacionados aos IDs do laudo em `EVIDENCIAS_ANTES_DEPOIS.md`.

## Validação em Produção

A aplicação publicada em **https://docepedido.pythonanywhere.com/** foi validada com HTTPS, persistência SQLite, envio de e-mail, consulta de localidades e os fluxos principais da solução.
