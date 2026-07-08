# AUDITORIA_PRE_LIMPEZA_ENCODING_FRONTEND_2026_07_07

## Status

AUDITORIA_PRE_LIMPEZA

## Data

2026-07-07

## Tema

Mapeamento de problemas de encoding visual no frontend TRIN.

---

## 1. Confluência documental obrigatória

Este documento não deve ser lido isoladamente.

Ele complementa:

- CHECKPOINT_CANDLEBUILDER_PAINEL_2026_07_07
- AUDITORIA_RTD_ESTAGNADO_CANDLEBUILDER_2026_07_07
- ROTEIRO_VALIDACAO_MERCADO_ABERTO_CANDLEBUILDER_2026_07_08
- Commits recentes do cockpit, gráfico e painel operacional

Este documento não altera:

- backend
- CandleBuilder
- Motor de Confluência
- Fiscal Temporal
- Bernardo
- Zé do Eucrázio
- Historiador
- Biblioteca Histórica oficial

Este documento não autoriza mudança de regra operacional.

---

## 2. Objetivo

Registrar a auditoria prévia dos problemas de encoding encontrados no frontend, antes de qualquer patch de limpeza.

A limpeza futura deve ser feita em commit separado, sem alterar regra, motor, backend ou cálculo.

---

## 3. Achados principais no App.js

Foram encontradas ocorrências de texto quebrado por encoding, especialmente em textos técnicos e cenários institucionais.

Exemplos encontrados:

- ABSORÃ‡ÃƒO ATIVA
- EXAUSTÃƒO INSTITUCIONAL
- COMPRESSÃƒO INSTITUCIONAL
- ACUMULAÃ‡ÃƒO COMPRADORA
- ACUMULAÃ‡ÃƒO VENDEDORA
- DISTRIBUIÃ‡ÃƒO VENDEDORA
- EXPLOSÃƒO DETECTADA
- SEM EXPLOSÃƒO
- PRESSÃƒO INSTITUCIONAL
- regiÃ£o
- confirmaÃ§Ã£o
- predominÃ¢ncia
- observaÃ§Ã£o

Também foram encontrados emojis quebrados em price lines:

- ðŸŸ¥ STOP
- ðŸŸ¨ PARCIAL
- ðŸŸ© ALVO

---

## 4. Achados de UTF8_BOM

Foram encontrados arquivos com UTF8_BOM no frontend.

Arquivos listados na auditoria:

- frontend/src/components/BoxDestaque.js
- frontend/src/components/Linhas.js
- frontend/src/components/PressaoBar.js
- frontend/src/components/Radar.js
- frontend/src/components/ScorePanel.js
- frontend/src/components/Secao.js
- frontend/src/components/SignalCard.js
- frontend/src/components/Titulo.js
- frontend/src/components/TopBar.js
- frontend/src/services/trinWebSocket.js
- frontend/src/App.test.js
- frontend/src/index.js
- frontend/src/reportWebVitals.js
- frontend/src/setupTests.js

---

## 5. Classificação

Os problemas encontrados foram classificados em dois grupos:

### Grupo A — texto visual quebrado

Afeta leitura visual e clareza do cockpit.

Pode aparecer quando o Fiscal liberar outros cenários ou quando o motor passar a entregar fases como absorção, exaustão, compressão, acumulação ou distribuição.

### Grupo B — UTF8_BOM

Gera warnings no build, mas não quebrou a compilação até o momento.

A remoção deve ser feita com cuidado, em patch próprio, com build obrigatório depois.

---

## 6. Regra para limpeza futura

A limpeza futura deve obedecer:

- não alterar lógica;
- não alterar cálculo;
- não alterar payload;
- não alterar backend;
- não alterar motor;
- não mexer em Fiscal, Bernardo, Zé ou Historiador;
- trocar apenas textos quebrados por textos ASCII simples;
- remover BOM apenas em commit separado ou seção claramente delimitada;
- rodar npm run build depois;
- commitar separadamente.

---

## 7. Sugestão de substituições futuras

Substituir textos quebrados por versões sem acento:

- ABSORCAO ATIVA
- EXAUSTAO INSTITUCIONAL
- COMPRESSAO INSTITUCIONAL
- ACUMULACAO COMPRADORA
- ACUMULACAO VENDEDORA
- DISTRIBUICAO VENDEDORA
- EXPLOSAO DETECTADA
- SEM EXPLOSAO
- PRESSAO INSTITUCIONAL
- regiao
- confirmacao
- predominancia
- observacao

Substituir emojis quebrados por texto simples:

- STOP
- PARCIAL
- ALVO

---

## 8. Parecer

A auditoria confirmou que a limpeza de encoding é necessária, mas não urgente o suficiente para ser misturada com os patches estruturais feitos hoje.

Recomendação:

Fazer a limpeza em etapa própria, com patch pequeno, build e commit separado.

---

## 9. Status final

ENCODING_FRONTEND_MAPEADO_AGUARDANDO_PATCH_CONTROLADO

