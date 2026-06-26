# DA_CANDLES_INEXISTENTES_POR_LEILAO.md

## Status

DECISAO_ARQUITETURAL_OFICIAL  
Data: 2026-06-25  
Projeto: TRIN  
Tema: Tratamento de candles inexistentes por leilao  

---

## 1. Contexto

O Fiscal Temporal v4.2 identificou ausencias de candles no arquivo matriz:

TRIN_HISTORICO/001_1_MIN/win/WIN_1min_2026_2026.csv

Candles inicialmente apontados como ausentes:

- 22/01/2026 12:41:00
- 26/01/2026 11:31:00
- 26/01/2026 11:32:00
- 26/01/2026 11:34:00

Essas ausencias geraram pendencias em cascata nos fractais derivados.

---

## 2. Evidencia externa

A Nelogica informou que:

- em 22/01/2026, o ativo esteve em leilao entre 12:40:21 e 12:42:21;
- por esse motivo, nao houve formacao do candle de 12:41;
- em 26/01/2026, houve leilao entre 11:30:41 e 11:33:10;
- posteriormente houve novo leilao entre 11:33:16 e 11:35:16;
- por esse motivo, esta dentro do esperado nao haver formacao de candles nesses horarios.

---

## 3. Decisao principal

Candles inexistentes por leilao nao devem ser tratados como erro de reconstrucao.

A ausencia de candle causada por leilao deve ser classificada como evento real de mercado.

Classificacao oficial:

CANDLE_INEXISTENTE_POR_LEILAO

Status operacional recomendado:

JUSTIFICADO_POR_EVENTO_DE_MERCADO

---

## 4. Proibicoes

Fica proibido:

- recriar candle inexistente por leilao;
- preencher candle manualmente;
- interpolar preco ou volume;
- copiar dado de outro ativo;
- atribuir ao Ze do Eucrazio erro que foi justificado por leilao;
- certificar como historico continuo limpo um trecho com ausencia justificada;
- apagar a rastreabilidade do evento de leilao.

---

## 5. Regra para o Ze do Eucrazio

O Ze do Eucrazio nao deve gerar candle 1_MIN nos horarios justificados por leilao.

O Ze pode regenerar fractais derivados desde que preserve a heranca da justificativa.

Status recomendado para candles/fractais derivados afetados:

LACUNA_HERDADA_JUSTIFICADA_POR_LEILAO

A regeneracao derivada nao elimina o evento de leilao.

---

## 6. Regra para o Fiscal Temporal

O Fiscal Temporal deve diferenciar:

- lacuna sem justificativa;
- lacuna por erro de base;
- lacuna por corte de arquivo;
- candle inexistente por leilao;
- lacuna herdada justificada em fractais derivados.

Quando uma ausencia estiver cadastrada como CANDLE_INEXISTENTE_POR_LEILAO, o Fiscal nao deve emitir ordem de correcao para o Ze.

O Fiscal deve registrar a ausencia como justificada.

---

## 7. Regra para Bernardo

O Bernardo deve registrar a origem da justificativa.

O evento nao deve ser escondido.

O evento tambem nao deve contaminar o indice como erro desconhecido.

O indice deve preservar a informacao de que o trecho possui ausencia justificada por evento de mercado.

---

## 8. Regra para Historiador

O Historiador pode manter o trecho no contexto historico, mas deve tratar os candles/fractais afetados como evidencia com ressalva.

Esses trechos nao devem ser usados como evidencia forte em estudos sensiveis de microestrutura.

A classificacao recomendada e:

CONTEXTO_COM_RESSALVA_DE_LEILAO

---

## 9. Regra para fractais superiores

Fractais derivados de periodos com candle inexistente por leilao devem carregar ressalva de origem.

Esses fractais nao devem ser tratados como erro independente se a causa matriz estiver registrada.

A cascata de pendencias deve ser consolidada na causa matriz:

CANDLE_INEXISTENTE_POR_LEILAO

---

## 10. Proximo passo tecnico

A proxima etapa tecnica deve ser feita em patch separado e controlado:

1. criar cadastro oficial de candles inexistentes por leilao;
2. ajustar Fiscal Temporal para consultar esse cadastro;
3. impedir emissao de ordem corretiva para Ze nesses casos;
4. propagar ressalva para fractais derivados;
5. reexecutar Fiscal Temporal;
6. reavaliar Bernardo;
7. somente depois retomar Historiador.

---

## 11. Decisao final

O TRIN reconhece que nem toda ausencia temporal de candle representa falha de base.

Quando a ausencia for causada por leilao confirmado, o tratamento oficial sera:

CANDLE_INEXISTENTE_POR_LEILAO

Esse evento deve ser registrado, preservado e propagado como ressalva, mas nao corrigido artificialmente.
