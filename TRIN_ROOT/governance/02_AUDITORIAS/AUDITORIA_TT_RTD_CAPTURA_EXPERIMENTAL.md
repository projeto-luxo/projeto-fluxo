# AUDITORIA_TT_RTD_CAPTURA_EXPERIMENTAL.md

## Status

AUDITORIA_EXPERIMENTAL
Data: 2026-06-30
Projeto: TRIN
Modulo: Times & Trades RTD / Excel / Captura Python
Tema: Captura experimental de negocios do Times & Trades via RTD

---

## 1. Objetivo

Registrar a descoberta, testes e parecer arquitetural sobre a captura de negocios do Times & Trades do Profit/Nelogica via RTD no Excel.

Esta auditoria nao homologa a fonte como tick a tick oficial.

Esta auditoria nao autoriza uso direto dos dados RAW para formacao de candles oficiais.

---

## 2. Contexto

Durante investigacao para melhorar o modo replay, leitura de fluxo e futura formacao de candles por negocio, foi identificado que a janela Times & Trades do Profit possui a opcao:

Linkar Janela com Excel (RTD)

A exportacao permitiu trazer para o Excel a tabela de negocios do ativo WINQ26, contendo campos como:

- Data/hora do negocio com milissegundos
- Compradora
- Valor
- Quantidade
- Vendedora
- Agressor
- Agente Agressor

Foi confirmado que a janela exportada possui limite pratico de 500 linhas.

---

## 3. Formulas RTD identificadas

Na guia T.T RTD foram observadas formulas do tipo:

- T&T0 / INFO / ATV = ativo
- T&T0 / INFO / TAB = aba da janela
- T&T0 / DAT = data/hora do negocio
- T&T0 / ACP = compradora
- T&T0 / PRE = preco
- T&T0 / QUL = quantidade
- T&T0 / AVD = vendedora
- T&T0 / AGR = agressor
- T&T0 / AGAG = agente agressor

Na guia RTD_PAINEL foram observadas formulas do ativo WINQ26_F_0:

- DAT = data
- HOR = hora
- ULT = ultimo
- ABE = abertura
- MAX = maximo
- MIN = minimo
- VOL = volume
- 67 = VWAP
- 98, 99, 100, 103 = campos relacionados a agressao/saldo

O campo contador acumulado "Negocios" do topo do T.T ainda nao foi identificado por formula RTD confiavel.

---

## 4. Testes realizados

Foram realizados testes com Python lendo a guia T.T RTD via Excel COM.

Resultados relevantes:

### Captura com retry

- Python conseguiu ler o Excel em tempo real
- Python conseguiu acumular mais de 100 mil registros
- Falhas Excel foram tratadas com retry
- Captura experimental mostrou viabilidade tecnica

### Captura por ancora

- Capturador por ancora foi testado
- Funcionou, mas apresentou perdas de ancoragem em mercado acelerado
- Conclusao: modo conservador evita duplicidade, mas pode perder negocios

### Captura RAW

Decidiu-se testar captura bruta:

- Copiar tudo que aparece na janela
- Nao deduplicar na captura
- Nao interpretar
- Nao formar candle
- Deixar a peneira para modulo posterior

Resultado da organizacao RAW:

- Arquivos analisados: 3
- Linhas validas T.T: 3.811.887
- Snapshots: 7.625
- Assinaturas observacionais unicas: 43.968
- Repeticoes observacionais: 3.767.919
- Maior arquivo RAW: tt_rtd_raw_20260630_171259.csv
- Tamanho maior arquivo: 483.679.799 bytes
- Status: TT_RAW_ORGANIZADO_NAO_PENEIRADO

---

## 5. Arquivos gerados

Arquivos de processamento diagnostico:

- TRIN_HISTORICO/00_PROCESSAMENTO_TT/resumo_tt_raw.csv
- TRIN_HISTORICO/00_PROCESSAMENTO_TT/amostra_tt_normalizada.csv
- TRIN_HISTORICO/00_PROCESSAMENTO_TT/painel_tt_raw_status.json
- TRIN_HISTORICO/00_PROCESSAMENTO_TT/diagnostico_tt_raw.txt

Arquivos RAW de captura:

- TRIN_HISTORICO/00_LOGS/tt_rtd_raw/tt_rtd_raw_contextual_20260630_173509.csv
- TRIN_HISTORICO/00_LOGS/tt_rtd_raw/tt_rtd_raw_20260630_171259.csv
- TRIN_HISTORICO/00_LOGS/tt_rtd_raw/tt_rtd_raw_20260630_170253.csv

Observacao: arquivos RAW sao grandes e nao devem ser versionados no Git sem decisao especifica.

---

## 6. Parecer arquitetural

A ponte:

Profit Times & Trades -> Excel RTD -> Python

foi considerada tecnicamente viavel para captura experimental.

Porem, por causa do limite de 500 linhas da janela T.T RTD e ausencia de ID unico oficial do negocio, a fonte ainda nao deve ser tratada como fonte oficial tick a tick homologada.

Classificacao atual:

TT_RTD_EXCEL_CAPTURA_EXPERIMENTAL_APROVADA

Nao homologar ainda como:

TT_RTD_FONTE_OFICIAL_TICK_A_TICK

---

## 7. Decisao provisoria

Enquanto a ProfitDLL / callback de trades nao estiver disponivel, o TRIN seguira provisoriamente com:

Times & Trades RTD
-> Excel
-> Capturador TT RAW
-> Bastiao TT Peneirador
-> CandleBuilder experimental
-> Painel diagnostico
-> Simulador operacional em tempo real

Essa decisao e provisoria, experimental e sujeita a revisao.

---

## 8. Separacao de responsabilidades

### Capturador TT RAW

Pode:

- copiar tudo que aparece na janela T.T
- criar id_raw proprio do TRIN
- registrar snapshot_id
- registrar linha_snapshot
- registrar hash observacional
- salvar RAW bruto

Nao pode:

- certificar
- apagar duplicados
- formar candle oficial
- gerar sinal operacional
- declarar verdade tick a tick

### Bastiao TT Peneirador

Pode:

- classificar duplicado provavel
- classificar novo provavel
- classificar repeticao real possivel
- classificar incerto
- apontar perda de janela
- gerar arquivos peneirados para uso experimental

Nao pode:

- certificar integridade oficial
- corrigir base
- declarar candle oficial

### Fiscal Temporal

Responsavel por:

- auditar integridade
- emitir laudo
- classificar ressalvas
- aprovar ou negar uso oficial

### CandleBuilder

Somente deve usar dados liberados pela etapa de peneira/validacao para construcao experimental.

---

## 9. Riscos identificados

- Janela T.T limitada a 500 linhas
- Mercado acelerado pode girar a janela antes da leitura Python
- Ausencia de ID unico oficial do negocio
- Duplicidade proposital no RAW
- Repeticoes reais podem parecer duplicados
- Duplicados podem parecer repeticoes reais
- Arquivos RAW crescem rapidamente
- Excel pode ficar pesado em longas capturas

---

## 10. Proxima etapa recomendada

1. Nao usar RAW direto no painel operacional.
2. Criar endpoint diagnostico para painel ler painel_tt_raw_status.json.
3. Criar Bastiao TT Peneirador v0.
4. Criar contrato oficial do Capturador TT RAW.
5. Criar contrato oficial do Bastiao TT Peneirador.
6. Investigar futuramente ProfitDLL / TNewTradeCallback.
7. Manter campo "Negocios" acumulado como pendencia investigativa.

---

## 11. Conclusao

A captura T.T RTD foi aprovada como experimento viavel.

A captura RAW mostrou capacidade de gravar grande volume de dados do Times & Trades em tempo real.

A fonte ainda nao esta homologada como base oficial tick a tick.

A arquitetura correta e:

Capturador copia.
Bastiao peneira.
Fiscal certifica.
CandleBuilder constrói.
Painel exibe diagnostico.
