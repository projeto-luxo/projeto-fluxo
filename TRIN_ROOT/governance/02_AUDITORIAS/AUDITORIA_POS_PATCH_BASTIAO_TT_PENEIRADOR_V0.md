# AUDITORIA POS-PATCH — BASTIAO TT PENEIRADOR v0

## Status

AUDITORIA_POS_PATCH

Data: 2026-07-09  
Projeto: TRIN  
Modulo: BASTIAO_TT_PENEIRADOR  
Script: tools_rtd/BASTIAO_TT_PENEIRADOR_01.ps1

---

## 1. Objetivo

Registrar o resultado do primeiro teste do BASTIAO_TT_PENEIRADOR v0 sobre arquivo TT RAW capturado via Excel/RTD.

---

## 2. Entrada auditada

Arquivo RAW:

TRIN_HISTORICO/000_TT_BRUTO/WINQ26/2026-07-09/TT_RAW_WINQ26_20260709.csv

Status da origem:

RAW_NAO_CERTIFICADO

---

## 3. Resultado observado

- total_raw: 500
- total_peneirado: 61
- total_rejeitados: 100
- total_incertezas: 339
- contrato: WINQ26
- data_pregao: 2026-07-09
- eventos_leilao_peneirado: 61
- eventos_pregao_peneirado: 0
- preco_min_peneirado: 172665
- preco_max_peneirado: 172665
- qtd_total_peneirada: 713

Status de saida:

TT_PENEIRADO_NAO_CERTIFICADO

Uso operacional:

DIAGNOSTICO_APENAS

Candle oficial:

false

---

## 4. Classificacoes observadas

### Peneirado

61 linhas classificadas como:

NEGOCIO_VALIDO_PROVAVEL / EVENTO_LEILAO

### Rejeitados

100 linhas classificadas como:

LINHA_CASCA_EXCEL

Motivo:

TIMESTAMP_INVALIDO; PRECO_INVALIDO; QUANTIDADE_INVALIDA

### Incertezas

339 linhas classificadas como:

REPETICAO_REAL_POSSIVEL + DUPLICADO_PROVAVEL + INCERTEZA_SEQUENCIAL / EVENTO_LEILAO

---

## 5. Parecer tecnico

O BASTIAO_TT_PENEIRADOR v0 cumpriu a responsabilidade definida no contrato:

- leu o TT RAW;
- nao alterou o arquivo bruto;
- separou linhas casca;
- classificou negocios validos provaveis;
- preservou incertezas em vez de apagar negocios potencialmente reais;
- manteve status nao certificado;
- manteve uso diagnostico apenas;
- nao declarou candle oficial.

---

## 6. Ressalvas

A amostra processada contem apenas eventos de leilao.

Portanto, este teste valida o funcionamento tecnico inicial do peneirador, mas ainda nao valida comportamento em pregao normal.

Para uso futuro em candle de 5 segundos, sera necessario testar o BASTIAO_TT_PENEIRADOR com TT RAW de mercado aberto normal, contendo eventos de pregao.

---

## 7. Modulos nao alterados

Este patch nao alterou:

- Zé do Eucrázio
- Fiscal Temporal
- Bernardo
- Motor de Confluencia
- Historiador
- Replay Diagnostico
- CandleBuilder
- Backend
- Frontend

---

## 8. Proximo passo recomendado

Apos registro do script e desta auditoria, o proximo passo arquitetural sera:

1. Capturar TT RAW durante pregao normal.
2. Rodar o BASTIAO_TT_PENEIRADOR v0.
3. Comparar classificacoes de EVENTO_PREGAO e EVENTO_LEILAO.
4. Somente depois projetar CANDLE_5S_DIAGNOSTICO a partir de TT_PENEIRADO_NAO_CERTIFICADO.

---

## Principio final

O gravador filma.

O Bastiao peneira.

O Fiscal certifica.

O Ze reconstrói.

O operador decide.
