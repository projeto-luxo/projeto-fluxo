# AUDITORIA PRE-PATCH CR-02A — IDEMPOTENCIA DO PROCESSAMENTO OPERACIONAL

## Identificacao

Data: 2026-07-09
Projeto: TRIN
Modulo principal: Backend / geracao de payload
Classificacao: AUDITORIA_PRE_PATCH
Codigo alterado nesta auditoria: NAO

## 1. Objetivo

Registrar a auditoria arquitetural previa para impedir que o mesmo evento de mercado seja processado repetidamente pelos motores a cada chamada de:

- gerar_payload;
- endpoint /data;
- WebSocket /ws.

## 2. Falha comprovada

O teste isolado CR-02 executou gerar_payload cinco vezes mantendo o mesmo historico com dois candles.

Resultado observado:

- historico permaneceu com 2 registros;
- fluxo_recente cresceu de 1 para 5;
- memoria_agressao cresceu de 1 para 5;
- history da confluencia cresceu de 1 para 5.

Classificacao do teste:

FALHA_ARQUITETURAL_CONFIRMADA

Relatorio:

C:\Users\User\TRIN_BACKUPS\TESTE_ISOLADO_CR02_20260709_233904\RELATORIO_TESTE_ISOLADO_CR02.json

## 3. Causa arquitetural

gerar_payload nao e uma funcao somente de leitura.

A cada chamada ela executa novamente:

- engine.processar;
- aggression_engine.calcular_frequencia;
- aggression_engine.calcular_memoria_agressao;
- aggression_engine.detectar_explosao_fluxo;
- motor_confluencia.process.

O endpoint /data e cada conexao WebSocket chamam gerar_payload.

Consequentemente, o numero de consumidores visuais pode alterar a memoria dos motores.

## 4. Motor de confluencia real

O backend importa:

core.confluence_engine.ConfluenceEngineV2

O modulo carregado corresponde a versao 2.2.

O metodo process registra o tick em history em toda chamada e pode consultar:

- HistoriadorAdapter;
- FiscalAdapter;
- BernardoAdapter.

O arquivo core/confluence_engine_v2.py corresponde a uma versao paralela 2.1 e nao sera alterado neste patch.

## 5. Situacao do TRINEngine

O arquivo core/engine.py atual nao possui o metodo processar.

O backend captura AttributeError e usa:

SIMULADO_TRINENGINE_SEM_PROCESSAR

Essa pendencia nao pertence ao CR-02A e devera receber auditoria propria.

## 6. Missao unica do CR-02A

Garantir idempotencia do processamento operacional.

Para o mesmo evento de mercado:

- os motores devem ser processados somente uma vez;
- chamadas posteriores devem reutilizar o ultimo calculo;
- AggressionEngine nao deve aumentar suas listas;
- ConfluenceEngineV2 nao deve aumentar history;
- consultas cognitivas nao devem ser repetidas;
- o payload deve continuar sendo entregue normalmente.

## 7. Identidade do evento

A identidade deve usar somente campos de origem do fato de mercado, sem campos derivados pelos motores.

Campos previstos:

- modo de dados: AO_VIVO ou REPLAY;
- ativo;
- time;
- close ou ultimo;
- volume;
- volume_real;
- volume_candle_estimado;
- delta;
- saldo;
- vwap_real.

Campos como explosao_detectada, tipo_explosao, score e confluencia nao podem participar da assinatura, pois sao resultados derivados.

## 8. Regra de novo fato

Sera considerado novo fato quando ao menos um campo da identidade mudar.

Exemplos:

- novo timestamp;
- preco alterado;
- volume alterado;
- delta alterado;
- saldo alterado;
- mudanca entre AO_VIVO e REPLAY.

Se nenhum desses campos mudar, o calculo anterior deve ser reutilizado.

## 9. Estado interno previsto

O backend podera manter:

- ultima_assinatura_evento_processado;
- ultimo_calculo_operacional;
- sequencia_processamento_operacional;
- telemetria de reutilizacao do cache.

Esses estados devem ser reiniciados pelo reset institucional do CR-01.

## 10. Preservacao de contrato

O CR-02A nao deve alterar:

- estrutura atual do payload;
- nomes dos campos consumidos pelo frontend;
- formulas de score;
- regras de entrada;
- contratos do Fiscal;
- contratos do Bernardo;
- contratos do Historiador;
- leitura RTD;
- leitura Replay;
- agregacao dos timeframes.

Podera ser acrescentado apenas um bloco de telemetria diagnostica sobre o processamento.

## 11. Proibicoes

Fica proibido durante o CR-02A:

- alterar os motores individualmente;
- corrigir CandleEngine e VWAPEngine no mesmo patch;
- implementar produtor unico do WebSocket;
- reescrever o backend;
- corrigir o TRINEngine;
- remover a versao paralela da confluencia;
- calibrar scores;
- mexer no frontend.

## 12. Testes obrigatorios

O patch somente podera ser aprovado se demonstrar:

1. cinco chamadas com o mesmo evento geram uma unica entrada na agressao;
2. cinco chamadas com o mesmo evento geram uma unica entrada na confluencia;
3. o payload continua sendo retornado nas cinco chamadas;
4. alteracao real de preco gera novo processamento;
5. alteracao real de delta gera novo processamento;
6. alteracao real de saldo gera novo processamento;
7. novo timestamp gera novo processamento;
8. reset do CR-01 elimina assinatura e cache;
9. AO VIVO e REPLAY nao compartilham cache;
10. Git permanece limitado ao arquivo autorizado.

## 13. Pendencias separadas

Permanecem fora do CR-02A:

### CR-02B

Deduplicacao tardia do CandleEngine e VWAPEngine.

### Produtor unico

Cada cliente WebSocket ainda executa seu proprio loop de atualizacao.

Essa alteracao exigira auditoria propria.

### TRINEngine

O motor atual nao possui processar e permanece em fallback simulado.

### Confluencia paralela

Existem arquivos v2.2 e v2.1 em caminhos diferentes.

A consolidacao exige decisao arquitetural propria.

## 14. Parecer

O CR-02A e necessario e esta arquiteturalmente autorizado como patch pequeno, isolado e reversivel.

O patch deve ocorrer somente em:

backend/server_institucional_v6.py

Nenhum commit de codigo deve ser realizado antes de teste isolado e revisao do diff.
