# LAUDO CR-03C — VWAP OFICIAL DO COCKPIT

## Identificação

Data: 2026-07-10
Projeto: TRIN
Branch: TRIN_CLEAN

Arquivo funcional alterado:

- backend/server_institucional_v6.py

## Problema identificado

O cockpit possuía duas fontes de VWAP concorrentes:

1. VWAP real presente no candle RTD/Excel;
2. VWAP calculada pelo VWAPEngine.

Após reinício do backend, com somente um candle na memória do motor,
a VWAP calculada podia coincidir com o último preço.

Isso provocava divergência entre:

- card VWAP;
- linha VWAP do gráfico;
- distância para VWAP;
- valor fornecido à confluência.

No Replay, os candles possuíam VWAP histórica, mas a série payload.vwap
podia permanecer vazia.

## Regra oficial implementada

### AO VIVO

Prioridade:

1. candle.vwap_real;
2. candle.vwap;
3. VWAPEngine como fallback derivado.

Fonte declarada:

- RTD_EXCEL_VWAP_REAL;
- RTD_EXCEL_VWAP;
- VWAP_ENGINE_CALCULADA.

### REPLAY

Prioridade:

1. candle.vwap;
2. candle.vwap_real;
3. VWAPEngine como fallback derivado.

Fonte declarada:

- REPLAY_CSV_VWAP;
- REPLAY_CSV_VWAP_REAL;
- VWAP_ENGINE_CALCULADA.

## Contrato publicado

O payload passou a declarar:

- vwap;
- vwap_atual;
- vwap_oficial;
- vwap_real;
- vwap_fonte;
- distancia_vwap.

## Validação AO VIVO

- último preço: 175390,00;
- VWAP oficial: 174002,00;
- série VWAP: 174002,00;
- distância: 1388,00;
- fonte: RTD_EXCEL_VWAP_REAL;
- todos os oito checks automatizados aprovados.

## Validação REPLAY

- modo: REPLAY;
- replay ativo: verdadeiro;
- candles analisados: 14;
- último preço: 193185,90;
- VWAP oficial: 193063,55338976817;
- série VWAP: 193063,55;
- distância: 122,35;
- fonte: REPLAY_CSV_VWAP;
- linha VWAP visualmente coerente com os candles.

## Preservações

Não foram alterados:

- frontend/src/App.js;
- core/vwap_engine.py;
- replay_diagnostico.py;
- Fiscal;
- regras de autorização;
- stop;
- parcial;
- alvo.

## Classificação

CR-03C_VWAP_OFICIAL: APROVADO
AO_VIVO: APROVADO
REPLAY: APROVADO
CARD_E_GRAFICO: COERENTES
DISTANCIA_VWAP: COERENTE
BLOQUEIO_FISCAL: PRESERVADO
COMMIT: AUTORIZADO
