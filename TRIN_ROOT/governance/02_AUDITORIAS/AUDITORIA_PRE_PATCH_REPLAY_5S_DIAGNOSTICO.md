# AUDITORIA PRE-PATCH — REPLAY 5S DIAGNOSTICO

## Status

PRE_PATCH / ANALISE_ARQUITETURAL / NAO CODAR AINDA

Data: 2026-07-09
Projeto: TRIN
Modulo proposto: REPLAY_5S_DIAGNOSTICO

---

## 1. Objetivo

Avaliar a criacao de um replay visual separado para CANDLE_5S_DIAGNOSTICO.

Este documento existe para impedir que o Candle 5S Diagnostico seja misturado no Replay 1MIN atual ou no fluxo operacional.

---

## 2. Base ja existente

Documentos relacionados:

- governance/LEIA_PRIMEIRO/MAPA_GERAL_TRIN_ESTADO_E_PROXIMA_FASE.md
- governance/02_AUDITORIAS/AUDITORIA_PRE_INTEGRACAO_CANDLE_5S_REPLAY_DIAGNOSTICO.md
- governance/08_CONTRATOS/CONTRATO_REPLAY_5S_DIAGNOSTICO.md
- governance/08_CONTRATOS/CONTRATO_CANDLE_5S_DIAGNOSTICO.md
- governance/06_CHECKPOINTS/CHECKPOINT_TRIN_2026_07_09_TT_CANDLE_5S.md

---

## 3. Diagnostico do estado atual

O Replay atual ja existe e trabalha com CSV historico 1MIN.

O Candle 5S Diagnostico ja existe e nasce de:

RTD Excel TT
-> Gravador TT Bruto
-> Bastiao TT Peneirador
-> TT_PENEIRADO_NAO_CERTIFICADO
-> CANDLE_5S_DIAGNOSTICO

O Candle 5S atual possui status:

CANDLE_5S_DIAGNOSTICO_NAO_CERTIFICADO

Uso:

DIAGNOSTICO_APENAS

Candle oficial:

false

---

## 4. Risco principal

O maior risco e misturar duas reguas diferentes:

Replay atual:

REPLAY_CSV / 1MIN / REPLAY_AGREGADO

Replay 5S proposto:

REPLAY_5S_DIAGNOSTICO / 5S / NAO_OPERACIONAL

A integracao direta e proibida.

---

## 5. Decisao arquitetural

O Replay 5S deve nascer como modulo separado.

Nome proposto:

backend/replay_5s_diagnostico.py

Ele nao deve substituir nem alterar o Replay 1MIN atual.

---

## 6. Entrada permitida

Entrada permitida:

CANDLE_5S_DIAGNOSTICO_*.csv

Origem:

TRIN_HISTORICO/00_PROCESSAMENTO_TT/CANDLE_5S_DIAGNOSTICO

Campos esperados:

- data_pregao
- contrato
- timeframe
- bucket_inicio
- bucket_fim
- abertura
- maximo
- minimo
- fechamento
- volume_quantidade
- qtd_negocios
- fonte
- status_candle
- uso_operacional
- candle_oficial

---

## 7. Saida esperada

O modulo deve entregar candles ao painel com marcas claras:

- modo=REPLAY_5S_DIAGNOSTICO
- fonte_dados=CANDLE_5S_DIAGNOSTICO
- fonte_operacional=NAO_OPERACIONAL
- status_painel=REPLAY_5S_DIAGNOSTICO_NAO_OPERACIONAL
- uso_operacional=DIAGNOSTICO_APENAS
- candle_oficial=false
- bloqueio_operacional=true

---

## 8. Proibicoes tecnicas

O patch futuro nao deve:

- mexer no Motor de Confluencia
- mexer no Fiscal Temporal
- mexer no Bernardo
- mexer no Ze do Eucrazio
- mexer no Historiador
- mexer no CandleBuilder oficial
- transformar Candle 5S em candle oficial
- liberar entrada, stop, parcial ou alvo
- remover o bloqueio operacional
- misturar Replay 5S com Replay 1MIN sem marca clara

---

## 9. Caminho de implementacao recomendado

Implementacao futura em etapas:

1. Criar backend/replay_5s_diagnostico.py
2. Ler o CANDLE_5S_DIAGNOSTICO mais recente
3. Converter bucket_inicio para time do grafico
4. Entregar open/high/low/close/volume ao painel
5. Marcar payload como REPLAY_5S_DIAGNOSTICO
6. Bloquear qualquer campo operacional
7. Testar sem alterar Motor nem Fiscal
8. Registrar auditoria pos-patch

---

## 10. Parecer pre-patch

APROVADO PARA CODIGO CONTROLADO

Com restricoes:

- modulo separado
- uso diagnostico apenas
- bloqueio operacional permanente
- sem alterar Replay 1MIN neste primeiro patch
- sem alimentar decisao real

---

## 11. Principio final

Replay 5S e laboratorio.

Replay 1MIN continua intacto.

Candle 5S diagnostico nao vira oficial.

Fiscal continua bloqueando decisao.

Operador decide.
