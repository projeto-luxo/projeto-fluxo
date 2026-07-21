# TABELA — EXISTE / NÃO EXISTE — P04B V1.9

| Categoria | Conteúdo |
|---|---|
| EXISTE | backend `backend.server_institucional_v6:app`, porta 8001 |
| EXISTE | montador oficial `gerar_payload()` e endpoints `GET /data` e WebSocket `/ws` |
| EXISTE | dois retornos reais em `gerar_payload()`, ambos finalizados pelo P04B |
| EXISTE | `payload["fiscal"]` produzido pelo caminho oficial `consultar_fiscal_oficial()` |
| EXISTE | P04A e Historiador homologados na base declarada |
| EXISTE | sandbox temporária derivada do commit-base |
| NÃO EXISTE | autorização operacional, peso, direção, entrada, stop, parcial, alvo ou envio de ordem |
| NÃO PODE SER INVENTADO | certificado Fiscal, fonte, regime, `origem_id` ou experiência |
| DECISÃO | Fiscal exige fonte oficial, aprovação verdadeira e ausência de bloqueio |
| DECISÃO | regime exige valor explícito e fonte `HISTORIADOR_REPLAY_CONTEXTO_OFICIAL` |
| DECISÃO | ausência/divergência Fiscal → `BLOQUEADO` antes do P04A |
| DECISÃO | ausência de configuração replay → `INDISPONIVEL` |
| DECISÃO | P04A/Historiador divergentes da base → aplicação bloqueada |
| DECISÃO | testes falham na sandbox → projeto real permanece intocado |
| DECISÃO | somente após 89 P04A + 118 regressão o projeto real é alterado |
| DECISÃO | sucesso técnico local → evidências para auditoria; homologação não é automática |
