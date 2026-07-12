# CONTRATO OFICIAL — PLANEJADOR OPERACIONAL V1

**Status:** PLANEJADO / NÃO IMPLEMENTADO
**Uso operacional:** BLOQUEADO

## Missão

Transformar uma região elegível e confirmada em um plano operacional possível, sem executar ordens.

## Entradas

- região;
- direção;
- confluência;
- preço atual;
- qualidade das fontes;
- Fiscal;
- contrato ativo;
- parâmetros técnicos de risco;
- validade temporal.

## Saída

```json
{
  "id_plano": "PO-YYYYMMDD-000001",
  "estado": "SEM_OPERACAO|AGUARDAR|POSSIVEL_COMPRA|POSSIVEL_VENDA|MANTER|REDUZIR|SAIR",
  "direcao": "COMPRA|VENDA|NEUTRA",
  "entrada_inferior": null,
  "entrada_superior": null,
  "invalidacao": null,
  "stop": null,
  "parcial": null,
  "alvo": null,
  "autorizacao": "BLOQUEADA|PENDENTE|LIBERADA",
  "motivo_bloqueio": "",
  "versao_regra": "1.0"
}
```

## Segurança

Sem região válida, Fiscal aprovado, contrato correto e fontes saudáveis:

```text
estado = SEM_OPERACAO
autorizacao = BLOQUEADA
entrada = null
stop = null
parcial = null
alvo = null
```

## Proibições

Não executar ordem, não criar região, não certificar dados, não decidir quantidade de contratos, não ignorar Fiscal e não reutilizar valores fixos antigos.
