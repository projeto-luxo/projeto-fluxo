# 🏛️ CHECKLIST OFICIAL DE ARQUITETURA — TRIN

## Fila oficial de módulos

```text
🏛️ Bernardo
↓
🐂 Zé do Eucrázio
↓
🧬 Fiscal Temporal
↓
🛡️ Bastião
↓
📚 Historiador
↓
🧠 Motor de Confluência
↓
⚖️ Motor Geral de Pontuação
↓
📈 Pesos Dinâmicos
↓
🎯 Índice de Confiança TRIN
↓
🤖 Aprendizagem
↓
TRIN Completo
```

## Fluxo arquitetural oficial

```text
Mercado
↓
Profit
↓
RTD
↓
Excel
↓
Python
↓
Gravador
↓
Biblioteca Histórica
↓
API do Bernardo
↓
Bernardo
↓
Zé do Eucrázio
↓
Fiscal Temporal
↓
Bernardo atualiza memória
↓
Historiador
↓
Motor de Confluência
↓
Motor Geral de Pontuação
↓
Aprendizagem
↓
TRIN
↓
Operador
```

## Princípios arquiteturais

- [ ] Arquitetura antes do código.
- [ ] Memória antes da inteligência.
- [ ] Motor antes da estética.
- [ ] Cada módulo possui uma responsabilidade principal.
- [ ] Nenhum módulo futuro depende diretamente de outro módulo futuro.
- [ ] Dependências devem apontar apenas para módulos homologados.
- [ ] Dados brutos nunca são alterados.
- [ ] Todo dado derivado deve possuir origem rastreável.
- [ ] Todo módulo deve possuir contrato.
- [ ] Todo módulo deve produzir logs e manifesto quando aplicável.
- [ ] Nenhuma inteligência consome CSV diretamente; deve passar pela API do Bernardo/Bernardo.

## Regra Dado → Informação → Contexto → Conhecimento → Decisão

Cada módulo deve subir apenas um degrau:

```text
Gravador → dado
Bernardo → informação organizada
Zé → reconstrução temporal
Fiscal Temporal → certificação
Historiador → conhecimento histórico
Motor → contexto e pontuação
Operador → decisão
```

## Status atual

- Bernardo: congelado arquiteturalmente como camada oficial de persistência cognitiva.
- Zé do Eucrázio 4.0: aprovado em teste controlado; homologado para integração com Fiscal Temporal; não congelado definitivamente.
- Fiscal Temporal: próximo módulo estrutural.
