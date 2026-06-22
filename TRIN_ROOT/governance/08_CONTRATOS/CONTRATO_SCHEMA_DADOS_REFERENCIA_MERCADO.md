# CONTRATO_SCHEMA_DADOS_REFERENCIA_MERCADO.md

## Status

OFICIAL_EM_DEFINICAO  
Versao: 1.0  
Projeto: TRIN  
Pasta: governance/08_CONTRATOS  

---

## 1. Missao

Este contrato define o schema oficial dos dados de referencia de mercado usados pelo TRIN.

Ele separa:

- fonte primaria oficial;
- fonte operacional;
- contrato negociado;
- escala de preco;
- escala de volume;
- tick minimo;
- multiplicador;
- valor por ponto;
- vencimento;
- ajuste diario;
- referencias complementares.

Este schema nao gera sinal, nao corrige candle, nao certifica historico e nao substitui fonte oficial.

---

## 2. Responsabilidade unica

Definir os campos oficiais que descrevem as referencias de mercado de cada ativo e contrato usado pelo TRIN.

---

## 3. Campos oficiais

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---:|---|
| ativo | texto | sim | Ativo normalizado usado internamente pelo TRIN. |
| ativo_original | texto | sim | Codigo original recebido da fonte operacional. |
| contrato | texto | sim | Codigo oficial do contrato negociado. |
| contrato_rtd | texto | sim | Codigo usado na captura RTD/Profit/Excel. |
| tipo_contrato | texto | sim | Tipo do contrato: MINI_INDICE, INDICE_CHEIO, MINI_DOLAR, DOLAR_CHEIO ou outro aprovado. |
| data_inicio_validade | data | sim | Data inicial em que esta referencia passa a valer. |
| data_fim_validade | data | nao | Data final de validade da referencia, quando conhecida. |
| vencimento | data | sim | Data de vencimento do contrato. |
| status_contrato | texto | sim | ATIVO, ROLAGEM, VENCIDO ou ARQUIVADO. |
| tick_minimo | decimal | sim | Menor variacao minima de preco permitida para o contrato. |
| valor_por_ponto | decimal | sim | Valor financeiro de cada ponto por contrato, quando aplicavel. |
| multiplicador | decimal | sim | Multiplicador financeiro do contrato. |
| escala_preco | texto | sim | PONTOS, REAIS, TAXA, MILHAR ou outra escala aprovada. |
| escala_volume | texto | sim | CONTRATOS, QUANTIDADE ou FINANCEIRO. |
| ajuste_diario | booleano | sim | Indica se o ativo possui ajuste diario oficial. |
| preco_ajuste | decimal | nao | Preco de ajuste oficial, quando aplicavel. |
| ptax_referencia | decimal | nao | PTAX de referencia, quando aplicavel. |
| fonte_primaria | texto | sim | Fonte oficial da especificacao, como B3 ou BCB. |
| fonte_operacional | texto | sim | Fonte operacional usada pelo TRIN, como Profit/RTD/Excel. |
| status_referencia | texto | sim | OFICIAL, PENDENTE_HOMOLOGACAO, EM_REVISAO ou OBSOLETA. |
| observacao | texto | nao | Campo livre para ressalvas e contexto. |

---

## 4. Valores permitidos

### status_contrato

- ATIVO
- ROLAGEM
- VENCIDO
- ARQUIVADO

### status_referencia

- OFICIAL
- PENDENTE_HOMOLOGACAO
- EM_REVISAO
- OBSOLETA

---

## 5. Regras arquiteturais

1. Profit, RTD e Excel sao fontes operacionais, nao fonte oficial de especificacao.
2. A fonte primaria deve ser B3, BCB ou documento oficial equivalente.
3. O CandleBuilder nao deve decidir tick, multiplicador, escala, vencimento ou ajuste.
4. O Fiscal Temporal nao deve inventar dados de referencia de mercado.
5. O Bernardo deve preservar rastreabilidade da referencia usada.
6. O Historiador deve tratar estes dados como contexto, nao como evidencia operacional isolada.
7. Contrato vencido nao deve contaminar contrato ativo.
8. Periodo de rolagem deve ser identificado explicitamente.
9. Toda referencia deve ter status de homologacao.
10. Mudanca em referencia de mercado deve ser registrada em commit proprio.

---

## 6. Fora do escopo

Este schema nao deve:

- buscar dados automaticamente na B3;
- buscar PTAX automaticamente no BCB;
- corrigir historico;
- certificar candles;
- gerar sinal operacional;
- definir entrada, stop, parcial ou alvo;
- substituir o contrato principal de dados de referencia de mercado.

---

## 7. Consumidores previstos

- Bernardo
- Historiador
- Motor de Confluencia
- Fiscal Temporal
- CandleBuilderPainel
- Rotinas futuras de rolagem
- Rotinas futuras de validacao de especificacao

---

## 8. Observacao final

Este arquivo define apenas a forma oficial dos dados de referencia.

A base real de referencias de mercado devera ser criada em etapa separada, com auditoria propria, fonte primaria e rastreabilidade.
