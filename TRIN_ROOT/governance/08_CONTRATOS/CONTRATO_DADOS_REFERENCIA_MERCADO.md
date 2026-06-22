# CONTRATO — DADOS DE REFERENCIA DE MERCADO TRIN

## Status
PROPOSTA ARQUITETURAL

## Objetivo
Definir a camada oficial de Dados de Referencia de Mercado do TRIN.

Esta camada existe para impedir que preco, volume, ajuste, vencimento, rolagem, PTAX, milhar, ponto, contrato e escala sejam interpretados de forma solta por modulos diferentes.

## Problema identificado
Durante a auditoria do Historiador, do indice geral do Bernardo e do painel temporal, foram observados riscos de interpretacao numerica sem referencia contratual suficiente.

Exemplos de risco:
- preco medio distorcido;
- volume medio aparentemente fora de escala;
- comparacao incorreta entre WIN e WDO;
- confusao entre contrato cheio, mini contrato e ativo continuo;
- leitura historica sem saber vencimento/rolagem;
- uso de ajuste diario sem referencia formal;
- uso de PTAX sem contrato de origem;
- painel visual sem distinguir candle operacional de candle certificado.

## Regra central
Nenhum modulo do TRIN deve interpretar numericamente mercado sem referencia oficial de contrato, escala e contexto.

Dado de mercado sem referencia pode existir como dado bruto.
Mas nao deve virar conhecimento forte, confluencia forte, padrao historico ou decisao operacional.

---

# 1. RESPONSABILIDADE DA CAMADA

A camada Dados de Referencia de Mercado deve responder:

- qual ativo esta sendo analisado;
- qual contrato esta ativo;
- qual vencimento pertence ao contrato;
- qual multiplicador financeiro se aplica;
- qual escala de preco deve ser usada;
- qual tick minimo deve ser respeitado;
- qual regra de ajuste diario se aplica;
- qual referencia externa se aplica, quando existir;
- qual calendario de negociacao se aplica;
- se o periodo analisado esta em rolagem;
- se o dado pertence a contrato vencido, contrato atual ou contrato continuo.

---

# 2. ESCOPO INICIAL

## Ativos contemplados inicialmente
- WIN
- WDO

## Referencias de mercado contempladas
- contrato ativo;
- vencimento;
- rolagem;
- ajuste diario;
- preco de ajuste;
- tick minimo;
- valor por ponto;
- fator financeiro;
- escala/milhar;
- PTAX, quando aplicavel;
- calendario B3;
- horarios especiais;
- fonte oficial da referencia.

---

# 3. FONTES OFICIAIS

## B3
Fonte primaria para:
- especificacao de contratos;
- vencimentos;
- ajuste diario;
- preco de ajuste;
- horarios de negociacao;
- calendario de mercado;
- regras dos derivativos;
- tick minimo;
- valor financeiro do ponto;
- estrutura de contrato cheio e mini contrato.

## Banco Central do Brasil
Fonte primaria para:
- PTAX;
- series e referencias oficiais de cambio;
- dados historicos de cotacao quando aplicavel.

## Profit / RTD / Excel
Fonte operacional de leitura em tempo real.

Regra:
Profit/RTD/Excel fornece snapshot operacional, mas nao substitui a fonte oficial B3/BCB para especificacao do contrato.

---

# 4. RELACAO COM MODULOS DO TRIN

## Bernardo
Bernardo pode indexar arquivos e metadados, mas deve registrar a referencia de mercado usada quando o dado depender de contrato, escala, vencimento ou rolagem.

Bernardo nao deve declarar confiabilidade forte quando faltar referencia de mercado essencial.

## Zé do Eucrazio
Zé gera fractais determinísticos.

Zé nao deve corrigir escala de mercado por conta propria.
Zé deve consumir referencia externa quando a geracao depender de:
- sessao;
- vencimento;
- contrato;
- rolagem;
- ajuste;
- escala.

## Fiscal Temporal
Fiscal certifica integridade temporal.

Fiscal pode consultar Dados de Referencia de Mercado para diferenciar:
- lacuna real;
- feriado;
- horario especial;
- rolagem;
- contrato vencido;
- troca de contrato;
- corte de arquivo.

Fiscal nao deve manter a base de referencia de mercado.
Fiscal apenas consulta.

## Historiador
Historiador nao deve transformar estatistica em conhecimento forte sem referencia de mercado.

Media de preco, volume, range, delta ou comportamento historico deve ser classificada com ressalva quando faltar:
- contrato;
- escala;
- vencimento;
- ajuste;
- rolagem;
- fator financeiro.

## Motor de Confluencia
Motor nao deve receber evidencia historica forte sem referencia de mercado validada.

Qualquer evidencia derivada de historico sem referencia deve entrar como:
EVIDENCIA_FRACA_COM_RESSALVA

## Painel
Painel pode exibir candle operacional ao vivo.

Mas deve declarar:
- regua usada;
- timeframe usado;
- status operacional;
- se o candle e certificado ou nao.

Painel nao deve chamar candle operacional de fractal oficial.

## Bastiao
Bastiao deve consultar referencia de contrato ativo para impedir leitura operacional sobre contrato errado, vencido ou em rolagem nao resolvida.

---

# 5. CAMPOS MINIMOS FUTUROS

A base de Dados de Referencia de Mercado deve possuir, no minimo:

## ativo
Exemplos:
WIN
WDO

## ativo_original
Exemplos:
WINFUT
WDOFUT

## contrato
Exemplo:
WINQ26
WDOQ26

## contrato_rtd
Exemplo:
WINQ26_F_0

## tipo_contrato
Valores:
CHEIO
MINI
CONTINUO
DESCONHECIDO

## data_inicio_validade
Data em que a referencia passa a valer.

## data_fim_validade
Data em que a referencia deixa de valer.

## vencimento
Data de vencimento do contrato.

## status_contrato
Valores:
ATIVO
VENCIDO
EM_ROLAGEM
FUTURO
DESCONHECIDO

## tick_minimo
Menor variacao de preco permitida.

## valor_por_ponto
Valor financeiro associado ao ponto do contrato.

## multiplicador
Multiplicador financeiro do contrato.

## escala_preco
Regra de leitura da cotacao.

## escala_volume
Regra de leitura do volume.

## ajuste_diario
Indica se o contrato possui regra de ajuste diario relevante.

## preco_ajuste
Referencia de preco de ajuste, quando disponivel.

## ptax_referencia
Indica se PTAX e referencia relevante para o ativo/contrato.

## fonte_primaria
Exemplo:
B3
BCB

## fonte_operacional
Exemplo:
PROFIT_RTD
EXCEL_RTD

## observacao
Campo livre para ressalvas.

---

# 6. STATUS DE CONFIANCA

Valores permitidos:

- REFERENCIA_NAO_CONFIGURADA
- REFERENCIA_INICIAL_COM_RESSALVAS
- REFERENCIA_OFICIAL_VALIDADA
- REFERENCIA_DESATUALIZADA
- REFERENCIA_EM_ROLAGEM
- REFERENCIA_REPROVADA

Estado inicial do projeto:

REFERENCIA_INICIAL_COM_RESSALVAS

---

# 7. PROIBICOES

Sem Dados de Referencia de Mercado, nenhum modulo deve:

- afirmar confiabilidade forte de preco medio;
- afirmar confiabilidade forte de volume medio;
- comparar WIN e WDO financeiramente;
- interpretar milhar/escala por suposicao;
- corrigir dado historico automaticamente;
- gerar padrao historico forte;
- liberar aprendizagem com valor financeiro;
- homologar candle diario ou semanal;
- tratar ajuste diario como dado implicito;
- usar PTAX sem fonte definida;
- misturar contrato vencido com contrato ativo sem registro.

---

# 8. RELACAO COM DIARIO E SEMANAL

Candles DIARIO e SEMANAL exigem referencia adicional:

- calendario B3;
- horario oficial da sessao;
- feriados;
- horarios especiais;
- contrato ativo por data;
- rolagem;
- vencimento;
- ajuste diario;
- fechamento oficial;
- fonte de preco de ajuste, quando aplicavel.

Enquanto isso nao estiver formalizado, DIARIO e SEMANAL permanecem:

PLANEJADO / BLOQUEADO_POR_GOVERNANCA

---

# 9. RELACAO COM CANDLEBUILDER DO PAINEL

O CandleBuilder do Painel pode operar ate 60_MIN como candle operacional intraday.

Status:

OPERACIONAL_NAO_CERTIFICADO

Ele nao substitui:
- Zé do Eucrazio;
- Fiscal Temporal;
- Historico certificado;
- Profit;
- B3.

Ele apenas agrega snapshots RTD/Excel para visualizacao operacional.

---

# 10. PROXIMOS PASSOS

1. Criar schema da base de Dados de Referencia de Mercado.
2. Definir pasta oficial da base.
3. Definir formato CSV/JSON.
4. Definir campos obrigatorios para WIN e WDO.
5. Criar processo de validacao da referencia.
6. Integrar consulta futura ao Bastiao.
7. Integrar consulta futura ao Fiscal Temporal.
8. Integrar consulta futura ao Historiador.
9. Integrar referencia futura ao CandleBuilder DIARIO/SEMANAL.

---

# 11. PARECER FINAL

A camada Dados de Referencia de Mercado e necessaria para impedir interpretacao numerica sem contrato, escala e fonte oficial.

Ela deve ser tratada como base auxiliar estrutural do TRIN.

Sem essa camada, o TRIN pode continuar operando visualmente em tempo real e intraday, mas nao deve homologar estatisticas historicas fortes, candles diarios/semanais, comparacoes financeiras entre ativos ou conhecimento historico dependente de contrato.
