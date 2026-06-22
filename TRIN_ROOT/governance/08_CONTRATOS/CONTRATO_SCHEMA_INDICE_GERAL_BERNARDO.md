# CONTRATO — SCHEMA DO INDICE GERAL DO BERNARDO

## Status
PROPOSTA ARQUITETURAL

## Arquivo alvo
TRIN_HISTORICO/00_INDICES/indice_geral.csv

## Vinculo
Este contrato complementa:

- governance/08_CONTRATOS/contrato_bernardo.md
- governance/08_CONTRATOS/CONTRATO_INDICE_GERAL_BERNARDO.md
- governance/08_CONTRATOS/CONTRATO_ENTRADAS_SAIDAS_HISTORIADOR.md

## Missao
Definir o schema minimo do indice_geral.csv para que ele seja tratado como saida oficial indexada do Bernardo e possa alimentar o Historiador sem ser confundido com CSV bruto livre.

## Regra central
indice_geral.csv e uma tabela de metadados da memoria historica.

Ele nao e candle.
Ele nao e fractal.
Ele nao e certificacao temporal.
Ele nao e sinal operacional.

Ele apenas descreve arquivos conhecidos, organizados e indexados pelo Bernardo.

---

# 1. FORMATO OFICIAL

## Separador
;

## Encoding
utf-8-sig

## Header
Obrigatorio.

## Uma linha representa
Um arquivo historico indexado pelo Bernardo.

---

# 2. COLUNAS OBRIGATORIAS

## ativo
Tipo: texto

Exemplos:
WIN
WDO

Regra:
Identifica o ativo principal do arquivo.

Obrigatorio:
SIM

## fractal
Tipo: texto

Exemplos:
1_MIN
2_MIN
5_MIN
10_MIN
15_MIN
30_MIN
60_MIN
DIARIO
SEMANAL
MENSAL

Regra:
Identifica o fractal ou periodicidade do arquivo.

Obrigatorio:
SIM

## arquivo
Tipo: texto

Regra:
Nome do arquivo indexado.

Obrigatorio:
SIM

## caminho
Tipo: texto

Regra:
Caminho relativo ou absoluto do arquivo dentro da biblioteca historica.

Obrigatorio:
SIM

## linhas
Tipo: inteiro

Regra:
Quantidade de registros existentes no arquivo.

Obrigatorio:
SIM

Valor padrao permitido:
0, quando o arquivo existir mas ainda nao tiver leitura valida.

## data_inicio
Tipo: data ou texto padronizado

Formato recomendado:
dd/mm/aaaa
ou
dd/mm/aaaa hh:mm:ss

Regra:
Primeira data/hora reconhecida no arquivo.

Obrigatorio:
SIM

Valor permitido quando desconhecido:
N/D

## data_fim
Tipo: data ou texto padronizado

Formato recomendado:
dd/mm/aaaa
ou
dd/mm/aaaa hh:mm:ss

Regra:
Ultima data/hora reconhecida no arquivo.

Obrigatorio:
SIM

Valor permitido quando desconhecido:
N/D

## status
Tipo: texto controlado

Valores permitidos:
OK
ALERTA
ERRO
PENDENTE_FISCAL
CERTIFICADO
APROVADO_COM_RESSALVAS
REPROVADO

Regra:
Status de organizacao/indexacao do arquivo segundo Bernardo e/ou integracao futura com Fiscal.

Obrigatorio:
SIM

## origem
Tipo: texto

Valores recomendados:
BERNARDO
BERNARDO_ARQUIVISTA
BERNARDO_BIBLIOTECARIO
IMPORTACAO_MANUAL
LEGADO
DESCONHECIDA

Regra:
Identifica quem ou qual processo registrou o item no indice.

Obrigatorio:
SIM

---

# 3. COLUNAS COMPLEMENTARES RECOMENDADAS

## tamanho_mb
Tipo: decimal

Regra:
Tamanho do arquivo em megabytes.

## confiabilidade
Tipo: decimal ou inteiro

Escala recomendada:
0 a 100

Regra:
Grau de confianca de organizacao atribuido pelo Bernardo.

Nao substitui certificacao do Fiscal Temporal.

## delta_medio
Tipo: decimal

Regra:
Media de delta quando disponivel no indice.

Se nao existir:
N/D

## volume_medio
Tipo: decimal

Regra:
Media de volume quando disponivel no indice.

Se nao existir:
N/D

## data_indexacao
Tipo: data/hora

Formato recomendado:
dd/mm/aaaa hh:mm:ss

Regra:
Momento em que Bernardo registrou ou atualizou o item.

## hash
Tipo: texto

Regra:
Hash do arquivo indexado, quando disponivel.

## observacao
Tipo: texto

Regra:
Campo livre para ressalvas de Bernardo, Fiscal ou governanca.

---

# 4. COLUNAS FUTURAS PLANEJADAS

## fiscal_status
Tipo: texto

Valores recomendados:
NAO_VERIFICADO
CERTIFICADO
APROVADO_COM_RESSALVAS
REPROVADO
REPROVADO_COM_PENDENCIAS

Regra:
Status recebido do Fiscal Temporal.

## fiscal_data
Tipo: data/hora

Regra:
Data da ultima certificacao fiscal associada ao arquivo.

## fiscal_id
Tipo: texto

Regra:
ID, lote ou protocolo da certificacao fiscal relacionada.

## manifesto_ze
Tipo: texto

Regra:
Referencia ao manifesto do Ze do Eucrazio, quando o arquivo for fractal derivado.

---

# 5. VALORES NULOS E DESCONHECIDOS

Valores vazios devem ser evitados.

Quando a informacao nao existir, usar:

N/D

Quando a informacao estiver pendente:

PENDENTE

Quando houver erro:

ERRO

---

# 6. REGRAS DE VALIDACAO

O indice_geral.csv deve ser considerado valido quando:

1. possuir todas as colunas obrigatorias;
2. usar separador ponto e virgula;
3. usar encoding utf-8-sig;
4. possuir header;
5. cada linha representar um arquivo;
6. ativo nao estiver vazio;
7. fractal nao estiver vazio;
8. arquivo nao estiver vazio;
9. caminho nao estiver vazio;
10. status pertencer aos valores permitidos;
11. origem estiver preenchida.

---

# 7. RELACAO COM BERNARDO

O indice_geral.csv e responsabilidade do Bernardo.

Bernardo deve garantir:

- organizacao dos metadados;
- rastreabilidade dos arquivos;
- consistencia minima do indice;
- nao exposicao de CSV bruto como memoria livre;
- manutencao futura do manifesto do indice.

---

# 8. RELACAO COM HISTORIADOR

O Historiador pode consumir indice_geral.csv como entrada inicial com ressalvas.

O Historiador nao deve assumir que:

- status OK significa certificacao temporal;
- indice completo significa conhecimento historico;
- delta_medio ou volume_medio sao suficientes para padrao operacional;
- indice substitui memoria certificada;
- indice substitui Fiscal Temporal.

---

# 9. RELACAO COM FISCAL TEMPORAL

O Fiscal Temporal certifica integridade temporal e estrutural.

O indice_geral.csv pode registrar o resultado do Fiscal, mas nao substitui o Fiscal.

Bernardo indexa.
Fiscal certifica.
Historiador interpreta.

---

# 10. RELACAO COM MOTOR DE CONFLUENCIA

O Motor de Confluencia nao deve consumir indice_geral.csv diretamente como evidencia forte.

Se algum conhecimento derivado do indice chegar ao Motor, deve chegar via:

Historiador
ou
HistoriadorAdapter

e com peso fraco enquanto nao houver homologacao.

---

# 11. PROIBICOES

indice_geral.csv nao pode ser usado para:

- gerar ordem operacional;
- decidir entrada;
- decidir stop;
- decidir parcial;
- decidir alvo;
- substituir Fiscal Temporal;
- substituir Bernardo;
- substituir Ze do Eucrazio;
- alimentar aprendizagem sem contrato especifico;
- provar padrao historico sem mineracao e auditoria.

---

# 12. STATUS DE CONFIANCA ATUAL

Enquanto nao houver manifesto oficial do indice, o status do indice_geral.csv deve ser:

MEMORIA_INDEXADA_COM_RESSALVAS

---

# 13. MANIFESTO FUTURO

A geracao oficial do indice deve produzir:

TRIN_HISTORICO/00_INDICES/manifesto_indice_geral_bernardo.json

Campos recomendados:

- versao_bernardo
- data_execucao
- total_arquivos_indexados
- total_linhas_referenciadas
- total_por_ativo
- total_por_fractal
- erros
- alertas
- arquivos_ignorados
- hash_indice_geral
- status_final

---

# 14. PARECER FINAL

Este schema autoriza o indice_geral.csv como saida oficial indexada do Bernardo, desde que respeite as colunas obrigatorias e regras deste contrato.

Essa autorizacao nao homologa o Historiador.

Essa autorizacao nao substitui o Fiscal Temporal.

Essa autorizacao apenas permite que o Historiador use o indice como entrada inicial controlada, sem violar a doutrina contra consumo livre de CSV bruto.
