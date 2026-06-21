# EXPERIMENTO — Atualizacao de Contrato RTD via Config

## Status
EXPERIMENTAL

## Objetivo
Provar que o TRIN consegue trocar o contrato usado nas formulas RTD do Excel a partir de uma fonte de configuracao externa.

## Resultado observado
O script conseguiu localizar formulas RTD no MARCO_ZERO_INSTITUCIONAL.xlsx e substituir o contrato:

WINM26_F_0 -> WINQ26_F_0

Foram encontradas 24 formulas RTD e alteradas 26 celulas/formulas.

## Importante
Este experimento ainda NAO representa a arquitetura final.

A arquitetura final devera usar:

Calendario B3 Oficial
-> ContratoAtivoResolver
-> Bastiao valida/certifica
-> Atualizador Excel aplica
-> Leitor RTD le
-> Backend/Painel exibem

## Limitacoes atuais
- O contrato ainda esta definido manualmente no CSV.
- O calendario B3 oficial ainda nao foi integrado.
- O Bastiao ainda nao esta validando automaticamente.
- O Excel foi alterado como planilha viva local.

## Decisao
Manter este script apenas como prova tecnica de que o Excel pode ser atualizado por automacao.
Nao tratar como solucao final de rolagem.
