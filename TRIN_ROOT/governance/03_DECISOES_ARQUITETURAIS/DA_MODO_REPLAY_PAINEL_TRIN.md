# DA_MODO_REPLAY_PAINEL_TRIN.md

## Status

DECISAO_ARQUITETURAL_OFICIAL  
Data: 2026-06-26  
Projeto: TRIN  
Tema: Modo Replay do Painel TRIN  

---

## 1. Contexto

O painel TRIN atualmente opera em modo AO_VIVO, alimentado por Profit, RTD, Excel e backend.

Como o mercado nem sempre esta aberto, foi identificada a necessidade de criar um modo REPLAY para permitir testes operacionais do painel, CandleBuilder e timeframes usando historico CSV da Biblioteca TRIN.

---

## 2. Decisao principal

O TRIN podera ter dois modos oficiais de fonte de dados:

AO_VIVO

e

REPLAY

O modo AO_VIVO usa dados do Profit/RTD/Excel.

O modo REPLAY usa dados historicos CSV da Biblioteca TRIN.

Esses modos nao devem ser misturados na mesma execucao.

---

## 3. Objetivo do modo Replay

O modo Replay serve para testar:

- painel;
- CandleBuilderPainel;
- seletor de timeframe;
- agregacao intraday;
- virada de candle;
- fluxo WebSocket;
- comportamento visual;
- leitura sequencial de dados historicos;
- integracao operacional sem depender de mercado aberto.

---

## 4. O que o Replay nao faz

O modo Replay nao:

- certifica historico;
- corrige candle;
- substitui Fiscal Temporal;
- substitui mercado aberto;
- valida latencia real de RTD;
- valida execucao operacional real;
- gera dado novo;
- inventa candle;
- mistura historico com dado ao vivo.

---

## 5. Fonte de dados

A fonte do Replay deve ser a Biblioteca Historica TRIN.

Exemplo de origem:

TRIN_HISTORICO/001_1_MIN/win

ou outro arquivo historico escolhido de forma controlada.

O Replay deve ler registros em ordem temporal crescente.

---

## 6. Arquitetura oficial

Fluxo aprovado:

TRIN_HISTORICO CSV  
-> ReplayReader  
-> ReplayClock  
-> CandleBuilderPainel  
-> WebSocket  
-> Painel React  

O painel nao deve depender diretamente do CSV.

O backend deve entregar ao painel o mesmo tipo de estrutura operacional que entrega no modo AO_VIVO.

---

## 7. Identificacao obrigatoria no painel

Quando o modo REPLAY estiver ativo, o painel deve exibir claramente:

MODO REPLAY

ou

FONTE: REPLAY

Isso evita confusao com mercado real.

---

## 8. Regras de seguranca

Fica proibido:

- usar Replay como se fosse mercado ao vivo;
- misturar RTD e Replay ao mesmo tempo;
- gravar dados de Replay como se fossem captura real;
- alterar Biblioteca Historica durante Replay;
- usar Replay para certificar historico;
- gerar ordem operacional real baseada em Replay.

---

## 9. Controles desejados

O modo Replay devera evoluir para suportar:

- escolher ativo;
- escolher arquivo;
- escolher data inicial;
- play;
- pause;
- reset;
- velocidade 1x, 5x, 10x;
- passo a passo;
- status visivel no painel.

Esses controles podem ser implementados em etapas separadas.

---

## 10. Primeira implementacao autorizada

A primeira implementacao deve ser minima e conservadora.

Escopo inicial autorizado:

- criar modo REPLAY no backend;
- ler um CSV historico escolhido;
- enviar dados sequenciais ao WebSocket;
- marcar painel como REPLAY;
- nao alterar Fiscal, Ze, Bernardo ou Historiador;
- nao substituir modo AO_VIVO.

---

## 11. Criterio de sucesso

O modo Replay sera considerado funcional inicialmente se:

- o backend conseguir ler um CSV historico;
- o painel receber dados em sequencia temporal;
- o CandleBuilder formar candles operacionais;
- o seletor de timeframe continuar funcionando;
- o painel indicar claramente que esta em Replay;
- o modo AO_VIVO permanecer intacto.

---

## 12. Decisao final

O modo Replay fica aprovado como simulacao operacional do TRIN.

Ele permite continuar desenvolvimento e validacao interna em mercado fechado, mas nao substitui validacao em mercado aberto.

Status:

REPLAY_APROVADO_COMO_SIMULACAO_OPERACIONAL
