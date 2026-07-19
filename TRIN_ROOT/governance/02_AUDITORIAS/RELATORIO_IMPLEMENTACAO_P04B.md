# RELATÓRIO DE IMPLEMENTAÇÃO — P04B CONSOLIDADO ATÉ V1.14

## Alteração mínima

1. cria `backend/confluencia_replay_backend.py`;
2. adiciona um finalizador P04B ao backend oficial;
3. encaminha os dois retornos de `gerar_payload()` pelo mesmo finalizador;
4. cria contrato, schema e quatro arquivos de teste P04B;
5. não altera P04A, Historiador, frontend, Cockpit ou Planejador.

## Proteções

- patch byte a byte com reversão exata;
- LF/CRLF e newline final preservados;
- blob Git e `git show` conferidos no Windows;
- sandbox construída do commit-base antes da aplicação real;
- P04A e regressão obtidos por `git ls-tree`, sem busca recursiva aberta;
- working tree sujo não alvo comparado por status, tamanho e SHA-256;
- rollback automático;
- reaplicação idempotente;
- nenhum commit ou push.

## Portão local obrigatório

O candidato só pode avançar quando o computador oficial reproduzir:

```text
P04B = suíte aprovada
P04A = 89 passed
regressão = seleção dinâmica: nodeids coletados = executados = aprovados
/data = contrato presente
/ws = contrato presente
rollback = aprovado
reaplicação = aprovada
```

A execução técnica gera `P04B_EVIDENCIAS_FINAL.zip`; somente a auditoria dessas
evidências permite homologação.


## Correção funcional V1.14 — timeout e gate Fiscal

A auditoria final da execução V1.13 aprovou embalagem, aplicação, idempotência,
P04B, P04A e regressão, mas manteve dois bloqueadores funcionais:

1. o trabalhador em timeout recebia o repositório oficial e a conferência
   posterior não era garantida em todos os caminhos;
2. booleanos favoráveis podiam liberar um `status` Fiscal contraditório.

A correção V1.14 é restrita ao adaptador e às provas permanentes:

- avaliação sobre cópia física temporária do JSONL;
- conferência do arquivo oficial em `finally`;
- limpeza da cópia pelo próprio trabalhador;
- apenas um trabalhador ativo, sem fila;
- coerência entre fonte, status e booleanos do Fiscal;
- autoridade de estados liberados consumida diretamente de `FiscalAdapter.STATUS_LIBERADOS`;
- remoção de qualquer lista local de status no P04B;
- cobertura explícita do alias `RESSALVA`;
- teste de mutação tardia após timeout;
- testes de status reprovado/desconhecido com booleanos favoráveis;
- preservação integral e dinâmica do vocabulário vigente do fornecedor Fiscal.

## Correção arquitetural R5 — compatibilidade integral

A decisão da Guia 1 de 19/07/2026 determinou que o P04B não seja fonte de verdade do contrato Fiscal. A revisão R5 remove a lista local parcial e consulta diretamente `FiscalAdapter.STATUS_LIBERADOS`. A migração canônica do contrato Fiscal permanece fora desta frente.

Não há alteração de P04A, Historiador, Planejador, frontend, peso, impacto ou
schema público do backend. O candidato permanece `AGUARDANDO_AUDITORIA`.
