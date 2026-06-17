# ✅ CHECKLIST DE TESTE CONTROLADO — ZÉ DO EUCRÁZIO 4.0

## Antes de rodar

```text
[ ] Git atualizado
[ ] Backup feito
[ ] Bernardo não será alterado
[ ] Fiscal Temporal ainda não será chamado
[ ] MODO_TESTE_CONTROLADO = True
[ ] MAX_ARQUIVOS_TESTE = 1
[ ] SOBRESCREVER_SAIDA = False
```

## Comando sugerido

```powershell
cd "C:\Users\User\projeto_fluxo"
python backend\ze_do_eucrazio_4_0.py
```

## Conferir após rodar

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

## Atenção

Se aparecer muitos candles PARCIAIS, não é necessariamente erro.

Pode ser consequência natural de fractais não divisores ou de sessões com quantidade irregular de candles.

A certificação final será responsabilidade do Fiscal Temporal.
