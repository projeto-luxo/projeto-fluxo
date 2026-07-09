# CONTRATO OFICIAL — REPLAY 5S DIAGNOSTICO

## Status

PLANEJADO / DIAGNOSTICO / NAO OPERACIONAL / NAO CERTIFICADO

Data de criacao: 2026-07-09
Projeto: TRIN
Modulo proposto: REPLAY_5S_DIAGNOSTICO

---

## 1. Missao

Permitir replay visual de candles de 5 segundos gerados a partir de CANDLE_5S_DIAGNOSTICO.

Este modulo existe apenas para laboratorio visual, estudo e comparacao.

---

## 2. Entrada oficial

Fonte permitida:

CANDLE_5S_DIAGNOSTICO

Status exigido:

CANDLE_5S_DIAGNOSTICO_NAO_CERTIFICADO

Uso permitido:

DIAGNOSTICO_APENAS

Campo obrigatorio:

candle_oficial=false

---

## 3. Saida oficial

Modo:

REPLAY_5S_DIAGNOSTICO

Status:

REPLAY_5S_DIAGNOSTICO_NAO_OPERACIONAL

Uso:

LABORATORIO_VISUAL

---

## 4. Responsabilidade unica

O REPLAY_5S_DIAGNOSTICO apenas entrega candles 5S diagnosticos ao painel para visualizacao controlada.

Ele nao interpreta mercado.

Ele nao certifica dados.

Ele nao transforma TT em candle oficial.

---

## 5. Proibicoes

Este modulo nunca deve:

- alimentar decisao operacional
- liberar entrada
- liberar stop
- liberar parcial
- liberar alvo
- acionar Motor de Confluencia operacional
- substituir Replay 1MIN
- alterar Replay 1MIN existente
- substituir Fiscal Temporal
- substituir Ze do Eucrazio
- declarar candle oficial
- remover marca diagnostica

---

## 6. Separacao obrigatoria

Replay 1MIN existente:

REPLAY_CSV / REPLAY_AGREGADO

Replay 5S proposto:

REPLAY_5S_DIAGNOSTICO

Esses caminhos nao devem ser misturados.

---

## 7. Campos obrigatorios no payload

O payload futuro deve preservar:

- modo=REPLAY_5S_DIAGNOSTICO
- fonte_dados=CANDLE_5S_DIAGNOSTICO
- fonte_operacional=NAO_OPERACIONAL
- status_painel=REPLAY_5S_DIAGNOSTICO_NAO_OPERACIONAL
- uso_operacional=DIAGNOSTICO_APENAS
- candle_oficial=false
- bloqueio_operacional=true

---

## 8. Consumidores permitidos

Permitidos:

- painel visual diagnostico
- auditoria
- comparacao visual
- estudo de microestrutura

Proibidos:

- Motor de Confluencia operacional
- ordem automatica
- entrada manual autorizada pelo sistema
- Fiscal como aprovado
- Bernardo como memoria certificada

---

## 9. Proximo passo

Antes de codar, executar:

AUDITORIA_PRE_PATCH_REPLAY_5S_DIAGNOSTICO

---

## 10. Principio final

Replay 5S e laboratorio.

Replay 1MIN continua separado.

TT peneirado nao certificado nao vira decisao.

Candle 5S diagnostico nao vira candle oficial.

Operador decide.
