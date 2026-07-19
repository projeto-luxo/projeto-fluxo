# CONTRATO DE INTEGRAÇÃO — CONFLUÊNCIA REPLAY BACKEND V1

## Fronteira oficial

```text
backend.server_institucional_v6:app
→ gerar_payload()
→ replay_reader.aplicar_payload(...)
→ anexar_confluencia_replay_backend(...)
→ /data e /ws
```

## Fornecedores permitidos

- `RepositorioExperiencias.consultar_experiencias(origem_id, direcao=None)`;
- `avaliar_confluencia_replay(..., validar_schema_saida=True)`;
- `payload["fiscal"]` com fonte `FISCAL_TEMPORAL_LAUDO_OFICIAL`.

## Configuração explícita, sem valores fabricados

Os valores abaixo só habilitam o caminho de sucesso quando correspondem ao
contexto oficial do replay/Historiador:

```text
TRIN_CONFLUENCIA_REPLAY_ORIGEM_ID
TRIN_CONFLUENCIA_REPLAY_REPOSITORIO_JSONL
TRIN_CONFLUENCIA_REPLAY_REGIME
TRIN_CONFLUENCIA_REPLAY_REGIME_FONTE=HISTORIADOR_REPLAY_CONTEXTO_OFICIAL
```

Ausência não é suprida por default. O ativo pode ser obtido do payload oficial e
a sessão pode ser obtida do status oficial do replay. Caminho dentro de
`TRIN_ROOT` ou `TRIN_HISTORICO` é proibido.

## Campo de saída

`confluencia_replay` segue o schema `CONFLUENCIA_REPLAY_BACKEND_V1.schema.json`.
É aditivo, não remove nem muda tipo de chave preexistente e deve existir nos dois
retornos de `gerar_payload()`.

## Invariantes

```text
modo = SOMBRA
peso = 0
impacto_operacional = 0
operacional = false
ordem_operacional = NENHUMA
frontend = SEM_ALTERACAO
planejador = SEM_ALTERACAO
```

## Fail-closed

Fiscal não aprovado, fonte desconhecida, schema/hash P04A divergente, origem
divergente, repositório indisponível, timeout ou exceção nunca derrubam o
backend e nunca produzem autorização.


## Coerência obrigatória do gate Fiscal

O campo `payload["fiscal"]` só libera a consulta quando quatro elementos
concordam simultaneamente:

```text
fonte = FISCAL_TEMPORAL_LAUDO_OFICIAL
status ∈ FiscalAdapter.STATUS_LIBERADOS
aprovado_operacional = true
bloqueio_operacional = false
```

A autoridade vigente é `intelligence.fiscal_adapter.FiscalAdapter`.
O P04B não declara, copia nem mantém conjunto local de estados. Na base
autorizada, a autoridade expõe `CERTIFICADO`, `APROVADO`, `OK`,
`APROVADO_COM_RESSALVAS` e `RESSALVA`. Mudança futura dessa política deve
ocorrer no fornecedor e ser consumida pelo P04B sem duplicação.

Status bloqueado, ausente, desconhecido ou reprovado não pode ser
neutralizado por booleanos favoráveis. Contradição termina em
`P04B_FISCAL_STATUS_INCOMPATIVEL`.

## Isolamento físico da avaliação e timeout

O avaliador P04A nunca recebe o caminho do repositório JSONL oficial. Antes da
avaliação, o P04B:

1. registra SHA-256 e tamanho do arquivo oficial;
2. cria uma cópia física em diretório temporário fora do projeto;
3. abre o `RepositorioExperiencias` sobre essa cópia;
4. entrega somente a instância isolada ao trabalhador;
5. confere o arquivo oficial em `finally`, inclusive em timeout ou exceção;
6. remove a área temporária quando o trabalhador termina.

Se o timeout ocorrer, o trabalho remanescente pode atuar somente sobre a cópia
descartável. Nenhuma nova tarefa é criada enquanto o trabalhador anterior
permanecer ativo.
