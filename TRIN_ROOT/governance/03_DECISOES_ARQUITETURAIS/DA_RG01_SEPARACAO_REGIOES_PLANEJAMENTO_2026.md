# DECISÃO ARQUITETURAL RG-01 — SEPARAÇÃO ENTRE REGIÕES E PLANEJAMENTO

**Data:** 2026-07-12
**Status:** PROPOSTA PARA HOMOLOGAÇÃO

## Decisão

Criar módulos independentes:

- `MotorRegioes`
- `PlanejadorOperacional`

O `TRINEngine` administrativo permanece preservado.

## Fluxo

```text
Dados qualificados
→ Motor de Regiões
→ Motor de Confluência
→ Planejador Operacional
→ Gestão de Risco
→ Cockpit
→ Operador
```

## Política de segurança

Quando qualquer condição crítica falhar:

```text
estado = SEM_OPERACAO
autorizacao = BLOQUEADA
entrada = null
stop = null
parcial = null
alvo = null
```

O frontend apenas apresenta o contrato recebido.

## Consequência

A lógica legada será mantida somente como referência histórica. Nenhum valor antigo será reutilizado sem auditoria e teste.
