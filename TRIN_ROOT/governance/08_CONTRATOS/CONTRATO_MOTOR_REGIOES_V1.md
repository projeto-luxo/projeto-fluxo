# CONTRATO OFICIAL — MOTOR DE REGIÕES V1

**Status:** PLANEJADO / NÃO IMPLEMENTADO
**Uso operacional:** BLOQUEADO

## Missão

Identificar, manter, classificar e invalidar regiões relevantes do mercado.

## Entradas

- preço;
- candles canônicos;
- máxima, mínima e abertura;
- VWAP e bandas;
- milhares;
- fractais certificados;
- volume agregado;
- contexto temporal;
- eventos históricos;
- microestrutura futura homologada.

Toda entrada declara fonte, timestamp, contrato, timeframe, qualidade e certificação.

## Saída

```json
{
  "id_regiao": "RG-YYYYMMDD-000001",
  "tipo": "REVERSAO|PARADA|CONTINUACAO|MILHAR|VWAP|MAXIMA_MINIMA|ABERTURA|FRACTAL|DEFESA",
  "limite_inferior": 0.0,
  "limite_superior": 0.0,
  "direcao_provavel": "COMPRA|VENDA|NEUTRA",
  "forca": 0.0,
  "confianca": 0.0,
  "origens": [],
  "condicao_invalidacao": "",
  "status": "CANDIDATA|ATIVA|ENFRAQUECIDA|INVALIDADA|EXPIRADA|BLOQUEADA",
  "versao_regra": "1.0"
}
```

## Proibições

Não executar ordem, não gerar entrada, não calcular stop/parcial/alvo, não definir contratos, não substituir Fiscal, não inventar dados e não usar diagnóstico como certificado.
