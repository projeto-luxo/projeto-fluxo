# CONTRATO OFICIAL — ZÉ DO EUCRÁZIO

## Status

Zé 4.0 aprovado em teste controlado e homologado para integração com Fiscal Temporal. Não congelado definitivamente.

## Responsabilidade única

Reconstruir o tempo do mercado gerando fractais determinísticos a partir do histórico base.

## Entrada

Histórico 1_MIN, configuração externa de fractais, padrões de CSV, caminhos da Biblioteca Histórica.

## Saída

Fractais derivados, manifesto JSON, logs, relatório de candles parciais e arquivos aguardando certificação.

## Garantias

- Não altera arquivos originais.
- Não atravessa sessões.
- Registra candles completos e parciais.
- Gera hashes e manifesto.
- Usa saída padronizada.

## O que este módulo nunca deve fazer

- Certificar definitivamente.
- Interpretar mercado.
- Produzir score.
- Gerar sinais.
- Atualizar Bernardo diretamente sem etapa de certificação.

## Consumidores

Fiscal Temporal e, após certificação, Bernardo.

## Fornecedores

Histórico 1_MIN, Registro Oficial de Fractais, padrões da governança.

## Auditoria obrigatória

Todo uso estrutural deste contrato deve passar por checklist de teste e Auditoria HARD.
