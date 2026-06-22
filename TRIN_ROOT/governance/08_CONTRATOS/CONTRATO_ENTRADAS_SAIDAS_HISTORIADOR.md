# CONTRATO — ENTRADAS E SAIDAS DO HISTORIADOR TRIN

## Status
PROPOSTA ARQUITETURAL

## Vinculo
Este contrato complementa:

- governance/08_CONTRATOS/contrato_historiador.md
- governance/02_AUDITORIAS/AUDITORIA_ARQUITETURAL_PRELIMINAR_HISTORIADOR.md

Nao substitui o contrato principal do Historiador.

## Missao
Definir quais entradas o Historiador pode consumir e quais saidas ele pode produzir, evitando consumo indevido de CSV bruto e evitando que conhecimento inicial seja tratado como decisao operacional.

## Responsabilidade do Historiador
Transformar memoria validada e dados certificados em conhecimento historico organizado.

O Historiador nao corrige base, nao gera fractais, nao certifica tempo, nao produz ordem operacional e nao substitui o Motor de Confluencia.

---

# 1. ENTRADAS PERMITIDAS

## 1.1 indice_geral.csv

Caminho atual:

TRIN_HISTORICO/00_INDICES/indice_geral.csv

Classificacao:
ENTRADA PERMITIDA COM RESSALVAS

Condicao:
O indice_geral.csv so pode ser usado pelo Historiador se for reconhecido como saida oficial do Bernardo.

Interpretacao arquitetural:
indice_geral.csv nao deve ser tratado como CSV bruto livre.
Ele deve ser tratado como produto indexado da memoria organizada pelo Bernardo.

## 1.2 indices auxiliares

Caminhos atuais:

TRIN_HISTORICO/00_INDICES/indice_win.csv
TRIN_HISTORICO/00_INDICES/indice_wdo.csv

Classificacao:
ENTRADA PLANEJADA

Condicao:
So devem ser usados se forem formalizados como saidas oficiais do Bernardo.

## 1.3 Certificacoes do Fiscal Temporal

Caminho atual:

TRIN_HISTORICO/00_CERTIFICACOES/

Entradas relevantes futuras:

- certificado_temporal.csv
- resumo_por_arquivo.csv
- resumo_por_motivo.csv
- laudo_temporal.txt
- registro_protocolos_fiscal.csv

Classificacao:
DEPENDENCIA OBRIGATORIA PARA HOMOLOGACAO

Regra:
O Historiador pode gerar conhecimento inicial em modo controlado, mas nao deve ser homologado enquanto a base usada nao tiver passado pelo Fiscal Temporal.

## 1.4 Calendario B3

Caminhos possiveis:

TRIN_HISTORICO/00_CONFIG/calendario_b3_2026.csv
config/calendarios/calendario_contratos_b3.csv

Classificacao:
ENTRADA DE CONTEXTO, NAO DE DECISAO

Regra:
O Historiador pode usar calendario para contexto historico, rolagem, vencimento, feriado e sessao.
Nao pode decidir contrato ativo.
Contrato ativo pertence ao ContratoAtivoResolver e ao Bastiao.

---

# 2. ENTRADAS PROIBIDAS

O Historiador nao pode consumir diretamente:

- CSV historico bruto sem passar por Bernardo;
- arquivos 1_MIN originais como fonte livre de mineracao;
- fractais nao certificados como se fossem verdade;
- saidas temporais reprovadas pelo Fiscal;
- dados de RTD/Excel ao vivo;
- dados do painel operacional em tempo real.

Qualquer leitura detalhada futura deve passar por:

Bernardo/API do Bernardo
ou
memoria certificada
ou
pacote oficialmente liberado pela governanca.

---

# 3. SAIDAS OFICIAIS DO HISTORIADOR

Pasta oficial:

TRIN_HISTORICO/00_CONHECIMENTO/

Saidas atuais permitidas em modo inicial:

- estatistica_biblioteca.csv
- cobertura_temporal.csv
- distribuicao_fractais.csv
- estatistica_delta.csv
- estatistica_volume.csv
- catalogo_padroes_historiador.csv
- contexto_historiador.csv
- relatorio_historiador.txt

## 3.1 estatistica_biblioteca.csv
Resumo estatistico por ativo/fractal.

Nao e certificacao.
Nao e sinal operacional.

## 3.2 cobertura_temporal.csv
Mapa de cobertura temporal por ativo/fractal/arquivo.

Nao substitui o Fiscal Temporal.

## 3.3 distribuicao_fractais.csv
Distribuicao de arquivos e linhas por fractal.

Nao valida qualidade dos fractais.

## 3.4 estatistica_delta.csv
Resumo inicial de delta quando delta_medio existir no indice oficial.

Nao deve buscar CSV bruto diretamente em versoes futuras sem autorizacao arquitetural.

## 3.5 estatistica_volume.csv
Resumo inicial de volume quando volume_medio existir no indice oficial.

Nao deve buscar CSV bruto diretamente em versoes futuras sem autorizacao arquitetural.

## 3.6 catalogo_padroes_historiador.csv
Catalogo inicial de padroes preparados para mineracao.

PADRAO_CATALOGADO nao significa padrao comprovado.

## 3.7 contexto_historiador.csv
Mapa inicial de contexto por horario/evento.

Contexto catalogado nao significa conhecimento historico certificado.

## 3.8 relatorio_historiador.txt
Relatorio humano da execucao do Historiador.

Nao substitui manifesto nem Auditoria HARD.

---

# 4. STATUS DE CONFIANCA DAS SAIDAS

Toda saida futura do Historiador deve conter ou ser acompanhada por status de confianca.

Status recomendados:

- INICIAL
- GERADO_POR_INDICE_BERNARDO
- AGUARDANDO_FISCAL
- CERTIFICADO_POR_FISCAL
- APROVADO_COM_RESSALVAS
- REPROVADO
- ARQUIVADO

Enquanto nao houver certificacao completa, as saidas devem ser tratadas como:

CONHECIMENTO_INICIAL_COM_RESSALVAS

---

# 5. HISTORIADOR ADAPTER

Arquivo:

intelligence/historiador_adapter.py

Classificacao:
ADAPTER FRACO / INFORMATIVO

Responsabilidade:
Ler conhecimento ja produzido em 00_CONHECIMENTO e entregar pacote padronizado ao Motor de Confluencia.

Proibicoes:
- nao minerar dados;
- nao certificar dados;
- nao gerar ordem;
- nao corrigir arquivos;
- nao substituir o Historiador gerador;
- nao substituir o Motor de Confluencia.

## Regra de peso
score_historico 0.25 ou 0.35 deve ser tratado como evidencia fraca.

Interpretacao:

SEM_CONHECIMENTO -> peso zero
PADRAO_CATALOGADO -> evidencia conceitual fraca
COBERTURA_ENCONTRADA -> evidencia estrutural fraca
PADRAO_MINERADO -> somente no futuro, apos Fiscal, Bernardo e Auditoria HARD

---

# 6. MANIFESTO FUTURO OBRIGATORIO

Toda execucao oficial futura do Historiador deve gerar manifesto contendo:

- data_execucao
- versao_historiador
- arquivos de entrada usados
- origem do indice
- status do Fiscal Temporal
- arquivos de saida gerados
- quantidade de registros gerados
- ressalvas
- hash dos arquivos principais
- status final da execucao

Arquivo futuro recomendado:

TRIN_HISTORICO/00_CONHECIMENTO/manifesto_historiador.json

---

# 7. PROIBICOES GERAIS

O Historiador nao deve:

- corrigir base historica;
- gerar fractais;
- certificar integridade temporal;
- produzir ordem operacional;
- decidir entrada, stop, parcial ou alvo;
- consumir CSV bruto livremente;
- ignorar Bernardo;
- ignorar Fiscal Temporal;
- transformar padrao catalogado em verdade historica;
- entregar score forte ao Motor antes de homologacao.

---

# 8. CLASSIFICACAO ATUAL

Historiador:
PLANEJADO / EM AUDITORIA ARQUITETURAL

Scripts atuais:
APROVADOS COMO ESQUELETO INICIAL

Execucao oficial:
REPROVADA ATE NOVA AUDITORIA HARD

Adapter:
APROVADO COMO EVIDENCIA FRACA / INFORMATIVA

---

# 9. PROXIMO PASSO RECOMENDADO

Antes de qualquer patch de codigo:

1. Formalizar indice_geral.csv como saida oficial do Bernardo.
2. Definir schema minimo do indice_geral.csv.
3. Definir schema minimo das saidas em 00_CONHECIMENTO.
4. Definir manifesto_historiador.json.
5. Definir como o Motor de Confluencia deve ponderar o HistoriadorAdapter.
6. Executar Auditoria HARD antes de homologacao.

## Parecer final
O Historiador pode continuar existindo como esqueleto inicial, mas nao deve ser tratado como modulo homologado.

A evolucao correta e contratual antes de funcional.
