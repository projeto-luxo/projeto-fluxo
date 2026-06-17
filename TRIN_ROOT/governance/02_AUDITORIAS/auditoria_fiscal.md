# 🧬 AUDITORIA ARQUITETURAL INICIAL — FISCAL TEMPORAL

## Status

```text
APROVADO PARA PROJETO
NÃO IMPLEMENTADO
```

## Justificativa

O Fiscal Temporal é necessário para impedir que erros de série temporal contaminem Bernardo, Historiador e Motor de Confluência.

## Missão

Certificar arquivos gerados pelo Zé antes da entrada na memória oficial.

## Deve verificar

- Header.
- Encoding.
- Contrato de saída.
- Timestamps.
- Timezone.
- Sessão.
- Continuidade temporal.
- Duplicidade.
- Lacunas.
- OHLC.
- Volume.
- Delta.
- Saldo.
- Hash.
- Manifesto.
- Candles parciais.

## Saída esperada

```text
CERTIFICADO
REPROVADO
APROVADO COM RESSALVAS
```

com relatório técnico.
