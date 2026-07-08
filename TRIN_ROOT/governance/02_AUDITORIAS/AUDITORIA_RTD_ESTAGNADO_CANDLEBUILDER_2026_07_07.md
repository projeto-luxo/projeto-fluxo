# AUDITORIA_RTD_ESTAGNADO_CANDLEBUILDER_2026_07_07

## Status

AUDITORIA_FECHADA_COM_PATCH_APROVADO

## Data

2026-07-07

## Tema

Detecção de fonte RTD/Excel estagnada no CandleBuilderPainel.

---

## 1. Confluência documental obrigatória

Este documento não deve ser lido isoladamente.

Ele complementa os seguintes registros do TRIN:

- CHECKPOINT_CANDLEBUILDER_PAINEL_2026_07_07
- AUDITORIA_VOLUME_CANDLEBUILDER_PAINEL_2026_07_07
- Commit ed754bc — TRIN reconstrói gráfico quando histórico muda
- Commit a775a03 — TRIN bloqueia candle novo com RTD estagnado

Este documento não altera:

- Zé do Eucrázio
- Fiscal Temporal
- Bernardo
- Historiador
- Biblioteca Histórica oficial
- Regras de certificação histórica
- Regras de geração de fractais oficiais
- Regras de homologação do projeto

Escopo exato:

Este documento trata apenas do comportamento operacional AO_VIVO do CandleBuilderPainel quando a fonte RTD/Excel fica estagnada.

Regra vigente adicionada:

Timestamp do backend sozinho não prova candle novo.
Candle operacional do painel só deve nascer quando a fonte RTD/Excel entregar alteração real na assinatura da leitura.

Este documento não transforma o CandleBuilderPainel em fonte histórica oficial.

---

## 2. Contexto

Após o PATCH_GRAFICO_01, o gráfico deixou de apresentar falhas visuais do tipo histórico esburacado.

Porém, em mercado fechado, foi observado que o gráfico permanecia desenhando uma linha reta contínua.

A investigação mostrou que o backend continuava criando candles novos mesmo quando a fonte RTD/Excel não apresentava nenhuma alteração real.

---

## 3. Sintoma observado antes do patch

O histórico continuava crescendo em intervalos de 30 segundos, mesmo com todos os campos operacionais iguais:

- open
- high
- low
- close
- volume_candle_estimado
- delta
- saldo

Resultado confirmado antes do patch:

historico_cresceu : True
candles_novos     : 1
time_mudou        : True
preco_mudou       : False
volume_mudou      : False
delta_mudou       : False
saldo_mudou       : False

---

## 4. Diagnóstico

O problema não estava no gráfico.

O problema estava no backend, que usava o timestamp gerado pelo relógio do computador como parte prática da formação de novo candle.

O leitor institucional gera o campo time com o horário atual do backend.

Quando o mercado está fechado ou a fonte RTD fica congelada, o relógio continua andando, mas os dados de mercado não mudam.

Com isso, o backend criava candles novos apenas porque o tempo mudou, mesmo sem nova leitura efetiva do RTD/Excel.

---

## 5. Causa raiz

Causa raiz:

FONTE_RTD_ESTAGNADA_TRATADA_COMO_CANDLE_NOVO

O backend confundia tempo passando com mercado entregando dado novo.

---

## 6. Decisão arquitetural

A assinatura operacional da fonte RTD deve ignorar o campo time e considerar os campos reais de mercado.

O campo time é importante para exibição temporal, mas não pode ser usado sozinho como prova de novo candle operacional.

Campos usados na assinatura RTD:

- ativo
- open
- high
- low
- close
- ultimo
- volume_real
- delta
- saldo
- vwap
- vwap_real
- volume_compra
- volume_venda
- volume_saldo

---

## 7. Patch aplicado

Commit:

a775a03 TRIN bloqueia candle novo com RTD estagnado

Arquivo alterado:

backend/server_institucional_v6.py

Funções adicionadas:

- assinatura_fonte_rtd()
- fonte_rtd_estagnada()

Comportamento novo:

Se a assinatura RTD atual for igual à assinatura anterior:

- não cria candle novo;
- não alimenta engines;
- não adiciona no histórico;
- marca o último candle como fonte_estagnada=True;
- define status_fonte=RTD_ESTAGNADO;
- define status_painel=OPERACIONAL_NAO_CERTIFICADO_FONTE_ESTAGNADA.

---

## 8. Teste pós-patch

Após reinício do backend e novo teste com mercado fechado, o resultado foi:

historico_cresceu : False
candles_novos     : 0
time_mudou        : False
preco_mudou       : False
volume_mudou      : False
delta_mudou       : False
saldo_mudou       : False
status_fonte      : RTD_ESTAGNADO
fonte_estagnada   : True

---

## 9. Limites da homologação

Esta homologação não substitui validação em mercado aberto.

Com mercado aberto, ainda será necessário confirmar:

- se candles novos continuam nascendo quando preço, volume, delta ou saldo mudam;
- se o status volta para RTD_ATUALIZANDO;
- se o painel não bloqueia candles flats legítimos com alteração de volume ou agressão;
- se 15s, 30s e 2_MIN continuam funcionando corretamente;
- se o gráfico permanece contínuo sem candles artificiais.

---

## 10. Status final

PATCH_CANDLEBUILDER_02_APROVADO_EM_MERCADO_FECHADO

---

## 11. Parecer final

A auditoria comprovou que o TRIN precisava distinguir tempo de mercado de tempo de relógio.

A partir deste patch, o CandleBuilderPainel não registra candle novo apenas porque o relógio avançou.

Candle novo exige nova assinatura operacional da fonte RTD/Excel.

