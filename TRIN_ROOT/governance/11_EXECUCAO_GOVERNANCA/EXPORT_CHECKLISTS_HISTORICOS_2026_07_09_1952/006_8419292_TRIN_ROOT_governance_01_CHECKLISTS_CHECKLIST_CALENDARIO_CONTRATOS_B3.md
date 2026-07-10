# CHECKLIST — Calendario B3 de Contratos

## Fase 1 — Estrutura
[x] Criar pasta config/calendarios
[x] Criar modelo calendario_contratos_b3.csv
[x] Criar padrao de governanca do calendario

## Fase 2 — Fonte oficial
[ ] Baixar/consultar calendario oficial B3 de vencimentos financeiros
[ ] Baixar/consultar calendario oficial B3 de feriados/sessoes
[ ] Registrar fonte e data de revisao
[ ] Nao aceitar datas sem fonte

## Fase 3 — Contratos WIN
[ ] Preencher contratos WIN do ano corrente
[ ] Registrar data_vencimento_oficial
[ ] Registrar UDN
[ ] Registrar LF
[ ] Registrar inicio_validade
[ ] Registrar fim_validade
[ ] Marcar status_confiabilidade

## Fase 4 — Resolver contrato ativo
[ ] Criar ContratoAtivoResolver
[ ] Resolver contrato esperado pela data atual
[ ] Recusar calendario ausente
[ ] Recusar data fora da cobertura
[ ] Recusar conflito de regra

## Fase 5 — Bastiao
[ ] Bastiao valida contrato esperado
[ ] Bastiao compara contrato esperado x Excel
[ ] Bastiao compara contrato esperado x Backend
[ ] Bastiao emite APROVADO / RESSALVA / REPROVADO / BLOQUEADO
