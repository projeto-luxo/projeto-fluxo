# CONTRATO OFICIAL — CANDLE 5S DIAGNOSTICO

## Status

EXPERIMENTAL / DIAGNOSTICO / NAO CERTIFICADO

Data de criacao: 2026-07-09  
Projeto: TRIN  
Modulo: CANDLE_5S_DIAGNOSTICO  
Script inicial: tools_rtd/CANDLE_5S_DIAGNOSTICO_01.ps1

---

## 1. Missao

Transformar negocios provaveis vindos do TT_PENEIRADO_NAO_CERTIFICADO em candles de 5 segundos para analise diagnostica.

Este modulo cria uma regua curta de tempo para estudo, replay futuro e comparacao visual.

---

## 2. Entrada oficial

Fonte permitida:

TT_PENEIRADO_NAO_CERTIFICADO

Fornecedor:

Bastiao TT Peneirador

Status da entrada:

NAO_CERTIFICADO

---

## 3. Saida oficial

Saida:

CANDLE_5S_DIAGNOSTICO

Status:

CANDLE_5S_DIAGNOSTICO_NAO_CERTIFICADO

Uso:

DIAGNOSTICO_APENAS

Campo obrigatorio:

candle_oficial=false

---

## 4. Responsabilidade unica

O Candle 5S Diagnostico apenas organiza negocios provaveis em buckets de 5 segundos.

Ele calcula:

- abertura
- maxima
- minima
- fechamento
- volume_quantidade
- qtd_negocios
- eventos_pregao
- eventos_leilao

---

## 5. Proibicoes

Este modulo nunca deve:

- gerar ordem
- gerar sinal operacional
- liberar entrada
- certificar candle
- substituir o Fiscal Temporal
- substituir o Ze do Eucrazio
- alterar TT RAW
- alterar TT Peneirado
- alimentar o motor operacional diretamente
- declarar candle oficial

---

## 6. Consumidores permitidos

Consumidores permitidos nesta fase:

- auditorias diagnosticas
- estudos visuais
- replay diagnostico futuro
- comparacao com Profit quando possivel

Consumidores proibidos nesta fase:

- Motor de Confluencia operacional
- entrada automatica
- decisao operacional
- certificacao temporal oficial

---

## 7. Garantias

O modulo deve preservar as marcas:

- fonte=TT_PENEIRADO_NAO_CERTIFICADO
- status_candle=CANDLE_5S_DIAGNOSTICO_NAO_CERTIFICADO
- uso_operacional=DIAGNOSTICO_APENAS
- candle_oficial=false

---

## 8. Relacao com outros modulos

TT bruto filma.

Bastiao TT Peneirador separa negocio provavel, rejeicao e incerteza.

Candle 5S Diagnostico organiza a regua curta.

Fiscal Temporal certifica quando existir regra oficial para isso.

Ze do Eucrazio reconstrói fractais oficiais somente depois de fonte certificada.

Operador decide.

---

## 9. Estado atual

Primeiro teste executado em 2026-07-09:

- contrato: WINQ26
- negocios validos: 22
- candles 5s gerados: 2
- status: NAO CERTIFICADO
- uso: DIAGNOSTICO_APENAS

Parecer:

Modulo tecnicamente funcional como prova inicial, mas ainda sem homologacao operacional.
