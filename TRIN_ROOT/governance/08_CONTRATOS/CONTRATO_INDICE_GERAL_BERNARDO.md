# CONTRATO — INDICE GERAL DO BERNARDO

## Status
PROPOSTA ARQUITETURAL

## Arquivo oficial
TRIN_HISTORICO/00_INDICES/indice_geral.csv

## Vinculo
Este contrato complementa:

- governance/08_CONTRATOS/contrato_bernardo.md
- governance/08_CONTRATOS/CONTRATO_ENTRADAS_SAIDAS_HISTORIADOR.md
- governance/02_AUDITORIAS/AUDITORIA_ARQUITETURAL_PRELIMINAR_HISTORIADOR.md

## Missao
Formalizar o indice_geral.csv como produto oficial indexado do Bernardo, permitindo que modulos consumidores usem este arquivo sem violar a regra de nao consumir CSV bruto diretamente.

## Decisao arquitetural
indice_geral.csv nao deve ser tratado como CSV bruto livre.

Ele deve ser tratado como:

SAIDA OFICIAL INDEXADA DO BERNARDO

Desde que seja gerado, mantido ou validado pelo fluxo oficial do Bernardo.

## Responsabilidade do Bernardo
O Bernardo e responsavel por:

- organizar a memoria historica;
- indexar arquivos reconhecidos;
- registrar metadados da biblioteca;
- informar ativo, fractal, arquivo, caminho e cobertura;
- expor memoria organizada para modulos consumidores;
- impedir que inteligencias futuras leiam CSV bruto sem mediacao.

## O que o indice_geral.csv pode representar
O indice_geral.csv pode conter metadados como:

- ativo
- fractal
- arquivo
- caminho
- linhas
- tamanho_mb
- data_inicio
- data_fim
- status
- confiabilidade
- delta_medio, quando disponivel
- volume_medio, quando disponivel
- data_indexacao
- origem
- observacao

## Consumidores permitidos
Podem consumir indice_geral.csv com ressalvas:

- Historiador
- Fiscal Temporal, quando precisar conferir cobertura indexada
- Governanca
- ferramentas de auditoria
- Bernardo Adapter, se aplicavel

## Consumidores proibidos
Nao devem consumir indice_geral.csv para decisao operacional direta:

- Motor de Confluencia como verdade forte
- Motor Geral de Pontuacao
- Painel operacional como sinal
- Modulos de aprendizagem sem auditoria
- Qualquer modulo que transforme indice em ordem

## Relacao com Historiador
O Historiador pode usar indice_geral.csv como entrada inicial se, e somente se, este indice estiver formalizado como saida oficial do Bernardo.

Classificacao para o Historiador:

ENTRADA PERMITIDA COM RESSALVAS

O Historiador deve tratar o indice como fonte de memoria organizada, nao como base historica bruta.

## Relacao com Fiscal Temporal
O indice_geral.csv nao substitui o Fiscal Temporal.

Mesmo que um arquivo esteja indexado pelo Bernardo, isso nao significa que esteja certificado temporalmente.

Indexado pelo Bernardo significa:
arquivo conhecido e organizado.

Certificado pelo Fiscal significa:
arquivo aprovado temporal e estruturalmente.

## Relacao com Ze do Eucrazio
O indice_geral.csv nao gera fractais e nao substitui manifestos do Ze.

Se houver necessidade de regenerar fractais, a ordem deve vir do Fiscal ou da governanca, nao do Historiador diretamente.

## Proibicoes
O indice_geral.csv nao pode ser usado para:

- corrigir arquivos historicos;
- certificar integridade temporal;
- gerar ordem operacional;
- substituir Bernardo;
- substituir Fiscal Temporal;
- substituir manifestos do Ze;
- criar padrao historico comprovado sem auditoria;
- alimentar aprendizagem sem contrato especifico.

## Condicao de validade
Para ser considerado oficial, o indice_geral.csv deve possuir:

1. origem Bernardo;
2. local padronizado em TRIN_HISTORICO/00_INDICES;
3. separador ponto e virgula;
4. encoding utf-8-sig;
5. colunas minimas definidas;
6. data de geracao ou atualizacao;
7. status ou confiabilidade quando disponivel;
8. rastreabilidade para os arquivos indexados.

## Colunas minimas recomendadas
- ativo
- fractal
- arquivo
- caminho
- linhas
- data_inicio
- data_fim
- status
- origem

## Colunas complementares recomendadas
- tamanho_mb
- confiabilidade
- delta_medio
- volume_medio
- data_indexacao
- hash
- observacao

## Status de confianca
O indice pode usar status como:

- OK
- ALERTA
- ERRO
- PENDENTE_FISCAL
- CERTIFICADO
- APROVADO_COM_RESSALVAS
- REPROVADO

Enquanto nao houver integracao plena com o Fiscal Temporal, o indice deve ser tratado como:

MEMORIA_INDEXADA_COM_RESSALVAS

## Manifesto futuro recomendado
A geracao oficial do indice deve produzir manifesto contendo:

- versao do Bernardo
- data_execucao
- quantidade de arquivos indexados
- quantidade por ativo
- quantidade por fractal
- erros de leitura
- alertas
- arquivos ignorados
- hash do indice gerado
- origem dos dados

Arquivo recomendado:

TRIN_HISTORICO/00_INDICES/manifesto_indice_geral_bernardo.json

## Parecer final
O indice_geral.csv pode ser reconhecido como saida oficial do Bernardo e usado pelo Historiador como entrada inicial com ressalvas.

Essa autorizacao nao permite leitura livre de CSV bruto.

Essa autorizacao nao homologa o Historiador.

Essa autorizacao apenas fecha a porteira arquitetural entre Bernardo e Historiador.
