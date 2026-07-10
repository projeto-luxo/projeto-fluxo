# LAUDO CR-02B — CANDLE CANONICO NOS MOTORES

## Identificacao

Data: 2026-07-10
Projeto: TRIN
Modulo: Backend / CandleEngine / VWAPEngine

Arquivos alterados:

- backend/server_institucional_v6.py
- core/candle_engine.py
- core/vwap_engine.py

## Objetivo

Alinhar temporalmente:

- historico operacional do cockpit;
- CandleEngine;
- VWAPEngine.

O mesmo timestamp deve representar somente um candle em cada memoria.

## Falha original

Antes do CR-02B, duas atualizacoes do mesmo timestamp produziam:

- historico com 1 candle;
- CandleEngine com 2 candles;
- VWAPEngine com 2 candles.

A causa era a alimentacao dos motores antes da consolidacao temporal do historico.

## Correcao aplicada

Foi criado nos dois motores o metodo:

adicionar_ou_atualizar_candle

Comportamento:

- lista vazia: ADICIONADO;
- mesmo timestamp do ultimo candle: ATUALIZADO;
- novo timestamp: ADICIONADO;
- limite maximo: 50 candles.

Os metodos antigos adicionar_candle foram preservados.

## Copia defensiva

CandleEngine e VWAPEngine armazenam:

dict(candle)

Dessa forma, os motores nao compartilham a mesma referencia mutavel do historico operacional.

## Nova ordem no backend

No modo AO_VIVO:

1. gerar leitura;
2. enriquecer volume;
3. detectar fonte estagnada;
4. consolidar o historico;
5. obter historico[-1] como candle canonico;
6. atualizar CandleEngine;
7. calcular reversao;
8. atualizar VWAPEngine;
9. retornar o candle canonico.

## Teste isolado pos-patch

Status: APROVADO

Resultado:

- testes executados: 15;
- aprovados: 15;
- reprovados: 0.

Foram validados:

- primeiro candle acrescentado nos dois motores;
- mesmo timestamp atualizado sem aumentar tamanho;
- novo timestamp acrescentado;
- copia defensiva;
- metodos legados preservados;
- reversao calculada sobre candle canonico atualizado;
- VWAP sem timestamp duplicado;
- limite de 50 candles;
- consolidacao do historico antes dos motores;
- historico, CandleEngine e VWAPEngine com os mesmos timestamps;
- RTD estagnado preservando os dados de mercado e os motores;
- metadados de estagnacao registrados no historico;
- CR-02A permanecendo idempotente;
- reset CR-01 recriando os motores vazios;
- escopo Git preservado.

Relatorio:

C:\Users\User\TRIN_BACKUPS\TESTE_POS_PATCH_CR02B_20260710_003632\RELATORIO_TESTE_POS_PATCH_CR02B.json

## Teste no backend real

Status: APROVADO

O backend foi reiniciado carregando os tres arquivos alterados.

Resultado observado:

- endpoint /painel/replay/status respondeu;
- Replay permaneceu inativo;
- modo de dados: AO_VIVO;
- endpoint /data respondeu;
- historico retornado: 1 candle;
- processamento: NOVO_EVENTO_PROCESSADO;
- sequencia operacional: 1;
- origem: RTD_EXCEL_AGREGADO;
- frontend e contratos de payload permaneceram operacionais.

## Fonte estagnada

Durante o smoke test, o painel informou:

OPERACIONAL_NAO_CERTIFICADO_FONTE_ESTAGNADA

Esse resultado e coerente com o mercado fechado.

A fonte estagnada nao reprova o CR-02B.

## Hashes finais

backend/server_institucional_v6.py

f14a9897ccd91ceee1d6d24d0b9223114c3fb3ee98a91520167470906012e886

core/candle_engine.py

00bce838cd59632c479afa810d8b40745d70053df437ffc6945520ccc91d32aa

core/vwap_engine.py

586c8cf01f74bd4f9daa140f95f0f66d1a3ec110e0024e8b60dcf6a9326a59ec

## Escopo preservado

O CR-02B nao alterou:

- AggressionEngine;
- ConfluenceEngine;
- cache do CR-02A;
- reset institucional do CR-01;
- TRINEngine;
- formulas da VWAP;
- regra matematica de reversao;
- frontend;
- timeframes;
- leitura Replay;
- produtor WebSocket.

## Pendencias separadas

### Validacao complementar em mercado aberto

Quando o RTD estiver avancando, deve ser observado:

- mesmo timestamp atualiza os motores sem aumentar a quantidade;
- novo timestamp acrescenta exatamente um candle.

Essa validacao complementar nao impede o commit tecnico atual.

### Produtor unico WebSocket

Cada cliente ainda possui seu proprio ciclo de atualizacao.

O tema exige auditoria propria.

### TRINEngine

O motor atual permanece sem o metodo processar.

Essa pendencia nao pertence ao CR-02B.

### Replay nos motores

O Replay continua fora da alimentacao direta de CandleEngine e VWAPEngine.

Qualquer integracao futura exige decisao arquitetural propria.

## Classificacao final

CR-02B_CODIGO: APROVADO
TESTE_ISOLADO: APROVADO_15_DE_15
SMOKE_TEST_BACKEND_REAL: APROVADO
BACKEND: OPERACIONAL_COM_CR02B
ROLLBACK: NAO_NECESSARIO
COMMIT_TECNICO: AUTORIZADO
VALIDACAO_RTD_MERCADO_ABERTO: PENDENTE_COMPLEMENTAR

## Parecer

O CR-02B corrigiu a divergencia temporal entre historico, CandleEngine e VWAPEngine.

Atualizacoes do mesmo timestamp agora substituem o candle em formacao nos motores, sem criar duplicidades.

Novos timestamps continuam acrescentando novos candles.

A correcao esta aprovada para preservacao no Git.
