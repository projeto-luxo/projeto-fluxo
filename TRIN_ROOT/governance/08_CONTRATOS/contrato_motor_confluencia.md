# CONTRATO OFICIAL — MOTOR DE CONFLUÊNCIA

## Status

Planejado.

## Responsabilidade única

Medir evidências ponderadas de oportunidade com base em múltiplos módulos e memória histórica.

## Entrada

VWAP, Delta, fluxo, absorção, contexto, fractal, memória histórica, histórico estatístico e conhecimento do Historiador.

## Saída

Score de confluência, evidências ponderadas, justificativa contextual e índice preliminar de qualidade.

## Garantias

- Produz evidências, não ordens.
- Mantém operador como decisor final.
- Soma contexto sem bloquear operações por autoridade própria.

## O que este módulo nunca deve fazer

- Executar ordem.
- Substituir operador.
- Acessar CSV bruto diretamente.
- Ignorar Bernardo.

## Consumidores

Motor Geral de Pontuação, painel TRIN, operador.

## Fornecedores

Bernardo, Historiador, engines atuais e memória certificada.

## Auditoria obrigatória

Todo uso estrutural deste contrato deve passar por checklist de teste e Auditoria HARD.

---

## Atualizacao de governanca — 2026-06-21

### Classificacao atual
EM TESTE CONTROLADO

### Observacao
Motor de Confluencia esta integrado ao backend e ao painel como camada de leitura cognitiva, evidencias e score de confluencia.

Ainda nao esta congelado arquiteturalmente.

### Responsabilidade preservada
Medir evidencias ponderadas a partir de dados ja organizados, certificados ou contextualizados, produzindo leitura cognitiva explicavel.

### Dependencias obrigatorias
- Bernardo como memoria organizada.
- Fiscal Temporal como certificador de integridade.
- Historiador como fonte futura de conhecimento historico.
- Bastiao como validador de conformidade arquitetural quando aplicavel.
- Backend institucional como camada de entrega ao painel.

### O que permanece proibido
- Gerar ordem operacional.
- Substituir operador.
- Corrigir dados historicos.
- Ler CSV bruto diretamente.
- Ignorar Bernardo.
- Ignorar bloqueios ou ressalvas do Fiscal/Bastiao.
- Assumir papel de Motor Geral de Pontuacao.

### Ressalvas
- Confluencia v2.2 aparece no painel, mas ainda deve passar por Auditoria HARD.
- Ainda depende de memoria e certificacoes mais maduras.
- Nao deve ser tratado como decisor final.
- Nao esta congelado arquiteturalmente.
