# PARECER RG-02 — DESENHO DO MOTOR DE REGIÕES

**Projeto:** TRIN
**Data:** 2026-07-12
**Status:** CONCLUÍDO / DECISÃO APROVADA

## Conclusão

O TRIN ainda não possui um Motor de Regiões operacional homologado.

Existem fornecedores parciais e referências disponíveis, mas o contrato RG-01 mistura:

- origem da região;
- função operacional provável.

Exemplos de origem:

- MILHAR;
- VWAP;
- ABERTURA;
- MÁXIMA;
- MÍNIMA;
- FRACTAL.

Exemplos de função provável:

- INDETERMINADA;
- EQUILÍBRIO;
- PARADA;
- REVERSÃO;
- CONTINUAÇÃO;
- DEFESA.

A primeira versão não deve prever comportamento. Deve localizar e registrar referências determinísticas e rastreáveis.

A identidade permanente da referência deve ser separada do evento de criação ou atualização. Fornecedor, campo de origem e proveniência devem permanecer explícitos.

O RG-02B — Agregador/Classificador de Regiões permanece previsto como etapa futura para reunir referências próximas sem apagar suas identidades ou origens. Sua implementação dependerá de auditoria, contrato e testes próprios.

## Fornecedores avaliados

| Referência | Estado |
|---|---|
| Milhar | DISPONÍVEL POR REGRA DETERMINÍSTICA |
| VWAP oficial | DISPONÍVEL COM PROVENIÊNCIA |
| Abertura da sessão | DADO EXISTE, PRESERVAÇÃO CANÔNICA PENDENTE |
| Máxima da sessão | DADO EXISTE, PRESERVAÇÃO CANÔNICA PENDENTE |
| Mínima da sessão | DADO EXISTE, PRESERVAÇÃO CANÔNICA PENDENTE |
| Fractais | PATRIMÔNIO EXISTENTE, INTEGRAÇÃO AO VIVO PENDENTE |
| Topo e fundo | SEM FORNECEDOR HOMOLOGADO |
| Reversão simples do CandleEngine | NÃO EQUIVALE A REGIÃO ESTRUTURAL |

## Decisão recomendada

Criar o RG-02A — Núcleo de Referências de Mercado.

Primeira responsabilidade:

- localizar referências;
- declarar origem;
- declarar fornecedor e campo de origem;
- declarar qualidade;
- declarar validade;
- declarar estado;
- preservar identidade e proveniência quando houver sobreposição;
- tratar `fornecedor` e `campo_origem` como origem direta na RG-02A;
- reservar `origens` para a coleção estruturada de referências preservadas no RG-02B futuro;
- nunca gerar entrada;
- nunca classificar automaticamente como reversão, continuação ou defesa.

## Ordem de implementação recomendada

1. MILHAR.
2. VWAP_OFICIAL.
3. ABERTURA_SESSAO.
4. MAXIMA_SESSAO.
5. MINIMA_SESSAO.
6. Integrações futuras com fractais e outras fontes homologadas.

## Estado operacional

```text
USO OPERACIONAL: BLOQUEADO
CALIBRAGEM: NÃO INICIADA
AUTORIZAÇÃO DE ENTRADA: PROIBIDA
```
