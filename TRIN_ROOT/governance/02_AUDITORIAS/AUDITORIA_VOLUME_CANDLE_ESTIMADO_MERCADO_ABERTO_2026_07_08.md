# AUDITORIA_VOLUME_CANDLE_ESTIMADO_MERCADO_ABERTO_2026_07_08

## Status

AUDITORIA_ABERTA_SEM_PATCH

## Data

2026-07-08

## Tema

Auditoria da escala do volume_candle_estimado no CandleBuilderPainel em mercado aberto.

---

## 1. Confluência documental

Esta auditoria complementa:

- AUDITORIA_VOLUME_CANDLEBUILDER_PAINEL_2026_07_07
- VALIDACAO_MERCADO_ABERTO_CANDLEBUILDER_2026_07_08
- AUDITORIA_STATUS_FONTE_RTD_MERCADO_ABERTO_2026_07_08

Esta auditoria não altera código.

---

## 2. Contexto

Durante a validação em mercado aberto, o CandleBuilderPainel recebeu dados reais via:

RTD_EXCEL_PLAN1

Contrato observado:

WINQ26_F_0

Timeframes testados:

- 2_MIN
- 30s
- 15s

Os candles foram formados corretamente em termos temporais, mas o campo volume_candle_estimado apresentou escala excessiva para leitura visual.

---

## 3. Achado principal

O campo volume_candle_estimado apresentou valores muito elevados.

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
- 867196575
- 1482643843
- 6133822
- 288423225
- 11721278
- 71651664

---

## 4. Interpretação inicial

O volume_real recebido via RTD aparenta vir em escala acumulada/bruta muito alta.

Exemplos de volume_real observados:

- 439215688041
- 440532782122
- 442533094796
- 444061793356
- 445955105396
- 446644098297
- 448144812829
- 449246953096
- 450738210111

O volume_candle_estimado parece derivar da diferença entre leituras de volume_real, mas ainda sem normalização visual adequada.

---

## 5. Risco operacional

O volume_candle_estimado não deve ser usado ainda como leitura visual confiável para tomada de decisão.

Risco:

- superestimar força do candle;
- confundir volume acumulado com volume efetivo do candle;
- distorcer leitura de agressão;
- contaminar interpretação do operador;
- gerar confiança indevida no painel.

---

## 6. O que está aprovado apesar da ressalva

Mesmo com volume_candle_estimado em escala inadequada, foram aprovados:

- leitura RTD real;
- contrato WINQ26_F_0;
- formação temporal em 2_MIN;
- formação temporal em 30s;
- formação temporal em 15s;
- gráfico recebendo candles reais;
- preço, delta e saldo variando.

---

## 7. O que não deve ser feito

Não corrigir volume no chute.

Não trocar volume por volume_real diretamente.

Não remover o volume_normalizado_capado legado sem auditoria.

Não alterar Motor de Confluência.

Não alterar Bernardo.

Não alterar Zé do Eucrázio.

Não alterar Fiscal Temporal.

Não promover CandleBuilderPainel a histórico oficial.

---

## 8. Hipóteses para investigação futura

Hipótese 1:

volume_real vem acumulado em escala bruta do RTD/Profit.

Hipótese 2:

volume_candle_estimado calcula delta entre leituras corretas, mas precisa normalização.

Hipótese 3:

primeiro candle após reinício do backend pode carregar diferença acumulada exagerada.

Hipótese 4:

a escala correta para exibição visual deve ser diferente da escala usada internamente.

---

## 9. Recomendação futura

Criar uma auditoria técnica específica no backend para comparar:

- volume;
- volume_real;
- volume_normalizado_capado;
- volume_delta_estimado;
- volume_candle_estimado;
- volume_quantidade, se disponível;
- delta;
- saldo.

Somente depois definir PATCH_VOLUME_CANDLE_02.

Objetivo do patch futuro:

- preservar campos legados;
- não quebrar motores;
- criar campo visual seguro;
- separar volume bruto, volume normalizado e volume estimado;
- deixar claro no painel qual escala está sendo exibida.

---

## 10. Parecer

O CandleBuilderPainel está funcional em mercado aberto quanto à formação temporal dos candles.

Porém, o volume_candle_estimado ainda não está pronto para uso operacional visual confiável.

Status final:

VOLUME_CANDLE_ESTIMADO_REQUER_AUDITORIA_DE_ESCALA_ANTES_DE_PATCH

