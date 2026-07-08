# CHECKPOINT_CANDLEBUILDER_PAINEL_2026_07_07

## Status

CHECKPOINT_FECHADO

## Data

2026-07-07

## Tema

Validação observacional do CandleBuilderPainel AO_VIVO em mercado aberto.

---

## Resumo executivo

O CandleBuilderPainel foi validado observacionalmente em ambiente AO_VIVO, com dados vindos do Excel/RTD/Profit por meio da PLAN1_RTD_PAINEL.

O painel saiu do fallback 100.00 após reinício controlado do backend institucional e passou a receber dados reais do contrato WINQ26_F_0.

---

## Ambiente validado

- Backend: backend.server_institucional_v6:app
- Porta: 8001
- Frontend: React / localhost:3000
- Fonte operacional: RTD_EXCEL_PLAN1
- Origem temporal: RTD_EXCEL_AGREGADO
- Contrato: WINQ26_F_0
- Status do contrato: APROVADO
- Status do painel: OPERACIONAL_NAO_CERTIFICADO

---

## Evidências observacionais

### 1. Saída do fallback 100.00

Antes do restart do backend, o painel exibia candles em 100.00, volume 0, delta 0 e saldo 0.

Após restart controlado, o backend passou a entregar preço real, VWAP, delta, saldo e volume_real.

### 2. Timeframe 2_MIN

Validado observacionalmente com intervalos de 120 segundos.

Status:

APROVADO_OBSERVACIONALMENTE

### 3. Timeframe 30s

Validado observacionalmente com intervalos de 30 segundos.

Status:

APROVADO_OBSERVACIONALMENTE

### 4. Timeframe 15s

Validado observacionalmente com intervalos de 15 segundos.

Status:

APROVADO_OBSERVACIONALMENTE

### 5. Retorno para 2_MIN

Após testes em 30s e 15s, o painel retornou corretamente para 2_MIN, mantendo intervalos de 120 segundos.

Status:

APROVADO_OBSERVACIONALMENTE

---

## Patches realizados e salvos no GitHub

### Identidade operacional do gráfico

Commit:

3da14fa TRIN exibe identidade operacional no grafico

Resultado:

O painel passou a exibir modo, fonte, timeframe, status e contrato.

### Segundos dinâmicos no gráfico

Commit:

81f4a9 TRIN ajusta segundos dinamicos no grafico

Resultado:

O gráfico passou a ajustar a exibição de segundos conforme o timeframe:
- 15s e 30s: segundos visíveis
- 1_MIN ou maior: visual limpo

### Auditoria do volume

Commit:

fd6b11 TRIN registra auditoria do volume do CandleBuilder

Resultado:

Foi identificada a causa do volume travado em 5000: o leitor institucional normaliza e limita volume_trin em 5000.

### Volume estimado no backend

Commit:

f22ee43 TRIN adiciona volume estimado ao CandleBuilder

Resultado:

Foram adicionados campos novos sem alterar o volume legado:
- volume_normalizado_capado
- volume_real
- volume_delta_estimado
- volume_candle_estimado
- volume_tipo

### Volume estimado no painel

Commit:

da407f4 TRIN exibe volume estimado no painel

Resultado:

O painel passou a exibir o volume normalizado e o volume estimado do candle dentro do bloco Fonte Operacional.

---

## Ressalvas

Este checkpoint não homologa histórico oficial.

O CandleBuilderPainel permanece com status:

OPERACIONAL_NAO_CERTIFICADO

O painel usa snapshots RTD/Excel agregados para visualização operacional.

Os timeframes 15s e 30s foram observados funcionando no painel, mas a fonte TT_RAW/Plan2 permanece como diagnóstico apenas e ainda depende do Bastião TT Peneirador para uso estruturado.

---

## Decisão arquitetural preservada

O CandleBuilderPainel não substitui:

- Zé do Eucrázio
- Fiscal Temporal
- Bernardo
- Historiador
- Biblioteca Histórica oficial

Ele permanece como painel operacional AO_VIVO.

---

## Próximas etapas recomendadas

1. Criar modo Replay temporal correto, com formação progressiva de candle.
2. Auditar TT_RAW e Bastião TT Peneirador.
3. Limpar encoding visual do App.js.
4. Documentar contrato oficial do CandleBuilderPainel.
5. Validar novamente em mercado aberto após qualquer alteração estrutural.
6. Manter DIARIO e SEMANAL reservados por governança.

---

## Parecer final

O CandleBuilderPainel apresentou evolução relevante e está operacional para observação em tempo real.

A validação do dia confirmou que o painel consegue:
- receber dado real AO_VIVO;
- respeitar timeframes de 2_MIN, 30s e 15s;
- alternar timeframes sem quebrar o gráfico;
- exibir identidade operacional;
- preservar volume legado;
- exibir volume estimado do candle.

Status final:

APROVADO_OBSERVACIONALMENTE_COM_RESSALVAS

