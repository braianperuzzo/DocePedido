# Publicação, PWA e SEO

## Ambiente Publicado

| Item | Situação Final |
| --- | --- |
| Hospedagem | PythonAnywhere |
| URL | https://docepedido.pythonanywhere.com/ |
| HTTPS | Validado |
| Back-end | Python com Flask |
| Persistência | SQLite com SQLAlchemy |
| E-mail transacional | Validado |
| CEP e localidades | Validados |
| Mobile e Modo Escuro | Validados |
| PWA e offline | Validados |

## PWA e Modo Offline

O manifesto define a identidade da aplicação, escopo e comportamento de instalação. O Service Worker mantém recursos públicos necessários à experiência PWA e utiliza a tela `/offline` como fallback de navegação quando a rede não está disponível. Conteúdo privado, requisições de alteração e dados autenticados não são tratados como conteúdo offline.

## SEO

A solução possui metadados compatíveis com compartilhamento e indexação, canonical, dados estruturados, `robots.txt` e `sitemap.xml`. Recursos de análise são separados das funções essenciais e respeitam as preferências de cookies.

## Estado de Produção

A versão publicada foi validada nos fluxos de cadastro, autenticação, conta, endereços, catálogo, carrinho, cupom, revisão, pedido, histórico, e-mail, persistência, localidades, mobile, Modo Escuro, PWA e offline.
