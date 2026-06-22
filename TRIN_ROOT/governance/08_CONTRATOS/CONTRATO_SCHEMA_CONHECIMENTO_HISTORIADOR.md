# CONTRATO — SCHEMA DAS SAIDAS DO HISTORIADOR

## Status
PROPOSTA ARQUITETURAL

## Pasta alvo
TRIN_HISTORICO/00_CONHECIMENTO/

## Vinculo
Este contrato complementa:

- governance/08_CONTRATOS/contrato_historiador.md
- governance/08_CONTRATOS/CONTRATO_ENTRADAS_SAIDAS_HISTORIADOR.md
- governance/08_CONTRATOS/CONTRATO_SCHEMA_INDICE_GERAL_BERNARDO.md
- governance/02_AUDITORIAS/AUDITORIA_ARQUITETURAL_PRELIMINAR_HISTORIADOR.md

## Missao
Definir o schema minimo das saidas produzidas pelo Historiador, impedindo que conhecimento inicial seja tratado como certificacao, sinal ou decisao operacional.

## Regra central
Toda saida do Historiador e conhecimento derivado.

Nao e dado bruto.
Nao e certificacao temporal.
Nao e sinal operacional.
Nao e ordem.
Nao substitui o Motor de Confluencia.

---

# 1. FORMATO OFICIAL

## Separador
;

## Encoding
utf-8-sig

## Header
Obrigatorio.

## Pasta oficial
TRIN_HISTORICO/00_CONHECIMENTO/

---

# 2. ARQUIVOS OFICIAIS ATUAIS

As saidas atuais reconhecidas em modo inicial sao:

- estatistica_biblioteca.csv
- cobertura_temporal.csv
- distribuicao_fractais.csv
- estatistica_delta.csv
- estatistica_volume.csv
- catalogo_padroes_historiador.csv
- contexto_historiador.csv
- relatorio_historiador.txt

---

# 3. CAMPOS DE GOVERNANCA RECOMENDADOS PARA TODA SAIDA CSV

Toda saida futura do Historiador deve conter, quando aplicavel:

- origem
- versao_historiador
- data_execucao
- status_confianca
- base_bernardo
- base_fiscal
- observacao

Enquanto os scripts atuais nao possuirem esses campos, as saidas devem ser tratadas como:

CONHECIMENTO_INICIAL_COM_RESSALVAS

---

# 4. SCHEMA — estatistica_biblioteca.csv

## Missao
Resumir a biblioteca por ativo e fractal.

## Colunas atuais aceitas
- ativo
- fractal
- arquivos
- linhas_total
- tamanho_total_mb
- data_inicio
- data_fim
- alertas
- erros
- confiabilidade_media

## Colunas futuras recomendadas
- origem
- versao_historiador
- data_execucao
- status_confianca
- base_bernardo
- base_fiscal
- observacao

## Proibicao
Este arquivo nao certifica qualidade temporal.
Este arquivo nao gera sinal.

---

# 5. SCHEMA — cobertura_temporal.csv

## Missao
Mapear cobertura temporal por ativo, fractal e arquivo.

## Colunas atuais aceitas
- ativo
- fractal
- arquivo
- data_inicio
- data_fim
- anos_cobertos
- linhas
- status

## Colunas futuras recomendadas
- origem
- versao_historiador
- data_execucao
- status_confianca
- base_bernardo
- base_fiscal
- observacao

## Proibicao
Este arquivo nao substitui o Fiscal Temporal.
Cobertura temporal nao equivale a certificacao temporal.

---

# 6. SCHEMA — distribuicao_fractais.csv

## Missao
Resumir distribuicao de arquivos e linhas por fractal.

## Colunas atuais aceitas
- fractal
- ativos
- arquivos
- linhas_total
- status_ok
- status_alerta

## Colunas futuras recomendadas
- origem
- versao_historiador
- data_execucao
- status_confianca
- base_bernardo
- base_fiscal
- observacao

## Proibicao
Distribuicao de fractais nao valida integridade dos fractais.

---

# 7. SCHEMA — estatistica_delta.csv

## Missao
Resumir delta quando existir informacao indexada oficial.

## Colunas atuais aceitas
- ativo
- fractal
- arquivos
- linhas_total
- delta_medio_disponivel
- observacao

## Regra
Delta detalhado futuro nao pode ser buscado em CSV bruto livremente.

Deve passar por:
- Bernardo/API do Bernardo
ou
- memoria certificada
ou
- pacote liberado pela governanca.

---

# 8. SCHEMA — estatistica_volume.csv

## Missao
Resumir volume quando existir informacao indexada oficial.

## Colunas atuais aceitas
- ativo
- fractal
- arquivos
- linhas_total
- volume_medio_geral
- observacao

## Regra
Volume detalhado futuro nao pode ser buscado em CSV bruto livremente.

Deve passar por:
- Bernardo/API do Bernardo
ou
- memoria certificada
ou
- pacote liberado pela governanca.

---

# 9. SCHEMA — catalogo_padroes_historiador.csv

## Missao
Registrar catalogo inicial de padroes preparados para mineracao.

## Colunas atuais aceitas
- codigo
- padrao
- descricao
- status
- origem

## Status permitido atual
PREPARADO_PARA_MINERACAO

## Regra
PADRAO_CATALOGADO nao significa padrao comprovado.

## Proibicao
Este arquivo nao pode ser usado como prova historica forte.
Este arquivo nao pode gerar sinal operacional.

---

# 10. SCHEMA — contexto_historiador.csv

## Missao
Registrar contexto inicial por horario ou evento.

## Colunas atuais aceitas
- contexto
- hora_inicio
- hora_fim
- descricao
- status

## Contextos atuais aceitos
- ABERTURA
- MEIO_PREGAO
- FECHAMENTO
- VENCIMENTO
- ROLAGEM

## Regra
Contexto catalogado nao significa conhecimento historico certificado.

VENCIMENTO e ROLAGEM devem ser integrados futuramente com:
- Calendario B3
- ContratoAtivoResolver
- Bastiao
- Fiscal Temporal

---

# 11. SCHEMA — relatorio_historiador.txt

## Missao
Gerar relatorio humano da execucao do Historiador.

## Conteudo minimo recomendado
- data_execucao
- versao_historiador
- status
- arquivos gerados
- ressalvas
- caminho das saidas

## Regra
Relatorio nao substitui manifesto.

---

# 12. MANIFESTO FUTURO OBRIGATORIO

Arquivo recomendado:

TRIN_HISTORICO/00_CONHECIMENTO/manifesto_historiador.json

Campos recomendados:

- versao_historiador
- data_execucao
- indice_bernardo_usado
- hash_indice_bernardo
- fiscal_status_base
- arquivos_saida
- quantidade_registros_por_saida
- status_final
- ressalvas
- auditoria_requerida

---

# 13. STATUS DE CONFIANCA DAS SAIDAS

Valores permitidos:

- CONHECIMENTO_INICIAL_COM_RESSALVAS
- GERADO_POR_INDICE_BERNARDO
- AGUARDANDO_FISCAL
- CERTIFICADO_POR_FISCAL
- APROVADO_COM_RESSALVAS
- REPROVADO
- ARQUIVADO

Status atual dos scripts existentes:

CONHECIMENTO_INICIAL_COM_RESSALVAS

---

# 14. RELACAO COM MOTOR DE CONFLUENCIA

O Motor de Confluencia pode receber conhecimento do Historiador apenas via HistoriadorAdapter.

Enquanto o Historiador nao estiver homologado, o peso deve ser fraco.

Regra:

SEM_CONHECIMENTO -> peso zero
PADRAO_CATALOGADO -> evidencia conceitual fraca
COBERTURA_ENCONTRADA -> evidencia estrutural fraca
PADRAO_MINERADO -> somente no futuro, apos Auditoria HARD

---

# 15. PROIBICOES

As saidas do Historiador nao podem:

- virar ordem operacional;
- decidir entrada;
- decidir stop;
- decidir parcial;
- decidir alvo;
- substituir Fiscal Temporal;
- substituir Bernardo;
- substituir Motor de Confluencia;
- provar padrao historico sem mineracao auditada;
- alimentar aprendizagem sem contrato especifico.

---

# 16. PARECER FINAL

As saidas atuais do Historiador sao aceitas como conhecimento inicial com ressalvas.

Este contrato nao homologa o Historiador.

Este contrato apenas define o limite das saidas em 00_CONHECIMENTO, evitando que arquivos iniciais sejam tratados como inteligencia operacional forte.
