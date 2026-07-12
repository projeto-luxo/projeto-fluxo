# AUDITORIA PRÉ-PATCH RG-01 — REGIÕES E PLANEJAMENTO OPERACIONAL

**Projeto:** TRIN
**Data:** 2026-07-12
**Status:** CONCLUÍDA PARA DECISÃO ARQUITETURAL

## Problema confirmado

O backend atual consome `engine_zona_low` e `engine_zona_high` e calcula `stop`, `parcial` e `alvo` dentro de `backend/server_institucional_v6.py`.

O arquivo oficial `core/engine.py` possui função administrativa de estados do projeto e não deve ser tratado como motor de inteligência de mercado.

Existe colisão entre:

- `TRINEngine` administrativo;
- motor de mercado esperado pelo backend.

## Evidências

Foram localizados:

- casca visual de Hot Zone;
- linhas e PriceLines de STOP, PARCIAL e ALVO;
- cálculo de gestão misturado ao servidor;
- valores legados fixos para scalping;
- `engine_zona_low` e `engine_zona_high` sem fornecedor homologado;
- marcador simples de reversão entre candles;
- lógica histórica de zonas útil como referência, mas não homologada.

## Riscos

1. Backend acumulando decisão, gestão e transporte de dados.
2. Frontend podendo inferir validade operacional.
3. Stop, parcial e alvo provenientes de regra legada sem contrato.
4. Casca visual sugerindo inteligência sem fornecedor real.
5. Confusão entre alternância de candle e reversão estrutural.
6. Colisão entre motor administrativo e motor de mercado.
7. Possibilidade de exibir plano quando o Fiscal estiver bloqueado.

## Decisão recomendada

Separar:

1. Motor de Regiões.
2. Motor de Confluência.
3. Planejador Operacional.
4. Gestão de Risco.

## Estado

| Componente | Estado |
|---|---|
| Casca visual de região | EXISTE |
| Linhas STOP/PARCIAL/ALVO | EXISTEM VISUALMENTE |
| Fornecedor atual de regiões | INOPERANTE / NÃO HOMOLOGADO |
| Gestão inline no backend | LEGADO ARQUITETURAL |
| Regra fixa de scalping | BLOQUEADA |
| Reversão simples do CandleEngine | DIAGNÓSTICO VISUAL |
| Uso operacional | BLOQUEADO |

## Limites do primeiro patch

Não restaurar o motor antigo integralmente, não calibrar regiões, não liberar entrada, não alterar gestão financeira, não substituir o Fiscal e não mudar o cockpit antes dos contratos.
