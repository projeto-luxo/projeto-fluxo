# AUDITORIA_STATUS_FONTE_RTD_MERCADO_ABERTO_2026_07_08

## Status

AUDITORIA_ABERTA_SEM_PATCH

## Data

2026-07-08

## Tema

Refinamento do status_fonte no CandleBuilderPainel em mercado aberto.

---

## 1. Confluência documental

Esta auditoria complementa:

- AUDITORIA_RTD_ESTAGNADO_CANDLEBUILDER_2026_07_07
- VALIDACAO_MERCADO_ABERTO_CANDLEBUILDER_2026_07_08
- Commits:
  - a775a03 TRIN bloqueia candle novo com RTD estagnado
  - ce0bfda TRIN exibe status da fonte RTD no painel
  - 810f30a TRIN registra validacao parcial do CandleBuilder em mercado aberto
  - 9c9b68 TRIN complementa validacao dos timeframes curtos em mercado aberto

Esta auditoria não altera código.

---

## 2. Contexto

Durante mercado fechado, o patch de detecção de RTD estagnado foi necessário para impedir que o backend criasse candles falsos apenas porque o relógio avançava.

Durante mercado aberto, foi confirmado que o RTD_EXCEL_PLAN1 voltou a entregar dados reais para o painel.

Contrato observado:

WINQ26_F_0

Timeframes testados:

- 2_MIN
- 30s
- 15s

---

## 3. Resultado validado

Foram aprovados em mercado aberto:

- leitura real via RTD_EXCEL_PLAN1;
- contrato WINQ26_F_0;
- formação de candles 2_MIN com intervalo de 120 segundos;
- formação de candles 30s com intervalo de 30 segundos;
- formação de candles 15s com coerência temporal;
- gráfico recebendo candles reais;
- preço, delta, saldo e volume mudando em mercado aberto.

---

## 4. Problema identificado

Em alguns momentos, mesmo com alteração real de:

- preço;
- volume;
- delta;
- saldo;

o painel temporal marcou:

- status_fonte: RTD_ESTAGNADO
- fonte_estagnada: true
- status_painel: OPERACIONAL_NAO_CERTIFICADO_FONTE_ESTAGNADA

Isso indica que o detector está sensível demais para mercado aberto.

---

## 5. Interpretação técnica

Uma leitura RTD repetida isolada não deve ser classificada imediatamente como RTD_ESTAGNADO.

Em mercado aberto, é normal ocorrer:

- pequena pausa entre ticks;
- repetição momentânea do snapshot;
- atualização de alguns campos antes de outros;
- ausência de mudança por poucos segundos.

Isso não significa necessariamente falha da fonte.

---

## 6. Regra proposta para refinamento futuro

Separar os estados:

### RTD_ATUALIZANDO

Quando há alteração real recente em preço, volume, delta, saldo ou VWAP.

### SEM_NOVO_TICK_NA_LEITURA

Quando a leitura atual veio igual à anterior, mas ainda dentro de uma janela curta aceitável.

### RTD_ESTAGNADO_CONFIRMADO

Quando a assinatura RTD permanecer igual por tempo superior ao limite definido.

Sugestão inicial:

- abaixo de 30 segundos sem mudança: SEM_NOVO_TICK_NA_LEITURA
- acima de 30 ou 60 segundos sem mudança: RTD_ESTAGNADO_CONFIRMADO

O tempo exato deve ser definido após nova auditoria.

---

## 7. O que não deve ser feito

Não voltar ao comportamento antigo de criar candle falso com fonte parada.

Não remover a proteção contra RTD estagnado.

Não misturar este patch com auditoria de volume_candle_estimado.

Não alterar Zé do Eucrázio.

Não alterar Fiscal Temporal.

Não alterar Bernardo.

Não alterar Historiador.

Não promover CandleBuilderPainel a histórico oficial.

---

## 8. Recomendação

Criar futuramente:

PATCH_CANDLEBUILDER_03_STATUS_FONTE_RTD

Missão do patch:

- manter proteção contra candle falso;
- evitar carimbo prematuro de RTD_ESTAGNADO;
- criar estado intermediário SEM_NOVO_TICK_NA_LEITURA;
- marcar RTD_ESTAGNADO apenas após janela temporal confirmada;
- manter status do painel como OPERACIONAL_NAO_CERTIFICADO.

---

## 9. Parecer

O mecanismo de proteção contra RTD estagnado foi arquiteturalmente correto e impediu a criação de candles falsos.

Porém, em mercado aberto, o status_fonte precisa distinguir pausa curta de leitura e estagnação confirmada.

Status final:

STATUS_FONTE_RTD_REQUER_REFINAMENTO_CONTROLADO

