# 🚀 TRIN — Checklist Oficial (Pronto para colar)

## 📌 Estado Atual do Projeto

🟢 **STATUS:** OPERACIONAL  
🖥 **Frontend:** React  
⚡ **Backend:** FastAPI  
📊 **Gráfico:** lightweight-charts  
🔄 **Atualização:** tempo real via WebSocket  
🔧 **Módulos funcionando:** 
  - Engine (absorção, trap, seq_delta, score, fase)
  - VWAPEngine (VWAP e bandas)
  - CandleEngine (candles e reversão)
  - AggressionEngine (frequência, memória agressão, explosão)
📜 **Dados:** Candles realistas, histórico atualizado, JSON consistente

---

## ✅ Etapa 1 — Backend

* [x] FastAPI rodando (`server.py`)
* [x] Endpoint `/data` funcionando
* [x] WebSocket `/ws` ativo e estável
* [x] Histórico de candles atualizado corretamente
* [x] Engines base sincronizadas
* [x] Payload JSON consistente com todos os dados necessários para o frontend

---

## ✅ Etapa 2 — Frontend

* [x] React rodando (`App.jsx`)
* [x] WebSocket conectado (`connectTrinWebSocket`) e recebendo dados
* [x] Gráfico candlestick atualizado em tempo real
* [x] Painel lateral institucional funcionando
* [x] VWAP e bandas exibidas
* [x] Candles amarelos de reversão visíveis
* [x] Score institucional visualizado
* [x] Tendência institucional funcionando
* [x] Linhas de STOP, PARCIAL e ALVO corretas
* [x] Glow dinâmico no gráfico
* [x] Radar de pressão institucional presente

---

## ✅ Etapa 3 — Dados e Lógica

* [x] Funções de fluxo (`flow_data.py`) retornando sinais confiáveis
* [x] Cálculos de agressão consistentes (`AggressionEngine`)
* [x] Detectores de reversão funcionando (`CandleEngine`)
* [x] Absorção detectada corretamente (`Engine`)
* [x] Score e fase institucionais corretos
* [x] Explosões de fluxo funcionando (`AggressionEngine`)

---

## 📌 Etapa 4 — Diretrizes Oficiais de Trabalho

### 1️⃣ Princípio Central
Construir sistema funcional, estável, evolutivo e tecnicamente confiável.

### 2️⃣ Regras do Projeto
1. **Não mexer em código funcional sem necessidade.**
2. **Salvar antes de qualquer teste.**
3. **Testar backend isolado antes do frontend.**
4. **Uma alteração por vez.**
5. **Checklist atualizado diariamente.**
6. **Manter App.js e server.py organizados.**
7. **Confirmação de WebSocket ativo antes de testar sinais.**
8. **Se quebrar → parar, corrigir, testar, só depois evoluir.**

### 3️⃣ Anti-Bajulação Técnica
Não implementar ideias que aumentem risco técnico sem benefício proporcional:
- Não adicionar múltiplas features ao mesmo tempo
- Não automatizar antes da leitura manual
- Não trocar arquitetura estável por modismo
- Não implementar IA antes das engines estarem maduras

### 4️⃣ Clarificação Obrigatória
Confirmar termos vagos antes de alterar:
- "institucional" → visual profissional / fluxo real / footprint / tape reading / DOM L2 / replay / automação / IA comparativa

### 5️⃣ Sistemática do Repetível
Checklist diário:
- **Frontend:** App.jsx sem erro, console limpo, renderização normal, WebSocket conectado, JSON chegando
- **Backend:** server sobe, endpoints respondem, WebSocket ativo, payload consistente, engines sincronizadas
- **Integração:** frontend/backend comunicam, dados atualizam, sem loops quebrados ou freeze

### 6️⃣ Verificação Antes de Entregar
- Imports corretos
- Função existe
- Nomes consistentes
- Sintaxe válida
- Frontend compatível
- Backend compatível
- JSON bate
- Estrutura modular respeitada

### 7️⃣ Admitir Incerteza Técnica
- Profit API
- WebSocket externo
- DOM real
- L2 real
- Provedor real
- Replay proprietário
→ Não fingir certeza, testar antes

### 8️⃣ Arquitetura Primeiro
Antes de codar:
- Definir problema
- Impacto
- Módulo afetado
- Dependências
- Risco de quebra

### 9️⃣ Uma Alteração por Vez
Nunca alterar:
- backend + frontend + websocket + layout juntos
Sempre: 1 mudança → teste → validação → próximo passo

### 🔟 Preservação de Estabilidade
Se algo funciona:
- não reescrever por impulso
- questionar benefício técnico real

---

## 🔮 Etapa 5 — Próximos Passos Seguros

### NÍVEL 4.6 — Heatmap Institucional
* [ ] Desenhar zonas quentes
* [ ] Identificar regiões institucionais
* [ ] Mostrar defesa compradora/vendedora
* [ ] Melhorar leitura visual do fluxo
* [ ] Aproximar visual ASG institucional

### Evolução futura
* Painel estilo ASG
* Tape reading visual
* Replay mode
* Alertas sonoros
* Detector de armadilhas
* Detector de spoofing
* Multiativos
* Multi-timeframe
* IA de classificação de contexto
* Conexão Profit Pro / NinjaTrader
* Backend online
* Frontend online
* Domínio próprio

---

# ⚠️ Observação Final
Este checklist é **documento oficial diário**.  
Antes de qualquer mudança:
- Revisar checklist
- Garantir compatibilidade
- Testar alterações isoladas
- Atualizar status após conclusão
