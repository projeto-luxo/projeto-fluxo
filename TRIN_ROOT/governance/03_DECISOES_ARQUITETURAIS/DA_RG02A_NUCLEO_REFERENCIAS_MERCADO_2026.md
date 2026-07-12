# DECISÃO ARQUITETURAL RG-02A — NÚCLEO DE REFERÊNCIAS DE MERCADO

**Data:** 2026-07-12
**Status:** APROVADA
**Projeto:** TRIN

## Contexto

O contrato inicial do Motor de Regiões mistura natureza da referência com interpretação operacional.

Uma referência de MILHAR ou VWAP pode resultar em parada, reversão, continuação, defesa ou nenhum efeito.

## Decisão

Criar um núcleo determinístico que responda primeiro:

```text
ONDE existe uma referência?
```

A interpretação futura responderá:

```text
O QUE essa referência pode representar?
```

## Separação obrigatória

```text
origem_tipo
≠
funcao_provavel
```

### origem_tipo

- MILHAR;
- VWAP_OFICIAL;
- ABERTURA_SESSAO;
- MAXIMA_SESSAO;
- MINIMA_SESSAO;
- FRACTAL;
- OUTRA_FONTE_HOMOLOGADA.

### funcao_provavel

- INDETERMINADA;
- EQUILIBRIO;
- PARADA;
- REVERSAO;
- CONTINUACAO;
- DEFESA.

O RG-02A produzirá inicialmente:

```text
funcao_provavel = INDETERMINADA
status_funcao = NAO_AVALIADA
```

## Fluxo

```text
Fornecedores qualificados
→ Núcleo de Referências
→ Agregador/Classificador futuro — RG-02B
→ Motor de Confluência
→ Planejador Operacional
→ Gestão de Risco
→ Cockpit
→ Operador
```

O RG-02B permanece previsto, mas não implementado. Sua introdução dependerá de auditoria, contrato próprio, regras de agrupamento, preservação das referências de origem e testes sintéticos específicos.

## Escopo da primeira implementação

A primeira implementação deve começar por:

1. MILHAR;
2. VWAP_OFICIAL.

Abertura, máxima e mínima da sessão somente entram depois que os campos originais forem preservados separadamente do candle operacional sintético.

## Princípio de identidade e sobreposição

A identidade determinística da referência deve ser separada do evento de criação ou atualização.

A composição definitiva de `chave_referencia` será homologada antes da implementação. Ela deverá considerar, no mínimo:

- ativo;
- contrato;
- sessão ou data de referência;
- `origem_tipo`;
- fornecedor;
- `campo_origem`;
- `timeframe_origem`;
- valor ou faixa normalizada;
- versão da regra.

Não é necessário definir algoritmo ou hash nesta etapa.

`timestamp_processamento` e `id_evento` não poderão participar da identidade determinística da referência.

Na RG-02A, `fornecedor` e `campo_origem` representam a origem direta. O campo `origens` permanece reservado e vazio nesta etapa.

No RG-02B futuro, `origens` poderá conter a coleção estruturada das referências preservadas que formarem uma região composta.

Uma referência não apaga nem altera silenciosamente outra referência sobreposta. Cada origem preserva identidade e proveniência próprias.

## Proibições

O RG-02A não pode:

- gerar entrada;
- gerar stop;
- gerar parcial;
- gerar alvo;
- classificar sozinho como reversão;
- classificar sozinho como continuação;
- classificar sozinho como defesa;
- substituir Confluência;
- substituir Fiscal;
- substituir Gestão de Risco;
- usar bandas VWAP não homologadas;
- consumir fractal sem contrato de integração;
- alterar dados de origem.
