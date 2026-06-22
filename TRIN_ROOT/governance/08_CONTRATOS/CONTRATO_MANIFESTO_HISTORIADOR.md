# CONTRATO — MANIFESTO DO HISTORIADOR TRIN

## Status
PROPOSTA ARQUITETURAL

## Arquivo futuro alvo
TRIN_HISTORICO/00_CONHECIMENTO/manifesto_historiador.json

## Vinculo
Este contrato complementa:

- governance/08_CONTRATOS/contrato_historiador.md
- governance/08_CONTRATOS/CONTRATO_ENTRADAS_SAIDAS_HISTORIADOR.md
- governance/08_CONTRATOS/CONTRATO_SCHEMA_INDICE_GERAL_BERNARDO.md
- governance/08_CONTRATOS/CONTRATO_SCHEMA_CONHECIMENTO_HISTORIADOR.md
- governance/02_AUDITORIAS/AUDITORIA_ARQUITETURAL_PRELIMINAR_HISTORIADOR.md

## Missao
Definir o manifesto obrigatorio de cada execucao oficial futura do Historiador.

O manifesto deve registrar origem, entradas, saidas, hashes, ressalvas e status final da execucao.

## Regra central
Nenhuma execucao futura do Historiador deve ser considerada oficial sem manifesto.

Relatorio humano nao substitui manifesto.

---

# 1. FUNCAO DO MANIFESTO

O manifesto_historiador.json deve responder:

- quem executou;
- quando executou;
- qual versao executou;
- quais entradas foram usadas;
- quais saidas foram geradas;
- qual indice do Bernardo foi consumido;
- qual status Fiscal estava associado;
- quais ressalvas existem;
- qual foi o status final;
- quais hashes garantem rastreabilidade.

---

# 2. LOCAL OFICIAL

Arquivo:

TRIN_HISTORICO/00_CONHECIMENTO/manifesto_historiador.json

Pasta:

TRIN_HISTORICO/00_CONHECIMENTO/

Encoding recomendado:

utf-8

Formato:

JSON

---

# 3. CAMPOS OBRIGATORIOS

## modulo
Valor esperado:

HISTORIADOR

## versao_historiador
Exemplo:

v1.0

## data_execucao
Formato recomendado:

yyyy-mm-dd hh:mm:ss

## status_execucao
Valores permitidos:

- CONCLUIDO_COM_RESSALVAS
- CONCLUIDO
- FALHOU
- INTERROMPIDO
- REPROVADO_POR_GOVERNANCA

## modo_execucao
Valores permitidos:

- TESTE_CONTROLADO
- AUDITORIA
- PRODUCAO_OFICIAL

Enquanto nao houver homologacao:

TESTE_CONTROLADO

## classificacao_conhecimento
Valores permitidos:

- CONHECIMENTO_INICIAL_COM_RESSALVAS
- GERADO_POR_INDICE_BERNARDO
- AGUARDANDO_FISCAL
- CERTIFICADO_POR_FISCAL
- APROVADO_COM_RESSALVAS
- REPROVADO

---

# 4. ENTRADAS REGISTRADAS

O manifesto deve registrar:

## indice_bernardo
Caminho esperado:

TRIN_HISTORICO/00_INDICES/indice_geral.csv

Campos:
- caminho
- existe
- hash
- linhas
- status_schema
- contrato_schema

## fiscal_temporal
Campos:
- status_base
- laudo_usado
- data_laudo
- resumo_por_arquivo
- resumo_por_motivo
- ressalvas

## calendario_b3
Campos:
- calendario_sessoes
- calendario_contratos
- status

## contratos_governanca
Campos:
- contrato_historiador
- contrato_entradas_saidas
- contrato_schema_indice
- contrato_schema_conhecimento
- contrato_manifesto

---

# 5. SAIDAS REGISTRADAS

O manifesto deve listar as saidas geradas em 00_CONHECIMENTO:

- estatistica_biblioteca.csv
- cobertura_temporal.csv
- distribuicao_fractais.csv
- estatistica_delta.csv
- estatistica_volume.csv
- catalogo_padroes_historiador.csv
- contexto_historiador.csv
- relatorio_historiador.txt

Para cada saida:

- caminho
- existe
- linhas, quando CSV
- hash
- status
- ressalva

---

# 6. HASHES

O manifesto deve registrar hash dos principais arquivos de entrada e saida.

Algoritmo recomendado:

SHA256

Obrigatorio para:

- indice_geral.csv
- estatistica_biblioteca.csv
- cobertura_temporal.csv
- distribuicao_fractais.csv
- catalogo_padroes_historiador.csv
- contexto_historiador.csv

---

# 7. RESSALVAS OBRIGATORIAS

Enquanto o Historiador nao for homologado, o manifesto deve conter as ressalvas:

- Historiador nao homologado oficialmente.
- Conhecimento gerado apenas como inicial.
- HistoriadorAdapter deve ser tratado como evidencia fraca.
- Padrao catalogado nao significa padrao historico comprovado.
- Cobertura temporal nao substitui Fiscal Temporal.
- indice_geral.csv nao substitui certificacao Fiscal.

---

# 8. BLOQUEIOS

O manifesto deve bloquear status oficial quando:

- indice_geral.csv nao existir;
- indice_geral.csv nao respeitar schema minimo;
- nao houver contrato de entradas e saidas;
- nao houver contrato de schema de conhecimento;
- saidas obrigatorias nao forem geradas;
- houver erro na execucao;
- tentativa de rodar modo PRODUCAO_OFICIAL sem homologacao.

---

# 9. EXEMPLO DE ESTRUTURA JSON

{
  "modulo": "HISTORIADOR",
  "versao_historiador": "v1.0",
  "data_execucao": "2026-06-21 23:00:00",
  "status_execucao": "CONCLUIDO_COM_RESSALVAS",
  "modo_execucao": "TESTE_CONTROLADO",
  "classificacao_conhecimento": "CONHECIMENTO_INICIAL_COM_RESSALVAS",
  "entradas": {
    "indice_bernardo": {
      "caminho": "TRIN_HISTORICO/00_INDICES/indice_geral.csv",
      "existe": true,
      "hash": "PENDENTE",
      "linhas": 0,
      "status_schema": "PENDENTE_VALIDACAO"
    },
    "fiscal_temporal": {
      "status_base": "PENDENTE",
      "laudo_usado": "PENDENTE",
      "ressalvas": []
    }
  },
  "saidas": [],
  "ressalvas": [
    "Historiador ainda nao homologado.",
    "Conhecimento inicial com ressalvas.",
    "Adapter deve ser tratado como evidencia fraca."
  ],
  "status_final": "AGUARDANDO_AUDITORIA_HARD"
}

---

# 10. PROIBICOES

O manifesto nao pode:

- homologar o Historiador sozinho;
- substituir Auditoria HARD;
- liberar sinal operacional;
- liberar aprendizagem;
- substituir Fiscal Temporal;
- alterar dados historicos;
- alterar indice do Bernardo.

---

# 11. RELACAO COM CHECKPOINT

Checkpoint de fase so deve ser criado depois que:

1. contrato do manifesto existir;
2. schema de entrada existir;
3. schema de saida existir;
4. manifesto for implementado ou formalmente planejado;
5. auditoria definir se pode haver patch controlado.

---

# 12. PARECER FINAL

O manifesto_historiador.json sera o carimbo cartorial de cada execucao futura do Historiador.

Sem manifesto, a execucao pode existir como teste, mas nao como execucao oficial.

Este contrato nao implementa o manifesto.
Ele apenas define sua obrigatoriedade, estrutura e limites arquiteturais.
