# CONTRATO — CONSULTA CONFLUÊNCIA REPLAY V1

## Identidade

```text
contrato = ConsultaConfluenciaReplayV1
versao = 1.0.0
modo_analise = RETROSPECTIVO_SELADO
perfil_criterio = CRITERIO_CONFLUENCIA_REPLAY_V1
```

## Campos

### `origem_id`

Único filtro opcional repassado à API homologada. `null` significa universo completo.

### `campos_comparacao`

Lista fixa e ordenada:

```text
fato.evento.ativo
contexto.regime
contexto.sessao.sessao_id
```

O solicitante não escolhe nem remove campos.

### `contexto_alvo`

Contém exatamente:

```text
ativo
regime
sessao_id
```

### `particao_dados`

Constante:

```text
metodo = CORTE_TEMPORAL_50_50_V1_PROVISORIO
percentual_calibracao = 50
percentual_prova = 50
```

### `politica_universo`

```text
usar_universo_completo = true
top_n = null
limite_seguranca = 1000
ordem = timestamp_referencia_ordinal_referencia_experiencia_id_ASC
filtro_direcao = null
```

## Proibições

A consulta não aceita:

- filtros livres;
- direção;
- resultado;
- MFE/MAE;
- desfecho;
- IDs escolhidos manualmente;
- quantidade máxima escolhida pelo usuário;
- caminho de arquivo;
- caminho de Biblioteca Histórica.

## Reprodutibilidade

O hash da consulta é SHA-256 do JSON canônico RFC 8785. Consultas semanticamente iguais devem gerar o mesmo hash.
