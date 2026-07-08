# ROTEIRO_VALIDACAO_MERCADO_ABERTO_CANDLEBUILDER_2026_07_08

## Status

PENDENTE_VALIDACAO_MERCADO_ABERTO

## Objetivo

Validar em mercado aberto os patches aplicados no CandleBuilderPainel, no gráfico e na detecção de fonte RTD estagnada.

## Escopo

Este roteiro valida apenas o painel operacional AO_VIVO.

Não homologa histórico oficial.
Não altera Zé do Eucrázio.
Não altera Fiscal Temporal.
Não altera Bernardo.
Não altera Historiador.
Não altera Biblioteca Histórica oficial.

## Patches a validar

- ed754bc TRIN reconstrói grafico quando historico muda
- a775a03 TRIN bloqueia candle novo com RTD estagnado
- ce0bfda TRIN exibe status da fonte RTD no painel

## Validação 1 — Fonte RTD saindo de estagnada

Condição inicial esperada antes do mercado andar:

Fonte RTD: ESTAGNADA

Resultado esperado após chegada de dado novo:

Fonte RTD: ATUALIZANDO

Critério de aprovação:

- status_fonte muda para RTD_ATUALIZANDO
- fonte_estagnada muda para False
- painel não permanece travado em ESTAGNADA quando houver dado novo real

## Validação 2 — Candle novo só nasce com dado novo

Critério de aprovação:

- se preço, volume_real, delta, saldo e VWAP não mudarem, histórico não cresce
- se algum campo real da assinatura RTD mudar, candle pode nascer normalmente
- backend não fabrica candle apenas porque o relógio avançou

## Validação 3 — Gráfico contínuo

Critério de aprovação:

- gráfico não fica esburacado
- troca de timeframe reconstrói a série corretamente
- 15s mostra segundos
- 30s mostra segundos
- 2_MIN volta para visual limpo

## Validação 4 — Timeframes

Testar:

- 15s
- 30s
- 2_MIN

Critério de aprovação:

- 15s com intervalos de 15 segundos
- 30s com intervalos de 30 segundos
- 2_MIN com intervalos de 120 segundos
- sem duplicidade de timestamp
- sem crescimento de histórico com fonte estagnada

## Validação 5 — Volume estimado

Critério de aprovação:

- volume normalizado permanece visível
- volume_candle_estimado varia quando volume_real variar
- volume_candle_estimado fica 0 quando não houver novo dado real
- tipo permanece REAL_DELTA_ESTIMADO

## Validação 6 — Segurança operacional

Critério de aprovação:

- status do painel permanece OPERACIONAL_NAO_CERTIFICADO
- CandleBuilderPainel não vira histórico oficial
- DIARIO e SEMANAL continuam reservados
- TT_RAW continua diagnóstico apenas
- Replay continua ausente/não ativo até nova decisão arquitetural

## Resultado final esperado

Se todos os testes passarem:

CANDLEBUILDER_PAINEL_APROVADO_EM_MERCADO_ABERTO_COM_RESSALVAS

Se algum teste falhar:

ABRIR_AUDITORIA_ESPECIFICA_ANTES_DE_NOVO_PATCH

## Parecer

Este roteiro existe para impedir validação subjetiva no olho.

Amanhã, com mercado aberto, o TRIN deve provar que distingue:

- mercado andando
- fonte RTD estagnada
- relógio apenas avançando

