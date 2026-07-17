# RELATÓRIO DE IMPLEMENTAÇÃO — P04A CONFLUÊNCIA REPLAY V1.1 CANDIDATO

**Base exigida:** `be7714c16d0031b87bebcc1ef905b4daf5bba478`  
**Branch:** `TRIN_CLEAN`  
**Estado:** candidato corrigido e pré-validado em ambiente semelhante.

## Correção localizada incorporada

A V1.1 elimina a divergência entre a fixture sintética da V1 e o contrato homologado `ExperienciaReplayV1`.

Foram corrigidos:

```text
contrato_experiencia -> contrato
timestamp_evento -> timestamp_referencia
ordinal_evento -> ordinal_referencia
```

Deixaram de ser exigidos:

```text
rastreabilidade
certificado_id
```

A rastreabilidade é validada pelos campos oficiais:

```text
origem_tipo
solicitacao_id
origem_id
origem_hash
```

Também foi adicionado bloqueio fail-closed quando a porta recebe uma experiência cujo `origem_id` diverge da origem solicitada.

## Escopo preservado

```text
modo = SOMBRA
peso = 0
impacto_operacional = 0
backend = não alterado
frontend = não alterado
painel = não alterado
Planejador = não alterado
Historiador homologado = não alterado
commit = não executado
push = não executado
```

## Testes reproduzidos

```text
P04A isolado = 89 aprovados
suíte combinada controlada = 150 aprovados
falhas = zero
```

A suíte combinada utilizou:

```text
Base Controlada P03G V2
+ payload homologado P03H
+ payload corrigido P04A V1.1
```

## Estado

```text
P04A implementação = CANDIDATA PARA TESTE LOCAL CONTROLADO
Confluência Replay = ainda não homologada
PAINEL_MUDA = NAO
```
