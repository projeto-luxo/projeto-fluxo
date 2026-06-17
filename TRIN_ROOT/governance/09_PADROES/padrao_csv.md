# 📄 PADRÃO CSV — TRIN

## Regra geral

- Separador: `;`
- Encoding: `utf-8-sig`
- Preferência para `header=True` em novos contratos.
- Dados brutos antigos podem manter padrão original, mas devem ser descritos em contrato.

## Colunas mínimas para fractais do Zé 4.x

```text
ativo,data,hora,timestamp,timezone,sessao,fractal_minutos,status_candle,qtd_candles_origem,abertura,maximo,minimo,ultimo,volume,volume_quantidade,delta,saldo,agressao_compra,agressao_saldo,agressao_venda,vwap
```

## Regra

Mistura de layouts deve ser explicitamente registrada para evitar erro no Bernardo.
