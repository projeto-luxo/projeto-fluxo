# INVARIANTES SEMÂNTICOS — CONFLUÊNCIA REPLAY V1

O JSON Schema fecha as contradições estruturais. As invariantes abaixo também devem ser testadas no validador semântico futuro.

1. `quantidade_experiencias == len(ids_experiencias) == len(evidencias)`.
2. `quantidade_comparaveis == len(ids_comparaveis)`.
3. IDs de evidência, universo e partições são únicos.
4. `ids_calibracao ∩ ids_prova = ∅`.
5. A união das partições corresponde aos IDs incluídos.
6. `hash_universo` deriva dos pares ordenados ID/hash antes das métricas.
7. `hash_particao` deriva do método e dos IDs ordenados das duas partições.
8. Nenhum filtro pode referenciar `resultado`, MFE, MAE ou desfecho.
9. O resultado só é lido depois da seleção.
10. Duplicidade exata não duplica evidência.
11. Duplicidade conflitante bloqueia todo o resultado.
12. `COMPLETO` exige ao menos uma evidência, todos os campos avaliados e zero bloqueios.
13. `PARCIAL` exige ao menos uma evidência e campo não avaliado.
14. `SEM_EVIDENCIA` exige universo válido vazio.
15. `INSUFICIENTE` exige universo não vazio e zero comparáveis.
16. `BLOQUEADO` exige ao menos um bloqueio.
17. Zero comparáveis implica confiança `null`.
18. Confiança nunca cria peso, impacto ou ordem.
19. `timestamp_calculo` é o máximo timestamp de evidência incluída, nunca relógio da máquina.
20. `hash_resultado` exclui o próprio campo.
21. N chamadas iguais produzem bytes canônicos idênticos.
22. O Historiador, a memória ao vivo e o histórico bruto permanecem imutáveis.
