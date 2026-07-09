# AUDITORIA PRE-PATCH — BASTIAO TT PENEIRADOR

## Status

AUDITORIA_PRE_PATCH

Data: 2026-07-09  
Projeto: TRIN  
Modulo: BASTIAO_TT_PENEIRADOR  
Tema: Peneiramento tecnico do Times & Trades RAW

---

## 1. Objetivo

Registrar a auditoria previa antes de implementar qualquer codigo do BASTIAO_TT_PENEIRADOR.

Esta auditoria nao altera codigo.

---

## 2. Confluencia documental

Esta auditoria deriva de:

- governance/08_CONTRATOS/CONTRATO_BASTIAO_TT_PENEIRADOR.md
- governance/02_AUDITORIAS/AUDITORIA_TT_RTD_CAPTURA_EXPERIMENTAL.md
- governance/02_AUDITORIAS/AUDITORIA_PRE_PATCH_PAINEL_TT_RAW_DIAGNOSTICO.md
- governance/06_CHECKPOINTS/CHECKPOINT_CANDLEBUILDER_PAINEL_2026_07_07.md

Esta auditoria nao altera:

- Zé do Eucrázio
- Fiscal Temporal
- Bernardo
- Historiador
- Motor de Confluencia
- Replay diagnostico
- CandleBuilder

---

## 3. Contexto observado

Foi criada captura experimental de Times & Trades bruto via Excel/RTD.

A aba TT apresentou estrutura observada:

- C1 = hora com milissegundo
- C2 = compradora
- C3 = preco
- C4 = quantidade
- C5 = vendedora
- C6 = agressor / tipo do negocio
- C7 = agente agressor

Exemplo de linha valida observada:

18:31:24.112 ; compradora ; 172665 ; quantidade ; vendedora ; Leilao ; agente

Tambem foram observadas linhas casca/lixo no RAW:

- hora_tt = "-"
- preco = 0
- quantidade = 0
- agressor = "-"

---

## 4. Resultado da captura bruta recente

Arquivo observado:

TRIN_HISTORICO/000_TT_BRUTO/WINQ26/2026-07-09/TT_RAW_WINQ26_20260709.csv

Resumo observado:

- total_linhas_csv: 500
- primeiro_horario: 18:31:24.112
- ultimo_horario: "-"
- contrato: WINQ26
- agressores: "-", "Leilao"
- preco_min: 0
- preco_max: 172665
- qtd_total: 1776
- status_certificacao: RAW_NAO_CERTIFICADO

Parecer: o gravador capturou a filmagem bruta, mas a filmagem contem linhas validas e linhas casca do Excel.

---

## 5. Problema arquitetural

O TT RAW nao pode ser usado diretamente por consumidores operacionais, pois contem:

- linhas casca do Excel;
- snapshots repetidos;
- duplicidade observacional;
- repeticoes reais que podem parecer duplicidade;
- duplicidades falsas que podem parecer repeticao real;
- eventos de leilao;
- eventos de pregao;
- incerteza sequencial;
- ausencia de ID unico oficial do negocio.

---

## 6. Separacao de responsabilidades

### Gravador TT Bruto

Responsabilidade:

- capturar a filmagem bruta;
- preservar horario, preco, quantidade e campos disponiveis;
- gravar RAW_NAO_CERTIFICADO;
- nao apagar RAW;
- nao fazer julgamento pesado.

Nao deve:

- virar peneirador;
- certificar dado;
- reconstruir candle;
- alimentar entrada operacional.

### Bastiao TT Peneirador

Responsabilidade:

- ler TT RAW;
- classificar linhas;
- separar validos provaveis, lixo, duplicados provaveis e incertezas;
- gerar TT_PENEIRADO_NAO_CERTIFICADO;
- manter rastreabilidade com o RAW.

Nao deve:

- apagar RAW;
- certificar;
- reconstruir candle;
- gerar sinal;
- alimentar Motor diretamente.

### Fiscal TT / Fiscal Temporal futuro

Responsabilidade:

- certificar integridade quando houver criterio suficiente.

### Zé TT Reconstrutor futuro

Responsabilidade:

- reconstruir candle por negocio somente a partir de TT peneirado e auditado.

---

## 7. Classificacoes minimas exigidas

O BASTIAO_TT_PENEIRADOR deve classificar linhas em categorias como:

- NEGOCIO_VALIDO_PROVAVEL
- LINHA_CASCA_EXCEL
- TIMESTAMP_INVALIDO
- PRECO_INVALIDO
- QUANTIDADE_INVALIDA
- DUPLICADO_PROVAVEL
- REPETICAO_REAL_POSSIVEL
- EVENTO_LEILAO
- EVENTO_PREGAO
- INCERTEZA_SEQUENCIAL
- FONTE_INSUFICIENTE

---

## 8. Criterios iniciais de lixo/casca

Uma linha pode ser classificada como LINHA_CASCA_EXCEL quando apresentar:

- hora_tt vazia ou "-"
- preco vazio, "-", 0 ou invalido
- quantidade vazia, "-", 0 ou invalida

Essas linhas devem ser removidas da saida peneirada, mas preservadas em relatorio/rejeitados.

---

## 9. Criterios iniciais de duplicidade

Duplicidade em TT RAW nao pode ser tratada de forma simplista.

Mesmo horario, preco e quantidade podem significar:

- repeticao real de negocios semelhantes;
- duplicidade de snapshot;
- eco do Excel/RTD;
- incerteza por ausencia de ID unico.

Portanto, o BASTIAO_TT_PENEIRADOR deve preferir classificar incerteza a apagar negocio real.

---

## 10. Riscos

### Risco 1 — apagar negocio real

Se o peneirador for agressivo demais, pode remover negocios verdadeiros.

Mitigacao:

- preservar categoria REPETICAO_REAL_POSSIVEL;
- manter rejeitados;
- manter rastreabilidade com hash_evento e row_excel.

### Risco 2 — manter duplicidade falsa

Se o peneirador for frouxo demais, pode inflar volume e distorcer candles futuros.

Mitigacao:

- classificar DUPLICADO_PROVAVEL;
- gerar resumo de duplicidade;
- exigir auditoria antes de uso em candle.

### Risco 3 — transformar TT em operacional cedo demais

Mitigacao:

- status TT_PENEIRADO_NAO_CERTIFICADO;
- uso DIAGNOSTICO_APENAS;
- candle_oficial false.

---

## 11. Saidas esperadas do futuro patch

O patch futuro deve gerar, no minimo:

- TT_PENEIRADO_NAO_CERTIFICADO.csv
- TT_REJEITADOS.csv
- TT_INCERTEZAS.csv
- RESUMO_BASTIAO_TT_PENEIRADOR.csv
- MANIFESTO_BASTIAO_TT_PENEIRADOR.json
- RELATORIO_BASTIAO_TT_PENEIRADOR.txt

---

## 12. Parecer pre-patch

A implementacao do BASTIAO_TT_PENEIRADOR e arquiteturalmente necessaria.

Aprovado para proximo passo somente se respeitar:

- responsabilidade unica;
- nao alterar RAW;
- nao certificar;
- nao gerar candle;
- nao alimentar decisao operacional;
- preservar incertezas;
- manter rastreabilidade.

---

## 13. Proximo passo

Criar patch pequeno do BASTIAO_TT_PENEIRADOR v0, preferencialmente em modulo separado, lendo TT RAW e produzindo saidas diagnosticas nao certificadas.

Nenhuma alteracao deve ser feita no Zé, Fiscal, Bernardo, Motor, Replay ou CandleBuilder nesta etapa.

---

## Principio final

O gravador filma.

O Bastiao peneira.

O Fiscal certifica.

O Ze reconstrói.

O operador decide.
