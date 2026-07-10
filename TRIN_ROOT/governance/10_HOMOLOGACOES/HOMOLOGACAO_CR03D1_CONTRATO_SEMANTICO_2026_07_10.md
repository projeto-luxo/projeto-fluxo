# HOMOLOGAÇÃO CR-03D1 — CONTRATO SEMÂNTICO DELTA / SALDO

**Projeto:** TRIN
**Data:** 10/07/2026
**Status:** HOMOLOGADO TECNICAMENTE
**Git de partida:** 9c8ef8

---

## 1. ESCOPO

O CR-03D1 publicou metadados semânticos de Delta e Saldo no candle canônico.

Esta etapa não alterou:

- AggressionEngine;
- ConfluenceEngine;
- scores;
- sinais;
- regras de entrada;
- calibragem;
- frontend.

---

## 2. ARQUIVOS ALTERADOS

- backend/server_institucional_v6.py
- backend/replay_diagnostico.py

---

## 3. CAMPOS PUBLICADOS

- delta_fonte
- saldo_fonte
- delta_saldo_relacao
- delta_saldo_independentes
- saldo_fallback_delta
- fluxo_agressor_canonico
- fluxo_agressor_fonte
- fluxo_agressor_status

---

## 4. TESTES AUTOMATIZADOS

Foram aprovados oito cenários:

1. AO VIVO equivalente;
2. AO VIVO divergente;
3. fallback sem dados;
4. Replay com saldo real;
5. Replay com agressao_saldo;
6. Replay sem saldo;
7. normalização canônica do Replay;
8. agregação temporal do Replay.

Resultado: 8 de 8 aprovados.

---

## 5. VALIDAÇÃO AO VIVO

Resultado observado:

- modo_dados = AO_VIVO;
- delta_fonte = RTD_EXCEL_I2_DERIVADO_L2;
- saldo_fonte = RTD_EXCEL_J2_TOPICO_103;
- delta_saldo_relacao = EQUIVALENTES_OBSERVADOS;
- delta_saldo_independentes = false;
- saldo_fallback_delta = false;
- fluxo_agressor_status = CANONICO_DISPONIVEL.

Resultado: APROVADO.

---

## 6. VALIDAÇÃO REPLAY SEM DELTA E SALDO

O Replay declarou explicitamente:

- REPLAY_CSV_SEM_DELTA;
- REPLAY_CSV_SEM_SALDO;
- delta_saldo_relacao = SEM_DADOS;
- delta_saldo_independentes = false;
- saldo_fallback_delta = false.

Nenhum dado foi inventado.

Resultado: APROVADO.

---

## 7. VALIDAÇÃO REPLAY COM DELTA E SALDO REAIS

Arquivo testado:

memoria/TRIN_MEMORIA_2026_06_16.csv

Resultado observado:

- delta = 1488;
- saldo = 1488;
- delta_fonte = REPLAY_AGREGADO:REPLAY_CSV_CAMPO_DELTA;
- saldo_fonte = REPLAY_AGREGADO:REPLAY_CSV_CAMPO_SALDO;
- delta_saldo_relacao = EQUIVALENTES_OBSERVADOS;
- delta_saldo_independentes = false;
- saldo_fallback_delta = false;
- fluxo_agressor_canonico = 1488;
- fluxo_agressor_status = CANONICO_DISPONIVEL.

Resultado: APROVADO.

---

## 8. REGRESSÃO PÓS-REPLAY

Após interromper o Replay, o sistema retornou corretamente para AO_VIVO.

Resultado observado:

- replay_ativo = false;
- modo_dados = AO_VIVO;
- fontes RTD restauradas;
- relação EQUIVALENTES_OBSERVADOS preservada;
- fallback desativado;
- fluxo canônico disponível.

Resultado: APROVADO.

---

## 9. SINTAXE E INTEGRIDADE

A compilação Python dos dois arquivos foi aprovada.

O Git apresentou somente os dois arquivos autorizados como modificados.

---

## 10. LIMITAÇÃO DESTA HOMOLOGAÇÃO

O CR-03D1 publica proveniência e relação semântica.

Ele ainda não remove o peso duplicado dos motores.

AggressionEngine e ConfluenceEngine permanecem sob a ressalva registrada no laudo CR-03D.

---

## 11. RESULTADO FINAL

CR-03D1 HOMOLOGADO TECNICAMENTE.

Próxima etapa autorizada:

CR-03D2 — adequar o AggressionEngine para consumir apenas uma evidência quando Delta e Saldo não forem independentes.
