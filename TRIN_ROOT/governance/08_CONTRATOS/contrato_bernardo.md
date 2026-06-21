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
