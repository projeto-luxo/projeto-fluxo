# PADRÃO VISUAL — RESULTADOS OPERACIONAIS V1

## Princípio

O cockpit operacional entrega resultado. Não explica a engenharia.

## Conteúdo permitido

```text
REGIÃO PRINCIPAL
175.200 — 175.280

TIPO
POSSÍVEL REVERSÃO

ESTADO
AGUARDAR

ENTRADA
175.300 — 175.330

INVALIDAÇÃO
ABAIXO DE 175.160

STOP
175.130

PARCIAL
175.470

ALVO
175.620
```

## Estado bloqueado

```text
ESTADO
SEM OPERAÇÃO

MOTIVO
DADOS NÃO CERTIFICADOS
```

## Conteúdo proibido no cockpit principal

Nomes de tópicos RTD, `engine_zona_low`, `engine_zona_high`, nomes de classes, hashes, regras de cálculo, justificativas longas e parâmetros internos.

O frontend não infere autorização nem calcula níveis.
