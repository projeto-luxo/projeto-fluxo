# Ô£à CHECKLIST DE TESTE CONTROLADO ÔÇö Z├ë DO EUCR├üZIO 4.0

## Antes de rodar

```text
[ ] Git atualizado
[ ] Backup feito
[ ] Bernardo n├úo ser├í alterado
[ ] Fiscal Temporal ainda n├úo ser├í chamado
[ ] MODO_TESTE_CONTROLADO = True
[ ] MAX_ARQUIVOS_TESTE = 1
[ ] SOBRESCREVER_SAIDA = False
```

## Comando sugerido

```powershell
cd "C:\Users\User\projeto_fluxo"
python backend\ze_do_eucrazio_4_0.py
```

## Conferir ap├│s rodar

```text
[ ] Arquivo 2 min gerado
[ ] Arquivo 3 min gerado
[ ] Demais fractais gerados
[ ] Nenhum arquivo original alterado
[ ] Pastas criadas corretamente
[ ] CSV separado por ;
[ ] Encoding utf-8-sig
[ ] Header presente
[ ] Coluna timestamp presente
[ ] Coluna timezone presente
[ ] Coluna sessao presente
[ ] Coluna status_candle presente
[ ] Coluna qtd_candles_origem presente
[ ] Candles parciais registrados
[ ] Log TXT gerado
[ ] Manifesto JSON gerado
```

## Aten├º├úo

Se aparecer muitos candles PARCIAIS, n├úo ├® necessariamente erro.

Pode ser consequ├¬ncia natural de fractais n├úo divisores ou de sess├Áes com quantidade irregular de candles.

A certifica├º├úo final ser├í responsabilidade do Fiscal Temporal.
