# AUDITORIA_PRE_PATCH_PAINEL_TT_RAW_DIAGNOSTICO.md

## Status

AUDITORIA_PRE_PATCH
Data: 2026-06-30
Projeto: TRIN
Modulo: Frontend / Painel TRIN
Tema: Exibicao diagnostica do TT RAW no painel

---

## 1. Objetivo

Registrar a auditoria previa antes de alterar o painel TRIN para exibir o diagnostico da captura Times & Trades RAW.

Esta auditoria nao altera codigo.

---

## 2. Contexto

Foi criado e testado o endpoint backend:

GET /tt/raw/status

Esse endpoint le o arquivo:

TRIN_HISTORICO/00_PROCESSAMENTO_TT/painel_tt_raw_status.json

e retorna o diagnostico da captura experimental do Times & Trades RTD.

Status atual retornado:

- TT_RAW_ORGANIZADO_NAO_PENEIRADO
- uso_operacional: DIAGNOSTICO_APENAS
- candle_oficial: false
- proxima_etapa: BASTIAO_TT_PENEIRADOR

---

## 3. Regra arquitetural

O painel pode exibir o diagnostico TT RAW apenas como informacao visual.

O painel nao pode:

- usar TT RAW como candle oficial
- usar TT RAW para entrada operacional
- alimentar CandleBuilder diretamente
- substituir Fiscal Temporal
- substituir Bastiao TT Peneirador
- declarar captura homologada tick a tick

---

## 4. Responsabilidades preservadas

### Backend

Fornece endpoint diagnostico:

/tt/raw/status

### Frontend

Exibe bloco visual informativo.

### Capturador TT RAW

Copia dados brutos.

### Bastiao TT Peneirador

Ainda nao implementado.
Sera responsavel por classificar duplicados, novos provaveis, repeticoes possiveis e incertezas.

### Fiscal Temporal

Continua sendo o cartorio/certificador.
Nao participa desta alteracao.

---

## 5. Alteracao pretendida

Adicionar ao painel um bloco diagnostico com informacoes do endpoint:

- status
- total_linhas_validas_tt
- total_snapshots
- arquivos_analisados
- uso_operacional
- candle_oficial
- proxima_etapa

Exemplo visual:

TT RAW:
STATUS: ORGANIZADO_NAO_PENEIRADO
LINHAS TT: 3.811.887
SNAPSHOTS: 7.625
USO: DIAGNOSTICO_APENAS
CANDLE OFICIAL: NAO
PROXIMA ETAPA: BASTIAO_TT_PENEIRADOR

---

## 6. Risco

Risco principal: o operador interpretar o TT RAW como dado operacional homologado.

Mitigacao obrigatoria:

O painel deve exibir de forma clara:

- DIAGNOSTICO APENAS
- NAO PENEIRADO
- NAO E CANDLE OFICIAL

---

## 7. Parecer pre-patch

A alteracao e aprovada somente como bloco diagnostico visual.

Nao deve haver alteracao em:

- CandleBuilder
- Fiscal Temporal
- Zé do Eucrázio
- Bernardo
- Motor de Confluencia
- regra de entrada operacional

---

## 8. Proximo passo

Implementar patch pequeno no frontend para consumir:

GET /tt/raw/status

e exibir bloco informativo no painel.
