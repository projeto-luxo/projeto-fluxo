# AUDITORIA PRE-INTEGRACAO — CANDLE 5S DIAGNOSTICO -> REPLAY DIAGNOSTICO

## Status

PRE_INTEGRACAO / ANALISE_ARQUITETURAL / NAO_IMPLEMENTAR_NO_FACAO

Data: 2026-07-09  
Projeto: TRIN  
Origem: CANDLE_5S_DIAGNOSTICO  
Destino proposto: REPLAY_DIAGNOSTICO

---

## 1. Objetivo

Avaliar se o CANDLE_5S_DIAGNOSTICO pode ser integrado ao Replay Diagnostico existente.

---

## 2. Contexto tecnico ja verificado

O replay atual utiliza:

- backend/replay_diagnostico.py
- backend/server_institucional_v6.py
- frontend/src/App.js

O replay atual foi desenhado para CSV historico de 1 minuto.

O proprio replay registra que o menor passo real do replay historico atual e 1 minuto.

---

## 3. Fonte do Candle 5S

O CANDLE_5S_DIAGNOSTICO nasce de:

TT_RAW
-> BASTIAO_TT_PENEIRADOR
-> TT_PENEIRADO_NAO_CERTIFICADO
-> CANDLE_5S_DIAGNOSTICO

Status:

CANDLE_5S_DIAGNOSTICO_NAO_CERTIFICADO

Uso:

DIAGNOSTICO_APENAS

Candle oficial:

false

---

## 4. Risco arquitetural

Nao se deve inserir CANDLE_5S_DIAGNOSTICO diretamente no replay atual como se fosse CSV 1_MIN.

Riscos:

- contaminar replay historico 1_MIN
- misturar reguas temporais diferentes
- dar aparencia operacional a dado diagnostico
- confundir TT peneirado nao certificado com candle oficial
- induzir leitura visual falsa no painel

---

## 5. Parecer

INTEGRACAO DIRETA: REPROVADA

INTEGRACAO INDIRETA/CONTROLADA: POSSIVEL

A forma correta e criar um caminho separado:

REPLAY_5S_DIAGNOSTICO

Esse caminho deve preservar:

- fonte=TT_PENEIRADO_NAO_CERTIFICADO
- status=CANDLE_5S_DIAGNOSTICO_NAO_CERTIFICADO
- uso_operacional=DIAGNOSTICO_APENAS
- candle_oficial=false
- modo=REPLAY_5S_DIAGNOSTICO
- nao_operacional=true

---

## 6. Requisitos antes de implementar

Antes de qualquer codigo, definir:

1. Novo modo de replay separado.
2. Seletor de fonte: REPLAY_CSV_1MIN ou REPLAY_5S_DIAGNOSTICO.
3. Payload com marca visual clara.
4. Bloqueio operacional obrigatorio.
5. Sem liberar Motor de Confluencia.
6. Sem liberar entrada, stop, parcial ou alvo.
7. Sem declarar Fiscal aprovado.

---

## 7. Decisao arquitetural recomendada

Criar adaptador futuro:

backend/replay_5s_diagnostico.py

Responsabilidade unica:

Ler CANDLE_5S_DIAGNOSTICO e entregar candles ao painel apenas para laboratorio visual.

Nao alterar neste momento:

- replay_diagnostico.py original
- Motor de Confluencia
- Fiscal Temporal
- Bernardo
- Ze do Eucrazio
- Historiador
- CandleBuilder oficial

---

## 8. Proximo passo aprovado

Somente depois desta auditoria, criar contrato do REPLAY_5S_DIAGNOSTICO antes de codar.

---

## 9. Principio final

Replay 1MIN continua sendo replay 1MIN.

Candle 5S diagnostico nao vira candle oficial.

TT peneirado nao certificado nao vira decisao operacional.

A regua curta pode entrar no laboratorio, mas nao entra no curral operacional.
