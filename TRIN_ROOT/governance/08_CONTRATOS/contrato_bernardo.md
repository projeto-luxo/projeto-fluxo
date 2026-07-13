# CONTRATO OFICIAL — BERNARDO BIBLIOTECÁRIO

## Status

Congelado arquiteturalmente como camada oficial de persistência cognitiva.

## Responsabilidade única

Organizar, auditar, indexar, consultar e disponibilizar a memória validada do TRIN.

## Entrada

Biblioteca Histórica, artefatos certificados, índices, metadados, pacotes de módulos e consultas pela API do Bernardo.

## Saída

Informação organizada, índices, grafos, pacotes para Historiador, Zé e Motor de Confluência, relatórios de memória e respostas estruturadas.

## Garantias

- Não altera dado bruto original.
- Mantém rastreabilidade.
- Centraliza acesso à memória.
- Evita que IAs consumam CSV diretamente.

## O que este módulo nunca deve fazer

- Gerar fractais.
- Certificar séries temporais no lugar do Fiscal.
- Tomar decisão operacional.
- Produzir sinais de compra/venda.

## Consumidores

Historiador, Motor de Confluência, IA TRIN, operador, módulos de consulta.

## Fornecedores

Biblioteca Histórica, Fiscal Temporal, Zé do Eucrázio, Gravador, curadorias e pacotes internos.

## Auditoria obrigatória

Todo uso estrutural deste contrato deve passar por checklist de teste e Auditoria HARD.

---

## Atualizacao de governanca — 2026-06-21

### Classificacao atual
CONGELADO ARQUITETURALMENTE

### Observacao
Bernardo permanece como camada oficial de persistencia cognitiva e organizacao da memoria do TRIN.

Consumidores futuros devem acessar memoria por fluxo oficial/API do Bernardo, e nao por leitura direta de CSV bruto.

### Responsabilidade preservada
Bernardo organiza, protege, cataloga e fornece memoria validada.

### O que permanece proibido
- Gerar fractais.
- Certificar tempo no lugar do Fiscal Temporal.
- Produzir sinais operacionais.
- Substituir o Historiador.
- Permitir consumo direto de CSV bruto por inteligencias futuras.

### Ressalvas
- Integracoes futuras devem respeitar DA-001.
- Toda nova leitura de memoria deve passar pela camada oficial Bernardo/API do Bernardo.
- Auditorias futuras devem verificar se nenhum modulo esta burlando Bernardo.

<!-- TRIN:BERNARDO:INTERFACES_CANONICAS_INICIO -->
## Interfaces canônicas confirmadas

### Motor de Confluência

Arquivo interno oficial: `TRIN_HISTORICO/00_INDICES/pacote_motor_confluencia.csv`.

Acesso obrigatório por `intelligence/bernardo_adapter.py`.

O pacote não constitui, sozinho, direção operacional, similaridade histórica ou confiança estatística.

### Consumidores do índice

Consumidores devem usar `BernardoAdapter.consultar_indice(...)` em vez de abrir `indice_geral.csv` diretamente.

### Ordens do Fiscal Temporal

Entrada: `TRIN_HISTORICO/00_CERTIFICACOES/ordens_para_bernardo.csv`.

Resposta: `TRIN_HISTORICO/00_CERTIFICACOES/respostas_bernardo.csv`.

A ponte pode registrar `EM_ANALISE`, mas não pode declarar `CORRIGIDO`, `RECERTIFICAR` ou `ENCERRADO` sem execução e prova correspondentes.
<!-- TRIN:BERNARDO:INTERFACES_CANONICAS_FIM -->

<!-- TRIN:BERNARDO:PACOTE_ZE_RASTREAVEL_INICIO -->
## Rastreabilidade do pacote Bernardo → Zé do Eucrázio

O arquivo `pacote_ze_eucrazio.csv` deve registrar em cada linha:

- `versao_bernardo`;
- `id_execucao_bernardo`;
- `hash_indice_bernardo`;
- `status_autoinspecao_bernardo`;
- `manifesto_rastreabilidade`.

O hash SHA-256 do próprio pacote fica em
`manifesto_pacote_ze_bernardo.json`.

Essa separação é obrigatória porque inserir no próprio CSV o hash do arquivo
inteiro criaria autorreferência circular e impediria uma assinatura estável.

O pacote informa existência, ausência e ação recomendada. Ele não autoriza o
Zé a inventar candles, certificar séries ou declarar correção concluída.
<!-- TRIN:BERNARDO:PACOTE_ZE_RASTREAVEL_FIM -->
