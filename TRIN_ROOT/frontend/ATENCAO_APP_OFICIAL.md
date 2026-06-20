# ATENÇÃO — APP OFICIAL DO FRONTEND TRIN

O arquivo correto do painel React é:

frontend/src/App.js

Não usar frontend/App.js na raiz. Ele foi removido deste pacote para evitar confusão.

Este pacote preserva a estrutura React oficial:

frontend/
├── package.json
├── package-lock.json
├── public/
└── src/
    ├── App.js  ← APP OFICIAL, grande, integrado ao Confluence v2.2
    ├── index.js
    └── services/trinWebSocket.js

Backend esperado:

python -m uvicorn backend.server_institucional_v6:app --reload --port 8001

Frontend:

cd C:\Users\User\projeto_fluxo\TRIN_ROOT\frontend
npm install
npm start
