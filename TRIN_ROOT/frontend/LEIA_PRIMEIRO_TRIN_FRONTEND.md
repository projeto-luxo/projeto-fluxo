# TRIN — FRONTEND OFICIAL RECUPERADO E INTEGRADO

## Conteúdo deste pacote

Este pacote contém o frontend React oficial recuperado do ZIP `projeto_fluxo(3).zip`.

Origem auditada:

- projeto_fluxo/frontend/src/App.js
- tamanho original aproximado: 31.711 bytes
- contém painel avançado com gráfico, VWAP, bandas, heatmap, hot zone, radar, glow, painel lateral e WebSocket.

## Alterações aplicadas

1. `src/services/trinWebSocket.js`
   - porta WebSocket alterada de 8000 para 8001.

2. `src/App.js`
   - preservado o App oficial avançado.
   - adicionados blocos visuais para:
     - ConfluenceEngine v2.2
     - Fiscal Temporal
     - Bernardo
     - Historiador
     - Evidências da confluência
     - Bloqueio cognitivo

## Como instalar no TRIN_ROOT

1. Renomeie o frontend atual:

```powershell
cd "C:\Users\User\projeto_fluxo\TRIN_ROOT"
Rename-Item frontend frontend_backup_20260619
```

2. Extraia esta pasta `frontend` para:

```text
C:\Users\User\projeto_fluxo\TRIN_ROOT\frontend
```

3. Entre na pasta:

```powershell
cd "C:\Users\User\projeto_fluxo\TRIN_ROOT\frontend"
```

4. Instale dependências:

```powershell
npm install
```

5. Rode o frontend:

```powershell
npm start
```

## Backend esperado

Antes de abrir o frontend, o backend institucional deve estar rodando:

```powershell
cd "C:\Users\User\projeto_fluxo\TRIN_ROOT"
python -m uvicorn backend.server_institucional_v6:app --reload --port 8001
```

## Checklist de validação

- [ ] React abre em localhost:3000
- [ ] WebSocket fica ONLINE
- [ ] `/data` responde pela porta 8001
- [ ] gráfico aparece
- [ ] VWAP aparece
- [ ] bandas aparecem
- [ ] radar aparece
- [ ] heatmap aparece
- [ ] hot zone aparece
- [ ] painel lateral aparece
- [ ] score institucional aparece
- [ ] Confluence v2.2 aparece
- [ ] Fiscal aparece
- [ ] Bernardo aparece
- [ ] Historiador aparece
- [ ] bloqueio cognitivo aparece se Fiscal reprovar
