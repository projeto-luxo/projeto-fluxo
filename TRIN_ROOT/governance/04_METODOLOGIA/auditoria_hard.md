# 🔥 AUDITORIA HARD — NORMA OFICIAL

## Definição

Auditoria HARD é a análise conduzida com a intenção explícita de reprovar o módulo.

O auditor deve partir da hipótese:

> **O módulo contém um erro ainda não descoberto.**

## Áreas obrigatórias

- Matemática.
- Lógica.
- Arquitetura.
- Responsabilidade única.
- Escalabilidade.
- Performance.
- Rastreabilidade.
- Compatibilidade futura.
- Contratos.
- Segurança da memória.
- Coerência filosófica.

## Perguntas obrigatórias

- E se houver 10 milhões de registros?
- E se faltar candle no meio da sessão?
- E se houver timestamp duplicado?
- E se o contrato mudar daqui a 5 anos?
- E se o Bernardo interpretar esse campo de forma diferente?
- E se a saída estiver matematicamente coerente, mas arquiteturalmente errada?
- E se o módulo estiver invadindo responsabilidade de outro?

## Norma

Nenhum checklist substitui uma Auditoria HARD. Nenhuma Auditoria HARD substitui um checklist de teste. Ambos são obrigatórios.

## Máxima

> No TRIN, um módulo não é considerado bom porque funciona. É considerado robusto quando sobrevive a uma auditoria que tentou quebrá-lo e não conseguiu.
