# DA_LACUNAS_REMANESCENTES_SEM_FONTE_MATRIZ.md

## Status

DECISAO_ARQUITETURAL_OFICIAL  
Data: 2026-06-26  
Projeto: TRIN  
Tema: Tratamento de lacunas remanescentes sem fonte matriz localizada  

---

## 1. Contexto

A frente Nelogica / leilao / janeiro de 2026 foi encerrada com rastreabilidade.

O Fiscal Temporal passou a reconhecer:

CANDLE_INEXISTENTE_POR_LEILAO

e

LACUNA_HERDADA_JUSTIFICADA_POR_LEILAO

Mesmo apos essa correcao, restaram 6 ocorrencias de:

LACUNA_CANDLE_AUSENTE

atribuidas ao Ze do Eucrazio.

---

## 2. Pendencias remanescentes

Arquivos afetados:

- WIN_5min_2025_2026.csv
- WIN_10min_2025_2026.csv
- WDO_30min_2014_2016.csv
- WDO_30min_2020_2022.csv

Eventos observados:

- 03/06/2025, em fractais WIN 5_MIN e 10_MIN
- 21/08/2025, em fractais WIN 5_MIN e 10_MIN
- 30/11/2015, em WDO 30_MIN
- 11/10/2021, em WDO 30_MIN

---

## 3. Diagnostico inicial

Foi realizada busca em TRIN_HISTORICO por possiveis candles intermediarios.

A base matriz 1_MIN para WIN 2025 nao foi localizada automaticamente.

Alguns horarios apareceram apenas em fractais maiores ou em pasta de duplicidades.

Para WDO antigo, houve indicio de horario em fractal 60_MIN, mas isso nao autoriza reconstruir 30_MIN.

---

## 4. Decisao principal

O TRIN nao deve reconstruir fractais menores a partir de fractais maiores.

Fica proibido gerar:

- 5_MIN a partir de 10_MIN, 15_MIN, 30_MIN ou 60_MIN;
- 10_MIN a partir de 15_MIN, 30_MIN ou 60_MIN;
- 30_MIN a partir de 60_MIN;
- qualquer candle menor sem fonte matriz suficiente.

A reconstrucao so pode ocorrer de menor para maior.

---

## 5. Classificacao oficial provisoria

Enquanto a fonte matriz nao for localizada, as 6 lacunas remanescentes devem ser classificadas como:

LACUNA_REMANESCENTE_SEM_FONTE_MATRIZ

ou, quando aplicavel:

FRACTAL_DERIVADO_SEM_BASE_MATRIZ_LOCALIZADA

Essa classificacao nao equivale a correcao.

---

## 6. Regra para o Ze do Eucrazio

O Ze do Eucrazio nao deve regenerar esses arquivos enquanto a fonte matriz menor nao estiver localizada.

Se a base 1_MIN ou outra fonte matriz suficiente for encontrada, a regeneracao podera ser autorizada em patch controlado.

Sem fonte matriz, o Ze nao deve criar candle sintetico.

---

## 7. Regra para o Fiscal Temporal

O Fiscal Temporal deve manter essas ocorrencias como pendencias reais enquanto nao houver justificativa ou fonte matriz.

Essas lacunas nao devem ser misturadas com a frente ja resolvida de leilao.

O Fiscal nao deve reclassificar automaticamente essas pendencias como informativas sem prova externa ou matriz suficiente.

---

## 8. Regra para Bernardo

O Bernardo deve registrar essas pendencias como lacunas sem fonte matriz localizada.

Nao deve tratar os arquivos como historico plenamente continuo.

Nao deve esconder a pendencia em indice geral.

---

## 9. Regra para Historiador

O Historiador nao deve usar esses trechos como evidencia forte.

Enquanto a matriz nao for encontrada, esses periodos devem ser tratados como contexto historico com ressalva.

---

## 10. Proibicoes

Fica proibido:

- inventar candle;
- interpolar preco;
- estimar volume;
- copiar candle de outro fractal;
- reconstruir menor a partir de maior;
- certificar limpo sem fonte matriz;
- atribuir a correcao ao Ze sem materia-prima suficiente.

---

## 11. Caminhos autorizados

Sao permitidos apenas os seguintes caminhos:

1. localizar fonte matriz 1_MIN ou fonte confiavel menor;
2. auditar a fonte encontrada;
3. regenerar fractais derivados em teste controlado;
4. reexecutar Fiscal;
5. manter pendencia com ressalva se a fonte matriz nao for encontrada.

---

## 12. Decisao final

As 6 lacunas remanescentes nao devem ser corrigidas automaticamente.

Elas permanecem como pendencias reais ate que uma fonte matriz suficiente seja localizada ou ate que nova justificativa oficial seja registrada.

Status:

PENDENCIA_REAL_SEM_FONTE_MATRIZ_LOCALIZADA
