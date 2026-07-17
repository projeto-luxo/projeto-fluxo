# CONTRATO — CONFLUÊNCIA REPLAY V1

## Identidade

```text
versao_schema = 1.0.0
origem_tipo = ORIGEM_REPLAY
modo = SOMBRA
peso = 0
impacto_operacional = 0
```

## Missão

Produzir diagnóstico retrospectivo, neutro e rastreável a partir de experiências obtidas pela porta homologada do Historiador.

## Saída obrigatória

O schema formal contém:

- identidade e estado;
- garantia fiscal herdada;
- consulta normalizada;
- universo elegível e hash;
- partição calibração/prova;
- quantidade, IDs e evidências;
- NEUTRA/FAVORÁVEL/CONTRÁRIA/BLOQUEADORA;
- concordâncias e divergências tipadas;
- MFE/MAE agregados;
- acerto/falso positivo/falso negativo/acerto negativo/oportunidade perdida;
- resultados por horário, volatilidade e contexto;
- confiança descritiva não calibrada;
- bloqueios, motivos e rastreabilidade;
- hash canônico do resultado.

## Campos proibidos

```text
ordem
compra
venda
entrada
stop
parcial
alvo
quantidade_contratos
autorizacao_operacional
```

## Invariantes

- quantidade deve ser igual ao tamanho de `ids_experiencias` e `evidencias`;
- IDs devem ser únicos;
- `COMPLETO` exige pelo menos uma evidência e zero bloqueios;
- `SEM_EVIDENCIA` exige listas vazias;
- zero comparáveis exige confiança `null`;
- `BLOQUEADO` exige motivo e confiança `null`;
- saída canônica não inclui metadados de relógio de execução;
- resultado nunca alimenta seleção;
- peso e impacto permanecem zero.

## Idempotência

A saída é valor, não acumulador. Chamadas repetidas não anexarão evidências a estado interno.
