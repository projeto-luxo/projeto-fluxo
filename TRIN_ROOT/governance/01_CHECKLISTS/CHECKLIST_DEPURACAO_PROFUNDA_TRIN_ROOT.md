# CHECKLIST — DEPURACAO PROFUNDA DO TRIN_ROOT

## Objetivo

Levantar, a partir dos checklists historicos do projeto, o que ja foi validado, o que permanece no TRIN_ROOT atual, o que ainda roda, o que precisa ser conferido e o que falta implementar ou recuperar.

Este checklist nao homologa modulo.

Ele serve para depuracao profunda do estado real do TRIN_ROOT.

---

## 1. Intencao original do TRIN

Status historico:

VALIDADO COMO INTENCAO ORIGINAL

O TRIN nasceu como painel institucional de leitura de fluxo em tempo real.

Elementos historicos ja previstos:

- Backend FastAPI
- Frontend React
- Grafico candlestick
- VWAP
- Reversao institucional
- Absorcao
- Exaustao
- Tendencia institucional
- Score institucional
- Painel lateral institucional
- Heatmap futuro
- Tape reading futuro
- Replay futuro
- Multi-timeframe futuro
- Conexao Profit futura
- IA de contexto futura

Acao no TRIN_ROOT atual:

[ ] Conferir quais desses itens existem hoje em codigo.
[ ] Conferir quais desses itens rodam hoje.
[ ] Separar visual antigo de arquitetura atual.

---

## 2. Base operacional inicial

Historicamente validado:

- Backend FastAPI rodando
- Endpoint /data funcionando
- Frontend React rodando
- Integracao frontend + backend
- Comunicacao em tempo real
- Projeto versionado no Git

Status esperado no TRIN_ROOT atual:

PARCIALMENTE VALIDADO / PRECISA CONFERIR

Checklist de conferencia:

[ ] backend atual sobe sem erro.
[ ] frontend atual sobe sem erro.
[ ] websocket ou endpoint principal responde.
[ ] painel recebe dados.
[ ] Git esta em branch TRIN_CLEAN.
[ ] Git esta sincronizado com origin/TRIN_CLEAN.
[ ] nao existe arquivo modificado sem controle.

---

## 3. Visual institucional / cockpit

Historicamente validado:

- Layout institucional
- Historico de candles
- Atualizacao automatica
- Grafico candlestick
- Painel lateral
- Linhas de STOP
- Linhas de PARCIAL
- Linhas de ALVO
- VWAP
- Score visual
- Tendencia visual
- Contexto operacional

Status no TRIN_ROOT atual:

EXISTE / PRECISA TESTE VISUAL COMPLETO

Checklist:

[ ] grafico candlestick renderiza.
[ ] VWAP renderiza.
[ ] painel lateral renderiza.
[ ] score aparece.
[ ] tendencia aparece.
[ ] contexto aparece.
[ ] linhas de stop/parcial/alvo so aparecem quando ha entrada valida.
[ ] bloqueio fiscal impede uso operacional indevido.
[ ] cockpit nao induz decisao quando status esta bloqueado.

---

## 4. Inteligencia de fluxo antiga

Historicamente validado ou previsto:

- Reversao institucional
- Candle amarelo automatico
- Detector de absorcao
- Detector de exaustao
- Score institucional
- Tendencia institucional
- Mercado lateral
- Heatmap institucional futuro

Status no TRIN_ROOT atual:

PRECISA MAPEAR CODIGO ATUAL

Checklist:

[ ] localizar modulo atual de reversao.
[ ] localizar modulo atual de absorcao.
[ ] localizar modulo atual de exaustao.
[ ] localizar calculo de score.
[ ] localizar tendencia institucional.
[ ] confirmar se candle amarelo ainda existe.
[ ] confirmar se heatmap existe ou ficou apenas planejado.
[ ] marcar itens removidos, substituidos ou obsoletos.

---

## 5. Arquitetura oficial atual

Historicamente definido:

Mercado
-> Profit
-> RTD
-> Excel
-> Python
-> Gravador
-> Biblioteca Historica
-> API do Bernardo
-> Bernardo
-> Ze do Eucrazio
-> Fiscal Temporal
-> Bernardo atualiza memoria
-> Historiador
-> Motor de Confluencia
-> Motor Geral de Pontuacao
-> Aprendizagem
-> TRIN
-> Operador

Status no TRIN_ROOT atual:

ARQUITETURA DEFINIDA / IMPLEMENTACAO PARCIAL

Checklist:

[ ] Profit esta fora do codigo e funciona como fonte.
[ ] RTD/Excel existe como ponte.
[ ] Python le Excel.
[ ] Gravador existe.
[ ] Biblioteca Historica existe localmente.
[ ] Bernardo existe.
[ ] API do Bernardo existe ou precisa recuperar.
[ ] Ze do Eucrazio existe.
[ ] Fiscal Temporal existe.
[ ] Historiador existe.
[ ] Motor de Confluencia existe.
[ ] Motor Geral de Pontuacao existe ou falta.
[ ] Aprendizagem existe ou falta.
[ ] Operador permanece como decisor final.

---

## 6. Bernardo

Status historico:

CONGELADO ARQUITETURALMENTE COMO PERSISTENCIA COGNITIVA

Checklist TRIN_ROOT:

[ ] localizar arquivos atuais do Bernardo.
[ ] confirmar se nao foi quebrado por mudancas posteriores.
[ ] confirmar se consumidores nao leem CSV diretamente ignorando Bernardo.
[ ] confirmar se existe contrato oficial.
[ ] confirmar se existe auditoria/homologacao.
[ ] listar pendencias atuais do Bernardo.
[ ] listar se precisa implementar API, ajustar API ou apenas preservar.

---

## 7. Ze do Eucrazio

Status historico:

TESTE CONTROLADO / FRACTAIS / AGUARDANDO CERTIFICACAO DO FISCAL

Checklist historico do Ze previa:

- Git atualizado
- Backup feito
- Bernardo nao alterado
- Fiscal ainda nao chamado
- MODO_TESTE_CONTROLADO=True
- MAX_ARQUIVOS_TESTE=1
- SOBRESCREVER_SAIDA=False
- gerar 2min
- gerar 3min
- gerar demais fractais
- nao alterar originais
- gerar logs
- gerar manifesto
- separar CSV por ;
- usar utf-8-sig
- incluir timestamp/timezone/sessao/status_candle/qtd_candles_origem

Checklist TRIN_ROOT:

[ ] localizar script atual do Ze.
[ ] confirmar versao atual.
[ ] confirmar se modo teste controlado existe.
[ ] confirmar se saidas padronizadas existem.
[ ] confirmar se logs existem.
[ ] confirmar se manifesto existe.
[ ] confirmar se nao altera originais.
[ ] confirmar se ainda depende do Fiscal para certificacao.
[ ] listar o que falta implementar no Ze.
[ ] listar o que foi implementado mas precisa retestar.

---

## 8. Fiscal Temporal

Status historico:

PROXIMO MODULO ESTRUTURAL / CARTORIO TEMPORAL / CERTIFICACAO

Checklist TRIN_ROOT:

[ ] localizar Fiscal Temporal atual.
[ ] confirmar versao atual.
[ ] confirmar se usa calendario externo.
[ ] confirmar se trata lacunas dentro do pregao.
[ ] confirmar se trata lacunas fora do pregao.
[ ] confirmar se trata feriado/fim de semana.
[ ] confirmar se trata leilao.
[ ] confirmar se emite laudo.
[ ] confirmar se emite resumo por arquivo.
[ ] confirmar se emite resumo por motivo.
[ ] confirmar se emite ordens para Bernardo/Ze.
[ ] confirmar se possui criticidade.
[ ] confirmar se possui ID unico de ocorrencia.
[ ] confirmar se possui status de ordem.
[ ] listar pendencias atuais do Fiscal.

---

## 9. Calendario B3 / Contrato ativo

Historicamente previsto:

- calendario oficial de contratos
- calendario oficial de feriados/sessoes
- ContratoAtivoResolver
- Bastiao valida contrato esperado
- comparar contrato esperado x Excel
- comparar contrato esperado x Backend
- emitir aprovado/ressalva/reprovado/bloqueado

Status no TRIN_ROOT atual:

IMPLEMENTACAO PARCIAL / PRECISA CONFERIR

Checklist:

[ ] localizar calendario de contratos B3.
[ ] localizar calendario de feriados/sessoes.
[ ] confirmar fonte oficial registrada.
[ ] confirmar cobertura do ano atual.
[ ] localizar ContratoAtivoResolver.
[ ] confirmar validacao do contrato esperado.
[ ] confirmar comparacao contra Excel.
[ ] confirmar comparacao contra backend.
[ ] confirmar status APROVADO/RESSALVA/REPROVADO/BLOQUEADO.
[ ] listar pendencias do calendario.
[ ] listar pendencias do contrato ativo.

---

## 10. Historiador

Status historico:

PLANEJADO / IMPLEMENTADO EM VERSOES / DEPENDE DE BASE CERTIFICADA

Checklist TRIN_ROOT:

[ ] localizar historiador atual.
[ ] confirmar se existe historiador_temporal.py.
[ ] confirmar se existe historiador_v1_0.py ou versao atual.
[ ] confirmar se le apenas base validada/certificada.
[ ] confirmar saidas de estatistica.
[ ] confirmar saidas de cobertura temporal.
[ ] confirmar distribuicao de fractais.
[ ] confirmar catalogo de padroes.
[ ] confirmar relatorio.
[ ] listar o que esta rodavel.
[ ] listar o que depende do Fiscal/Bernardo.

---

## 11. Motor de Confluencia

Status historico:

IMPLEMENTADO / CALIBRACAO POSTERIOR / NAO DEVE IGNORAR BERNARDO/FISCAL

Checklist TRIN_ROOT:

[ ] localizar motor de confluencia atual.
[ ] confirmar entradas usadas.
[ ] confirmar se respeita bloqueio fiscal.
[ ] confirmar se nao gera ordem sozinho.
[ ] confirmar se nao substitui operador.
[ ] confirmar se nao consome fonte diagnostica como oficial.
[ ] confirmar se esta calibrado ou apenas funcional.
[ ] listar pendencias de calibragem.

---

## 12. CandleBuilder / Painel temporal

Historicamente validado para teste em mercado aberto:

- Preco
- Tempo
- Timeframes intraday
- Bloqueio DIARIO/SEMANAL
- Volume agregado
- Evidencias de teste
- Criterios de aprovacao/ressalva/reprovacao

Status no TRIN_ROOT atual:

RODAVEL / OPERACIONAL_NAO_CERTIFICADO

Checklist:

[ ] confirmar timeframes 15s, 30s, 1_MIN, 2_MIN, 5_MIN, 10_MIN, 15_MIN, 30_MIN, 60_MIN.
[ ] confirmar DIARIO bloqueado.
[ ] confirmar SEMANAL bloqueado.
[ ] confirmar virada correta de candle.
[ ] confirmar ausencia de timestamp duplicado.
[ ] confirmar preco OHLC coerente.
[ ] confirmar volume nao fixo.
[ ] confirmar status OPERACIONAL_NAO_CERTIFICADO.
[ ] confirmar que nao vira historico oficial.
[ ] listar pendencias de volume.
[ ] listar pendencias de rastreabilidade.

---

## 13. Replay Diagnostico 1MIN

Status atual:

RODAVEL / REPLAY_CSV / REPLAY_AGREGADO / NAO CERTIFICADO

Checklist TRIN_ROOT:

[ ] localizar backend/replay_diagnostico.py.
[ ] confirmar rotas start/status/stop/reset.
[ ] confirmar leitura de CSV 1MIN.
[ ] confirmar painel mostra REPLAY_CSV.
[ ] confirmar status REPLAY_OPERACIONAL_NAO_CERTIFICADO.
[ ] confirmar que nao usa mercado aberto.
[ ] confirmar que nao libera decisao operacional.
[ ] listar pendencias do replay 1MIN.

---

## 14. Times and Trades diagnostico

Status atual:

IMPLEMENTADO EM CADEIA DIAGNOSTICA

Componentes:

- Gravador TT Bruto
- Bastiao TT Peneirador
- Candle 5S Diagnostico

Checklist TRIN_ROOT:

[ ] localizar GRAVADOR_TT_BRUTO_01.ps1.
[ ] confirmar tratamento contra RPC_E_CALL_REJECTED.
[ ] confirmar pasta TT_RAW.
[ ] confirmar BASTIAO_TT_PENEIRADOR_01.ps1.
[ ] confirmar saidas peneiradas.
[ ] confirmar rejeitados.
[ ] confirmar incertezas.
[ ] confirmar CANDLE_5S_DIAGNOSTICO_01.ps1.
[ ] confirmar saida CANDLE_5S_DIAGNOSTICO.
[ ] confirmar status NAO_CERTIFICADO.
[ ] confirmar candle_oficial=false.
[ ] listar o que falta validar em mercado aberto.

---

## 15. Replay 5S Diagnostico

Status atual:

PLANEJADO / CONTRATO E AUDITORIA PRE-PATCH JA REGISTRADOS / NAO CODADO

Checklist:

[ ] confirmar contrato do Replay 5S.
[ ] confirmar auditoria pre-patch do Replay 5S.
[ ] confirmar que backend/replay_5s_diagnostico.py ainda nao deve ser criado antes da decisao final.
[ ] definir plano de implementacao.
[ ] implementar somente como modulo separado.
[ ] nao alterar Replay 1MIN no primeiro patch.
[ ] nao alimentar Motor de Confluencia.
[ ] nao liberar decisao operacional.
[ ] testar com Candle 5S ja gerado.
[ ] registrar auditoria pos-patch.

---

## 16. O que permanece no TRIN_ROOT

A preencher apos varredura real dos arquivos:

[ ] backend existente.
[ ] frontend existente.
[ ] core existente.
[ ] intelligence existente.
[ ] tools_rtd existente.
[ ] governance existente.
[ ] TRIN_HISTORICO local existente.
[ ] scripts de inicializacao existentes.
[ ] arquivos obsoletos identificados.
[ ] arquivos duplicados identificados.
[ ] arquivos planejados mas ausentes identificados.

---

## 17. O que precisa implementar novamente ou recuperar

A preencher apos varredura real:

[ ] modulo planejado mas ausente.
[ ] modulo antigo removido que ainda e necessario.
[ ] script sobrescrito por engano.
[ ] contrato sem implementacao.
[ ] auditoria sem patch.
[ ] patch sem auditoria.
[ ] checklist sem execucao.
[ ] homologacao pendente.
[ ] documento duplicado ou contaminado.
[ ] arquivo com encoding quebrado que precisa normalizar.

---

## 18. Decisao desta fase

Antes de codar qualquer coisa nova, executar levantamento real do TRIN_ROOT:

1. Listar arquivos atuais por pasta.
2. Cruzar com este checklist.
3. Marcar o que EXISTE.
4. Marcar o que RODA.
5. Marcar o que FALTA.
6. Marcar o que deve ser RECUPERADO.
7. Gerar laudo final de estado atual.

---

## 19. Proximo comando recomendado

Executar varredura do TRIN_ROOT para preencher este checklist com evidencia real.

---

## Status deste checklist

CRIADO PARA DEPURACAO PROFUNDA

Ainda nao preenchido com evidencias do filesystem atual.

---

## 20. Painel TRIN / Cockpit visual

Status historico:

IMPLEMENTADO EM VARIAS FASES / PRECISA DEPURACAO ATUAL

Objetivo do painel:

Transformar dados de mercado, contexto, confluencia, bloqueios e replay em leitura visual para o operador.

### 20.1 Estrutura visual principal

[ ] Layout institucional do painel existe.
[ ] Cockpit visual existe.
[ ] Grafico candlestick renderiza.
[ ] Painel lateral institucional renderiza.
[ ] Topbar operacional existe.
[ ] Rodape/alerta operacional existe.
[ ] Area central de contexto existe.
[ ] Cards de leitura operacional existem.
[ ] Tema escuro/institucional permanece funcional.

### 20.2 Grafico e candles

[ ] Historico de candles aparece no grafico.
[ ] Candle atual atualiza em tempo real.
[ ] Candles respeitam OHLC.
[ ] Grafico nao duplica timestamps.
[ ] Grafico reconstrói corretamente quando historico muda.
[ ] Marcadores institucionais aparecem quando aplicavel.
[ ] Candles amarelos/reversao ainda existem ou foram substituidos.
[ ] Filtro contra buraco temporal grande existe.
[ ] Painel ignora candle fallback invalido.

### 20.3 VWAP e referencias

[ ] VWAP aparece no grafico.
[ ] VWAP superior aparece quando disponivel.
[ ] VWAP inferior aparece quando disponivel.
[ ] Distancia da VWAP aparece no painel.
[ ] VWAP usa mesma regua temporal dos candles.
[ ] VWAP nao quebra quando muda timeframe.

### 20.4 Linhas operacionais

[ ] Linha de STOP existe.
[ ] Linha de PARCIAL existe.
[ ] Linha de ALVO existe.
[ ] PriceLine de STOP existe.
[ ] PriceLine de PARCIAL existe.
[ ] PriceLine de ALVO existe.
[ ] Linhas so aparecem quando existe entrada valida.
[ ] Linhas somem quando entrada deixa de ser valida.
[ ] Painel nao mostra stop/parcial/alvo em modo bloqueado.

### 20.5 Score, tendencia e contexto

[ ] Score institucional aparece.
[ ] Tendencia aparece.
[ ] Direcao aparece.
[ ] Contexto macro aparece.
[ ] Contexto micro aparece.
[ ] Estado central aparece.
[ ] Chamada principal aparece.
[ ] Qualidade da confluencia aparece.
[ ] Justificativa da confluencia aparece.
[ ] Alerta principal aparece.

### 20.6 Agressao / fluxo / pressao

[ ] Pressao de compra aparece.
[ ] Pressao de venda aparece.
[ ] Placar compra/venda aparece.
[ ] Percentual compra/venda aparece.
[ ] Frequencia de mercado aparece.
[ ] Intensidade de fluxo aparece.
[ ] Score de agressao aparece.
[ ] Leitura de agressao aparece.
[ ] Delta aparece.
[ ] Saldo aparece.
[ ] Volume aparece.
[ ] Volume normalizado/capado aparece.
[ ] Volume candle estimado aparece.
[ ] Tipo de volume aparece.

### 20.7 Detectores visuais

[ ] Reversao institucional aparece ou esta mapeada.
[ ] Absorcao aparece ou esta mapeada.
[ ] Exaustao aparece ou esta mapeada.
[ ] Explosao aparece ou esta mapeada.
[ ] Trap aparece ou esta mapeado.
[ ] Sequencia de delta aparece ou esta mapeada.
[ ] Ultimo topo aparece.
[ ] Ultimo fundo aparece.
[ ] Zona low aparece.
[ ] Zona high aparece.

### 20.8 Fiscal / bloqueio operacional

[ ] Status fiscal aparece.
[ ] Bloqueio por certificacao aparece.
[ ] Motivo do bloqueio aparece.
[ ] Autorizacao operacional aparece.
[ ] Painel mostra AGUARDAR CERTIFICACAO quando bloqueado.
[ ] Painel nao libera entrada quando Fiscal bloqueia.
[ ] Painel separa confluencia tecnica de autorizacao operacional.

### 20.9 Contrato ativo

[ ] Contrato Excel RTD aparece.
[ ] Contrato esperado aparece.
[ ] Status do contrato ativo aparece.
[ ] Motivo do contrato ativo aparece.
[ ] Bloqueio por contrato ativo aparece quando aplicavel.
[ ] Resolver de contrato aparece ou esta integrado.

### 20.10 Timeframes do painel

[ ] Seletor de timeframe existe.
[ ] 15s funciona.
[ ] 30s funciona.
[ ] 1_MIN funciona.
[ ] 2_MIN funciona.
[ ] 5_MIN funciona.
[ ] 10_MIN funciona.
[ ] 15_MIN funciona.
[ ] 30_MIN funciona.
[ ] 60_MIN funciona.
[ ] DIARIO permanece bloqueado.
[ ] SEMANAL permanece bloqueado.
[ ] Troca de timeframe limpa series corretamente.
[ ] Troca de timeframe nao quebra VWAP/bandas.

### 20.11 Status temporal do painel

[ ] Origem temporal aparece.
[ ] Regua do painel aparece.
[ ] Timeframe do painel aparece.
[ ] Status do painel aparece.
[ ] Status da fonte aparece.
[ ] Fonte estagnada aparece quando RTD para.
[ ] Painel diferencia AO_VIVO de REPLAY.
[ ] Painel mostra OPERACIONAL_NAO_CERTIFICADO quando aplicavel.

### 20.12 Replay no painel

[ ] Botao REPLAY ON/AO VIVO existe.
[ ] Campo de data do replay existe.
[ ] Botao CARREGAR DATA existe.
[ ] Status do replay aparece.
[ ] Indice/total do replay aparece.
[ ] Replay limpa grafico ao alternar modo.
[ ] Replay mostra REPLAY_CSV.
[ ] Replay mostra REPLAY_OPERACIONAL_NAO_CERTIFICADO.
[ ] Replay nao libera decisao real.

### 20.13 Times & Trades no painel

[ ] Status TT RAW aparece ou endpoint existe.
[ ] Painel nao trata TT RAW como candle oficial.
[ ] Painel nao usa TT bruto para decisao.
[ ] Painel diferencia TT diagnostico de dado operacional.

### 20.14 O que falta confirmar no App.js

[ ] Conferir se todos os campos acima ainda existem no frontend/src/App.js.
[ ] Conferir se nomes atuais batem com payload do backend.
[ ] Conferir se existe codigo morto/duplicado.
[ ] Conferir se ha texto com encoding quebrado.
[ ] Conferir se ha atributo visual antigo sem uso.
[ ] Conferir se ha atributo novo nao documentado.
[ ] Gerar laudo do painel antes de qualquer patch visual.

## Status da secao Painel/Cockpit

CRIADA PARA DEPURACAO.

Ainda nao marcada como pronta.

Cada item so recebera [v] depois de conferir no TRIN_ROOT atual.

---

## 20. Painel TRIN / Cockpit visual

Status historico:

IMPLEMENTADO EM VARIAS FASES / PRECISA DEPURACAO ATUAL

Objetivo do painel:

Transformar dados de mercado, contexto, confluencia, bloqueios e replay em leitura visual para o operador.

### 20.1 Estrutura visual principal

[ ] Layout institucional do painel existe.
[ ] Cockpit visual existe.
[ ] Grafico candlestick renderiza.
[ ] Painel lateral institucional renderiza.
[ ] Topbar operacional existe.
[ ] Rodape/alerta operacional existe.
[ ] Area central de contexto existe.
[ ] Cards de leitura operacional existem.
[ ] Tema escuro/institucional permanece funcional.

### 20.2 Grafico e candles

[ ] Historico de candles aparece no grafico.
[ ] Candle atual atualiza em tempo real.
[ ] Candles respeitam OHLC.
[ ] Grafico nao duplica timestamps.
[ ] Grafico reconstrói corretamente quando historico muda.
[ ] Marcadores institucionais aparecem quando aplicavel.
[ ] Candles amarelos/reversao ainda existem ou foram substituidos.
[ ] Filtro contra buraco temporal grande existe.
[ ] Painel ignora candle fallback invalido.

### 20.3 VWAP e referencias

[ ] VWAP aparece no grafico.
[ ] VWAP superior aparece quando disponivel.
[ ] VWAP inferior aparece quando disponivel.
[ ] Distancia da VWAP aparece no painel.
[ ] VWAP usa mesma regua temporal dos candles.
[ ] VWAP nao quebra quando muda timeframe.

### 20.4 Linhas operacionais

[ ] Linha de STOP existe.
[ ] Linha de PARCIAL existe.
[ ] Linha de ALVO existe.
[ ] PriceLine de STOP existe.
[ ] PriceLine de PARCIAL existe.
[ ] PriceLine de ALVO existe.
[ ] Linhas so aparecem quando existe entrada valida.
[ ] Linhas somem quando entrada deixa de ser valida.
[ ] Painel nao mostra stop/parcial/alvo em modo bloqueado.

### 20.5 Score, tendencia e contexto

[ ] Score institucional aparece.
[ ] Tendencia aparece.
[ ] Direcao aparece.
[ ] Contexto macro aparece.
[ ] Contexto micro aparece.
[ ] Estado central aparece.
[ ] Chamada principal aparece.
[ ] Qualidade da confluencia aparece.
[ ] Justificativa da confluencia aparece.
[ ] Alerta principal aparece.

### 20.6 Agressao / fluxo / pressao

[ ] Pressao de compra aparece.
[ ] Pressao de venda aparece.
[ ] Placar compra/venda aparece.
[ ] Percentual compra/venda aparece.
[ ] Frequencia de mercado aparece.
[ ] Intensidade de fluxo aparece.
[ ] Score de agressao aparece.
[ ] Leitura de agressao aparece.
[ ] Delta aparece.
[ ] Saldo aparece.
[ ] Volume aparece.
[ ] Volume normalizado/capado aparece.
[ ] Volume candle estimado aparece.
[ ] Tipo de volume aparece.

### 20.7 Detectores visuais

[ ] Reversao institucional aparece ou esta mapeada.
[ ] Absorcao aparece ou esta mapeada.
[ ] Exaustao aparece ou esta mapeada.
[ ] Explosao aparece ou esta mapeada.
[ ] Trap aparece ou esta mapeado.
[ ] Sequencia de delta aparece ou esta mapeada.
[ ] Ultimo topo aparece.
[ ] Ultimo fundo aparece.
[ ] Zona low aparece.
[ ] Zona high aparece.

### 20.8 Fiscal / bloqueio operacional

[ ] Status fiscal aparece.
[ ] Bloqueio por certificacao aparece.
[ ] Motivo do bloqueio aparece.
[ ] Autorizacao operacional aparece.
[ ] Painel mostra AGUARDAR CERTIFICACAO quando bloqueado.
[ ] Painel nao libera entrada quando Fiscal bloqueia.
[ ] Painel separa confluencia tecnica de autorizacao operacional.

### 20.9 Contrato ativo

[ ] Contrato Excel RTD aparece.
[ ] Contrato esperado aparece.
[ ] Status do contrato ativo aparece.
[ ] Motivo do contrato ativo aparece.
[ ] Bloqueio por contrato ativo aparece quando aplicavel.
[ ] Resolver de contrato aparece ou esta integrado.

### 20.10 Timeframes do painel

[ ] Seletor de timeframe existe.
[ ] 15s funciona.
[ ] 30s funciona.
[ ] 1_MIN funciona.
[ ] 2_MIN funciona.
[ ] 5_MIN funciona.
[ ] 10_MIN funciona.
[ ] 15_MIN funciona.
[ ] 30_MIN funciona.
[ ] 60_MIN funciona.
[ ] DIARIO permanece bloqueado.
[ ] SEMANAL permanece bloqueado.
[ ] Troca de timeframe limpa series corretamente.
[ ] Troca de timeframe nao quebra VWAP/bandas.

### 20.11 Status temporal do painel

[ ] Origem temporal aparece.
[ ] Regua do painel aparece.
[ ] Timeframe do painel aparece.
[ ] Status do painel aparece.
[ ] Status da fonte aparece.
[ ] Fonte estagnada aparece quando RTD para.
[ ] Painel diferencia AO_VIVO de REPLAY.
[ ] Painel mostra OPERACIONAL_NAO_CERTIFICADO quando aplicavel.

### 20.12 Replay no painel

[ ] Botao REPLAY ON/AO VIVO existe.
[ ] Campo de data do replay existe.
[ ] Botao CARREGAR DATA existe.
[ ] Status do replay aparece.
[ ] Indice/total do replay aparece.
[ ] Replay limpa grafico ao alternar modo.
[ ] Replay mostra REPLAY_CSV.
[ ] Replay mostra REPLAY_OPERACIONAL_NAO_CERTIFICADO.
[ ] Replay nao libera decisao real.

### 20.13 Times & Trades no painel

[ ] Status TT RAW aparece ou endpoint existe.
[ ] Painel nao trata TT RAW como candle oficial.
[ ] Painel nao usa TT bruto para decisao.
[ ] Painel diferencia TT diagnostico de dado operacional.

### 20.14 O que falta confirmar no App.js

[ ] Conferir se todos os campos acima ainda existem no frontend/src/App.js.
[ ] Conferir se nomes atuais batem com payload do backend.
[ ] Conferir se existe codigo morto/duplicado.
[ ] Conferir se ha texto com encoding quebrado.
[ ] Conferir se ha atributo visual antigo sem uso.
[ ] Conferir se ha atributo novo nao documentado.
[ ] Gerar laudo do painel antes de qualquer patch visual.

## Status da secao Painel/Cockpit

CRIADA PARA DEPURACAO.

Ainda nao marcada como pronta.

Cada item so recebera [v] depois de conferir no TRIN_ROOT atual.

---

## 21. Coleta RTD — Livro de Ofertas

Status atual:

PLANEJADO / IMPORTANTE PARA COCKPIT / NAO IMPLEMENTADO AINDA

Objetivo:

Criar uma coleta diagnostica do Livro de Ofertas via RTD/Excel para alimentar futuramente a leitura visual do cockpit.

Esta coleta nao deve gerar ordem, nao deve liberar entrada e nao deve substituir o operador.

### 21.1 Intencao

O Livro de Ofertas deve ajudar o TRIN a enxergar:

- pressao compradora no book;
- pressao vendedora no book;
- paredes de compra;
- paredes de venda;
- defesa de preco;
- retirada de liquidez;
- spread;
- desequilibrio entre compra e venda;
- possivel absorcao;
- possivel agressao contra liquidez;
- contexto visual para o cockpit.

### 21.2 Fonte esperada

[ ] Profit fornece Livro de Ofertas.
[ ] Excel recebe Livro de Ofertas via RTD.
[ ] Aba especifica do Excel sera definida para o Book.
[ ] Python/PowerShell consegue ler a aba do Book.
[ ] Contrato do Book bate com contrato ativo do painel.
[ ] Timestamp de captura do PC sera registrado.
[ ] Data do pregao sera registrada.

### 21.3 Estrutura minima desejada

Cada snapshot do Livro de Ofertas deve conter, quando disponivel:

[ ] data_pregao.
[ ] timestamp_captura_pc.
[ ] contrato.
[ ] nivel_book.
[ ] preco_compra.
[ ] quantidade_compra.
[ ] agente_compra, se disponivel.
[ ] preco_venda.
[ ] quantidade_venda.
[ ] agente_venda, se disponivel.
[ ] spread.
[ ] soma_quantidade_compra.
[ ] soma_quantidade_venda.
[ ] desequilibrio_book.
[ ] origem=EXCEL_RTD_BOOK.
[ ] status_certificacao=BOOK_RTD_DIAGNOSTICO_NAO_CERTIFICADO.

### 21.4 Gravador Book RTD

Modulo futuro sugerido:

tools_rtd/GRAVADOR_BOOK_RTD_BRUTO_01.ps1

Responsabilidade:

filmar snapshots do Livro de Ofertas sem interpretar mercado.

Checklist:

[ ] criar contrato do Gravador Book RTD.
[ ] criar auditoria pre-patch do Gravador Book RTD.
[ ] identificar aba correta no Excel.
[ ] mapear colunas do Book.
[ ] criar gravador bruto.
[ ] salvar RAW sem apagar dados anteriores.
[ ] tratar Excel ocupado/RPC_E_CALL_REJECTED.
[ ] registrar origem e timestamp.
[ ] nao gerar candle.
[ ] nao gerar sinal.
[ ] nao alimentar motor operacional.

### 21.5 Processamento futuro do Book

Modulo futuro possivel:

Bastiao Book / Peneirador Book

Funcao:

[ ] separar snapshot valido.
[ ] rejeitar linha vazia/casca.
[ ] identificar book congelado.
[ ] identificar spread invalido.
[ ] preservar incertezas.
[ ] calcular desequilibrio diagnostico.
[ ] calcular pressao por nivel.
[ ] calcular parede provavel.
[ ] nao declarar intencao institucional como certeza.

### 21.6 Uso no cockpit

O cockpit podera futuramente exibir:

[ ] pressao book compra.
[ ] pressao book venda.
[ ] desequilibrio book.
[ ] spread atual.
[ ] maior parede compradora.
[ ] maior parede vendedora.
[ ] defesa de preco.
[ ] alerta de book congelado.
[ ] status BOOK_RTD_DIAGNOSTICO.
[ ] aviso NAO_OPERACIONAL.

### 21.7 Proibicoes

A coleta do Livro de Ofertas nao pode:

[ ] gerar entrada.
[ ] gerar stop.
[ ] gerar parcial.
[ ] gerar alvo.
[ ] substituir Times & Trades.
[ ] substituir CandleBuilder.
[ ] substituir Fiscal.
[ ] alimentar Motor de Confluencia como dado oficial.
[ ] ser tratada como certificada.
[ ] ser usada isoladamente para decisao operacional.

### 21.8 Status de validacao

[ ] aba do Livro de Ofertas definida.
[ ] colunas mapeadas.
[ ] coleta bruta criada.
[ ] coleta bruta testada em mercado aberto.
[ ] arquivo RAW gerado.
[ ] duplicidade/congelamento avaliados.
[ ] laudo gerado.
[ ] cockpit recebeu apenas casca diagnostica.
[ ] integracao operacional bloqueada.

---

## 22. Time / Candle 5 Segundos Diagnostico

Status atual:

5S-01 HOMOLOGADO NO COCKPIT / AMOSTRA AINDA INSUFICIENTE PARA VALIDACAO DE CONTINUIDADE

Objetivo:

Organizar definitivamente a regua de 5 segundos diagnostica para servir como base visual curta do cockpit, sem transformar esse dado em candle oficial.

### 22.1 Cadeia atual

Cadeia existente:

RTD Excel TT
-> Gravador TT Bruto
-> Bastiao TT Peneirador
-> TT_PENEIRADO_NAO_CERTIFICADO
-> CANDLE_5S_DIAGNOSTICO

Checklist:

[v] Gravador TT Bruto existe.
[v] Gravador TT foi reforcado contra Excel ocupado/RPC_E_CALL_REJECTED.
[v] Bastiao TT Peneirador v0 existe.
[v] Candle 5S Diagnostico v0 existe.
[v] Primeiro teste gerou candles 5S.
[ ] Validar com amostra maior de mercado aberto.
[ ] Validar continuidade temporal.
[ ] Validar volume por bucket.
[ ] Validar varios horarios do pregao.
[ ] Validar comparacao visual com Profit.
[ ] Validar comportamento em leilao.
[ ] Validar comportamento em pouca liquidez.

### 22.2 Campos obrigatorios do Candle 5S

Cada Candle 5S Diagnostico deve possuir:

[v] data_pregao.
[v] contrato.
[v] timeframe=5S.
[v] bucket_inicio.
[v] bucket_fim.
[v] abertura.
[v] maximo.
[v] minimo.
[v] fechamento.
[v] volume_quantidade.
[v] qtd_negocios.
[v] eventos_pregao.
[v] eventos_leilao.
[v] fonte=TT_PENEIRADO_NAO_CERTIFICADO.
[v] status_candle=CANDLE_5S_DIAGNOSTICO_NAO_CERTIFICADO.
[v] uso_operacional=DIAGNOSTICO_APENAS.
[v] candle_oficial=false.

### 22.3 Organização para cockpit

O cockpit deve tratar Candle 5S como:

[ ] regua curta diagnostica.
[ ] laboratorio visual.
[v] fonte nao operacional.
[ ] complemento de leitura.
[v] nunca como autorizacao de entrada.
[v] nunca como candle oficial.
[v] nunca como substituto do Fiscal.

Campos visuais futuros:

[v] status do Candle 5S.
[v] quantidade de candles 5S gerados.
[v] origem TT_PENEIRADO.
[v] horario inicial/final.
[v] volume por 5S.
[v] qtd negocios por 5S.
[v] aviso DIAGNOSTICO_APENAS.
[v] aviso NAO_CERTIFICADO.

### 22.4 Replay 5S Diagnostico

Status atual:

PLANEJADO / CONTRATO E AUDITORIA PRE-PATCH REGISTRADOS / NAO IMPLEMENTAR SEM DECISAO FINAL

Checklist:

[ ] confirmar contrato do Replay 5S Diagnostico.
[ ] confirmar auditoria pre-patch do Replay 5S Diagnostico.
[ ] criar plano de implementacao controlado.
[ ] criar backend/replay_5s_diagnostico.py somente quando autorizado.
[ ] manter separado do Replay 1MIN.
[ ] preservar status REPLAY_5S_DIAGNOSTICO_NAO_OPERACIONAL.
[ ] bloquear entrada, stop, parcial e alvo.
[ ] testar com arquivo Candle 5S ja existente.
[ ] gerar auditoria pos-patch.
[ ] somente depois avaliar exibicao no painel.

### 22.5 Dependencias do 5S

O Candle 5S depende de:

[ ] TT RAW confiavel.
[ ] Bastiao TT funcionando.
[ ] tratamento de duplicidade/incerteza.
[ ] timestamp correto.
[ ] contrato correto.
[ ] validacao de mercado aberto.
[ ] decisao futura do Fiscal sobre certificacao.

### 22.6 O que falta para considerar 5S pronto para cockpit

[ ] coletar mais TT em mercado aberto.
[ ] rodar Bastiao em amostra maior.
[ ] gerar Candle 5S em amostra maior.
[ ] comparar visualmente com Profit.
[ ] verificar se buckets nao pulam tempo indevidamente.
[ ] verificar se volume esta coerente.
[ ] verificar se nao ha duplicidade de snapshot.
[ ] criar Replay 5S separado, se aprovado.
[v] exibir no cockpit como diagnostico.
[v] manter bloqueio operacional.

### 22.7 Proibicoes

O 5S nao pode:

[v] virar candle oficial agora.
[v] alimentar Bernardo como memoria certificada.
[v] alimentar Historiador como base validada.
[v] alimentar Motor de Confluencia operacional.
[v] liberar entrada.
[v] liberar stop.
[v] liberar parcial.
[v] liberar alvo.
[v] substituir Replay 1MIN.
[v] substituir CandleBuilder oficial.
[v] ignorar Fiscal.


### 22.8 Marco homologado — 5S-01

[v] Endpoint GET /tt/5s/status criado.
[v] Endpoint isolado do payload operacional.
[v] Ultimo Candle 5S apresentado no cockpit.
[v] Resumo e cobertura apresentados no cockpit.
[v] Status NAO CERTIFICADO apresentado.
[v] Status DIAGNOSTICO APENAS apresentado.
[v] Status NAO OPERACIONAL apresentado.
[v] Amostra insuficiente declarada explicitamente.
[v] Validacao tecnica: 19 testes aprovados.
[v] Validacao visual concluida.
[v] Commit oficial: fce102d.

Escopo atual:

- WIN apenas.
- WDO adiado ate a conclusao do eixo atual e realizacao de coleta propria.

Pendencias mantidas:

[ ] coletar amostra maior durante mercado aberto.
[ ] validar continuidade temporal.
[ ] validar volume por bucket.
[ ] comparar visualmente com o Profit.
[ ] validar varios periodos do pregao.

## Status da secao 5S

5S-01 HOMOLOGADO PARA STATUS DIAGNOSTICO NO COCKPIT. CONTINUIDADE E FIDELIDADE AINDA PENDENTES.

So marcar [v] depois de evidencia real no TRIN_ROOT atual.
