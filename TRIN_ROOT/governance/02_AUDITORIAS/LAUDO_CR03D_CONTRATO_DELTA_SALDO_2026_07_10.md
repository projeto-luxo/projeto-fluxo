# LAUDO CR-03D — CONTRATO SEMÂNTICO DELTA / SALDO

**Projeto:** TRIN
**Data:** 10/07/2026
**Classificação:** Auditoria arquitetural e semântica
**Status:** CONCLUÍDA COM REPROVAÇÃO SEMÂNTICA
**Git de referência:** 45b4696 — TRIN unifica VWAP oficial entre ao vivo e replay

---

## 1. OBJETIVO

Determinar se os campos `delta` e `saldo` representam evidências
operacionais independentes e se podem ser consumidos simultaneamente pelos
motores do TRIN sem produzir duplicidade de peso.

A auditoria também verificou:

- origem no Excel RTD;
- transporte Excel → backend;
- consumo pelo AggressionEngine;
- consumo pelo ConfluenceEngine;
- comportamento do Replay;
- apresentação no cockpit.

---

## 2. FONTE AUDITADA

### Excel

Arquivo:

`MARCO_ZERO_INSTITUCIONAL.xlsx`

Aba:

`PLAN1 RTD_PAINEL`

Campos:

| Célula | Identificação |
|---|---|
| I2 | TR_DELTA |
| J2 | TR - Saldo Acumulado de Agressão |
| K2 | TR - Volume de Agressão - Compra |
| L2 | TR - Volume de Agressão - Saldo |
| M2 | TR - Volume de Agressão - Venda |

Foi confirmado que:

- `I2` possui fórmula vinculada a `L2`;
- `J2` possui tópico RTD próprio;
- `K2`, `L2` e `M2` representam compra, saldo e venda de agressão.

---

## 3. AMOSTRAGEM TEMPORAL

Foram coletadas:

- 60 amostras válidas;
- 71 tentativas totais;
- 11 janelas descartadas por transição temporal.

Resultado:

| Verificação | Resultado |
|---|---:|
| I2 igual L2 | 60 / 60 |
| J2 igual L2 | 60 / 60 |
| backend.delta confere I2 | 60 / 60 |
| backend.delta confere L2 | 60 / 60 |
| backend.saldo confere J2 | 60 / 60 |
| backend.volume_saldo confere L2 | 60 / 60 |
| backend.volume_compra confere K2 | 60 / 60 |
| backend.volume_venda confere M2 | 60 / 60 |
| backend.delta igual backend.saldo | 60 / 60 |
| Divergências J2 x L2 | 0 |

---

## 4. CONCLUSÃO SOBRE ORIGEM E TRANSPORTE

O transporte Excel → backend está correto.

Não foi encontrada:

- troca de coluna;
- inversão entre delta e saldo;
- erro de leitura;
- erro de normalização numérica;
- divergência estável entre Excel e backend.

Portanto:

- a origem está tecnicamente aprovada;
- o leitor está tecnicamente aprovado;
- o backend transporta os campos corretos.

O problema identificado não é de transporte.

O problema é de interpretação semântica.

---

## 5. PROBLEMA SEMÂNTICO

Durante toda a amostragem observada:

`delta == saldo == volume_saldo`

Embora os campos possuam nomes e origens contratuais distintas, não foi
demonstrada independência operacional entre eles.

A mesma grandeza está sendo apresentada aos motores como se fossem duas
confirmações separadas.

### Classificação

`EVIDENCIA_DUPLICADA_NA_FONTE_ATUAL`

### Estado de independência

`NAO_COMPROVADA`

---

## 6. IMPACTO NO AGGRESSION ENGINE

Arquivo:

`core/aggression_engine.py`

### Frequência

A intensidade é calculada somando:

- valor absoluto do saldo;
- valor absoluto do delta;
- volume.

Quando `saldo == delta`, a mesma pressão é contabilizada duas vezes.

### Persistência

A persistência compradora exige:

`saldo > 0 and delta > 0`

A persistência vendedora exige:

`saldo < 0 and delta < 0`

Quando ambos são equivalentes, a confirmação dupla é automática e não
representa duas evidências independentes.

### Score de agressão

O score-base soma:

`saldo_total + delta_total`

Quando os dois campos representam a mesma grandeza, o score recebe peso
duplicado.

### Explosão de fluxo

As regras de explosão também exigem simultaneamente saldo e delta.

Quando os dois campos são equivalentes, os dois critérios não constituem
confirmação independente.

### Status

`REPROVADO_COM_RESSALVA_CRITICA`

---

## 7. IMPACTO NO CONFLUENCE ENGINE

Arquivos:

- `core/confluence_engine.py`
- `core/confluence_engine_v2.py`

A evidência de fluxo calcula:

`bruto = (delta + saldo) / 20000`

A direção é confirmada quando delta e saldo possuem o mesmo sinal.

Quando os valores são equivalentes:

- a intensidade é duplicada;
- a concordância é artificial;
- a mesma grandeza recebe aparência de duas evidências.

O ConfluenceEngine ainda adiciona a evidência `AGRESSAO`, cujo score foi
produzido pelo AggressionEngine usando delta e saldo.

Assim, a mesma informação pode influenciar:

1. a evidência `FLUXO_DELTA_SALDO`;
2. o `score_agressao`;
3. a evidência `AGRESSAO`;
4. regras diretas do backend que usam delta e score de agressão.

### Status

`REPROVADO_COM_RESSALVA_CRITICA`

---

## 8. IMPACTO NO BACKEND

Arquivo:

`backend/server_institucional_v6.py`

O backend transporta corretamente delta e saldo e entrega ambos aos motores.

Portanto:

- transporte: aprovado;
- interpretação: não homologada;
- regras dependentes do score de agressão: sob ressalva;
- calibragem: bloqueada.

### Status

`TRANSPORTE_APROVADO_INTERPRETACAO_NAO_HOMOLOGADA`

---

## 9. IMPACTO NO REPLAY

Arquivo:

`backend/replay_diagnostico.py`

O Replay possui fallback que utiliza delta como saldo quando o campo saldo não
está disponível.

Conceitualmente:

`saldo = delta`

Esse fallback não publica de forma explícita que o saldo foi derivado.

Depois, delta e saldo são agregados separadamente, podendo produzir aparência
de duas séries independentes.

### Risco

O Replay pode fabricar independência semântica onde existe apenas cópia ou
derivação.

### Status

`REPROVADO_POR_FALLBACK_SILENCIOSO`

---

## 10. IMPACTO NO FRONTEND

Arquivo:

`frontend/src/App.js`

O cockpit exibe dois cards:

- DELTA;
- SALDO.

O frontend não altera os valores e está tecnicamente correto.

Porém, dois cards distintos transmitem ao operador a ideia de duas métricas
independentes, o que não foi comprovado.

### Status

`FUNCIONAL_NAO_HOMOLOGADO_SEMANTICAMENTE`

---

## 11. DECISÃO ARQUITETURAL

Os campos brutos não serão apagados.

Devem ser preservados:

- `delta`;
- `saldo`;
- `volume_saldo`;
- respectivas fontes originais.

Antes dos motores, deverá existir um contrato semântico capaz de informar a
relação entre delta e saldo.

### Metadados propostos

- `delta_fonte`;
- `saldo_fonte`;
- `delta_saldo_relacao`;
- `delta_saldo_independentes`;
- `saldo_fallback_delta`;
- `fluxo_agressor_canonico`.

### Estados previstos

- `INDEPENDENTES`;
- `EQUIVALENTES_OBSERVADOS`;
- `SALDO_DERIVADO_DELTA`;
- `DELTA_DERIVADO_SALDO`;
- `INDETERMINADO`.

### Estado atual do AO VIVO

`delta_saldo_relacao = EQUIVALENTES_OBSERVADOS`

`delta_saldo_independentes = false`

### Estado previsto para fallback do Replay

`delta_saldo_relacao = SALDO_DERIVADO_DELTA`

`delta_saldo_independentes = false`

`saldo_fallback_delta = true`

---

## 12. DIRETRIZ DE CORREÇÃO

A solução aprovada conceitualmente é:

1. preservar dados brutos;
2. publicar origem e relação semântica;
3. produzir fluxo agressor canônico;
4. impedir peso duplicado quando delta e saldo forem equivalentes ou derivados;
5. impedir que equivalência seja tratada como confirmação independente;
6. tornar o fallback do Replay explícito;
7. informar a relação semântica no cockpit.

A correção deverá atingir, de forma controlada:

- candle canônico;
- Replay;
- AggressionEngine;
- ConfluenceEngine;
- payload do backend;
- cockpit.

---

## 13. PROIBIÇÕES

Até a implementação e homologação do contrato semântico:

- não apagar delta;
- não apagar saldo;
- não modificar a planilha RTD;
- não recalibrar scores;
- não recalibrar limites;
- não tratar igualdade como confirmação;
- não ocultar fallback do Replay;
- não liberar operacionalmente scores dependentes da duplicidade.

---

## 14. STATUS OFICIAL

| Componente | Status |
|---|---|
| Origem Excel | APROVADA |
| Transporte Excel → backend | APROVADO |
| Independência semântica | NÃO COMPROVADA |
| AggressionEngine | REPROVADO COM RESSALVA CRÍTICA |
| ConfluenceEngine | REPROVADO COM RESSALVA CRÍTICA |
| Backend | TRANSPORTE APROVADO / INTERPRETAÇÃO NÃO HOMOLOGADA |
| Replay | REPROVADO POR FALLBACK SILENCIOSO |
| Frontend | FUNCIONAL / NÃO HOMOLOGADO SEMANTICAMENTE |
| Calibragem | BLOQUEADA |
| Git antes da alteração | LIMPO |

---

## 15. PRÓXIMO PASSO

Realizar auditoria pré-patch do contrato semântico canônico para definir:

- proprietário da normalização;
- ponto único de criação dos metadados;
- comportamento AO VIVO;
- comportamento REPLAY;
- compatibilidade com consumidores existentes;
- testes de não regressão;
- critérios de homologação.

Nenhum motor deve ser alterado antes dessa definição.

---

## PARECER FINAL

O CR-03D não encontrou falha de transporte.

Foi comprovado que o sistema atual consome uma grandeza equivalente por meio
dos nomes delta e saldo e atribui a ela peso de evidências independentes.

A arquitetura deve preservar os dados brutos, mas corrigir a interpretação
antes dos motores.

**Resultado:** REPROVADO SEMANTICAMENTE, COM CORREÇÃO OBRIGATÓRIA ANTES DE
CALIBRAGEM OU HOMOLOGAÇÃO OPERACIONAL.
