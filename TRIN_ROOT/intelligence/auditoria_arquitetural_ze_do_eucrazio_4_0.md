# 🏛️ AUDITORIA ARQUITETURAL CRÍTICA — ZÉ DO EUCRÁZIO 4.0

## Status deste documento

Este documento refaz a evolução do Zé do Eucrázio seguindo a metodologia oficial do TRIN.

A versão gerada deve ser tratada como:

```text
ZÉ DO EUCRÁZIO 4.0 — OFICIAL PARA TESTE CONTROLADO
```

Não deve ser considerada congelada até passar por execução real, conferência dos arquivos gerados e futura certificação do Fiscal Temporal.

---

# ETAPA ZERO — ANÁLISE DE NECESSIDADE EVOLUTIVA

## Problema que o módulo resolve

O TRIN possui histórico de 1 minuto e precisa gerar fractais derivados para enriquecer a Biblioteca Histórica.

## Esse problema já é resolvido por outro módulo?

Não.

O Bernardo organiza memória, mas não deve reconstruir tempo.

O Fiscal Temporal certifica, mas não deve gerar fractais.

O Historiador interpreta experiências, mas não deve transformar dados brutos.

## O módulo é necessário?

Sim.

Sem o Zé, o TRIN dependeria de múltiplas fontes externas para cada timeframe, aumentando divergência temporal e risco de inconsistência histórica.

## Melhoria incremental resolveria?

A v0.3 era funcional, mas limitada a 2 e 3 minutos, sem contrato formal de saída, sem manifesto, sem política de parcial e sem separação clara entre geração e certificação.

Portanto, a evolução estrutural é justificada.

## Responsabilidade única

O Zé deve apenas:

```text
ler → normalizar → agrupar → gerar → registrar
```

Ele não deve:

```text
certificar → interpretar → pontuar → aprender → decidir
```

## Veredito da Etapa Zero

A criação da versão 4.0 é necessária e fortalece a arquitetura.

---

# ETAPA 1 — AUDITORIA ARQUITETURAL

## Missão

Gerar fractais determinísticos a partir de histórico de 1 minuto.

## Entrada

Arquivos CSV localizados em:

```text
C:\Users\User\projeto_fluxo\TRIN_HISTORICO\01_1_MIN\win
```

Formatos aceitos:

```text
Histórico Profit — 9 colunas
Histórico Profit reduzido — 8 colunas
Memória Viva TRIN — 15 colunas
```

## Saída

CSV oficial com:

```text
separador ;
encoding utf-8-sig
header=True
timestamp
timezone
sessao
fractal_minutos
status_candle
qtd_candles_origem
OHLC
volume
delta
saldo
agressões
vwap
```

## Consumidor futuro

Fiscal Temporal.

Depois da certificação:

```text
Bernardo → Historiador → Motor
```

## Riscos identificados na v0.3

### 1. Resample poderia alinhar por relógio, não por sessão

A v0.3 usava:

```python
df.resample(f"{minutos}min")
```

Isso é funcional, mas pode causar ambiguidade em fractais não divisores ou sessões com buracos.

A v4.0 agrupa por contador dentro da sessão para impedir cruzamento entre pregões.

### 2. Risco de cruzar pregões

A v0.3 não tinha uma regra explícita de sessão.

A v4.0 cria a coluna:

```text
sessao = data do pregão
```

Ainda não é calendário B3 completo, mas já impede misturar dias diferentes.

### 3. Candles parciais silenciosos

A v0.3 não registrava sobras de fractais como 7, 9, 45, 90, 180.

A v4.0 marca:

```text
COMPLETO
PARCIAL
```

e gera relatório de candles parciais.

### 4. VWAP agregada incorreta

A v0.3 usava o último VWAP.

A v4.0 usa VWAP ponderada por volume quando possível:

```text
Σ(vwap * volume) / Σ(volume)
```

Se o volume for zero, usa o último VWAP disponível.

### 5. Risco de sobrescrita

A v0.3 sobrescrevia arquivos sem política explícita.

A v4.0 tem:

```python
SOBRESCREVER_SAIDA = False
```

### 6. Ausência de manifesto

A v0.3 imprimia resumo, mas não deixava manifesto JSON estruturado.

A v4.0 gera manifesto com:

```text
origem
hash origem
saída
hash saída
linhas
parciais
alertas
erros
configuração
```

### 7. Header

A v0.3 salvava sem header.

A v4.0 salva com header=True porque um contrato oficial de módulo deve ser autoexplicativo.

Atenção: se o Bernardo atual espera header=False, o contrato do Bernardo precisará ser ajustado antes da integração.

---

# ETAPA 2 — CONTRATO DO MÓDULO

## O Zé 4.0 promete

1. Nunca alterar arquivos originais.
2. Nunca gerar sinais.
3. Nunca certificar definitivamente.
4. Nunca atravessar sessões.
5. Registrar candles parciais.
6. Produzir arquivos rastreáveis.
7. Gerar manifesto e log.
8. Ser determinístico para a mesma entrada e configuração.

## O Zé 4.0 não promete

1. Validar calendário completo da B3.
2. Corrigir buracos na série.
3. Homologar a integridade final.
4. Interpretar o mercado.
5. Atualizar Bernardo automaticamente.

Essas responsabilidades pertencem a outros módulos.

---

# ETAPA 3 — DECISÕES TÉCNICAS DA IMPLEMENTAÇÃO

## Agrupamento

A v4.0 usa agrupamento sequencial dentro de cada sessão:

```text
sessao 2026-06-01
candle 0..minutos-1 → grupo 0
candle minutos..2*minutos-1 → grupo 1
```

Isso garante que um candle de ontem nunca será somado com um candle de hoje.

## Candle parcial

Política adotada:

```text
não descartar
marcar como PARCIAL
registrar em relatório
```

## Saldo

O campo saldo foi mantido como último valor do bloco, porque frequentemente representa estado acumulado/posição de fluxo, e não soma simples.

## Delta

Delta é somado.

## Agressões

Agressões são somadas.

## VWAP

VWAP é ponderada por volume.

## Timezone

Registrado como:

```text
America/Sao_Paulo
```

Sem conversão automática nesta versão, porque a origem atual já vem como data/hora local.

---

# ETAPA 4 — TESTE CONTROLADO

A versão vem com:

```python
MODO_TESTE_CONTROLADO = True
MAX_ARQUIVOS_TESTE = 1
SOBRESCREVER_SAIDA = False
```

Isso impede que a primeira execução processe a biblioteca inteira ou sobrescreva arquivos importantes.

Depois de validar o primeiro teste, o operador poderá mudar:

```python
MODO_TESTE_CONTROLADO = False
```

---

# ETAPA 5 — LIMITAÇÕES ASSUMIDAS

A v4.0 ainda não resolve:

1. Calendário oficial da B3 com feriados.
2. Horário real de pregão por ativo.
3. Leilões e sessões especiais.
4. Certificação definitiva.
5. Integração automática com Bernardo.
6. Memory Player.
7. Diário, semanal e mensal.
8. Teste de performance em milhões de linhas.

Esses pontos são responsabilidade de etapas futuras.

---

# VEREDITO

## Aprovado para download?

Sim.

## Aprovado para teste controlado?

Sim.

## Aprovado para congelamento arquitetural?

Não ainda.

## Classificação oficial

```text
ZÉ DO EUCRÁZIO 4.0
STATUS: OFICIAL PARA TESTE CONTROLADO
PRÓXIMO PASSO: Executar em 1 arquivo e analisar manifesto/log
CERTIFICAÇÃO FINAL: Fiscal Temporal
```

---

# Próximo passo recomendado

1. Baixar o arquivo.
2. Salvar no projeto como:

```text
C:\Users\User\projeto_fluxo\backend\ze_do_eucrazio_4_0.py
```

3. Rodar com modo teste controlado.
4. Conferir:
   - pasta de saída;
   - log;
   - manifesto;
   - relatório de candles parciais.
5. Só depois liberar processamento total.
