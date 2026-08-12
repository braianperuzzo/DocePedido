# Matriz de Rastreabilidade

| Exigência / Requisito | Implementação / Documento | Verificação | Evidência |
| --- | --- | --- | --- |
| Escopo e requisitos | `01-PLANEJAMENTO-E-MODELAGEM/ESCOPO_E_REQUISITOS.md` | conferência com a solução final | documentação do escopo |
| UML | `MODELAGEM_UML.md` e `diagramas/` | coerência com código e banco | fontes PlantUML |
| IHC | `IHC_E_UX.md` | testes de interface e validação externa | `evidencias/` |
| Banco conceitual, lógico e físico | `BANCO_DE_DADOS.md` | modelos SQLAlchemy | modelo e dicionário |
| Front-end | `aplicacao/templates/` e `aplicacao/static/` | testes de interface | capturas finais |
| Back-end | `aplicacao/controladores/`, `servicos/`, `modelos/` | suíte automatizada | resultados técnicos |
| Cadastro e autenticação | controladores e templates de autenticação | testes de autenticação e segurança | login, validação e conta |
| Catálogo e produto | controladores e templates de produtos | testes de produto e busca | catálogo e detalhe |
| Carrinho e cupom | carrinho, pedidos e serviço de cupons | testes de carrinho e cupom | carrinho com BEMVINDO |
| Conta e endereços | controladores de conta e recursos | testes de conta | Minha Conta e favoritos |
| Checkout e pedidos | controlador de pedidos | testes de pedidos | revisão, confirmação e histórico |
| Segurança e privacidade | configuração, serviços e páginas institucionais | testes de segurança | página de segurança |
| PWA e offline | manifesto, Service Worker e página offline | testes PWA/mobile | captura offline |
| Avaliação com cinco pessoas | `03-TESTES-E-QUALIDADE/AVALIACOES_EXTERNAS.md` | reteste | laudo de qualidade |
| Publicação | `02-DESENVOLVIMENTO-E-PUBLICACAO/PUBLICACAO_PWA_SEO.md` | validação no ambiente final | URL pública |
