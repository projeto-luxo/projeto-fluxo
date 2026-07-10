# CHECKLIST_VALIDACAO_CANDLEBUILDER_MERCADO_ABERTO.md

## Status

CHECKLIST_PRE_OPERACIONAL  
Projeto: TRIN  
Modulo: CandleBuilderPainel  
Condicao: executar somente com mercado aberto  

---

## 1. Objetivo

Definir o roteiro de validacao real do CandleBuilderPainel em mercado aberto.

Este checklist nao altera codigo.

Ele serve para orientar a proxima etapa de teste operacional dos candles agregados a partir de snapshots RTD/Excel.

---

## 2. Pre-condicoes obrigatorias

Antes de iniciar a validacao:

- Git deve estar limpo.
- Excel RTD deve estar recebendo dados.
- Profit deve estar aberto e conectado.
- Backend do TRIN deve estar ativo.
- Frontend do TRIN deve estar ativo.
- Mercado deve estar aberto.
- Timeframe inicial deve ser intraday.
- DIARIO e SEMANAL devem continuar bloqueados.

---

## 3. O que deve ser validado

### 3.1 Preco

Validar se cada candle apresenta corretamente:

- abertura;
- maxima;
- minima;
- fechamento;
- ultimo preco recebido;
- coerencia visual com o fluxo do mercado.

---

### 3.2 Tempo

Validar se o CandleBuilder respeita:

- virada correta de candle;
- duracao correta do timeframe selecionado;
- nao duplicacao de timestamps;
- continuidade temporal;
- comportamento apos troca de timeframe.

---

### 3.3 Timeframes intraday

Testar, um por vez:

- 15s
- 30s
- 1_MIN
- 2_MIN
- 5_MIN
- 10_MIN
- 15_MIN
- 30_MIN
- 60_MIN

Regra:

Nao testar todos de forma apressada.  
Validar primeiro timeframes curtos, depois maiores.

---

### 3.4 Bloqueio de governanca

Confirmar que permanecem bloqueados:

- DIARIO
- SEMANAL

Resultado esperado:

BLOQUEADO_POR_GOVERNANCA

---

### 3.5 Volume agregado

Validar com cuidado especial:

- se o volume esta variando;
- se o volume nao esta fixo;
- se o volume nao esta capado;
- se o volume acumulado faz sentido dentro do candle;
- se a origem do volume e snapshot RTD esta clara.

Observacao:

Volume ainda nao esta homologado.  
Qualquer comportamento estranho deve gerar auditoria propria, nao patch imediato.

---

## 4. O que nao fazer durante o teste

Nao fazer:

- alterar codigo durante o pregao;
- liberar DIARIO;
- liberar SEMANAL;
- mexer nas pendencias do Ze;
- mexer nas ressalvas do Bernardo;
- promover CandleBuilder para historico oficial;
- usar CandleBuilder como fonte do Historiador;
- usar CandleBuilder como memoria oficial do Bernardo;
- corrigir volume sem auditoria propria.

---

## 5. Evidencias a coletar

Durante o teste, coletar:

- print do painel em 1_MIN;
- print do painel em 5_MIN;
- print do bloqueio DIARIO/SEMANAL;
- horario do teste;
- ativo testado;
- timeframe testado;
- observacao sobre volume;
- observacao sobre virada de candle;
- eventuais mensagens do backend;
- eventuais erros do console/frontend.

---

## 6. Criterios de aprovacao

O CandleBuilderPainel podera ser considerado aprovado operacionalmente para painel intraday se:

- candles virarem no tempo correto;
- timestamps nao duplicarem;
- preco respeitar abertura, maxima, minima e fechamento;
- troca de timeframe nao quebrar o painel;
- DIARIO e SEMANAL permanecerem bloqueados;
- status continuar OPERACIONAL_NAO_CERTIFICADO;
- volume nao apresentar anomalia grave.

---

## 7. Criterios de ressalva

Gerar ressalva se:

- preco funcionar, mas volume permanecer duvidoso;
- candle virar corretamente, mas houver pequena divergencia visual;
- timeframe funcionar, mas precisar de melhor rastreabilidade;
- backend responder corretamente, mas frontend exibir atraso.

---

## 8. Criterios de reprovacao

Reprovar a validacao se:

- candle nao virar;
- timestamps duplicarem;
- abertura/maxima/minima/fechamento ficarem incoerentes;
- troca de timeframe quebrar o grafico;
- DIARIO ou SEMANAL forem liberados indevidamente;
- volume ficar fixo/capado sem explicacao;
- painel travar ou perder fluxo.

---

## 9. Decisao final esperada

Ao final do teste com mercado aberto, gerar laudo separado com um dos status:

- APROVADO_OPERACIONAL_COM_RESSALVAS
- REPROVADO_COM_PENDENCIAS
- TESTE_INCONCLUSIVO

Este checklist nao homologa historico.

A homologacao historica depende de Fiscal Temporal, Bernardo e regras proprias de certificacao.
