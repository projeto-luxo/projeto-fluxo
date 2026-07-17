# CONTRATO — MÉTRICAS GPS DA CONFLUÊNCIA REPLAY V1

## Evidência

### FAVORÁVEL

Todos os três campos fixos concordam com o contexto-alvo.

### CONTRÁRIA

Ao menos um campo fixo diverge.

### NEUTRA

Nenhum campo diverge, porém ao menos um não pôde ser avaliado.

### BLOQUEADORA

A experiência viola schema, origem, proveniência ou integridade.

Nenhuma classe é direção operacional.

## Matriz de qualidade da hipótese

```text
ACERTO
FALSO_POSITIVO
FALSO_NEGATIVO
ACERTO_NEGATIVO
OPORTUNIDADE_PERDIDA
NAO_AVALIAVEL
```

A classificação só ocorre com marcadores explícitos. Ausência não é inferida como abstenção deliberada.

## Estratificações

### Horário

Faixas horárias civis `HH:00-HH:59`.

### Volatilidade

Amplitude do evento. Limites Q33/Q66 calculados apenas em calibração e congelados para prova.

### Contexto

Chaves `contexto.regime` e `contexto.sessao.sessao_id`.

## Calibração e prova

Corte temporal 50/50, provisório e não operacional. Calibração antecede prova. IDs não podem se repetir entre partições.

## Cherry-picking

Universo completo, sem top-N, sem filtro de direção, sem filtro de resultado e sem seleção manual de IDs.

## Confiança

Índice descritivo:

```text
taxa_favoravel * cobertura
```

Sem faixas, sem threshold operacional, sem alteração de peso.
