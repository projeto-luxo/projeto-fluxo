# CONTRATO — PORTA HISTORIADOR PARA CONFLUÊNCIA V1

## API homologada refletida

```text
consultar_experiencia(experiencia_id)
consultar_experiencias(origem_id=None, direcao=None)
```

A porta do P04A não inventa método novo no Historiador.

## Chamada permitida

```text
consultar_experiencias(
    origem_id=<consulta.origem_id>,
    direcao=None
)
```

`direcao` deve ser sempre `None`. Qualquer tentativa de filtrar por direção é violação contratual.

## Garantia fiscal

Decisão adotada: **Opção C — garantia herdada da fronteira homologada**.

A Confluência:

- confia que o Historiador só persiste experiências após seu gate;
- exige origem e rastreabilidade disponíveis;
- não exige nem fabrica certificado individual ausente;
- não acessa uma fonte lateral;
- não reabre o Historiador.

## Campos mínimos consumidos

```text
experiencia_id
origem_tipo
solicitacao_id
origem_id
origem_hash
timestamp_referencia
ordinal_referencia
fato
contexto
hipotese
resultado
```

## Fail-closed

Bloquear quando:

- retorno não vier da instância da porta homologada;
- origem não for `ORIGEM_REPLAY`;
- faltar `solicitacao_id`, `origem_id` ou `origem_hash`;
- schema/versão forem desconhecidos;
- o mesmo ID possuir hashes diferentes;
- a chamada solicitar `direcao` diferente de `None`.

## Imutabilidade

A porta expõe somente leitura. P04A não chama registrar, salvar, atualizar, excluir ou compactar.
