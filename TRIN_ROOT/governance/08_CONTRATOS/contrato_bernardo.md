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
