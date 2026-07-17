# MATRIZ CRITÉRIO → IMPLEMENTAÇÃO → TESTE — P04A V2

**Base:** `be7714c16d0031b87bebcc1ef905b4daf5bba478`  
**Natureza:** desenho documental; nenhum código nesta entrega.

| ID | Critério | Responsável futuro | Entrada controlada | Resultado esperado | Tipo |
|---|---|---|---|---|---|
| CF-01 | Entrada somente pela API homologada | porta_historiador | porta fake com métodos reais | nenhum CSV/caminho aceito | contrato |
| CF-02 | Garantia fiscal herdada declarada | modelos/porta | objeto retornado pela porta | modelo herdado preservado | contrato |
| CF-03 | Origem/rastreabilidade inválida bloqueia | validador | origem divergente ou hash ausente | BLOQUEADO | funcional |
| CF-04 | ORIGEM_REPLAY preservada | modelos | experiência válida | ORIGEM_REPLAY | schema |
| CF-05 | Resultado não participa da seleção | criterios | mesmos fatos com resultados trocados | mesmos IDs selecionados | metamórfico |
| CF-06 | Ausência de experiências | núcleo | lista vazia | SEM_EVIDENCIA | funcional |
| CF-07 | Direção não inventada | projeção | direção ausente | null | contrato |
| CF-08 | Peso zero | modelo | qualquer saída | 0 | schema |
| CF-09 | Impacto zero | modelo | qualquer saída | 0 | schema |
| CF-10 | Nenhuma ordem | serialização | tentativa de campo operacional | schema rejeita | negativo |
| CF-11 | Historiador não mutado | porta | snapshot antes/depois | hash igual | imutabilidade |
| CF-12 | Memória ao vivo não mutada | núcleo | sentinela | hash igual | imutabilidade |
| CF-13 | Zero acesso à Biblioteca Histórica | guardião | path monitorado | zero tentativas | segurança |
| CF-14 | Saída determinística | serialização | ordens físicas distintas | mesmos bytes/hash | propriedade |
| CF-15 | IDs rastreáveis | serialização | universo conhecido | todos os IDs/hashes presentes | contrato |
| CF-16 | MFE/MAE ligados às origens | estatísticas | valores conhecidos | métricas e IDs exatos | unitário |
| CF-17 | Schema inválido bloqueia | validador | campo ausente | BLOQUEADO | funcional |
| CF-18 | Consumidores atuais não quebram | regressão | base limpa | suíte existente aprovada | regressão |
| CF-19 | Rollback futuro | aplicador futuro | falha forçada | estado restaurado | integração |
| CF-20 | Commit seletivo futuro | Git simulado | lista permitida | somente P04A staged | Git |
| CF-21 | NEUTRA/FAVORÁVEL/CONTRÁRIA/BLOQUEADORA | criterios | quatro cenários | classes exatas | parametrizado |
| CF-22 | Matriz de qualidade | metricas_gps | cenários explícitos | categorias exatas/NAO_AVALIAVEL | parametrizado |
| CF-23 | Resultados por horário | estratificação | horas conhecidas | grupos determinísticos | unitário |
| CF-24 | Resultados por volatilidade | estratificação | calibração/prova sintéticas | Q33/Q66 congelados | unitário |
| CF-25 | Resultados por contexto | estratificação | regimes/sessões conhecidos | grupos exatos | unitário |
| CF-26 | Partições sem interseção | particionamento | universo ordenado | calibração ∩ prova vazia | propriedade |
| CF-27 | Cherry-picking bloqueado | consulta/schema | filtro resultado/direção/IDs | schema rejeita | negativo |
| CF-28 | Top-N desabilitado | consulta/núcleo | universo > limite | BLOQUEADO, sem subconjunto | funcional |
| CF-29 | Hash do universo | hashing | vetor conhecido | SHA conhecido | vetor |
| CF-30 | Idempotência N chamadas | núcleo | mesma instância/consulta N vezes | sem acúmulo; mesmo hash | idempotência |
| CF-31 | id_confluencia determinístico | hashing | vetor conhecido | ID conhecido | vetor |
| CF-32 | hash_resultado sem autorreferência | hashing | vetor conhecido | SHA conhecido | vetor |
| CF-33 | COMPLETO com zero rejeitado | schema | documento adversarial | rejeitado | schema negativo |
| CF-34 | Quantidade/listas divergentes rejeitadas | schema | documento adversarial | rejeitado | schema negativo |
| CF-35 | Confiança 100 com zero rejeitada | schema | documento adversarial | rejeitado | schema negativo |
| CF-36 | campos_comparacao vazio rejeitado | schema consulta | lista vazia | rejeitado | schema negativo |
