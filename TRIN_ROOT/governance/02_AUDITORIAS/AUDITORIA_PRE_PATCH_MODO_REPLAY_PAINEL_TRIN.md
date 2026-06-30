# AUDITORIA_PRE_PATCH_MODO_REPLAY_PAINEL_TRIN.md

## Status

AUDITORIA_PRE_PATCH  
Data: 2026-06-26  
Projeto: TRIN  
Modulo: Backend / Painel / WebSocket  
Tema: Implementacao inicial do Modo Replay  

---

## 1. Objetivo

Registrar a auditoria previa antes de implementar o Modo Replay no painel TRIN.

Esta auditoria nao altera codigo.

---

## 2. Decisao arquitetural relacionada

A decisao arquitetural oficial do Modo Replay ja foi registrada em:

governance/03_DECISOES_ARQUITETURAIS/DA_MODO_REPLAY_PAINEL_TRIN.md

O Replay foi aprovado como simulacao operacional, nao como mercado real.

---

## 3. Arquivo principal analisado

Arquivo backend principal:

backend/server_institucional_v6.py

Funcoes relevantes identificadas:

- gerar_candle()
- atualizar_historico()
- agregar_historico_painel()
- gerar_payload()
- websocket_endpoint()
- rotas /painel/timeframes e /painel/timeframe/{timeframe}

---

## 4. Fluxo atual identificado

O fluxo atual do painel e:

RTD/Excel  
-> gerar_candle()  
-> atualizar_historico()  
-> gerar_payload()  
-> WebSocket /ws  
-> frontend React  

O WebSocket envia payload continuamente em loop, com intervalo aproximado de 1 segundo.

---

## 5. Ponto de insercao recomendado

O ponto de insercao mais seguro para o Replay e dentro da camada que fornece candles ao historico.

No modo AO_VIVO:

gerar_candle() deve continuar lendo Excel/RTD.

No modo REPLAY:

um ReplayReader deve fornecer o proximo registro historico CSV convertido para o mesmo formato operacional usado pelo painel.

---

## 6. Regra de preservacao do frontend

A primeira implementacao nao deve alterar o frontend.

O frontend ja recebe dados pelo WebSocket e processa o payload recebido.

O backend deve manter a mesma estrutura de payload.

---

## 7. Campo de identificacao obrigatorio

O payload deve informar claramente quando estiver em Replay.

Campos recomendados em painel_temporal:

origem: REPLAY_CSV  
regua_painel: REPLAY_AGREGADO  
status_painel: REPLAY_OPERACIONAL_NAO_CERTIFICADO  

Tambem deve haver indicacao textual de que nao se trata de mercado ao vivo.

---

## 8. Proibicoes

Fica proibido nesta etapa:

- alterar Fiscal Temporal;
- alterar Ze do Eucrazio;
- alterar Bernardo;
- alterar Historiador;
- misturar Replay com RTD ao vivo;
- gravar dado de Replay como captura real;
- certificar historico via Replay;
- executar ordem real baseada em Replay.

---

## 9. Escopo minimo autorizado

O primeiro patch pode implementar:

- variavel de modo de fonte: AO_VIVO ou REPLAY;
- leitura sequencial de CSV historico;
- conversao de linha historica para candle operacional;
- envio pelo mesmo WebSocket /ws;
- identificacao REPLAY no payload;
- preservacao do modo AO_VIVO.

---

## 10. Criterio de sucesso

O patch sera considerado funcional se:

- o backend subir sem erro;
- o modo AO_VIVO continuar intacto;
- o modo REPLAY conseguir ler um CSV historico;
- o painel receber candles em sequencia;
- o seletor de timeframe continuar funcionando;
- o painel indicar origem REPLAY;
- nao houver alteracao em Fiscal, Ze, Bernardo ou Historiador.

---

## 11. Parecer

Patch autorizado somente se for pequeno, isolado e reversivel.

A primeira implementacao deve priorizar continuidade operacional do painel, nao recursos completos de play/pause/velocidade.
