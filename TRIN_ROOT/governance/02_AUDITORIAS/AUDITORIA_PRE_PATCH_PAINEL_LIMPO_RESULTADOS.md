# AUDITORIA_PRE_PATCH_PAINEL_LIMPO_RESULTADOS.md

## Status

AUDITORIA_PRE_PATCH  
Data: 2026-07-01  
Projeto: TRIN  
Modulo: Frontend / Painel TRIN  
Tema: Painel limpo de resultados com regua fixa de mercado

---

## 1. Objetivo

Organizar o painel lateral do TRIN para deixar a tela principal limpa, objetiva e operacional.

O painel principal deve mostrar resultados e leitura de mercado, nao relatorio tecnico bruto.

---

## 2. Problema atual

O painel lateral exibe muitas informacoes no mesmo nivel visual:

- confluencia
- fiscal
- contrato
- TT RAW
- Bernardo
- Historiador
- evidencias
- fluxo
- agressao
- stop/parcial/alvo
- sinais
- diagnosticos internos

Isso cria poluicao visual e pode confundir informacao operacional com informacao tecnica.

---

## 3. Decisao arquitetural

O painel principal sera dividido em duas categorias:

### 3.1 Fixo no painel

Informacoes de regua objetiva do mercado:

- ultimo preco
- maxima do dia
- minima do dia
- volume
- delta
- saldo
- VWAP
- distancia da VWAP
- ultimo topo
- ultimo fundo
- macro
- micro
- timeframe
- contrato
- status geral

Essas informacoes ficam sempre visiveis.

### 3.2 Condicional no painel

Informacoes que so aparecem quando existir evento real:

- possivel reversao
- possivel absorcao
- explosao
- exaustao
- entrada autorizada
- stop
- parcial
- alvo
- bloqueio operacional
- alerta critico

Se nao houver evento, nao deve aparecer poluicao visual.

---

## 4. Regra operacional

Entrada, stop, parcial e alvo nao devem aparecer como elementos operacionais se nao houver entrada valida.

Se houver apenas reversao provavel, o painel deve mostrar alerta de atencao, nao ordem.

Se houver bloqueio por Fiscal, contrato ou governanca, o painel deve informar bloqueio e impedir leitura como entrada operacional.

---

## 5. Informacoes tecnicas

Informacoes tecnicas devem ficar ocultas, recolhidas ou em area secundaria:

- TT RAW detalhado
- linhas e snapshots TT RAW
- evidencias brutas
- Bernardo detalhado
- Historiador detalhado
- Fiscal detalhado
- logs
- diagnosticos internos

O painel principal nao deve virar laudo tecnico.

---

## 6. Escopo do patch

Este patch deve alterar apenas:

- frontend/src/App.js

Nao alterar:

- backend
- core
- data/leitor_institucional.py
- TT RAW
- Fiscal Temporal
- Bernardo
- Historiador
- CandleBuilder
- scripts de launcher

---

## 7. Estrutura visual desejada

### Bloco 1 - Status Geral

- WS
- Backend/Fonte
- Contrato
- Fiscal/Governanca
- Status final

### Bloco 2 - Regua de Mercado

- Ultimo
- Maxima
- Minima
- Volume
- Delta
- Saldo
- VWAP
- Distancia VWAP

### Bloco 3 - Estrutura

- Macro
- Micro
- Ultimo topo
- Ultimo fundo
- Tendencia

### Bloco 4 - Decisao

- Direcao
- Entrada
- Confianca
- Alerta relevante

### Bloco 5 - Risco

Aparece somente se houver entrada valida:

- Entrada
- Stop
- Parcial
- Alvo

### Bloco 6 - Tecnico recolhido

- TT RAW
- Bernardo
- Historiador
- Evidencias
- Diagnosticos

---

## 8. Criterio de aceite

O patch sera aceito se:

- o painel principal ficar visualmente mais limpo
- TT RAW nao parecer dado operacional
- stop/parcial/alvo so aparecerem com entrada valida
- dados tecnicos ficarem secundarios
- grafico continuar recebendo candles reais
- /data continuar funcionando
- /tt/raw/status continuar funcionando
- git diff --check nao apresentar erro

---

## 9. Parecer

APROVADO PARA PATCH VISUAL CONTROLADO.

A proxima alteracao deve ser pequena, concentrada no frontend/src/App.js, sem mexer na arquitetura operacional.
