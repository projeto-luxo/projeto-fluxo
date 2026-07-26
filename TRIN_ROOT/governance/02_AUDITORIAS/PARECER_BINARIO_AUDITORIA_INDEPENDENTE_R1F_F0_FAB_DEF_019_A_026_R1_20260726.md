# PARECER BINÁRIO — AUDITORIA INDEPENDENTE DA R1F

## 1. Decisão final

```text
DECISAO=F0_APROVADA_E_ENCERRADA
R1F_INTEGRIDADE=APROVADA
R1F_CONTEUDO=APROVADO
R1F_IDENTIDADES=APROVADAS
R1F_GRAFO=APROVADO
R1F_MATRIZES=APROVADAS
R1F_ORIGENS=APROVADAS
R1F_NAO_INTERFERENCIA=APROVADA_NO_MODELO_PROBATORIO_DA_F0
```

## 2. Integridade externa

```text
SHA256_CALCULADO=4cfbe61a97839581f5e60a7829ad564bd2a8d39f06342dd12f3f7f276509616b
SHA256_ESPERADO=4cfbe61a97839581f5e60a7829ad564bd2a8d39f06342dd12f3f7f276509616b
SHA256=APROVADO
ZIP_CRC=APROVADO
MEMBROS_FISICOS=131
MEMBROS_UNICOS=131
CAMINHOS_INSEGUROS=0
```

O manifesto externo cobre 130 arquivos e exclui apenas o próprio manifesto,
evitando autorreferência. Todos os 130 hashes foram recalculados sem
divergência.

## 3. Fontes byte-exatas

```text
FONTES_FISICAS=112
LISTA_EXATA=112
HASHES_DECLARADOS=112
HASHES_RECALCULADOS=112
DIVERGENCIAS=0
CAMINHOS_AUSENTES=0
CAMINHOS_EXTRAS=0
```

O ZIP canônico `FONTES_BYTE_EXATAS_R1F_112_20260726.zip` também foi reaberto:

```text
CRC=APROVADO
MEMBROS=112
CAMINHOS_NORMALIZADOS_UNICOS=112
COPIAS_COINCIDENTES_COM_A_ENTREGA=112
```

Os 112 hashes recalculados coincidem integralmente com o índice físico
embutido da R1E.

## 4. Identidade dos componentes

A identidade foi recomputada segundo:

```text
component_instance_id=
CI- + SHA256(relative_path + LF + content_sha256)
```

Resultado:

```text
CAMINHOS=112
COMPONENT_INSTANCE_ID_UNICOS=112
IDS_DUPLICADOS=0
CONTENT_SHA256_UNICOS=109
```

Os três pares de bytes idênticos agora permanecem corretamente separados por
caminho físico.

## 5. Grafo

```text
NOS=112
EVENTOS_DE_REFERENCIA=119
ARESTAS_RESOLVIDAS=119
ENDPOINTS_INVALIDOS=0
TOKENS_NAO_ENCONTRADOS=0
REFERENCIAS_AMBIGUAS=0
REFERENCIAS_NAO_RESOLVIDAS=0
```

Os 119 tokens foram verificados diretamente nas linhas físicas, normalizando
simultaneamente `\` e `/`. A redução de 127 arestas da R1E para 119 na R1F é
coerente: a R1E duplicava oito referências ambíguas; a R1F resolve cada evento
para uma única instância física.

## 6. Matrizes e origens

```text
MATRIZ_DE_CANDIDATOS_R1E_RECONCILIADA=154_LINHAS
MATRIZ_FINAL_DE_ORIGENS=40_LINHAS
FAB_DEFS=8
PAPEIS_POR_FAB_DEF=5
```

Para cada `FAB-DEF-019` a `FAB-DEF-026`, foram confirmados fisicamente:

```text
ORIGEM
GERADOR_TEMPLATE
VALIDADOR
TESTE
CONSUMIDOR
```

Todas as 40 identidades, hashes e linhas de prova foram recalculados ou
comparados diretamente contra as 112 fontes.

### Mapa de origem aprovado

```text
FAB-DEF-019=avaliador_semantico.py
FAB-DEF-020=carregador_autoridades.py
FAB-DEF-021=executor_testes_materializados.py
FAB-DEF-022=corretor_tecnico_controlado.py
FAB-DEF-023=gerador_delta_exato.py
FAB-DEF-024=hashes_io.py
FAB-DEF-025=preflight_isolamento.py
FAB-DEF-026=hashes_io.py
```

Este mapa identifica a origem e seus cinco papéis. Ele não declara os defeitos
corrigidos.

## 7. FAB-DEF-025

A ausência formal da R1E foi refutada.

Consumidor físico confirmado:

```text
15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/motor_sidecar.py
```

Provas físicas aprovadas:

```text
IMPORTA_PREFLIGHT=SIM
CHAMA_validate_canonical_preflight=SIM
BLOQUEIA_PREFLIGHT_REPROVADO=SIM
PERSISTE_preflight_registry=SIM
```

## 8. Evidências internas

```text
EVIDENCIAS_R1F_SHA256=247b3c5ab91c1c6f788b8f1d336554d0b77edac09482600057401d0e26e86967
SHA=APROVADO
CRC=APROVADO
MEMBROS=23
HASHES_INTERNOS=22
DIVERGENCIAS=0
COPIAS_BYTE_EXATAS_DE_ENTREGAVEIS=10_DE_10
```

O arquivo de hashes internos exclui apenas a si próprio.

## 9. Não interferência

A prova disponível combina:

- 112 hashes iguais à fotografia R1E;
- auditoria estática do analisador;
- ausência de subprocessos e comandos Git no analisador;
- zero importação ou execução dos componentes da Fábrica;
- registro operacional do Windows;
- escrita restrita à raiz externa de saída.

```text
ZERO_MODIFICACOES=APROVADO_NO_ESCOPO_PROBATORIO_DA_F0
ZERO_EXECUCOES_COMPONENTES=APROVADO
ZERO_TRIN=APROVADO
ZERO_GIT=APROVADO
```

## 10. Efeito institucional

A F0 encerra a localização da origem. Ela não encerra os defeitos.

```text
F0=ENCERRADA
FAB_DEF_019_A_026=CAUSA_RAIZ_LOCALIZADA
CORRECAO_APLICADA=NAO
DEFEITOS_ENCERRADOS=NAO
```

Atos autorizados após este parecer:

1. atualizar documentalmente o Registro Vivo da Fábrica;
2. emitir o termo técnico de encerramento da F0;
3. preparar, em missão separada, o desenho controlado do Bloco I.

Atos não autorizados:

```text
PATCH=NAO
APLICACAO=NAO
TRIN=NAO
COMMIT=NAO
PUSH=NAO
```
