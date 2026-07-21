# AUDITORIA ARQUITETURAL — P04B BACKEND REAL — V1.9

**Base obrigatória:** `cbbbbd0a914d1b6d88b87f3a53fdd53a363efe72`
**P04A homologado:** `3100aef9e543bc5d71d3bf94d9510514df286ef5`
**Backend oficial:** `backend.server_institucional_v6:app`
**Porta:** `8001`
**Endpoints consumidores:** `/data` e `/ws`
**Montador único:** `gerar_payload()`
**Overlay replay existente:** `replay_reader.aplicar_payload(...)`

## Missão única

Acrescentar `confluencia_replay` ao payload oficial em modo diagnóstico, aditivo,
somente leitura e fail-closed. Não altera P04A, Historiador, frontend, Cockpit,
Planejador, Biblioteca Histórica, peso ou autorização operacional.

## Seis perguntas arquiteturais — respostas congeladas

### 1. Qual entrada oficial recebe?

A integração chama exclusivamente:

```python
avaliar_confluencia_replay(
    consulta=consulta,
    repositorio=repositorio,
    validar_schema_saida=True,
)
```

O repositório é `intelligence.historiador_replay.RepositorioExperiencias` e a
consulta é `ConsultaConfluenciaReplayV1`. Os valores externos não possuem
default semântico: origem, repositório e regime ausentes deixam o campo
`INDISPONIVEL`; fonte divergente deixa o campo `BLOQUEADO`. Nenhum CSV é lido
diretamente e nenhum certificado, regime ou experiência é fabricado.

### 2. Como confirma aprovação do Fiscal?

Antes de chamar P04A, lê somente `payload["fiscal"]`, já montado pelo backend
oficial. Exige simultaneamente:

```text
fonte = FISCAL_TEMPORAL_LAUDO_OFICIAL
aprovado_operacional = true
bloqueio_operacional = false
```

Ausência, fonte divergente, reprovação ou bloqueio impedem a chamada ao P04A e
geram código rastreável no campo `gate_fiscal`.

### 3. Como percorre a requisição no tempo?

`gerar_payload()` monta o payload legado, aplica o overlay replay e somente
então chama o finalizador P04B. A ordenação, o universo completo e o corte
50/50 permanecem responsabilidade do P04A homologado. O adapter não filtra por
direção, resultado, MFE/MAE ou IDs. O timeout admite no máximo um trabalhador
daemon ativo e não cria fila nem novas threads enquanto o anterior estiver vivo.

### 4. Qual estrutura entrega?

Campo aditivo `confluencia_replay`, contrato `ConfluenciaReplayBackendV1`,
versão `1.0.0`, presente nos dois retornos de `gerar_payload()`. Mantém:

```text
modo = SOMBRA
peso = 0
impacto_operacional = 0
operacional = false
```

`/data` e `/ws` recebem o mesmo objeto porque ambos consomem `gerar_payload()`.

### 5. O que faz com parciais e falhas?

Preserva os estados P04A `COMPLETO`, `PARCIAL`, `SEM_EVIDENCIA`,
`INSUFICIENTE` e `BLOQUEADO`. Configuração ou fonte ausente produz
`INDISPONIVEL`; saída inválida ou gate negado produz `BLOQUEADO`; exceção não
classificada produz `ERRO_DIAGNOSTICO`. O backend continua respondendo.

### 6. Como prova que não altera nada?

O adapter trabalha sobre cópia profunda. O repositório JSONL é hasheado antes e
depois da consulta. O aplicador testa primeiro uma sandbox extraída diretamente
do commit-base, cria backup byte a byte, preserva LF/CRLF e newline final,
hasheia working tree sujo não alvo, protege P04A/Historiador/frontend/Planejador,
testa reaplicação e executa rollback automático em falha.

## Estado

```text
P04A = HOMOLOGADO_E_ENCERRADO
P04B = CANDIDATO_PARA_TESTE_LOCAL_WINDOWS
PAINEL_MUDA = NAO
FRONTEND_MUDA = NAO
PLANEJADOR_MUDA = NAO
PESO = 0
IMPACTO_OPERACIONAL = 0
COMMIT = NAO
PUSH = NAO
HOMOLOGACAO = SOMENTE_NO_PC_OFICIAL_DO_USUARIO
```
