# DA CR-03D — CONTRATO SEMÂNTICO CANÔNICO DELTA / SALDO

**Projeto:** TRIN
**Data:** 10/07/2026
**Status:** APROVADO PARA IMPLEMENTAÇÃO CONTROLADA
**Base:** Laudo CR-03D e auditoria pré-patch
**Git de referência:** 786c29d

---

## 1. Problema

Delta e saldo foram transportados corretamente, mas apresentaram equivalência
em 60 de 60 amostras válidas.

Os motores atuais tratam os campos como evidências independentes, produzindo
risco de peso duplicado.

---

## 2. Proprietário

O candle canônico no backend é o proprietário da normalização semântica.

O leitor RTD fornece origem física.

O Replay declara existência, ausência ou derivação dos campos.

AggressionEngine e ConfluenceEngine consomem dados já classificados.

O frontend apenas apresenta valores, proveniência e status.

---

## 3. Ponto de normalização

A normalização deve ocorrer depois da obtenção do candle da fonte e antes de o
candle canônico alimentar histórico e motores.

Fluxo:

FONTE -> NORMALIZAÇÃO SEMÂNTICA -> CANDLE CANÔNICO -> MOTORES -> PAYLOAD

---

## 4. Campos obrigatórios

- delta
- saldo
- volume_saldo
- delta_fonte
- saldo_fonte
- delta_saldo_relacao
- delta_saldo_independentes
- saldo_fallback_delta
- fluxo_agressor_canonico
- fluxo_agressor_fonte
- fluxo_agressor_status

---

## 5. Estados oficiais

- INDEPENDENTES
- EQUIVALENTES_OBSERVADOS
- SALDO_DERIVADO_DELTA
- DELTA_DERIVADO_SALDO
- INDETERMINADO
- SEM_DADOS

---

## 6. Regra AO VIVO atual

Enquanto o contrato Excel permanecer como auditado:

- delta_fonte = RTD_EXCEL_I2_DERIVADO_L2
- saldo_fonte = RTD_EXCEL_J2_TOPICO_103
- delta_saldo_relacao = EQUIVALENTES_OBSERVADOS
- delta_saldo_independentes = false
- saldo_fallback_delta = false

O fluxo agressor canônico deve priorizar volume_saldo quando compra, venda e
saldo de agressão estiverem disponíveis.

---

## 7. Regra REPLAY

Quando o CSV possuir saldo real:

- saldo_fallback_delta = false
- saldo_fonte deve identificar o campo encontrado

Quando o CSV não possuir saldo:

- saldo = delta
- saldo_fonte = REPLAY_FALLBACK_DELTA
- delta_saldo_relacao = SALDO_DERIVADO_DELTA
- delta_saldo_independentes = false
- saldo_fallback_delta = true
- fluxo_agressor_canonico = delta

Nenhum fallback pode permanecer silencioso.

---

## 8. Sequência de implementação

### CR-03D1

Publicar metadados semânticos no candle canônico e declarar o fallback do
Replay.

Não altera scores nem limites.

### CR-03D2

Fazer o AggressionEngine consumir uma única evidência quando delta e saldo não
forem independentes.

### CR-03D3

Fazer o ConfluenceEngine impedir confirmação dupla por equivalência ou
derivação.

### CR-03D4

Exibir proveniência e relação semântica no cockpit.

### CR-03D5

Executar testes AO VIVO, REPLAY, regressão, cache e troca de modo.

---

## 9. Proibições

- não apagar delta;
- não apagar saldo;
- não modificar a planilha RTD;
- não recalibrar nesta etapa;
- não alterar score durante CR-03D1;
- não tratar fallback como fonte independente;
- não corrigir a semântica apenas no frontend;
- não misturar memória AO VIVO e REPLAY.

---

## 10. Testes obrigatórios

- AO VIVO com campos equivalentes;
- AO VIVO com divergência simulada;
- Replay com saldo real;
- Replay sem saldo;
- Replay com agressao_saldo;
- candle fallback sem dados;
- agregação temporal preservando metadados;
- troca AO VIVO para REPLAY;
- troca REPLAY para AO VIVO;
- cache operacional sem reprocessamento indevido;
- valores brutos preservados;
- Git limpo antes e depois.

---

## 11. Decisão

O patch CR-03D1 está arquiteturalmente autorizado.

A autorização limita-se à publicação do contrato semântico e da proveniência.

AggressionEngine, ConfluenceEngine, regras de entrada, calibragem e cockpit
permanecem inalterados nesta primeira etapa.
