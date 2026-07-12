# CHECKLIST RG-02A — NÚCLEO DE REFERÊNCIAS DE MERCADO

**Status atual:** DOCUMENTAÇÃO EM REVISÃO FINAL
**Uso operacional:** BLOQUEADO
**Implementação:** NÃO INICIADA

## A. Arquitetura

[ ] Parecer RG-02 registrado.
[ ] Decisão RG-02A registrada.
[ ] Contrato Motor de Regiões V1.1 registrado.
[ ] Separação entre `origem_tipo` e `funcao_provavel` homologada.
[ ] `DEFESA` classificada como função provável, nunca como origem.
[ ] Estado inicial homologado: `funcao_provavel = INDETERMINADA`.
[ ] Estado inicial homologado: `status_funcao = NAO_AVALIADA`.
[ ] Fluxo preserva RG-02B futuro, Motor de Confluência, Planejador Operacional e Gestão de Risco.
[ ] RG-02B — Agregador/Classificador permanece previsto, mas não implementado.
[ ] RG-02A não gera plano operacional.
[ ] RG-02A não substitui Confluência.
[ ] RG-02A não substitui Fiscal.

## B. Escopo inicial

[ ] MILHAR homologado como primeira referência determinística.
[ ] VWAP_OFICIAL homologada como segunda referência determinística.
[ ] ABERTURA_SESSAO bloqueada até preservação canônica.
[ ] MAXIMA_SESSAO bloqueada até preservação canônica.
[ ] MINIMA_SESSAO bloqueada até preservação canônica.
[ ] FRACTAL bloqueado até contrato de integração.
[ ] TOPO/FUNDO bloqueados por ausência de fornecedor homologado.

## C. Saída canônica

[ ] `chave_referencia` determinística separada de `id_evento`.
[ ] Composição semântica mínima da `chave_referencia` declarada antes da implementação.
[ ] `status_funcao` usa `CONFIRMADA`, sem confundir inteligência com homologação ou autorização.
[ ] `fornecedor` e `campo_origem` representam a origem direta na RG-02A.
[ ] `origens` permanece reservado para coleção estruturada no RG-02B futuro.
[ ] Fornecedor e campo de origem declarados explicitamente.
[ ] Timeframe, modo de dados e certificação declarados explicitamente.
[ ] `direcao_provavel`, `forca` e `confianca` ausentes da primeira versão.
[ ] Sobreposição preserva identidade e proveniência de cada referência.

## D. Testes sintéticos futuros

[ ] Mesmo preço gera mesmas referências de milhar.
[ ] Mesmas entradas semânticas geram a mesma `chave_referencia`.
[ ] `timestamp_processamento` não altera a identidade da referência.
[ ] Mudança de milhar atualiza referências corretamente.
[ ] Preço inválido bloqueia saída.
[ ] VWAP ausente não gera referência.
[ ] VWAP válida preserva fornecedor, campo, origem e timestamp.
[ ] Nenhum teste gera entrada, stop, parcial ou alvo.
[ ] Todas as saídas permanecem `uso_operacional = BLOQUEADO`.

## E. Integração futura

[ ] Criar módulo isolado em arquivo próprio.
[ ] Não alterar `core/engine.py`.
[ ] Não alterar Motor de Confluência no primeiro patch.
[ ] RG-02B recebe auditoria, contrato e testes próprios antes da implementação.
[ ] Não alterar frontend no primeiro patch.
[ ] Não remover lógica legada antes de substituição homologada.
[ ] Criar testes unitários.
[ ] Criar laudo pós-patch.
[ ] Atualizar checklist-eixo.
[ ] Commit e push próprios.

## F. Critério de encerramento

[ ] Documentação homologada.
[ ] Código determinístico aprovado em testes sintéticos.
[ ] Integração somente leitura aprovada.
[ ] Uso operacional continua bloqueado.
