# README — Calendarios TRIN

## Arquivo principal
calendario_contratos_b3.csv

## Status atual
Estrutura criada.
Calendario ainda nao homologado.

## Motivo
O TRIN nao deve usar contrato ativo por chute nem por substituicao manual no Excel.

## Fluxo correto
Calendario B3 oficial
-> ContratoAtivoResolver
-> Bastiao valida
-> Atualizador Excel aplica
-> Leitor RTD le
-> Backend/Painel exibem

## Observacao importante
Este diretorio pode conter modelos e calendarios operacionais.
Antes de usar em decisao operacional, o calendario precisa ser certificado pelo Bastiao.
