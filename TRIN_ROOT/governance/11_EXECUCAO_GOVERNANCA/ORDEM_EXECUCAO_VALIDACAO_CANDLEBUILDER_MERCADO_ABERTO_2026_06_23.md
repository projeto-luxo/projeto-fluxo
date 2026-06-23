# ORDEM_EXECUCAO_VALIDACAO_CANDLEBUILDER_MERCADO_ABERTO_2026_06_23.md

## Status

ORDEM_DE_EXECUCAO_PRE_OPERACIONAL
Data prevista: 2026-06-23
Projeto: TRIN
Modulo: CandleBuilderPainel
Condicao: executar somente com mercado aberto

---

## 1. Missao

Executar validacao operacional do CandleBuilderPainel em mercado aberto, seguindo o checklist:

governance/01_CHECKLISTS/CHECKLIST_VALIDACAO_CANDLEBUILDER_MERCADO_ABERTO.md

Esta ordem nao autoriza alteracao de codigo.

---

## 2. Regra principal

Nao corrigir durante o teste.

Se aparecer erro, anomalia, volume estranho, candle travado ou comportamento inesperado:

1. parar;
2. registrar evidencia;
3. nao colar comando novo;
4. nao alterar codigo;
5. gerar laudo ou auditoria propria.

---

## 3. Pre-condicoes

- Git limpo.
- Branch TRIN_CLEAN ativa.
- Profit aberto e conectado.
- Excel RTD recebendo dados.
- Backend do TRIN ativo.
- Frontend do TRIN ativo.
- Mercado aberto.
- Status do painel mantido como OPERACIONAL_NAO_CERTIFICADO.

---

## 4. Validacoes obrigatorias

- Validar 1_MIN.
- Validar 5_MIN.
- Validar 15s.
- Validar 30s.
- Confirmar bloqueio de DIARIO.
- Confirmar bloqueio de SEMANAL.
- Observar volume agregado sem corrigir na hora.

---

## 5. Proibicoes

Nao fazer durante a execucao:

- alterar CandleBuilder;
- alterar backend;
- alterar frontend;
- liberar DIARIO;
- liberar SEMANAL;
- mexer no Fiscal Temporal;
- mexer no Ze do Eucrazio;
- mexer no Bernardo;
- mexer no Historiador;
- promover CandleBuilder para historico oficial;
- usar dado do painel como memoria oficial.

---

## 6. Evidencias minimas

- print do painel em 1_MIN;
- print do painel em 5_MIN;
- print do bloqueio DIARIO;
- print do bloqueio SEMANAL;
- horario do teste;
- ativo testado;
- observacao sobre preco;
- observacao sobre tempo;
- observacao sobre volume.

---

## 7. Encerramento

A execucao deve terminar com um dos pareceres:

- TESTE_CONCLUIDO_COM_RESSALVAS
- TESTE_REPROVADO_COM_PENDENCIAS
- TESTE_INCONCLUSIVO

Esta ordem autoriza apenas teste observacional em mercado aberto.

Nao autoriza patch, calibragem, correcao de volume, destravamento de timeframe ou integracao com memoria/historico/conhecimento.
