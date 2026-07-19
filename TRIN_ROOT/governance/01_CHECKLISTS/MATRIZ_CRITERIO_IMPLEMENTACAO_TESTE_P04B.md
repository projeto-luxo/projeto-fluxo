# MATRIZ CRITÉRIO → IMPLEMENTAÇÃO → TESTE P04B

| ID | Critério | Prova futura |
|---|---|---|
| P04B-01 | novo campo possui versão | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-02 | chaves antigas preservadas | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-03 | tipos antigos preservados | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-04 | payload sem P04A continua válido | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-05 | payload P04A válido passa schema | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-06 | peso zero | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-07 | impacto zero | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-08 | operacional false | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-09 | nenhum campo operacional | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-10 | importa P04A oficial | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-11 | usa API pública | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-12 | não lê CSV | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-13 | não acessa TRIN_HISTORICO | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-14 | não modifica P04A | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-15 | não modifica Historiador | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-16 | idempotência | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-17 | hash P04A preservado | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-18 | P04A indisponível | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-19 | schema ausente/divergente | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-20 | saída estrutural inválida | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-21 | versão desconhecida | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-22 | exceção interna | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-23 | timeout | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-24 | origem divergente | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-25 | hash inválido | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-26 | falha não libera operação | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-27 | backend importa | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-28 | backend gera payload | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-29 | endpoint HTTP `/data` responde pelo app real | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-30 | JSON serializável | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-31 | erro diagnóstico não derruba endpoint | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-32 | consumidores antigos preservados | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-33 | sem estado acumulado | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-34 | hashes fornecedores antes/depois | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-35 | working tree preservado | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-36 | frontend não alterado | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-37 | Planejador não alterado | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-38 | manifesto | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-39 | SHA externo | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-40 | requirements | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-41 | preflight | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-42 | rollback | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-43 | reaplicação | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-44 | staged bloqueado | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-45 | alvo conflitante bloqueado | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-46 | falha intermediária restaura | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-47 | zero commit | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-48 | zero push | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-49 | git diff --check | suíte `tests/p04b_backend` / aplicador / evidência |
| P04B-50 | WebSocket `/ws` transporta o mesmo contrato | suíte `tests/p04b_backend/test_integracao_backend.py` / evidência local |
| P04B-51 | gate Fiscal lê `payload["fiscal"]` oficial | suíte `tests/p04b_backend/test_fail_closed.py` / evidência local |
| P04B-52 | Fiscal ausente, divergente ou bloqueado impede P04A | suíte `tests/p04b_backend/test_fail_closed.py` / evidência local |
| P04B-53 | suíte completa roda na sandbox e no `TRIN_ROOT` real | aplicador / logs brutos / evidência local |

| P04B-54 | timeout opera sobre cópia física, nunca sobre JSONL oficial | `test_timeout_isola_repositorio_e_descarta_mutacao_tardia` |
| P04B-55 | arquivo oficial é conferido também em timeout/exceção | suíte `tests/p04b_backend/test_nao_mutacao_idempotencia.py` |
| P04B-56 | status Fiscal contraditório não atravessa booleanos favoráveis | `test_fiscal_status_contraditorio_com_booleanos_favoraveis_bloqueia` |
| P04B-57 | somente status Fiscal aprovado e booleanos coerentes liberam P04A | `test_fiscal_status_aprovado_coerente_permite_avaliacao` |
| P04B-58 | trabalhador temporário remove a área isolada ao concluir | `test_timeout_isola_repositorio_e_descarta_mutacao_tardia` |

| P04B-59 | P04B não declara lista local de status Fiscais | `test_p04b_nao_declara_lista_local_de_status_fiscais` |
| P04B-60 | gate usa diretamente `FiscalAdapter.STATUS_LIBERADOS` | parametrização dinâmica em `test_fiscal_status_aprovado_coerente_permite_avaliacao` |
| P04B-61 | alias `RESSALVA` da autoridade vigente libera consulta diagnóstica | `test_fiscal_ressalva_da_autoridade_vigente_permite_avaliacao` |
| P04B-62 | status ausente ou desconhecido falha fechado | `test_fiscal_status_ausente_bloqueia` e `test_fiscal_status_desconhecido_bloqueia` |
| P04B-63 | booleanos contraditórios não liberam o avaliador | `test_fiscal_booleanos_contraditorios_bloqueiam` |
