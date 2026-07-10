# HOMOLOGAÇÃO CR-03D2 — AGGRESSION ENGINE SEM DUPLICIDADE

**Projeto:** TRIN
**Data:** 10/07/2026
**Status:** HOMOLOGADO TECNICAMENTE
**Git de partida:** 2054322

---

## 1. ESCOPO

O CR-03D2 adequou o AggressionEngine para consumir uma única evidência
quando Delta e Saldo não forem semanticamente independentes.

Os valores brutos Delta e Saldo foram preservados.

Não foram alterados:

- ConfluenceEngine;
- frontend;
- planilha RTD;
- limites de frequência;
- limites de explosão;
- regras de entrada;
- calibragem.

---

## 2. ARQUIVOS ALTERADOS

- core/aggression_engine.py
- backend/server_institucional_v6.py

---

## 3. COMPORTAMENTO IMPLEMENTADO

Quando delta_saldo_independentes = false:

- o motor utiliza fluxo_agressor_canonico uma única vez;
- modo_evidencia_agressao = CANONICA_UNICA;
- fluxo_agressor_utilizado identifica o valor consumido;
- score_base_agressao publica a base do cálculo;
- Delta e Saldo não recebem peso duplicado.

Quando Delta e Saldo forem independentes, o comportamento legado permanece
disponível.

---

## 4. TESTES AUTOMATIZADOS

Foram aprovados 12 cenários:

1. compatibilidade legada independente;
2. frequência sem peso duplicado;
3. score legado preservado para independentes;
4. score canônico sem duplicidade;
5. persistência por evidência canônica;
6. saldo derivado não duplica peso;
7. ausência de dados permanece neutra;
8. explosão independente preservada;
9. explosão canônica única;
10. limite de explosão não recalibrado;
11. baseline real reduz duplicidade pela metade;
12. backend encaminha contrato aos três cálculos.

Resultado: 12 de 12 aprovados.

---

## 5. BASELINE AO VIVO ANTES DA CORREÇÃO

A baseline real apresentou:

- Delta e Saldo equivalentes;
- score de agressão próximo de 134,8;
- persistência compradora de 100 por cento;
- evidência duplicada no cálculo.

---

## 6. VALIDAÇÃO AO VIVO APÓS A CORREÇÃO

Resultado observado:

- delta = 354769;
- saldo = 354769;
- fluxo_agressor_canonico = 354769;
- modo_evidencia_agressao = CANONICA_UNICA;
- fluxo_agressor_utilizado = 354769;
- score_base_agressao = 35,4769;
- score_agressao = 70,95.

O score legado teórico seria aproximadamente 141,91.

Resultado: peso duplicado removido e validação AO VIVO aprovada.

---

## 7. VALIDAÇÃO REPLAY REAL

Arquivo utilizado:

memoria/TRIN_MEMORIA_2026_06_16.csv

Resultado observado:

- delta = 1488;
- saldo = 1488;
- relação = EQUIVALENTES_OBSERVADOS;
- independentes = false;
- fluxo canônico = 1488;
- modo do motor = CANONICA_UNICA;
- score novo esperado = 0,30;
- score novo recebido = 0,30;
- score legado teórico = 0,60.

Resultado: duplicidade removida pela metade e Replay aprovado.

---

## 8. RETORNO PÓS-REPLAY

Após a parada do Replay:

- replay_ativo = false;
- modo_dados = AO_VIVO;
- estado interno do Replay foi limpo;
- estado operacional foi reinicializado.

Resultado: APROVADO.

---

## 9. LIMITES E CALIBRAGEM

Nenhum limite foi recalibrado.

A leitura AGRESSÃO NEUTRA no Replay com score 0,30 é coerente com o limite
atual de 8 pontos.

A calibragem permanece bloqueada até a conclusão das correções semânticas
dos consumidores seguintes.

---

## 10. RESULTADO FINAL

CR-03D2 HOMOLOGADO TECNICAMENTE.

O AggressionEngine deixou de contar duas vezes Delta e Saldo quando o
contrato semântico informar que não são independentes.

Próxima etapa autorizada:

CR-03D3 — adequar o ConfluenceEngine para não interpretar equivalência como
confirmação independente.
