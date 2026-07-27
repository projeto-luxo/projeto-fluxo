# NOTIFICAÃ‡ÃƒO E REGISTRO VIVO DE DEFEITOS DA FÃBRICA
## Geradores de candidatos, aplicadores, runners e evidÃªncias

```text
DOCUMENTO=NOTIFICACAO_REGISTRO_VIVO_DEFEITOS_FABRICA
DATA_ABERTURA=2026-07-23
ESTADO=ABERTO
NATUREZA=GOVERNANCA_E_CORRECAO_DA_ORIGEM
APLICACAO_FUNCIONAL_NO_TRIN=NAO
GIT=NAO
```

## 1. Finalidade

Este documento registra defeitos confirmados nos mecanismos da FÃ¡brica que
geram candidatos, aplicadores, runners, testes e evidÃªncias.

A finalidade Ã© impedir que um erro seja corrigido apenas no artefato produzido
e depois desapareÃ§a da memÃ³ria do projeto enquanto a origem geradora permanece
defeituosa.

Toda Guia que assumir a correÃ§Ã£o da FÃ¡brica deverÃ¡ ler este documento antes de
alterar templates, geradores, validadores, runners ou emissores de evidÃªncias.

## 2. Regra permanente

```text
CORRECAO_LOCAL_NO_ARTEFATO=CONTENCAO
CORRECAO_NO_TEMPLATE_OU_GERADOR=CORRECAO_DA_ORIGEM
DEFEITO_ENCERRADO_SEM_CORRECAO_DA_ORIGEM=PROIBIDO
```

Quando um defeito surgir:

1. interromper a execuÃ§Ã£o no primeiro ponto seguro;
2. preservar as evidÃªncias;
3. registrar o defeito neste documento;
4. identificar o artefato gerado e o gerador/template responsÃ¡vel;
5. aplicar contenÃ§Ã£o localizada somente quando necessÃ¡ria para proteger o TRIN;
6. abrir correÃ§Ã£o da origem na FÃ¡brica;
7. criar teste negativo ou end-to-end que reproduza o defeito;
8. auditar independentemente a correÃ§Ã£o;
9. somente entÃ£o alterar o estado do defeito para `ENCERRADO_NA_ORIGEM`.

## 3. CritÃ©rio de encerramento de um defeito

Um defeito da FÃ¡brica somente pode ser encerrado quando todos os itens abaixo
forem comprovados:

```text
GERADOR_OU_TEMPLATE_LOCALIZADO=SIM
CAUSA_RAIZ_CONFIRMADA=SIM
CORRECAO_APLICADA_NA_ORIGEM=SIM
TESTE_DE_REGRESSAO_ADICIONADO=SIM
CICLO_END_TO_END_DESCARTAVEL=APROVADO
EMISSAO_REAL_DE_EVIDENCIAS=APROVADA
ZIP_REABERTO_E_VALIDADO=SIM
HASHES_INTERNOS_RECALCULADOS_E_CONFERIDOS=SIM
CAMINHO_DE_ROLLBACK_TESTADO=SIM
AUDITORIA_INDEPENDENTE=APROVADA
```

CompilaÃ§Ã£o, importaÃ§Ã£o ou testes unitÃ¡rios isolados nÃ£o sÃ£o prova suficiente.

## 4. Ciclo mÃ­nimo obrigatÃ³rio da FÃ¡brica

Todo gerador de aplicador deverÃ¡ provar o ciclo completo:

```text
GERAR
â†’ EXECUTAR_EM_BASE_DESCARTAVEL
â†’ VALIDAR_HASHES_ANTES
â†’ TESTAR_ANTES_DA_ESCRITA
â†’ APLICAR
â†’ TESTAR_DEPOIS_DA_ESCRITA
â†’ EMITIR_EVIDENCIAS
â†’ CRIAR_ZIP
â†’ REABRIR_ZIP
â†’ VALIDAR_MEMBROS
â†’ VALIDAR_HASHES_INTERNOS
â†’ TESTAR_ROLLBACK
â†’ CONFIRMAR_PRESERVACAO
```

A FÃ¡brica nÃ£o poderÃ¡ declarar um aplicador pronto apenas porque o cÃ³digo
compilou ou porque o mÃ³dulo funcional passou seus testes.

---

# 5. DEFEITOS CONFIRMADOS

## FAB-DEF-001 â€” Import ausente em teste gerado

```text
DATA=2026-07-23
ETAPA=FABRICACAO_TT01_CONTINUIDADE_R2
ARTEFATO_AFETADO=FABRICADOR_R2_INICIAL
SINTOMA=55_DE_56_TESTES
ERRO=NameError
ESTADO=CONTIDO_NO_ARTEFATO_ABERTO_NA_FABRICA
```

### DescriÃ§Ã£o

A funÃ§Ã£o `telemetria_indica_correcao_exercitada` foi criada no mÃ³dulo
funcional, mas o fabricador nÃ£o a adicionou Ã  lista explÃ­cita de imports do
arquivo de testes gerado.

### Impacto

O candidato nÃ£o pÃ´de ser emitido na primeira fabricaÃ§Ã£o, apesar de a lÃ³gica R2
estar correta.

### CorreÃ§Ã£o exigida na origem

O gerador deve validar automaticamente que toda referÃªncia usada nos testes
gerados estÃ¡ importada ou definida antes da execuÃ§Ã£o.

TambÃ©m deverÃ¡ existir teste negativo que falhe quando um sÃ­mbolo utilizado pelo
teste nÃ£o estiver disponÃ­vel no namespace.

---

## FAB-DEF-002 â€” Runner PowerShell gerado com `Join-Path` quebradiÃ§o

```text
DATA=2026-07-23
ETAPA=EXECUCAO_DO_FABRICADOR_R2
ARTEFATO_AFETADO=WRAPPER_POWERSHELL
SINTOMA=PROMPT_INTERATIVO_Path[0]
ESTADO=CONTIDO_NO_ARTEFATO_ABERTO_NA_FABRICA
```

### DescriÃ§Ã£o

O wrapper PowerShell foi emitido com quebra de linha invÃ¡lida em chamada
`Join-Path`, fazendo o PowerShell solicitar interativamente o parÃ¢metro
`Path[0]`.

### Impacto

A execuÃ§Ã£o aparentou travamento e exigiu desvio manual para executar o
fabricador Python diretamente.

### CorreÃ§Ã£o exigida na origem

Os wrappers gerados deverÃ£o:

```text
EVITAR_JOIN_PATH_MULTILINHA_FRAGIL=SIM
USAR_CAMINHOS_DIRETOS_QUANDO_POSSIVEL=SIM
SET_STRICTMODE=SIM
EXECUCAO_NAO_INTERATIVA=OBRIGATORIA
TESTE_POWERSHELL_5_1_REAL=OBRIGATORIO
```

DeverÃ¡ existir teste que rejeite runners que solicitem parÃ¢metros interativos
nÃ£o previstos.

---

## FAB-DEF-003 â€” Base externa reconstruÃ­da com configuraÃ§Ã£o histÃ³rica

```text
DATA=2026-07-23
ETAPA=APLICACAO_CONTROLADA_R2
ARTEFATO_AFETADO=APLICADOR_R2_INICIAL
SINTOMA=CONFIG_VALIDACAO_EXTERNA_DIVERGENTE
ESCRITA_INICIADA=NAO
ESTADO=CONTIDO_NO_ARTEFATO_ABERTO_NA_FABRICA
```

### DescriÃ§Ã£o

A base externa de validaÃ§Ã£o foi reconstruÃ­da a partir de uma coleta anterior Ã 
R1. Como o candidato R2 preservava a configuraÃ§Ã£o e nÃ£o a incluÃ­a em seu ZIP, a
configuraÃ§Ã£o histÃ³rica permaneceu na base externa e divergiu da configuraÃ§Ã£o
fÃ­sica instalada e auditada.

### Impacto

O aplicador parou corretamente antes da escrita, mas a montagem da base de
validaÃ§Ã£o nÃ£o reproduziu o estado real auditado.

### CorreÃ§Ã£o exigida na origem

O gerador de aplicadores deverÃ¡ distinguir explicitamente:

```text
ARQUIVO_MODIFICADO_PELO_CANDIDATO
ARQUIVO_PRESERVADO_DA_BASE_FISICA
ARQUIVO_HISTORICO_DA_COLETA
```

Arquivos preservados deverÃ£o ser copiados da base fÃ­sica somente depois da
validaÃ§Ã£o de seus hashes, sem alteraÃ§Ã£o do TRIN real.

---

## FAB-DEF-004 â€” DicionÃ¡rio Python gerado como elemento de `set`

```text
DATA=2026-07-23
ETAPA=EMISSAO_DE_EVIDENCIAS_POS_APLICACAO
ARTEFATO_AFETADO=APLICADOR_R2_R1C
SINTOMA=cannot_use_dict_as_a_set_element
TESTE_EXTERNO=56_DE_56
TESTE_POS_APLICACAO=56_DE_56
ROLLBACK=APROVADO
ESTADO=CONTIDO_NO_ARTEFATO_ABERTO_NA_FABRICA
```

### DescriÃ§Ã£o

O template gerou uma chamada equivalente a:

```python
write_json(caminho, {{"path": "...", "before": "..."}})
```

As chaves duplicadas transformaram a expressÃ£o em um `set` contendo um
dicionÃ¡rio, causando erro por objeto nÃ£o hashable.

### Impacto

A R2 foi aplicada e passou 56/56 testes no TRIN, mas o aplicador falhou ao
emitir o arquivo de evidÃªncia. O rollback restaurou a R1.

### CorreÃ§Ã£o exigida na origem

O gerador deverÃ¡ rejeitar qualquer bloco Python produzido com chaves de escape
residuais quando o resultado esperado for um dicionÃ¡rio.

DeverÃ¡ haver anÃ¡lise sintÃ¡tica e execuÃ§Ã£o real do caminho de emissÃ£o de
evidÃªncias.

---

## FAB-DEF-005 â€” Hashes internos emitidos como placeholders literais

```text
DATA=2026-07-23
ETAPA=EMISSAO_DE_HASHES_INTERNOS
ARTEFATO_AFETADO=APLICADOR_R2_R1C
SINTOMA=PLACEHOLDER_LITERAL
ESTADO=CONTIDO_NO_ARTEFATO_ABERTO_NA_FABRICA
```

### DescriÃ§Ã£o

O gerador produziu textos literais equivalentes a:

```text
{sha256_file(path)}  {path.relative_to(evidence_root).as_posix()}
```

em vez de avaliar a f-string e registrar o SHA-256 real.

### Impacto

Mesmo que o erro anterior nÃ£o interrompesse a execuÃ§Ã£o, o arquivo de hashes
internos seria invÃ¡lido e nÃ£o serviria como prova de integridade.

### CorreÃ§Ã£o exigida na origem

O emissor deverÃ¡:

```text
CALCULAR_HASH_REAL=SIM
REABRIR_ARQUIVO_DE_HASHES=SIM
RECALCULAR_CADA_MEMBRO=SIM
CONFIRMAR_100_PORCENTO=SIM
BLOQUEAR_CHAVES_LITERAIS=SIM
```

Qualquer ocorrÃªncia residual de padrÃµes como `{sha256_`, `{path.`, `{{` ou `}}`
em artefatos executÃ¡veis ou evidÃªncias deverÃ¡ reprovar a fabricaÃ§Ã£o, salvo
quando explicitamente documentada como texto de exemplo.

---

# 6. Estado dos artefatos TT-01 relacionados

```text
CANDIDATO_TT01_CONTINUIDADE_R2=AUDITADO_E_PRESERVADO
APLICACAO_R2_R1D=CONCLUIDA_COM_SUCESSO
TESTE_EXTERNO=56_DE_56
TESTE_POS_APLICACAO=56_DE_56
TT01_R2_INSTALADA_OFFLINE=SIM
HOMOLOGACAO=NAO
MERCADO_ABERTO_APOS_R2=PENDENTE
```

O sucesso do aplicador R1D Ã© uma contenÃ§Ã£o vÃ¡lida para a frente TT-01, mas nÃ£o
encerra os cinco defeitos registrados na FÃ¡brica.

# 7. Regra de notificaÃ§Ã£o futura

A partir deste documento, todo novo defeito associado Ã  FÃ¡brica deverÃ¡ ser
notificado imediatamente e receber o prÃ³ximo identificador sequencial:

```text
FAB-DEF-006
FAB-DEF-007
FAB-DEF-008
...
```

Cada nova entrada deverÃ¡ conter:

```text
DATA
ETAPA
ARTEFATO_AFETADO
SINTOMA
ERRO_EXATO
CAUSA_RAIZ
RISCO
CONTENCAO_REALIZADA
CORRECAO_EXIGIDA_NA_ORIGEM
EVIDENCIA
ESTADO
```

## Estados permitidos

```text
ABERTO
CONTIDO_NO_ARTEFATO_ABERTO_NA_FABRICA
EM_CORRECAO_NA_ORIGEM
AGUARDANDO_AUDITORIA
ENCERRADO_NA_ORIGEM
```

NÃ£o apagar entradas antigas. AtualizaÃ§Ãµes devem preservar o histÃ³rico e incluir
data, responsÃ¡vel lÃ³gico e evidÃªncia de transiÃ§Ã£o.

# 8. MissÃ£o futura da Guia responsÃ¡vel pela FÃ¡brica

A prÃ³xima Guia que assumir esta frente deverÃ¡:

1. localizar os templates e geradores responsÃ¡veis pelos defeitos 001â€“005;
2. provar quais defeitos compartilham a mesma causa de escape/renderizaÃ§Ã£o;
3. corrigir a origem, nÃ£o apenas os artefatos jÃ¡ gerados;
4. criar uma bateria de testes negativos e end-to-end;
5. fabricar um aplicador de prova em base descartÃ¡vel;
6. executar sucesso completo e falha com rollback;
7. reabrir e validar o ZIP de evidÃªncias;
8. emitir auditoria independente;
9. atualizar este documento sem apagar o histÃ³rico.

```text
FRENTE_CORRECAO_FABRICA=ABERTA_PARA_GUIA_FUTURA
CORRECAO_IMEDIATA_DURANTE_TT01=NAO
TRIN_FUNCIONAL=NAO_MODIFICAR_POR_ESTA_MISSAO
GIT=NAO_AUTORIZADO_POR_ESTE_DOCUMENTO
```

---

# 9. ATUALIZAÃ‡ÃƒO 01 â€” FALHA DE FABRICAÃ‡ÃƒO G0B R1

```text
DATA=2026-07-23
PACOTE_AFETADO=PACOTE_PREPARADOR_WINDOWS_COLETOR_G0B_R1_20260723.zip
PACOTE_SHA256=e59b78d8b0ec3704bfa66b715086446d541bc955a777b538525ecd068aa6544f
RESULTADO=TESTES_PORTATEIS_REPROVADOS
CANDIDATO_FABRICADO=NAO
COLETA_REAL_EXECUTADA=NAO
TRIN_ACESSADO=NAO
GIT_EXECUTADO=NAO
```

## FAB-DEF-006 â€” ProibiÃ§Ã£o textual confundiu Registro com automaÃ§Ã£o COM

```text
ETAPA=FABRICACAO_COLETOR_G0B_R1
ARTEFATO_AFETADO=TESTE_PORTATIL_GERADO
SINTOMA=TESTES_PORTATEIS_REPROVADOS
CAUSA_RAIZ=FALSO_POSITIVO_POR_SUBSTRING
ESTADO=CONTIDO_NO_ARTEFATO_ABERTO_NA_FABRICA
```

O teste proibia a substring `Excel.Application`. O coletor usava
`Excel.Application\CLSID` somente como caminho para leitura do Registro do
Windows. Nenhum objeto COM era instanciado.

```text
LER_PROGID_NO_REGISTRO=PERMITIDO
INSTANCIAR_EXCEL_VIA_COM=PROIBIDO
```

A correÃ§Ã£o na origem deverÃ¡ validar APIs efetivas de automaÃ§Ã£o, como
`Dispatch`, `EnsureDispatch`, `GetActiveObject`, `CreateObject` e
`CoCreateInstance`, sem reprovar um ProgID usado apenas em chave de Registro.

## FAB-DEF-007 â€” DiagnÃ³stico detalhado dos testes foi ocultado

```text
ETAPA=FABRICACAO_COLETOR_G0B_R1
ARTEFATO_AFETADO=FABRICADOR_WINDOWS
SINTOMA=ERRO_GENERICO_SEM_TESTE_CAUSADOR
CAUSA_RAIZ=SAIDA_CAPTURADA_MAS_NAO_EMITIDA
ESTADO=CONTIDO_NO_ARTEFATO_ABERTO_NA_FABRICA
```

O fabricador capturou `stdout` e `stderr`, mas lanÃ§ou somente
`TESTES_PORTATEIS_REPROVADOS`. O terminal nÃ£o mostrou qual teste falhou.

Antes de abortar, todo fabricador deverÃ¡ imprimir o relatÃ³rio completo,
preservar um arquivo de log e informar o teste causador.

## Estado apÃ³s a atualizaÃ§Ã£o

```text
FAB_DEF_001_A_007=ABERTOS_NA_ORIGEM
PREPARADOR_G0B_R1=REPROVADO
PREPARADOR_G0B_R1C=CONTENCAO_LOCALIZADA
CANDIDATO_G0B=AINDA_NAO_FABRICADO
PROXIMO_IDENTIFICADOR=FAB-DEF-008
```

---

# 10. ATUALIZAÃ‡ÃƒO 02 â€” AUDITORIA DO CANDIDATO G0B R1

```text
DATA=2026-07-23
CANDIDATO=COLETOR_G0B_R1_CANDIDATO_WINDOWS.zip
CANDIDATO_SHA256=5a2cb68b83d37bf6ff575ab17b61170a961d5c3bfadeba7bdbbc56ccbb69b2b9
EVIDENCIAS=EVIDENCIAS_FABRICACAO_COLETOR_G0B_R1_WINDOWS.zip
EVIDENCIAS_SHA256=1a8340d4c7548892dff83e32e1b19b9e907da7af260c9fa9f2025141c230a771
AUDITORIA=REPROVADA_PARA_COLETA_REAL
COLETA_REAL_EXECUTADA=NAO
```

## FAB-DEF-008 â€” Lista fÃ­sica de membros incompleta

```text
ZIP_MEMBROS=9
LISTA_EXATA_ENTRADAS=7
ESTADO=ABERTO
```

`LISTA_EXATA_MEMBROS.txt` nÃ£o inclui a prÃ³pria lista nem
`SHA256_ARQUIVOS.txt`. A FÃ¡brica deve emitir uma enumeraÃ§Ã£o fÃ­sica integral e
validÃ¡-la contra o ZIP final.

## FAB-DEF-009 â€” Hashes internos sem recÃ¡lculo pÃ³s-empacotamento

O coletor reabre o ZIP somente para `testzip()`. Deve recalcular os SHA-256 dos
membros empacotados e comparar 100% com o arquivo de hashes.

## FAB-DEF-010 â€” Erros do Registro convertidos em falso sucesso

`OSError` Ã© transformado em ausÃªncia silenciosa e o resultado declara os
inventÃ¡rios concluÃ­dos incondicionalmente. A origem deve diferenciar ausÃªncia,
acesso negado, erro, interrupÃ§Ã£o e truncamento.

## FAB-DEF-011 â€” Snapshot de processos sem contrato ctypes e sem falha fechada

As funÃ§Ãµes WinAPI nÃ£o tÃªm `argtypes/restype` e falha de `Process32FirstW` pode
resultar em lista vazia. A origem deve tipar as APIs e registrar o erro exato.

## FAB-DEF-012 â€” Caminho de falha sem ZIP de evidÃªncias

ExceÃ§Ãµes nÃ£o produzem evidÃªncia auditÃ¡vel. A origem deve empacotar resultado de
falha, etapa, erro, arquivos parciais, hashes e declaraÃ§Ã£o de nÃ£o interferÃªncia.

## Estado apÃ³s a atualizaÃ§Ã£o

```text
FAB_DEF_001_A_012=ABERTOS_NA_ORIGEM
G0B_R1=REPROVADO_PARA_COLETA_REAL
G0B_R1C=CORRECAO_LOCALIZADA_PENDENTE
PROXIMO_IDENTIFICADOR=FAB-DEF-013
```

---

# 11. ATUALIZAÃ‡ÃƒO 03 â€” AUDITORIA DO CANDIDATO G0B R1C

```text
DATA=2026-07-23
CANDIDATO=COLETOR_G0B_R1C_CANDIDATO_WINDOWS.zip
CANDIDATO_SHA256=e4808ca7d0bfd6fa8d880431bfabdb74b181dafd9c803aaae54a2f1f02073f48
EVIDENCIAS=EVIDENCIAS_FABRICACAO_COLETOR_G0B_R1C_WINDOWS.zip
EVIDENCIAS_SHA256=b900ee2c70e7b3ce6d11e4d857cf9fa6759777c6650dbc78d4d227a254864a09
CORRECOES_FAB_DEF_008_A_012=APROVADAS
AUDITORIA_FINAL=REPROVADA_PARA_COLETA_REAL
COLETA_REAL_EXECUTADA=NAO
```

## FAB-DEF-013 â€” ValidaÃ§Ã£o fÃ­sica embutida pertence ao ZIP anterior

O arquivo `VALIDACAO_ZIP_EMITIDO.json` Ã© produzido apÃ³s validar o primeiro ZIP.
Em seguida, o ZIP Ã© recriado contendo esse arquivo, mas o registro nÃ£o Ã©
atualizado com os nÃºmeros do artefato final.

```text
PRIMEIRO_ZIP=11_MEMBROS_E_10_HASHES
ZIP_FINAL=12_MEMBROS_E_11_HASHES
REGISTRO_EMBUTIDO=OBSOLETO
ESTADO=ABERTO
```

## FAB-DEF-014 â€” RaÃ­zes do workbook podem ser omitidas sem evidÃªncia

RaÃ­zes configuradas que nÃ£o passam por `is_dir()` sÃ£o ignoradas. A coleta pode
declarar busca completa com lista de raÃ­zes inspecionadas vazia e sem erro.

A origem deverÃ¡ registrar cada raiz e distinguir ausÃªncia, acesso negado, erro
e exclusÃ£o por polÃ­tica.

## FAB-DEF-015 â€” ReferÃªncia LocalServer32 nÃ£o Ã© analisada como linha de comando

O valor completo Ã© tratado como caminho apÃ³s simples remoÃ§Ã£o de aspas. Valores
com argumentos podem apontar para um executÃ¡vel existente e ainda serem
registrados incorretamente.

O estado do arquivo fÃ­sico referenciado tambÃ©m deverÃ¡ participar da completude
do inventÃ¡rio RTD/COM.

## Estado apÃ³s a atualizaÃ§Ã£o

```text
FAB_DEF_001_A_015=ABERTOS_NA_ORIGEM
G0B_R1C=REPROVADO_PARA_COLETA_REAL
G0B_R1D=CORRECAO_LOCALIZADA_PENDENTE
PROXIMO_IDENTIFICADOR=FAB-DEF-016
```

---

# 12. ATUALIZAÃ‡ÃƒO 04 â€” FALHA DO PREPARADOR G0B R1D

```text
DATA=2026-07-23
PACOTE_AFETADO=PACOTE_PREPARADOR_WINDOWS_CANDIDATO_COLETOR_G0B_R1D_20260723.zip
PACOTE_SHA256=f910849f00e761a4ca2521f93eee7a97aac4c45d1f6329acf9cad5613948de58
ETAPA_FALHA=PATCH_SOURCE
ERRO=NameError: name 'ast' is not defined
CANDIDATO_R1D_FABRICADO=NAO
COLETA_REAL_EXECUTADA=NAO
TRIN_ACESSADO=NAO
GIT_EXECUTADO=NAO
```

## FAB-DEF-016 â€” DependÃªncia de execuÃ§Ã£o ausente no preparador

O preparador utilizava `ast.parse(source)` sem importar o mÃ³dulo `ast`.

A validaÃ§Ã£o de sintaxe externa aprovou o arquivo, mas nÃ£o executou o caminho
real onde o nome era resolvido. Portanto, a FÃ¡brica comprovou novamente que
compilaÃ§Ã£o isolada nÃ£o substitui preflight de execuÃ§Ã£o.

### CorreÃ§Ã£o exigida na origem

```text
VALIDAR_IMPORTS_RUNTIME=SIM
EXECUTAR_PREFLIGHT_DAS_DEPENDENCIAS=SIM
BLOQUEAR_NOMES_GLOBAIS_AUSENTES=SIM
TESTAR_O_CAMINHO_DE_PATCH_ANTES_DO_WINDOWS=SIM
```

## ContenÃ§Ã£o

```text
PREPARADOR_R1D_R1C=EMITIDO
IMPORT_AST=ADICIONADO
PREFLIGHT_AST=ADICIONADO
CANDIDATO_R1D=AINDA_NAO_FABRICADO
```

## Estado apÃ³s a atualizaÃ§Ã£o

```text
FAB_DEF_001_A_016=ABERTOS_NA_ORIGEM
G0B_R1D=FABRICACAO_PENDENTE
PROXIMO_IDENTIFICADOR=FAB-DEF-017
```

---

# 13. ATUALIZAÃ‡ÃƒO 05 â€” AUDITORIA DO PREPARADOR G0B R1D R1C

```text
DATA=2026-07-23
PACOTE_AFETADO=PACOTE_PREPARADOR_WINDOWS_CANDIDATO_COLETOR_G0B_R1D_R1C_20260723.zip
PACOTE_SHA256=a0b83fb2f2f54d7421ce9c73966dc2faf600111f6b012acda30796eb37442f04
ETAPA_FALHA=RUNNER_FILE_RESOLUTION
CANDIDATO_R1D_FABRICADO=NAO
COLETA_REAL_EXECUTADA=NAO
TRIN_ACESSADO=NAO
GIT_EXECUTADO=NAO
```

## FAB-DEF-017 â€” RenomeaÃ§Ã£o sobreposta duplicou a revisÃ£o no runner

O pacote contÃ©m:

```text
FABRICAR_CANDIDATO_COLETOR_G0B_R1D_R1C_WINDOWS.py
```

O runner procura:

```text
FABRICAR_CANDIDATO_COLETOR_G0B_R1D_R1C_R1C_WINDOWS.py
```

A causa raiz foi reconstruÃ­da como duas substituiÃ§Ãµes sucessivas e
sobrepostas. A substituiÃ§Ã£o ampla voltou a atuar sobre o nome jÃ¡ corrigido e
duplicou `_R1C`.

### Falha de controle associada

O pacote validou integridade, lista, hashes e sintaxe Python, mas nÃ£o verificou
a coerÃªncia cruzada entre o caminho declarado em `$Fabricador` e os membros
fÃ­sicos do ZIP.

### CorreÃ§Ã£o exigida na origem

```text
RENOMEACOES_IDEMPOTENTES=SIM
SUBSTITUICOES_SOBREPOSTAS=PROIBIDAS
VALIDAR_REFERENCIAS_RUNNER_CONTRA_ZIP=SIM
EXIGIR_UM_UNICO_FABRICADOR=SIM
BLOQUEAR_SUFIXO_DE_REVISAO_DUPLICADO=SIM
EXECUTAR_DRY_RUN_DE_RESOLUCAO_DO_RUNNER=SIM
```

## Estado apÃ³s a atualizaÃ§Ã£o

```text
FAB_DEF_001_A_017=ABERTOS_NA_ORIGEM
G0B_R1D=AINDA_NAO_FABRICADO
CORRECAO_RECOMENDADA=UMA_LINHA_NO_RUNNER_EXISTENTE
NOVA_PILHA_DE_REVISOES=PROIBIDA
PROXIMO_IDENTIFICADOR=FAB-DEF-018
```

---

# ATUALIZAÃ‡ÃƒO 06 â€” ENCERRAMENTO DA F0 DE LOCALIZAÃ‡ÃƒO DA ORIGEM

```text
DATA=2026-07-26
OBJETO=F0_LOCALIZACAO_ORIGEM_FAB_DEF_019_A_026
PACOTE_R1F_SHA256=4cfbe61a97839581f5e60a7829ad564bd2a8d39f06342dd12f3f7f276509616b
EVIDENCIAS_R1F_SHA256=247b3c5ab91c1c6f788b8f1d336554d0b77edac09482600057401d0e26e86967
PARECER_INDEPENDENTE_SHA256=31e29180de181abfe4d510e40fdd2fd6c2e3e7896fcc8d920a0c1001b7b57f1e
DECISAO=F0_APROVADA_E_ENCERRADA
```

## Resultado da localizaÃ§Ã£o

```text
FONTES_BYTE_EXATAS=112
HASHES_RECALCULADOS=112
COMPONENT_INSTANCE_ID_UNICOS=112
REFERENCIAS_RESOLVIDAS=119
REFERENCIAS_AMBIGUAS=0
REFERENCIAS_NAO_RESOLVIDAS=0
MATRIZ_RECONCILIADA=154
MATRIZ_FINAL_ORIGENS=40
FAB_DEF_025_CONSUMIDOR_PRESENTE=SIM
ZERO_MODIFICACOES=APROVADO_NO_MODELO_PROBATORIO_DA_F0
ZERO_EXECUCOES_COMPONENTES=SIM
ZERO_TRIN=SIM
ZERO_GIT=SIM
```

## Estado institucional

```text
F0_LOCALIZACAO=ENCERRADA
FAB_DEF_019_A_026=CAUSA_RAIZ_LOCALIZADA
CORRECAO_NA_ORIGEM=NAO_EXECUTADA
DEFEITOS_ENCERRADOS=NAO
```

## Origens confirmadas

```text
FAB-DEF-019=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/avaliador_semantico.py
FAB-DEF-020=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/carregador_autoridades.py
FAB-DEF-021=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/executor_testes_materializados.py
FAB-DEF-022=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/corretor_tecnico_controlado.py
FAB-DEF-023=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/gerador_delta_exato.py
FAB-DEF-024=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/hashes_io.py
FAB-DEF-025=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/preflight_isolamento.py
FAB-DEF-026=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/hashes_io.py
```

Os caminhos, hashes, identidades, papÃ©is e provas completos constam em
`03_MATRIZ_40_PAPEIS_CONFIRMADOS_R1F.csv`.

## PrÃ³ximo identificador

```text
PROXIMO_IDENTIFICADOR=FAB-DEF-027
```

Esta indicaÃ§Ã£o nÃ£o encerra nem corrige os defeitos 019â€“026.

# ANEXO A â€” MATRIZ DOS 40 PAPÃ‰IS CONFIRMADOS NA R1F

A matriz abaixo Ã© anexada sem alteraÃ§Ã£o de conteÃºdo e conserva caminhos, hashes, identidades, sÃ­mbolos e provas aprovados.

```csv
fab_def;dominio;papel;caminho_relativo;content_sha256;component_instance_id;simbolos;provas;origem_confirmada_guia3;estado
FAB-DEF-019;preflight_semantico;ORIGEM;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/avaliador_semantico.py;32aea7c773d60316de689a06c0229df443af3e4b1a2e7e9c650d7c2fec3f5a09;CI-3227203f51401f9bc41a11a706c794cb569256f7c40315bcf6ce864ec6a7e146;_get|_proof_consistent|_same_artifact|evaluate_envelope|fail;83:evaluate_envelope;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-019;preflight_semantico;GERADOR_TEMPLATE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/03_TEMPLATES/MODELO_AVALIADOR_SEMANTICO_FAB01_A_V1.json;f7f35545e9541452d0a1577dd6d826a420ab84da7733baf5d2e9b0c6663fe326;CI-33456dda2391b0e424d3dbfa9173dc80e16b70d08019b67dabd4676daf5aa0e8;;257:schema_version;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-019;preflight_semantico;VALIDADOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/01_CONTRATOS/AVALIADOR_SEMANTICO_FAB01_A_V1.schema.json;36c90a643a628ae705efa59e6954200aa8f713d67842ac2f782c6d5d6e576a68;CI-aa9112c8326b8cdd0f529cf6aa5ee0a87b6519276311178a1bb2234f2ddaff7f;;3:$schema;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-019;preflight_semantico;TESTE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/07_TESTES/test_avaliador_semantico.py;41aa32e15cb76c15b2c4ddfa62bd69d646b4edf81daa8ab5e67cc925bf7f8eb2;CI-31bca147e6dcbeb0f17449d0c129d664bbd87b012324b2cefceda1a3a1f1758f;SemanticTests|envelope|test_ext_01_estado_arbitrario|test_ext_04_child_igual_source|test_ext_05_parent_incorreto|test_ext_06_snapshot_alterado|test_ext_07_teste_alvo_ficticio|test_ext_08_contadores_contraditorios|test_ext_15_job_igual_parent|test_r2_avaliacao_limpa_aprova|test_r2_avaliacao_preserva_entrada|test_r2_avaliacao_regras_materializadas;66:SemanticTests;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-019;preflight_semantico;CONSUMIDOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/motor_sidecar.py;26e2e59dbad74e11dc922270e3cc41309a269acfa97f9c31faabe7211453c508;CI-351c6714fdff5176ea1e3b3217743cacd026e8ac7055d57f2a4588457aa2ca2d;SidecarEngine|__init__|_base_output|_child_job_id|_replace|process;8:evaluate_envelope|199:evaluate_envelope;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-020;congelamento_entradas;ORIGEM;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/carregador_autoridades.py;35ac67d724c9a4da3ff6d03b47e88469fd280e4a99946f648464b0d589d2fd10;CI-cc4a38a5a58c3ef0c9561e7167740d2a684773fc15fc0c3c5fabbb83b33a0682;AuthorityLoader|__init__|canonical_state_values|installed_authority_manifest|load_contract|load_installed_authority|require_canonical_state|require_hash|require_valid|validate_model|validator|verify_installed_authorities;17:AuthorityLoader|25:require_hash|46:require_hash;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-020;congelamento_entradas;GERADOR_TEMPLATE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/03_TEMPLATES/MODELO_POLITICA_CORRECAO_TECNICA_CONTROLADA_FAB01_V1.json;fd6ca93fb761ac57a69534253ce3074c0efa0d7d766a55bc5a42018f9aaf967a;CI-cac8eff34f8f287ca5f5249299d781c4d1f45ad3e8cced201159fc8bfebe8b43;;77:schema_version;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-020;congelamento_entradas;VALIDADOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/01_CONTRATOS/POLITICA_CORRECAO_TECNICA_CONTROLADA_FAB01_V1.schema.json;238f36eb2756c6062d7294f944515ebd501dd3ec24dd166d2e948a858e2900be;CI-3be815f6b4b878396782dbe7ee9a010bae3754803c61a3d56ac0e05b7380753d;;3:$schema;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-020;congelamento_entradas;TESTE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/07_TESTES/test_carregador_autoridades.py;296674873390cb5a3444ac4eca2da8b7709f246c27024ab076fd4b85b9221388;CI-f87f9bf38aa771c3256333a228750484eeae0c8d31978817475a0e932530dee2;AuthorityTests|test_r2_autoridade_hash_divergente_bloqueia|test_r2_autoridade_hash_exato;18:test_r2_autoridade_hash_exato;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-020;congelamento_entradas;CONSUMIDOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/motor_sidecar.py;26e2e59dbad74e11dc922270e3cc41309a269acfa97f9c31faabe7211453c508;CI-351c6714fdff5176ea1e3b3217743cacd026e8ac7055d57f2a4588457aa2ca2d;SidecarEngine|__init__|_base_output|_child_job_id|_replace|process;9:AuthorityLoader|26:AuthorityLoader;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-021;vetores_adversariais;ORIGEM;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/executor_testes_materializados.py;b3148d7817076c0f9a2318e8929370c94fa7941aed0b79ea07eb3be00662f480;CI-d7794ed2439e7d9117f16c447a310ec2e29d44812b6c4a2eeccbcacf78c148c1;_artifact|materialize_test_result;25:materialize_test_result;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-021;vetores_adversariais;GERADOR_TEMPLATE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/03_TEMPLATES/MODELO_RESULTADO_TESTE_ALVO_FAB01_V1.json;1dea1ada874647276f194d82a6a5c9550bc7a926560e460406810e133f46a365;CI-366a2d5d0d5a01fbabda99a0c7896f9c18c663ebef107bb97df721b721cc533d;;24:schema_version;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-021;vetores_adversariais;VALIDADOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/01_CONTRATOS/RESULTADO_TESTE_MATERIALIZADO_FAB01_V1.schema.json;916321cca5da3dac4bee023ff18df0e44c9016f589906e9de3167d74a4779a44;CI-e1159fb32aa7419917442d2e4b3f559b577de0f2f9b18577d47d49e2ae716188;;3:$schema;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-021;vetores_adversariais;TESTE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/07_TESTES/test_executor_testes_materializados.py;7d00a883347dac8f91c1540b2d0acbf47b90d41c1cc8b4490cfb6f4aaf42ad63;CI-14497f713d24f804eddba3221975240a3e265e4fc99661d7ab613486935f9445;ExecutorTests|test_r2_resultado_sem_artefato_bloqueia|test_r2_resultado_teste_materializado;18:test_r2_resultado_teste_materializado;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-021;vetores_adversariais;CONSUMIDOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/07_TESTES/VALIDAR_WINDOWS_FAB01_B_R2.py;b2ac31e8825f06868fafb8e60f1412edc0020df84bd129b98ea7aa51145153d7;CI-29c463e415b6066a2b25b0e5bf389451994e3e0a65bc2f2616d7a934d2e23ac2;assert_operational_runtime_without_compatibility_bypass|clean_env|main|materialize_frozen_test_tree|run_r1d|run_suite_subprocess|safe_adapter_member|sha256_bytes;418:run_suite_subprocess|614:run_suite_subprocess|620:run_suite_subprocess|627:run_suite_subprocess;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-022;e2e_idempotencia;ORIGEM;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/corretor_tecnico_controlado.py;001904781a2b5cba9b8d36bf8f3991c5b1e2ca88577653a44728ad3a40b4e1da;CI-a85f20ed074375b970eef1133eda979e1888382dda3b5fe82bc515e3b32bb00f;CorrectionPlanner|__init__|_child_job_id|plan|validate_policy;15:CorrectionPlanner;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-022;e2e_idempotencia;GERADOR_TEMPLATE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/03_TEMPLATES/MODELO_REGISTRO_CICLO_REPARO_TECNICO_FAB01_V1.json;24ccd2d847197d650ddb232442f14e13cecb6fbb5014e4d7b027fd5bbd0d286f;CI-52ebc1e59349a88b122b619ec601dd6fe5dcf60a76135ab8ca79ea8f03d51579;;67:schema_version|104:schema_version|131:schema_version;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-022;e2e_idempotencia;VALIDADOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/01_CONTRATOS/REGISTRO_CICLO_REPARO_TECNICO_FAB01_V1.schema.json;9629d40b9dc8b338476709a5193b7626381da61676b9c86e2a6523fe242fb540;CI-4ef688888de376c1287afdefc7f8820a66d6cbcd9dce28329a420128d421e158;;3:$schema;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-022;e2e_idempotencia;TESTE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/07_TESTES/test_corretor_tecnico_controlado.py;285b1a82e500eafb0a10fbceffed991e90c03e947a6b975a5eab735704bbc838;CI-0c5f29272968fe46b76d53302881fe8a0f25f94e2333466b96e83736b453d005;CorrectionTests|policy|test_ext_11_politica_sem_proibicoes_bloqueia|test_ext_12_tipos_reparo_divergentes|test_ext_13_classe_e_reparo_local_bloqueia|test_ext_14_classe_a_sem_fonte_canonica_bloqueia|test_r2_correcao_cria_job_filho_e_staging|test_r2_correcao_terceiro_ciclo_bloqueia;35:test_r2_correcao_cria_job_filho_e_staging;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-022;e2e_idempotencia;CONSUMIDOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/motor_sidecar.py;26e2e59dbad74e11dc922270e3cc41309a269acfa97f9c31faabe7211453c508;CI-351c6714fdff5176ea1e3b3217743cacd026e8ac7055d57f2a4588457aa2ca2d;SidecarEngine|__init__|_base_output|_child_job_id|_replace|process;15:SidecarEngine|41:SidecarEngine|43:SidecarEngine;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-023;nao_mutacao;ORIGEM;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/gerador_delta_exato.py;c92c501eac5f7523234ba82e65b5ed9f6877fa06c49bc861475a27320d26fed9;CI-38fd2d0191eeca28c50916fbc5a761a79341f958139fb1998ea6de66254fd137;validate_exact_delta;4:validate_exact_delta;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-023;nao_mutacao;GERADOR_TEMPLATE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/03_TEMPLATES/MODELO_PROVA_ESTADO_CANONICO_FAB01_V1.json;07fa305736a0208f0ed3b82dd756a0741595da0a702f2f210d47f07cfd81ca05;CI-c67c4cabc108e010439ffe2b293e9d11bfb1935409af44e8a1bf86d2cb8acacb;;30:schema_version;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-023;nao_mutacao;VALIDADOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/01_CONTRATOS/PROVA_ESTADO_CANONICO_FAB01_V1.schema.json;8b4df8fdaa04c1343078f0e45c940ed263908719732dadb28ced3c7a2acb0abf;CI-f29e944cbb0c81656884b8963236faad76f37f0697606e190a78abe097eff1cd;;3:$schema;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-023;nao_mutacao;TESTE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/07_TESTES/test_gerador_delta_exato.py;25773644d9a4506dd5fbc770911d24f3eccfc26412db1cf1cd54433068df434b;CI-2ecd7e3bdeb878e50356b3d93fe58742aec039e7de6f1d45b60cc30cfd3a3ed6;DeltaTests|test_r2_delta_colisao_bloqueia|test_r2_delta_exato_aprova;18:test_r2_delta_exato_aprova;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-023;nao_mutacao;CONSUMIDOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/motor_sidecar.py;26e2e59dbad74e11dc922270e3cc41309a269acfa97f9c31faabe7211453c508;CI-351c6714fdff5176ea1e3b3217743cacd026e8ac7055d57f2a4588457aa2ca2d;SidecarEngine|__init__|_base_output|_child_job_id|_replace|process;67:process;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-024;seguranca_caminhos;ORIGEM;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/hashes_io.py;f9e2398feec2cdd89f00369d201d9e9c42f60819de549aa543f98faa040eb769;CI-d8be7546e4b1f331fa63f7bd31071f46f4a031206c12007928ed6dc2b4ee11d5;assert_windows_compatible_path|canonical_json_bytes|deterministic_zip|load_json|normalize_windows_path|path_is_within|safe_relative_path|sha256_bytes|sha256_file|write_json|write_text;62:safe_relative_path|79:path_is_within;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-024;seguranca_caminhos;GERADOR_TEMPLATE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/03_TEMPLATES/MODELO_COMANDO_INTENCIONADO_GUARDA_FAB01_V1.json;def9090869425d18c170ffb0f8fb4d0105fd21989d1b689243920a7ad2e3ef5a;CI-0fdec9322de497730431fa6b5fea26c7353bd17cf04a29a6771fa9d1b469c205;;90:schema_version;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-024;seguranca_caminhos;VALIDADOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/01_CONTRATOS/COMANDO_INTENCIONADO_GUARDA_FAB01_V1.schema.json;ac4ecbeedb07abba625643cdc90dec4542326ad89fa6da5f116d2fbd60514927;CI-96c7f4a12623866c014e0b423e459c5dea4713cd3cae94aaef2b9bc58da3932c;;3:$schema;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-024;seguranca_caminhos;TESTE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/07_TESTES/test_cli.py;7735e09620ac0238ac5c680cfdcb9a45953e82c0e1b169084d24157c9ce26d54;CI-64077cdb4c89d121108d6a1a20e139765835d3d8de59ab7aadfdd985dd2a3574;CliTests|test_r2_cli_produz_saida|test_r2_cli_saida_sem_autorizacao_operacional;17:CliTests;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-024;seguranca_caminhos;CONSUMIDOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/cli.py;d96a7fc72e351688ee9d84d7eb40bb70ab123601ab8b1215db262567169fdf39;CI-485f665bbf20e2e148b51ac737d1b4c6c93603f394ac0a3487ad7e136692702a;main|validate_cli_path_before_io;12:validate_cli_path_before_io|34:validate_cli_path_before_io|39:validate_cli_path_before_io|49:validate_cli_path_before_io;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-025;preflight_persistido;ORIGEM;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/preflight_isolamento.py;0cdbd889f58355c3cd9573a97f8cb98c455d47a79e92dbdc43383e58d0abc055;CI-09755075c9f4797e749950cb00c890de6d3dac33757d5d7dd63efcb9e41e6f37;_artifact|_is_exact_job_root|require_isolation|validate_canonical_preflight|validate_isolation;28:validate_canonical_preflight;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-025;preflight_persistido;GERADOR_TEMPLATE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/03_TEMPLATES/MODELO_PREFLIGHT_ISOLAMENTO_FAB01_V1.json;d56b447a59aa22613234b9ede96551a08754db34058f04a3059590ea532e1dff;CI-4c7773e6ddbdd3e1a82e6993bd4f6329b7cdc3b7935c7e6f7a3a4cf2e28c0b2c;;20:schema_version;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-025;preflight_persistido;VALIDADOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/01_CONTRATOS/PREFLIGHT_ISOLAMENTO_FAB01_V1.schema.json;b4eeeddc01b584fd6821d4603a93864522987e7c05f606e852ada00f1c712b12;CI-63c25f6452674a4e8169c8bf321e8a1f00e8ce9155fc88474762ad97e01a42c6;;3:$schema;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-025;preflight_persistido;TESTE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/07_TESTES/test_preflight_isolamento.py;957cd39a33c21f3ddb4fa044018156c761a69473dc7ca557a23be0524aef775e;CI-9f29303ac71a3b9c4c34b03b506698d3eb3dc4475f28398de6170915b67f80aa;PreflightTests|test_ext_02_staging_dentro_origem|test_ext_03_output_dentro_origem|test_ext_16_staging_reutilizado|test_r2_preflight_raiz_protegida_bloqueia|test_r2_preflight_raizes_isoladas;17:PreflightTests;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-025;preflight_persistido;CONSUMIDOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/motor_sidecar.py;26e2e59dbad74e11dc922270e3cc41309a269acfa97f9c31faabe7211453c508;CI-351c6714fdff5176ea1e3b3217743cacd026e8ac7055d57f2a4588457aa2ca2d;SidecarEngine|__init__|_base_output|_child_job_id|_replace|process;12:validate_canonical_preflight|95:validate_canonical_preflight|143:preflight_registry;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-026;selagem_evidencias;ORIGEM;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/hashes_io.py;f9e2398feec2cdd89f00369d201d9e9c42f60819de549aa543f98faa040eb769;CI-d8be7546e4b1f331fa63f7bd31071f46f4a031206c12007928ed6dc2b4ee11d5;assert_windows_compatible_path|canonical_json_bytes|deterministic_zip|load_json|normalize_windows_path|path_is_within|safe_relative_path|sha256_bytes|sha256_file|write_json|write_text;101:deterministic_zip|23:sha256_file|133:sha256_file;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-026;selagem_evidencias;GERADOR_TEMPLATE;10_BIN/AUDITAR_PACOTE_TRIN_V0_1.py;091f81d0974927d80a22f87b121e6e1200bdcbdab8c7d6b88b1a80a3b6da83a3;CI-f99f9dad56dac08aee51af4f41cf5ee393b77e7830af543d8febfbf37f505ae6;AuditoriaError|audit_manifest|audit_zip|decode_text|main|parse_sha_file|safe_zip_name|sha256_bytes|sha256_file|write_report;9:zipfile|234:zipfile;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-026;selagem_evidencias;VALIDADOR;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/07_TESTES/AUDITAR_CANDIDATO_FAB01_B_R2.py;99e12139fe2b5bb6d5c67ba011fce09cec37ecc658009720a261435646a582f1;CI-98585b4edff36d997eefd433690598edc27c6e14a7052071eb8b487e4f7d286f;main|parse_hash_index|sha_file;24:parse_hash_index|71:parse_hash_index;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-026;selagem_evidencias;TESTE;15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/07_TESTES/test_hashes_io.py;df8488af176377af374c1bf3a033fce5ae2772cd9aac2a6d38407fd8294ccb50;CI-a30f2f8f0eef99150ea69808c3bbe83577a1cef14a090ca60e3e6045b7c2ef07;HashesIoTests|test_r2_hashes_caminho_relativo_seguro|test_r2_hashes_zip_deterministico;18:test_r2_hashes_zip_deterministico;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
FAB-DEF-026;selagem_evidencias;CONSUMIDOR;15_FABRICA_CANDIDATOS/10_BIN/COMPILAR_INTENCAO_TRIN_V0_1.py;e1f4da9f74981256d0d3029b2ee0dd72f91d93f2e5214cf786170f50f6ae09ef;CI-974ddbd40ce46647a06180c40a805e10558e42e54e291a83940156aa329fba59;CommandResult|FactoryError|apply_operations|apply_overlays|build_candidate|changed_files|compile_all_python|compile_intention|ensure_windows_environment|execute_test|execute_tests|export_base|git|inventory|locate_contract|log_result|main|memory_identity|parse_all_json|parse_all_powershell|parse_sha_file|repository_inventory|require_nonempty|resolve_test_python|restore_exact_git_blobs|run|safe_extract|safe_member|scan_intention|sha256_bytes|sha256_file|slug|tree_hash|validate_contract|validate_rel_path|verify_repository;1238:build_candidate|1503:build_candidate;SIM;AGUARDANDO_AUDITORIA_INDEPENDENTE
```

# ESTADO DE SAÃDA DA REVISÃƒO R7

```text
EMITIDO_EM=2026-07-26T14:58:34-03:00
REGISTRO_VIVO_REVISAO=R7
R6_PRESERVADA_BYTE_EXATA=SIM
R6_SHA256=22a88610bbe0bdddaec1b7e3042b7cc02551cd089181f8e1efe03530da414efc
F0_LOCALIZACAO=APROVADA_E_ENCERRADA
FAB_DEF_019_A_026=CAUSA_RAIZ_LOCALIZADA
CORRECAO_APLICADA_NA_ORIGEM=NAO
TESTES_DE_REGRESSAO_DA_CORRECAO=NAO
DEFEITOS_ENCERRADOS=NAO
FAB_DEF_018_ALTERADO=NAO
F0_DOCUMENTALMENTE_REGISTRADA=SIM
PROXIMO_PORTAO_DOCUMENTAL=VERIFICACAO_DOCUMENTAL_INDEPENDENTE_DA_R7_E_DO_TERMO
PROXIMA_MISSAO_APOS_APROVACAO=DESENHO_CONTROLADO_DO_BLOCO_I_SOB_NOVA_MISSAO
TRIN=NAO
GIT=NAO
PATCH=NAO
```
---

<!-- TRIN_FABRICA_ENCERRAMENTO_DOCUMENTAL_BLOCO_I_20260727 -->

# ATUALIZAÇÃO 07 — ENCERRAMENTO NA ORIGEM DO BLOCO I

~~~text
DATA_HORA=2026-07-27T03:01:57-03:00
FUSO_HORARIO=America/Sao_Paulo
OBJETO=FAB_DEF_019_020_025
PARECER_APLICACAO_REAL_SHA256=634cf18499fd362ee8330ae33e414f9b27fceec3c55d16c3cad86b1a8f05b77d
EVIDENCIAS_APLICACAO_REAL_SHA256=e1f00e972114a260195e720bfcca28266f7056ea5d0dfb1bff07033ac81f5039
PACOTE_ROLLBACK_SHA256=b65b62cf71051ca8d288d1171f9c755dfb178677f855ba921d1118c76be96a16
RETORNO_AUDITORIA_SHA256=70de9f9a84017d3906ac6c2169d857730e16346d6d27721d79a91f35667972e2
~~~

## Provas comuns de encerramento

~~~text
GERADOR_OU_TEMPLATE_LOCALIZADO=SIM
CAUSA_RAIZ_CONFIRMADA=SIM
CORRECAO_APLICADA_NA_ORIGEM=SIM
TESTE_DE_REGRESSAO_ADICIONADO=SIM
CICLO_END_TO_END_DESCARTAVEL=APROVADO
EMISSAO_REAL_DE_EVIDENCIAS=APROVADA
ZIP_REABERTO_E_VALIDADO=SIM
HASHES_INTERNOS_RECALCULADOS_E_CONFERIDOS=SIM
CAMINHO_DE_ROLLBACK_TESTADO=SIM_EM_BASE_DESCARTAVEL
ROLLBACK_REAL=DISPONIVEL_NAO_EXECUTADO
AUDITORIA_INDEPENDENTE=APROVADA_1156_DE_1156
~~~

## FAB-DEF-019 — domínio preflight_semantico

~~~text
ORIGEM=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/avaliador_semantico.py
ESTADO_ANTERIOR=CAUSA_RAIZ_LOCALIZADA
ESTADO_ATUAL=ENCERRADO_NA_ORIGEM
~~~

## FAB-DEF-020 — domínio congelamento_entradas

~~~text
ORIGEM=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/carregador_autoridades.py
ESTADO_ANTERIOR=CAUSA_RAIZ_LOCALIZADA
ESTADO_ATUAL=ENCERRADO_NA_ORIGEM
~~~

## FAB-DEF-025 — domínio preflight_isolamento

~~~text
ORIGEM=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/preflight_isolamento.py
CONSUMIDOR=15_FABRICA_CANDIDATOS/13_NUCLEO_ANTIVICIOS_FAB01_B/06_BIN/fab01_b/motor_sidecar.py
ESTADO_ANTERIOR=CAUSA_RAIZ_LOCALIZADA
ESTADO_ATUAL=ENCERRADO_NA_ORIGEM
~~~

## Estado dos demais defeitos da mesma F0

~~~text
FAB_DEF_021_022_023_024_026=ABERTOS_COM_CAUSA_RAIZ_LOCALIZADA
FAB_DEF_019_A_026_ENCERRADOS=PARCIAL_3_DE_8
PROXIMO_IDENTIFICADOR=FAB-DEF-027
~~~

## Limites

~~~text
TRIN_FUNCIONAL=NAO_ACESSADO
GIT_ESCRITA=NAO
BLOCO_II=NAO_ABERTO
PROXIMO_PORTAO=AGUARDAR_MISSAO_SEPARADA_DO_BLOCO_II
~~~

<!-- FIM_TRIN_FABRICA_ENCERRAMENTO_DOCUMENTAL_BLOCO_I_20260727 -->
