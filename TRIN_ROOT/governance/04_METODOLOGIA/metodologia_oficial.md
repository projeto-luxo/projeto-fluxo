# 🏛️ METODOLOGIA OFICIAL DE DESENVOLVIMENTO — TRIN

## Filosofia

O objetivo do TRIN não é produzir código rapidamente. O objetivo é construir uma arquitetura sólida, rastreável e evolutiva.

## Ciclo obrigatório

```text
ETAPA 0 — Análise de Necessidade Evolutiva
↓
ETAPA 1 — Auditoria Arquitetural
↓
ETAPA 2 — Contrato do Módulo
↓
ETAPA 3 — Implementação Conservadora
↓
ETAPA 4 — Teste Controlado
↓
ETAPA 5 — Auditoria HARD Pós-Implementação
↓
ETAPA 6 — Correções
↓
ETAPA 7 — Nova Auditoria, se necessário
↓
ETAPA 8 — Homologação
↓
ETAPA 9 — Checkpoint Git
↓
ETAPA 10 — Congelamento Arquitetural, quando aplicável
```

## Etapa Zero — perguntas obrigatórias

- Qual problema este módulo resolve?
- Esse problema já é resolvido por outro módulo?
- É realmente necessário criar um novo módulo?
- Uma melhoria incremental resolveria?
- Respeita responsabilidade única?
- Quem consome sua saída?
- Quem fornece sua entrada?
- Aumenta ou reduz acoplamento?
- Preserva Memória antes da Inteligência?
- Está na ordem correta da fila oficial?

## Regra suprema

```text
Pensar primeiro.
Projetar depois.
Auditar em nível HARD.
Programar por último.
```
