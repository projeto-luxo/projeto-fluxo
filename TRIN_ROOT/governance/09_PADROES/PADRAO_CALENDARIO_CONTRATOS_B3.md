# PADRAO — Calendario B3 de Contratos TRIN

## Status
MODELO OFICIAL - AGUARDANDO PREENCHIMENTO POR FONTE B3

## Objetivo
Definir o formato oficial do calendario de contratos futuros usado pelo TRIN.

Este arquivo nao deve ser preenchido por chute.
As datas devem vir de fonte oficial B3 ou de importador/validador que consulte fonte oficial.

## Fonte oficial esperada
- Calendario de vencimentos de contratos financeiros da B3
- Calendario de negociacao/feriados da B3
- Regras oficiais do produto negociado

## Principio
Regra matematica ajuda, mas nao substitui calendario oficial.

Exemplo:
O WIN vence em meses pares, na quarta-feira mais proxima do dia 15.
Mas se houver feriado, ausencia de sessao ou excecao operacional, prevalece a data oficial publicada.

## Responsabilidades

### calendario_contratos_b3.csv
Armazena datas oficiais de vencimento, UDN, LF e contrato correspondente.

### ContratoAtivoResolver
Consulta o calendario e resolve qual contrato deveria estar ativo na data operacional.

### Bastiao
Valida se o contrato resolvido pode ser usado.

### Atualizador Excel
Aplica no Excel somente contrato aprovado.

## Regra de ouro
Nenhum contrato deve ser considerado oficial apenas porque foi digitado manualmente.
Toda linha deve ter fonte, data de revisao e status de confiabilidade.
