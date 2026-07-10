# AUDITORIA PRE-PATCH CR-02B — CANDLE CANONICO NOS MOTORES

## Identificacao

Data: 2026-07-10
Projeto: TRIN
Classificacao: AUDITORIA_PRE_PATCH
Codigo alterado nesta auditoria: NAO

Modulos envolvidos:

- backend/server_institucional_v6.py
- core/candle_engine.py
- core/vwap_engine.py

## 1. Objetivo

Corrigir a divergencia entre:

- historico operacional do cockpit;
- memoria do CandleEngine;
- memoria do VWAPEngine.

Os tres componentes devem representar a mesma quantidade de candles e a mesma identidade temporal.

## 2. Falha comprovada

O teste isolado CR-02 demonstrou:

- duas atualizacoes com o mesmo timestamp;
- historico permaneceu com 1 candle;
- CandleEngine passou a conter 2 candles;
- VWAPEngine passou a conter 2 candles.

Classificacao:

FALHA_ARQUITETURAL_CONFIRMADA

Relatorio:

C:\Users\User\TRIN_BACKUPS\TESTE_ISOLADO_CR02_20260709_233904\RELATORIO_TESTE_ISOLADO_CR02.json

## 3. Causa

A ordem atual do backend e:

1. adicionar candle ao CandleEngine;
2. calcular reversao;
3. adicionar candle ao VWAPEngine;
4. verificar se o timestamp ja existe;
5. consolidar ou acrescentar no historico.

Assim, a deduplicacao ocorre tarde demais.

## 4. Consumidores auditados

A busca geral confirmou que o consumidor real em runtime dos metodos:

- CandleEngine.adicionar_candle;
- VWAPEngine.adicionar_candle;
- CandleEngine.calcular_reversao;
- VWAPEngine.calcular_vwap_e_bandas;

e:

backend/server_institucional_v6.py

As ocorrencias localizadas em governance/11_EXECUCAO_GOVERNANCA sao copias historicas e nao fazem parte do runtime.

O arquivo data/realtime_interface.py possui uma lista propria self.candles e nao utiliza CandleEngine ou VWAPEngine.

## 5. Decisao de compatibilidade

Os metodos legados:

- adicionar_candle;

serao preservados.

Sera criado em ambos os motores:

- adicionar_ou_atualizar_candle.

Essa decisao evita alterar o contrato antigo e explicita o novo comportamento temporal.

## 6. Contrato do novo metodo

Entrada:

- dicionario representando candle operacional canonico.

Identidade:

- campo time.

Comportamento:

### Lista vazia

Acrescentar copia do candle.

### Mesmo timestamp do ultimo candle

Substituir a ultima posicao por copia do candle atualizado.

### Timestamp diferente

Acrescentar copia do novo candle.

### Limite

Manter no maximo os 50 candles mais recentes.

### Retorno

Informar se a operacao foi:

- ADICIONADO;
- ATUALIZADO.

## 7. Copia defensiva

Os motores devem armazenar:

dict(candle)

e nao a mesma referencia mutavel mantida no historico.

Objetivo:

- impedir alteracao silenciosa da memoria do motor;
- garantir que atualizacao ocorra somente pelo metodo oficial;
- facilitar auditoria e testes.

## 8. Nova ordem do backend

No modo AO_VIVO:

1. gerar candle;
2. enriquecer volume;
3. detectar fonte RTD estagnada;
4. consolidar candle no historico;
5. definir o candle canonico como historico[-1];
6. atualizar ou acrescentar no CandleEngine;
7. calcular reversao usando a memoria canonica;
8. registrar reversao no candle canonico;
9. atualizar ou acrescentar no VWAPEngine;
10. retornar o candle canonico.

## 9. Candle em formacao

O candle atual nao deve esperar o fechamento definitivo para entrar nos motores.

Enquanto possuir o mesmo timestamp:

- CandleEngine substitui a ultima versao;
- VWAPEngine substitui a ultima versao;
- o numero de candles nao aumenta.

Quando o timestamp muda:

- um novo candle e acrescentado.

Isso mantem:

- VWAP atualizada;
- bandas atualizadas;
- reversao alinhada ao grafico;
- memoria dos motores alinhada ao historico.

## 10. Replay

O ramo Replay atualmente alimenta apenas o historico.

Integrar Replay ao CandleEngine e ao VWAPEngine ampliaria o escopo.

Portanto, fica fora do CR-02B.

## 11. Preservacoes obrigatorias

O CR-02B nao deve alterar:

- AggressionEngine;
- ConfluenceEngine;
- cache do CR-02A;
- reset do CR-01;
- TRINEngine;
- regras de score;
- formulas da VWAP;
- regra matematica de reversao;
- frontend;
- timeframes;
- leitura RTD;
- leitura Replay;
- produtor WebSocket.

## 12. Testes obrigatorios

O patch somente podera ser aprovado se comprovar:

1. primeiro candle e acrescentado aos dois motores;
2. mesmo timestamp atualiza os dois motores sem aumentar tamanho;
3. high, low, close e volume consolidados chegam aos motores;
4. novo timestamp acrescenta um segundo candle;
5. CandleEngine e VWAPEngine permanecem com o mesmo tamanho do historico;
6. reversao usa o candle canonico atualizado;
7. VWAP usa apenas uma ocorrencia por timestamp;
8. limite de 50 candles continua respeitado;
9. metodos legados permanecem disponiveis;
10. RTD estagnado nao altera os motores;
11. reset CR-01 continua recriando os motores vazios;
12. CR-02A permanece funcional;
13. Git permanece limitado aos tres arquivos autorizados.

## 13. Arquivos autorizados

Somente:

- backend/server_institucional_v6.py
- core/candle_engine.py
- core/vwap_engine.py

## 14. Proibicoes

Fica proibido durante o CR-02B:

- modificar copias historicas em governance;
- integrar Replay aos motores;
- alterar formulas;
- reescrever os motores;
- remover adicionar_candle;
- implementar produtor unico;
- corrigir TRINEngine;
- alterar frontend.

## 15. Parecer

O CR-02B e necessario e arquiteturalmente autorizado.

A correcao deve fazer com que historico, CandleEngine e VWAPEngine compartilhem a mesma identidade temporal sem compartilhar a mesma referencia mutavel.

Nenhum codigo deve ser commitado antes de teste isolado e revisao do diff.
