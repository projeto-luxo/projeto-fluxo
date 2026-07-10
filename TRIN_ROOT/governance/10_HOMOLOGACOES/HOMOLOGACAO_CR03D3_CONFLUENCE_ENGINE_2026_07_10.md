# HOMOLOGAÇÃO CR-03D3 — CONFLUENCE ENGINE SEM CONFIRMAÇÃO DUPLICADA

**Projeto:** TRIN
**Data:** 10/07/2026
**Status:** HOMOLOGADO TECNICAMENTE
**Git de partida:** 5952cba

---

## 1. ESCOPO

O CR-03D3 adequou os motores de Confluência para respeitar o contrato
semântico Delta / Saldo.

Quando Delta e Saldo não forem independentes, o motor utiliza somente a
parcela canônica do fluxo.

Não foram alterados:

- AggressionEngine;
- backend;
- frontend;
- pesos históricos;
- limites;
- regras de entrada;
- bloqueio do Fiscal;
- calibragem.

---

## 2. ARQUIVOS ALTERADOS

- core/confluence_engine.py
- core/confluence_engine_v2.py

---

## 3. COMPORTAMENTO IMPLEMENTADO

Quando delta_saldo_independentes = false:

- modo_evidencia_fluxo = CANONICA_UNICA;
- o impacto utiliza fluxo_agressor_canonico / 20000;
- Delta e Saldo não constituem duas confirmações;
- Fluxo e Agressão são declarados como correlacionados;
- Agressão deixa de votar como confirmação direcional independente;
- valores brutos permanecem preservados.

Quando Delta e Saldo forem independentes, o comportamento legado permanece
disponível.

---

## 4. TESTES AUTOMATIZADOS

Foram aprovados 13 cenários:

1. legado independente preservado;
2. equivalentes usam parcela canônica única;
3. venda canônica preserva sinal;
4. ausência de dados permanece neutra;
5. correlação Fluxo / Agressão declarada;
6. Agressão independente preservada;
7. voto correlacionado não confirma direção duas vezes;
8. voto independente continua ativo;
9. bloqueio do Fiscal preservado;
10. baseline reduz contribuição do fluxo pela metade;
11. peso da Agressão não foi recalibrado;
12. backend encaminha contrato semântico;
13. motores oficial e V2 permanecem coerentes.

Resultado: 13 de 13 aprovados.

---

## 5. BASELINE ANTES DA CORREÇÃO

Com Delta e Saldo equivalentes em 15841:

- impacto do fluxo = 1,5841;
- peso do fluxo = 2,0;
- contribuição do fluxo = 3,1682;
- contribuição da Agressão = 0,9510;
- justificativa tratava Delta e Saldo como confirmação compradora.

---

## 6. VALIDAÇÃO REPLAY REAL

Arquivo utilizado:

memoria/TRIN_MEMORIA_2026_06_16.csv

Resultado observado:

- delta = 1488;
- saldo = 1488;
- fluxo_agressor_canonico = 1488;
- relação = EQUIVALENTES_OBSERVADOS;
- independentes = false;
- modo_evidencia_fluxo = CANONICA_UNICA;
- Fluxo e Agressão correlacionados = true;
- Agressão como confirmação independente = false;
- impacto recebido = 0,0744;
- impacto esperado = 0,0744;
- contribuição recebida = 0,1488;
- contribuição esperada = 0,1488;
- contribuição legada = 0,2976.

Resultado: contribuição duplicada removida pela metade.

---

## 7. CERTIFICAÇÃO TEMPORAL

O bloqueio do Fiscal foi preservado:

- qualidade = BLOQUEADO_POR_CERTIFICACAO;
- alerta = CONFLUENCIA_BLOQUEADA_PELO_FISCAL.

O CR-03D3 não liberou operacionalmente dados não certificados.

---

## 8. RETORNO PÓS-REPLAY

O Replay foi encerrado corretamente e o sistema retornou para AO_VIVO.

Resultado: APROVADO.

---

## 9. LIMITES E CALIBRAGEM

Nenhum peso ou limite foi recalibrado.

A redução observada decorre exclusivamente da remoção da duplicidade
semântica.

A calibragem permanece bloqueada.

---

## 10. RESULTADO FINAL

CR-03D3 HOMOLOGADO TECNICAMENTE.

Os motores de Confluência deixaram de tratar Delta e Saldo equivalentes como
duas confirmações independentes.

Próxima etapa autorizada:

CR-03D4 — apresentar proveniência e relação semântica no cockpit.
