# VALIDACAO_MERCADO_ABERTO_CANDLEBUILDER_2026_07_08

## Status

VALIDACAO_PARCIAL_APROVADA_COM_RESSALVAS

## Data

2026-07-08

## Modulo

CandleBuilderPainel AO_VIVO

---

## 1. Objetivo

Validar em mercado aberto os patches recentes do painel operacional, principalmente:

- leitura RTD/Excel real;
- CandleBuilder em 2_MIN;
- bloqueio contra candle falso com RTD parado;
- exibição de status da fonte RTD;
- comportamento do gráfico com candles reais.

---

## 2. Condição do teste

Mercado aberto.

Fonte esperada:

RTD_EXCEL_PLAN1

Contrato observado:

WINQ26_F_0

Timeframe testado:

2_MIN

---

## 3. Resultado aprovado

Durante o teste, o painel saiu do fallback 100.00 e voltou a receber dado real via RTD/Excel.

Foram observados candles reais com preços do WINQ26_F_0 e variação em:

- preço;
- volume_real;
- delta;
- saldo;
- VWAP;
- gráfico.

Foi confirmado o nascimento de candle novo em 2_MIN com intervalo correto:

- historico_cresceu: True
- candles_novos: 1
- intervalo: 120

Parecer:

CandleBuilder 2_MIN aprovado em mercado aberto quanto à formação temporal básica.

---

## 4. Evidência operacional observada

Últimos candles observados apresentaram sequência temporal coerente em 2_MIN:

- 1783530720
- 1783530840
- 1783531080
- 1783531200
- 1783531320
- 1783531440
- 1783531560
- 1783531680
- 1783531800

Os candles apresentaram variação real de preço, delta, saldo e volume.

---

## 5. Ressalva 1 — status_fonte sensível demais

Foi observada contradição operacional:

O dado mudou, o candle nasceu e o intervalo temporal foi correto, mas o painel temporal marcou:

- status_painel: OPERACIONAL_NAO_CERTIFICADO_FONTE_ESTAGNADA
- status_fonte: RTD_ESTAGNADO
- fonte_estagnada: true

Conclusão:

O detector de RTD estagnado está funcional para evitar candle falso, mas está sensível demais em mercado aberto.

Uma leitura repetida isolada não deve necessariamente significar RTD_ESTAGNADO.

Recomendação futura:

Criar PATCH_CANDLEBUILDER_03 para diferenciar:

- SEM_NOVO_TICK_NA_LEITURA
- RTD_ESTAGNADO_CONFIRMADO

---

## 6. Ressalva 2 — volume_candle_estimado exagerado

Foi observado volume_candle_estimado com valores muito altos para leitura visual operacional.

Exemplos observados:

- 1056595563
- 1318549722
- 2000312674
- 1674492585
- 2018037342
- 767627564
- 1630142923
- 1158914373
- 1621524789

Conclusão:

O volume real do RTD parece vir em escala acumulada/bruta muito alta.

O volume_candle_estimado precisa de auditoria própria antes de ser usado como leitura visual confiável.

Recomendação futura:

Abrir AUDITORIA_VOLUME_CANDLE_ESTIMADO_MERCADO_ABERTO.

---

## 7. O que não foi alterado

Esta validação não altera:

- backend;
- frontend;
- Motor de Confluência;
- Fiscal Temporal;
- Bernardo;
- Zé do Eucrázio;
- Historiador;
- Biblioteca Histórica oficial.

---

## 8. Parecer final

O teste em mercado aberto confirmou que o CandleBuilderPainel voltou a receber dados reais via RTD_EXCEL_PLAN1 e formar candles 2_MIN com intervalo temporal correto.

A validação não é homologação final, pois restam duas ressalvas:

1. status_fonte RTD_ESTAGNADO sensível demais;
2. volume_candle_estimado em escala visual inadequada.

Status final:

CANDLEBUILDER_2MIN_VALIDADO_EM_MERCADO_ABERTO_COM_RESSALVAS

