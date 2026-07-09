# CONTRATO OFICIAL — BASTIAO TT PENEIRADOR

## Status

PLANEJADO / NECESSARIO / NAO IMPLEMENTADO

## Confluencia documental

Este contrato complementa:

- governance/08_CONTRATOS/contrato_bastião.md
- governance/02_AUDITORIAS/AUDITORIA_TT_RTD_CAPTURA_EXPERIMENTAL.md
- governance/02_AUDITORIAS/AUDITORIA_PRE_PATCH_PAINEL_TT_RAW_DIAGNOSTICO.md
- governance/06_CHECKPOINTS/CHECKPOINT_CANDLEBUILDER_PAINEL_2026_07_07.md

Este contrato nao altera:

- contrato_ze.md
- contrato_fiscal.md
- contrato_bernardo.md
- contrato_historiador.md
- contrato_motor_confluencia.md
- ADENDO_BASTIAO_CONTRATO_ATIVO.md

Este contrato nao substitui o contrato original do Bastiao.

Este contrato cria uma responsabilidade especifica e derivada para o submodulo:

BASTIAO_TT_PENEIRADOR

Regra vigente:

TT RAW continua sendo diagnostico apenas, nao certificado e nao oficial para candle, ate passar por peneiramento, auditoria especifica e futura certificacao.

---

## Justificativa

A captura Times & Trades RTD via Excel demonstrou capacidade de registrar dados brutos de negocios em tempo real.

Entretanto, a propria auditoria do projeto ja registrou que o TT RAW pode conter duplicidades, repeticoes observacionais, linhas casca, incertezas e eventos que nao podem ser usados diretamente como candle oficial.

Por isso, o TT RAW nao pode alimentar diretamente:

- CandleBuilder
- Ze do Eucrazio
- Motor de Confluencia
- Replay TT
- decisao operacional

antes de passar por peneiramento tecnico e rastreavel.

---

## Responsabilidade unica

Ler arquivos TT RAW e gerar uma camada derivada, classificada, rastreavel e nao certificada de TT peneirado.

O BASTIAO_TT_PENEIRADOR classifica a filmagem bruta.

Ele nao certifica.

Ele nao reconstrói candle.

Ele nao altera o RAW.

---

## Entrada

Arquivos TT RAW gerados pelo Gravador TT Bruto, contendo preferencialmente:

- data_pregao
- timestamp_captura_pc
- contrato
- row_excel
- hora_tt
- compradora
- preco
- quantidade
- vendedora
- agressor
- agente_agressor
- ocorrencia_snapshot
- hash_evento
- origem
- status_certificacao

Status esperado da entrada:

TT_RAW_ORGANIZADO_NAO_PENEIRADO

---

## Saida

Arquivos derivados em area propria de processamento TT, com status:

TT_PENEIRADO_NAO_CERTIFICADO

Saidas esperadas:

- arquivo TT peneirado
- arquivo de rejeitados/lixo
- arquivo de incertezas
- resumo por contrato/data
- relatorio de processamento
- manifesto com contagens e hashes

---

## Classificacoes obrigatorias

Cada linha processada deve receber classificacao explicita, podendo incluir:

- NEGOCIO_VALIDO_PROVAVEL
- LINHA_CASCA_EXCEL
- TIMESTAMP_INVALIDO
- PRECO_INVALIDO
- QUANTIDADE_INVALIDA
- DUPLICADO_PROVAVEL
- REPETICAO_REAL_POSSIVEL
- EVENTO_LEILAO
- EVENTO_PREGAO
- INCERTEZA_SEQUENCIAL
- FONTE_INSUFICIENTE

---

## Garantias

O BASTIAO_TT_PENEIRADOR deve garantir:

- nao apagar o TT RAW
- nao alterar arquivo bruto original
- manter rastreabilidade entre saida peneirada e linha bruta
- preservar incertezas
- separar leilao de pregao quando possivel
- nao inventar sequencia inexistente
- nao remover repeticao real apenas porque parece duplicada

---

## O que este modulo nunca deve fazer

- apagar duplicados do RAW original
- declarar dado homologado
- declarar candle oficial
- alimentar entrada operacional diretamente
- reconstruir candle
- gerar fractais
- substituir o Fiscal Temporal
- substituir o Ze do Eucrazio
- substituir o Bernardo
- substituir o Gravador TT Bruto
- misturar leilao e pregao sem etiqueta
- transformar incerteza em certeza

---

## Relacao com Gravador TT Bruto

O Gravador TT Bruto filma.

O BASTIAO_TT_PENEIRADOR peneira.

Filtro pesado, deduplicacao, classificacao de lixo e julgamento de validade pertencem ao BASTIAO_TT_PENEIRADOR, nao ao gravador.

---

## Relacao com Ze do Eucrazio

O Ze do Eucrazio nao deve consumir TT RAW diretamente.

Qualquer reconstrucao futura de candle por negocio deve usar somente camada TT peneirada, rastreavel e posteriormente auditada.

Fluxo futuro:

TT_RAW
-> BASTIAO_TT_PENEIRADOR
-> TT_PENEIRADO_NAO_CERTIFICADO
-> FISCAL_TT / auditoria futura
-> ZE_TT_RECONSTRUTOR

---

## Relacao com Fiscal Temporal

O BASTIAO_TT_PENEIRADOR classifica.

O Fiscal certifica.

O BASTIAO_TT_PENEIRADOR nao emite certificacao definitiva.

---

## Relacao com Painel

O painel pode exibir resumo diagnostico do TT peneirado, desde que declare claramente:

- DIAGNOSTICO_APENAS
- NAO_CERTIFICADO
- NAO_E_CANDLE_OFICIAL

---

## Status operacional

Uso operacional: DIAGNOSTICO_APENAS

Candle oficial: false

Alimenta CandleBuilder: false

Alimenta Motor de Confluencia: false

Alimenta Replay TT: somente apos auditoria especifica

---

## Auditoria obrigatoria antes da implementacao

Antes de codar o BASTIAO_TT_PENEIRADOR, deve existir auditoria pre-patch contendo:

- arquivos TT RAW de entrada
- volume de linhas
- exemplos de linhas validas
- exemplos de linhas casca
- criterio de duplicidade provavel
- criterio de repeticao real possivel
- criterio de evento leilao
- criterio de evento pregao
- formato oficial de saida
- riscos de perda de negocio real
- riscos de manutencao de duplicidade falsa

---

## Principio final

O gravador filma.

O Bastiao peneira.

O Fiscal certifica.

O Ze reconstrói.

O operador decide.

Nenhum modulo deve fazer o trabalho do outro.
