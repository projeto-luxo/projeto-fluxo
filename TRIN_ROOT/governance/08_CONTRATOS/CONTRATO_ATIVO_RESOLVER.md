# CONTRATO — ContratoAtivoResolver TRIN

## Status
PROPOSTA ARQUITETURAL

## Missao
Resolver qual contrato futuro deve ser considerado ativo pelo TRIN em uma data operacional.

Este modulo nao executa leitura RTD.
Este modulo nao altera Excel.
Este modulo nao valida operacionalmente.
Este modulo apenas resolve o contrato esperado.

## Problema que resolve
O Excel RTD pode ficar preso em contrato antigo, como WINM26_F_0.

O TRIN precisa saber, antes da leitura, qual contrato deveria estar ativo segundo fonte oficial.

## Responsabilidade unica
Determinar o contrato esperado para um ativo base, uma data e um calendario oficial.

Exemplo:

Entrada:
ativo_base = WIN
data_referencia = 2026-06-20

Saida esperada:
contrato_visual = WINQ26
contrato_rtd = WINQ26_F_0

## Entradas
- ativo_base
- data_referencia
- calendario_contratos_b3.csv
- calendario_feriados_b3.csv, quando existir
- regras oficiais de vencimento/rolagem, quando documentadas

## Saidas
- ativo_base
- contrato_visual_esperado
- contrato_rtd_esperado
- mes_vencimento
- data_udn
- data_lf
- criterio_usado
- status_resolucao
- motivo

## Status possiveis
- RESOLVIDO
- NAO_RESOLVIDO
- CALENDARIO_AUSENTE
- CALENDARIO_INCOMPLETO
- DATA_FORA_DA_COBERTURA
- CONFLITO_DE_REGRA

## O que este modulo NAO deve fazer
- Nao deve editar Excel.
- Nao deve alterar formulas RTD.
- Nao deve ler Profit.
- Nao deve ler WebSocket.
- Nao deve liberar operacao.
- Nao deve substituir o Bastiao.
- Nao deve inventar calendario quando fonte oficial estiver ausente.

## Consumidores
- Bastiao
- Atualizador Excel RTD
- Backend institucional
- Governanca

## Fornecedores
- calendario_contratos_b3.csv
- calendario_feriados_b3.csv
- regras oficiais registradas em governanca

## Relacao com o Bastiao
O ContratoAtivoResolver calcula o contrato esperado.

O Bastiao valida se:
1. o contrato esperado esta coerente;
2. o contrato aplicado no Excel bate com o esperado;
3. o contrato lido pelo backend bate com o esperado;
4. a leitura pode ser liberada ou deve ser bloqueada.

## Regra de ouro
O ContratoAtivoResolver resolve.
O Bastiao certifica.
O Atualizador Excel aplica.
O Leitor RTD le.
O Painel exibe.

---

## Atualizacao de governanca — 2026-06-21

### Classificacao atual
APROVADO COM RESSALVAS

### Observacao
ContratoAtivoResolver foi criado, testado e integrado ao Bastiao para resolver o contrato ativo esperado com base no calendario B3 de contratos.

### Responsabilidade preservada
Resolver qual contrato futuro deveria estar ativo em uma data operacional, sem alterar Excel, sem ler Profit diretamente e sem liberar operacao.

### Resultado observado
O resolvedor identificou corretamente:

- 2026-06-17 -> WINM26_F_0
- 2026-06-18 -> WINQ26_F_0
- 2026-06-21 -> WINQ26_F_0
- 2026-08-13 -> WINV26_F_0

### Integracao atual
Fluxo integrado:

Calendario B3
-> ContratoAtivoResolver
-> Bastiao valida
-> Backend entrega
-> Painel exibe

### O que permanece proibido
- Alterar Excel.
- Trocar formulas RTD.
- Ler Profit diretamente.
- Decidir entrada operacional.
- Gerar sinal.
- Substituir Bastiao.
- Inventar calendario quando fonte oficial estiver ausente.

### Ressalvas
- Calendario de feriados/sessoes B3 ainda nao integrado.
- Auditoria HARD pendente.
- Termo de homologacao pendente.
- Deve continuar recusando calendario ausente, incompleto ou fora de cobertura.
