# AUDITORIA_PRE_PATCH_FISCAL_CANDLE_INEXISTENTE_POR_LEILAO.md

## Status

AUDITORIA_PRE_PATCH  
Data: 2026-06-25  
Projeto: TRIN  
Modulo: Fiscal Temporal  
Arquivo alvo: intelligence/fiscal_temporal.py  
Tema: Tratamento de candles inexistentes por leilao  

---

## 1. Objetivo

Registrar a analise previa antes de alterar o Fiscal Temporal para reconhecer candles inexistentes por leilao.

Esta auditoria nao altera codigo.

---

## 2. Contexto

O Fiscal Temporal v4.2 identificou lacunas curtas no arquivo matriz WIN_1min_2026_2026.csv e classificou essas ausencias como:

LACUNA_CANDLE_AUSENTE

Essas ocorrencias foram atribuidas ao Ze do Eucrazio, gerando ordens de regeneracao.

Posteriormente, a Nelogica confirmou que os candles ausentes nao foram formados por causa de leiloes no ativo.

Portanto, a classificacao anterior detectou corretamente a ausencia temporal, mas atribuiu tratamento incompleto.

---

## 3. Arquivo oficial analisado

Arquivo:

intelligence/fiscal_temporal.py

Trechos relevantes identificados:

- linhas proximas de 276 a 322: definicao de criticidade por motivo;
- linhas proximas de 325 a 338: definicao de dependencia por motivo/responsavel;
- linhas proximas de 601 a 790: funcao classificar_lacunas;
- linhas proximas de 752 a 769: lacuna curta vira LACUNA_CANDLE_AUSENTE e ordem para ZE_DO_EUCRAZIO;
- linhas proximas de 1138 a 1150: ocorrencias reais sao filtradas e ordens para Ze sao gravadas em ordens_para_ze.csv.

---

## 4. Problema encontrado

A regra atual do Fiscal trata toda lacuna curta nao justificada pelo calendario como:

LACUNA_CANDLE_AUSENTE

com responsavel:

ZE_DO_EUCRAZIO

e acao recomendada:

REGENERAR_FRACTAL_A_PARTIR_DO_1_MIN

Essa regra e correta para lacunas curtas sem justificativa.

Porem, nao contempla o novo caso oficial:

CANDLE_INEXISTENTE_POR_LEILAO

---

## 5. Evidencia externa

A Nelogica confirmou:

- 22/01/2026: ativo em leilao entre 12:40:21 e 12:42:21, sem formacao do candle 12:41;
- 26/01/2026: leilao entre 11:30:41 e 11:33:10;
- 26/01/2026: novo leilao entre 11:33:16 e 11:35:16;
- ausencia dos candles nesses horarios esta dentro do esperado.

---

## 6. Cadastro criado

Foi criado cadastro operacional:

TRIN_HISTORICO/00_CERTIFICACOES/candles_inexistentes_por_leilao.csv

Foi criada copia versionada:

governance/09_PADROES/candles_inexistentes_por_leilao.csv

Campos principais:

- ativo_base
- contrato_operacional
- data
- hora
- motivo
- inicio_evento
- fim_evento
- fonte
- status
- observacao

---

## 7. Ponto de insercao recomendado

A nova regra deve ser aplicada dentro da funcao:

classificar_lacunas

antes do bloco atual de lacuna curta que gera:

LACUNA_CANDLE_AUSENTE

O Fiscal deve verificar se os candles intermediarios ausentes entre anterior e atual constam no cadastro de candles inexistentes por leilao.

Se todos os candles ausentes da lacuna curta estiverem justificados por leilao, a ocorrencia nao deve ser enviada ao Ze.

---

## 8. Nova classificacao recomendada

Motivo:

CANDLE_INEXISTENTE_POR_LEILAO

Status:

JUSTIFICADO_POR_EVENTO_DE_MERCADO

Responsavel:

EVENTO_MERCADO

Acao recomendada:

NENHUMA_ACAO_CORRETIVA

Certificacao:

JUSTIFICADO

Para fractais derivados:

LACUNA_HERDADA_JUSTIFICADA_POR_LEILAO

---

## 9. Riscos do patch

Riscos identificados:

1. marcar como justificada uma lacuna que nao esteja totalmente coberta pelo cadastro;
2. afetar outras lacunas curtas legitimas;
3. reduzir indevidamente ordens do Ze;
4. perder rastreabilidade da lacuna matriz;
5. alterar comportamento do Fiscal fora do caso Nelogica.

Mitigacao:

O patch deve ser restrito ao cadastro oficial.

Se a lacuna nao estiver no cadastro, a regra antiga deve permanecer intacta.

---

## 10. Criterio de sucesso

Apos o patch e reexecucao do Fiscal:

- candles inexistentes por leilao nao devem gerar ordem para Ze;
- as ausencias devem aparecer como justificadas;
- o Fiscal deve preservar rastreabilidade;
- demais lacunas nao cadastradas devem continuar sendo tratadas pela regra atual;
- ordens_para_ze.csv deve reduzir a cascata causada pelos eventos de leilao.

---

## 11. Parecer

Patch autorizado apenas se for pequeno, isolado e conservador.

Nao deve haver reescrita estrutural do Fiscal.

Nao deve haver alteracao no Ze, Bernardo ou Historiador nesta etapa.
