# AUDITORIA_VOLUME_CANDLEBUILDER_PAINEL_2026_07_07

## Status

AUDITORIA_CONCLUIDA_COM_CAUSA_IDENTIFICADA

## Tema

Volume exibido/agregado no CandleBuilderPainel aparecendo repetidamente como 5000.

## Contexto

Durante validação observacional do CandleBuilderPainel em mercado aberto, os timeframes 2_MIN, 30s e 15s apresentaram candles com preço, delta, saldo e VWAP variando corretamente, porém o campo `volume` permaneceu repetidamente em 5000.

## Evidência operacional

- 30s validado com intervalos de 30 segundos.
- 15s validado com intervalos de 15 segundos.
- Retorno para 2_MIN validado com intervalos de 120 segundos.
- `volume` permaneceu em 5000.
- `volume_real` variou e subiu continuamente.
- Contrato ativo aprovado: WINQ26_F_0.
- Origem do painel: RTD_EXCEL_AGREGADO.
- Status do painel: OPERACIONAL_NAO_CERTIFICADO.

## Causa encontrada

No arquivo:

`data/leitor_institucional.py`

foi identificado que o leitor calcula:

`volume_trin = int(volume_real / 100000000)`

e depois aplica limite:

`if volume_trin > 5000: volume_trin = 5000`

O retorno do leitor entrega:

- `volume`: volume normalizado/capado.
- `volume_real`: volume bruto acumulado vindo do Excel/RTD.

## Impacto

O campo `volume` usado pelo painel e por partes do backend não representa volume real do candle. Ele representa um volume normalizado/capado para uso operacional visual/motor atual.

## Risco de correção direta

Não é recomendado substituir diretamente `volume` por `volume_real`, pois `volume_real` é bruto/acumulado e pode afetar agressão, memória, explosão, frequência e sinais.

## Decisão recomendada

Separar responsabilidades:

1. Manter `volume` como campo legado/normalizado por enquanto.
2. Preservar `volume_real` como acumulado bruto.
3. Criar campo específico para painel, como `volume_candle_estimado`.
4. Calcular `volume_candle_estimado` por diferença entre valores de `volume_real`.
5. Informar claramente no payload o tipo de volume:
   - `NORMALIZADO_CAPADO`
   - `REAL_DELTA_ESTIMADO`

## Classificação

AUDITORIA APROVADA PARA PATCH FUTURO CONTROLADO

## Próximo patch recomendado

PATCH_VOLUME_01:

- Não alterar motor.
- Não alterar Fiscal, Zé, Bernardo ou Historiador.
- Não alterar contrato ativo.
- Adicionar campo novo para volume estimado do candle.
- Manter compatibilidade com o campo `volume`.
- Expor no painel a diferença entre volume normalizado e volume real estimado.

