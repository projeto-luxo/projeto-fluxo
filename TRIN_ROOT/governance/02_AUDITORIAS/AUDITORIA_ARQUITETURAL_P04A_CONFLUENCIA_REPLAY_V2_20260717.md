# AUDITORIA ARQUITETURAL — P04A CONFLUÊNCIA REPLAY V2

**Data:** 17/07/2026  
**Base imutável:** `be7714c16d0031b87bebcc1ef905b4daf5bba478`  
**Branch:** `TRIN_CLEAN`  
**Identidade:** `P04A_AUDITORIA_ARQUITETURAL_CONFLUENCIA_REPLAY_V2`  
**Natureza:** auditoria arquitetural documental; zero código, zero aplicador, zero alteração no projeto real.

# 1. Decisão final

# APROVADO PARA IMPLEMENTAÇÃO DO P04A

Esta decisão autoriza somente a próxima entrega mínima de implementação isolada. Ela não homologa a Confluência Replay, não altera o painel, não integra backend, não alimenta Planejador e não autoriza peso operacional.

```text
modo = SOMBRA
peso = 0
impacto_operacional = 0
ordem_operacional = NENHUMA
painel_muda = NÃO
```

# 2. Correções dos achados da Guia 2

| Achado | Correção V2 |
|---|---|
| P04A-ARCH-001 | Escolhida formalmente a **Opção C**: garantia fiscal herdada do ingresso no Historiador homologado; a Confluência não exige nem fabrica certificado individual e usa somente os campos realmente fornecidos pela API auditada. |
| P04A-ARCH-002 | Incorporados NEUTRA/FAVORÁVEL/CONTRÁRIA/BLOQUEADORA, acerto, falso positivo, falso negativo, oportunidade perdida, estratos por horário/volatilidade/contexto, partição calibração/prova, anti-cherry-picking e idempotência. |
| P04A-ARCH-003 | Entregues contrato e schema formais da consulta e contrato da porta. |
| P04A-ARCH-004 | Fechados `id_confluencia`, timestamp semântico, JCS, campos de hash, exclusão do próprio hash e vetores conhecidos. |
| P04A-ARCH-005 | Schema fechado: consulta sem filtros livres; campos fixos; listas tipadas; coerência quantidade/listas por `oneOf` de 0 a 1000; estados contraditórios rejeitados. |
| P04A-ARCH-006 | Universo completo obrigatório, filtro somente por `origem_id`, filtro de direção proibido, top-N desabilitado, IDs e exclusões registrados, hash do universo obrigatório. |
| P04A-ARCH-007 | Removidos os thresholds 5, 50% e faixas 25/50/75. A confiança é somente índice descritivo não calibrado. A divisão 50/50 é governança provisória explícita, não threshold de sinal. |
| P04A-ARCH-008 | Criado critério próprio de idempotência para N chamadas idênticas sem acúmulo e com saída canônica idêntica. |
| P04A-CART-001 | Hash do ZIP entregue em arquivo externo irmão. O arquivo interno registra hash do manifesto e declara a não autorreferência. |

# 3. Compatibilidade com o Historiador homologado

## 3.1 API pública considerada oficial

```text
RepositorioExperiencias.consultar_experiencia(experiencia_id)
RepositorioExperiencias.consultar_experiencias(origem_id=None, direcao=None)
```

## 3.2 Decisão formal: Opção C

A Confluência Replay não revalida o certificado individual porque a API auditada não o entrega como parte garantida da experiência. A aprovação fiscal é uma **garantia herdada da fronteira homologada**:

```text
Historiador só registra experiência depois do gate fiscal
→ RepositorioExperiencias é a fronteira homologada
→ Confluência aceita somente objetos retornados por essa fronteira
```

A Confluência exige para rastreabilidade:

```text
solicitacao_id
origem_id
origem_hash
origem_tipo = ORIGEM_REPLAY
```

Ela não inventa:

```text
id_certificado
status_certificado
versao_certificado
timestamp_fim_janela_posterior
```

Se a experiência não veio da porta oficial, tem origem divergente, schema incompatível ou rastreabilidade incompleta, o resultado é `BLOQUEADO`.

## 3.3 Limite temporal assumido

Como o contrato auditado não oferece `timestamp_fim_janela_posterior`, a V1 não promete consulta histórica “como se estivesse naquele instante”. O modo permitido é:

```text
RETROSPECTIVO_SELADO
```

Ele usa experiências já concluídas e persistidas pelo Historiador. O resultado não participa da seleção nem da classificação de similaridade. Um futuro modo rolling/as-of exigirá versão nova do contrato com término de janela explicitamente disponível.

# 4. Entrada oficial

A entrada é `ConsultaConfluenciaReplayV1`, definida em contrato e schema próprios.

Não há filtros livres. A consulta admite somente:

- `origem_id` exato ou `null`;
- contexto-alvo nos três campos fixos;
- perfil de critério fixo;
- universo completo;
- top-N desabilitado;
- filtro de direção obrigatoriamente `null`.

São proibidos filtros por resultado, MFE, MAE, desfecho, IDs escolhidos manualmente ou direção.

# 5. Percurso temporal

1. chamar `consultar_experiencias(origem_id=<valor>, direcao=None)`;
2. validar cada objeto sem modificá-lo;
3. ordenar por `timestamp_referencia`, `ordinal_referencia`, `experiencia_id`;
4. deduplicar apenas duplicatas exatas;
5. bloquear conflito do mesmo ID com hash diferente;
6. calcular `hash_universo` antes de qualquer métrica;
7. usar o universo completo;
8. se houver mais de 1000 experiências, bloquear; não selecionar top-N;
9. dividir deterministicamente o conjunto: primeira metade temporal em calibração, segunda metade em prova;
10. usar resultado somente depois da seleção, para métricas retrospectivas.

# 6. Unidade e critério de comparação

Unidade atômica: uma `ExperienciaReplayV1`.

Campos fixos:

```text
fato.evento.ativo
contexto.regime
contexto.sessao.sessao_id
```

Cada campo é comparado por igualdade exata. Ausência produz `NAO_AVALIADO`, nunca valor inventado.

Classificação:

- `FAVORAVEL`: todos os três campos concordam;
- `CONTRARIA`: pelo menos um campo diverge;
- `NEUTRA`: nenhum diverge, mas pelo menos um está ausente/não avaliável;
- `BLOQUEADORA`: quebra de schema, origem, proveniência ou duplicidade conflitante.

Essas classes são diagnósticas e não representam direção.

# 7. GPS da Confluência

## 7.1 Qualidade de hipótese

As categorias são:

```text
ACERTO
FALSO_POSITIVO
FALSO_NEGATIVO
ACERTO_NEGATIVO
OPORTUNIDADE_PERDIDA
NAO_AVALIAVEL
```

A V1 só classifica quando o contrato-fonte oferece informação suficiente. Campos ausentes não são inferidos.

- hipótese direcional explícita + resultado avaliável favorável: `ACERTO`;
- hipótese direcional explícita + resultado avaliável adverso: `FALSO_POSITIVO`;
- hipótese negativa/abstenção explicitamente registrada + resultado positivo: `FALSO_NEGATIVO`;
- hipótese negativa/abstenção explícita + resultado negativo: `ACERTO_NEGATIVO`;
- ausência deliberada registrada + oportunidade positiva comprovada: `OPORTUNIDADE_PERDIDA`;
- ausência dos marcadores necessários: `NAO_AVALIAVEL`.

A arquitetura não converte direção ausente em abstenção deliberada.

## 7.2 Resultados por horário

Agrupamento pelo horário civil de `timestamp_referencia`, em chaves `HH:00-HH:59`, preservando timezone original.

## 7.3 Resultados por volatilidade

A volatilidade é derivada da amplitude do evento quando os campos máximo e mínimo existem. Os limites de estrato são calculados somente na partição de calibração pelos percentis 33 e 66 e congelados para a partição de prova. Sem dados suficientes, o estrato é `NAO_AVALIAVEL`.

## 7.4 Resultados por contexto

Agrupamento por:

```text
contexto.regime
contexto.sessao.sessao_id
```

Sem preenchimento artificial.

# 8. Partição calibração/prova

Método fixo:

```text
CORTE_TEMPORAL_50_50_V1_PROVISORIO
```

Depois da ordenação determinística:

- primeira metade: `CALIBRACAO`;
- segunda metade: `PROVA`;
- número ímpar: o elemento central fica em `PROVA`.

O 50/50 é uma regra provisória de governança para impedir mistura entre ajuste e comprovação. Não é parâmetro científico, não altera peso e deverá ser versionado se for substituído.

A saída registra IDs, hashes, interseção vazia e hash da partição.

# 9. Controle contra cherry-picking

```text
universo = todos os objetos retornados pela porta oficial
filtro permitido = origem_id
filtro de direção = proibido
filtros por resultado = proibidos
top-N = desabilitado
seleção manual de IDs = proibida
```

O resultado registra:

- todos os IDs do universo em ordem;
- `hash_universo`;
- IDs incluídos;
- IDs excluídos e motivo;
- regra de seleção;
- filtros permitidos e proibidos.

Acima de 1000 registros, a execução bloqueia em vez de escolher subconjunto.

# 10. Determinismo e idempotência

## 10.1 JSON canônico

```text
serialização = RFC 8785 JCS
encoding = UTF-8
chaves = ordem canônica
NaN/Infinity = proibidos
```

## 10.2 id_confluencia

```text
identity_payload = {
  versao_schema,
  versao_algoritmo,
  hash_consulta,
  hash_universo,
  hash_particao,
  ids_incluidos_ordenados
}

id_confluencia =
"CFR-" + primeiros 32 hex maiúsculos de SHA256(JCS(identity_payload))
```

## 10.3 timestamp_calculo

Não é relógio da máquina. É o maior `timestamp_referencia` das experiências incluídas. Sem experiência, é `null`.

## 10.4 hash_resultado

```text
SHA256(JCS(saída canônica sem hash_resultado e sem metadados de execução))
```

O próprio hash nunca entra no material hasheado. Logs de execução ficam fora do contrato canônico.

## 10.5 Idempotência

N chamadas iguais na mesma instância devem produzir:

- zero anexação a estado interno;
- mesma quantidade;
- mesmos IDs únicos;
- mesmo `id_confluencia`;
- mesmo `timestamp_calculo`;
- mesmos bytes canônicos;
- mesmo `hash_resultado`.

Os vetores com hashes conhecidos estão em `VETORES_DETERMINISMO_P04A_V1.json`.

# 11. Confiança diagnóstica

Foram removidos:

```text
mínimo de 5
cobertura mínima de 50%
faixas 25/50/75
```

A V1 usa somente:

```text
valor = taxa_favoravel * cobertura
```

- `valor` fica entre 0 e 1;
- não existem faixas BAIXA/MÉDIA/ALTA;
- `nao_calibrada = true`;
- zero comparáveis produz `null`;
- nunca altera peso ou impacto operacional.

# 12. Estados

- `COMPLETO`: uma ou mais evidências válidas, sem bloqueio e todos os campos fixos avaliáveis;
- `PARCIAL`: evidências válidas com pelo menos um campo não avaliável;
- `SEM_EVIDENCIA`: universo válido vazio;
- `INSUFICIENTE`: universo não vazio, mas nenhuma evidência comparável;
- `BLOQUEADO`: origem, schema, rastreabilidade, duplicidade conflitante, limite ou reprodutibilidade inválidos.

# 13. Não mutação

A futura implementação deverá provar hash antes/depois de:

- objetos retornados pelo Historiador;
- repositório controlado;
- memória ao vivo;
- fixtures;
- payload/backend;
- consumidores existentes.

P04A é função pura sobre cópias imutáveis. Não possui método de escrita, não registra experiência e não acessa Biblioteca Histórica.

# 14. Resultado visual

```text
P04A: painel_muda = NÃO
P04B: integração diagnóstica no backend
P04C: exposição no Cockpit em SOMBRA / NÃO OPERACIONAL
```

# 15. Estado de saída

```text
base = be7714c16d0031b87bebcc1ef905b4daf5bba478
P04A = AUDITORIA ARQUITETURAL V2 CONCLUÍDA
ConfluenciaReplayV1 = CONTRATO FECHADO
ConsultaConfluenciaReplayV1 = CONTRATO FECHADO
PortaHistoriadorConfluenciaV1 = CONTRATO FECHADO
peso = 0
impacto_operacional = 0
painel = SEM ALTERAÇÃO
Confluência Replay = AINDA NÃO HOMOLOGADA
próximo passo = auditoria independente da V2
```
