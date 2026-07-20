from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
import math
import unittest

from core.planejador_operacional import PlanejadorOperacional


class EntradaQueFalha(Mapping):
    def __getitem__(self, key):
        raise RuntimeError("falha_controlada")

    def __iter__(self):
        raise RuntimeError("falha_controlada")

    def __len__(self):
        raise RuntimeError("falha_controlada")


class PlanejadorOperacionalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.planejador = PlanejadorOperacional()
        self.planejador_sombra = PlanejadorOperacional(
            modo_sombra_homologado=True
        )
        self.confluencia = {
            "score_confluencia": 6.67,
            "direcao": "COMPRA",
            "qualidade": "MEDIA",
        }
        self.regioes_bloqueadas = [
            {
                "chave_regiao": "REGIAO|WIN|180000",
                "status": "CANDIDATA",
                "uso_operacional": "BLOQUEADO",
            }
        ]

    def planejar(self, **ajustes):
        dados = {
            "confluencia": self.confluencia,
            "regioes": self.regioes_bloqueadas,
            "fiscal_aprovado": False,
            "contrato_ativo": "WINQ26",
            "fontes_saudaveis": True,
        }
        dados.update(ajustes)
        return self.planejador.planejar(**dados)

    def entrada_sombra_valida(self) -> dict:
        return {
            "schema_version":
                "PlanejamentoOperacionalSombraEntradaV1",
            "gate_fiscal": {
                "decisao": "APROVADA",
                "status_tecnico_bruto": "CERTIFICADO",
                "motivo": "STATUS_FINAL_FISCAL:CERTIFICADO",
                "fonte": "FISCAL_TEMPORAL_LAUDO_OFICIAL",
            },
            "contrato_ativo": "WINQ26",
            "fontes_saudaveis": True,
            "regioes_elegiveis": [
                {
                    "chave_regiao": "REGIAO|WIN|180000",
                    "status": "ATIVA",
                    "uso_operacional": "LIBERADO",
                }
            ],
            "confluencia_versionada": {
                "schema_version": "ConfluenciaOperacionalV1",
                "score_confluencia": 6.67,
                "direcao": "COMPRA",
                "qualidade": "MEDIA",
                "evidencias": [
                    {
                        "id": "CF-001",
                        "tipo": "CONTEXTO_DIAGNOSTICO",
                    }
                ],
            },
            "origem_contexto": "AO_VIVO",
            "identidade_snapshot": {
                "evento_id": "WINQ26|20260720T100000|1",
                "timestamp": "2026-07-20T10:00:00-03:00",
                "sequencia": 1,
                "periodo_parcial": False,
            },
        }

    def planejar_sombra(self, **ajustes):
        entrada = self.entrada_sombra_valida()
        entrada.update(ajustes)
        return self.planejador_sombra.planejar_sombra(entrada)

    def test_fiscal_bloqueado_impede_operacao_legado(self) -> None:
        plano = self.planejar()
        self.assertEqual("SEM_OPERACAO", plano["estado"])
        self.assertEqual("BLOQUEADA", plano["autorizacao"])
        self.assertEqual("FISCAL_NAO_APROVADO", plano["motivo_bloqueio"])

    def test_regioes_diagnosticas_nao_viram_plano_legado(self) -> None:
        plano = self.planejar(fiscal_aprovado=True)
        self.assertEqual(
            "REGIOES_SEM_ELEGIBILIDADE_OPERACIONAL",
            plano["motivo_bloqueio"],
        )
        self.assertEqual("BLOQUEADO", plano["uso_operacional"])

    def test_niveis_operacionais_permanecem_nulos_legado(self) -> None:
        plano = self.planejar(fiscal_aprovado=True)
        for campo in (
            "entrada_inferior",
            "entrada_superior",
            "invalidacao",
            "stop",
            "parcial",
            "alvo",
        ):
            self.assertIsNone(plano[campo])

    def test_mesmo_com_entradas_favoraveis_legado_permanece_bloqueado(
        self,
    ) -> None:
        plano = self.planejar(
            fiscal_aprovado=True,
            regioes=[
                {
                    "chave_regiao": "REGIAO|WIN|180000",
                    "status": "ATIVA",
                    "uso_operacional": "LIBERADO",
                }
            ],
        )
        self.assertEqual(
            "PLANEJADOR_NAO_HOMOLOGADO",
            plano["motivo_bloqueio"],
        )
        self.assertEqual("SEM_OPERACAO", plano["estado"])
        self.assertEqual("BLOQUEADA", plano["autorizacao"])

    def test_legado_nao_altera_entradas_recebidas(self) -> None:
        confluencia_original = dict(self.confluencia)
        regioes_originais = [dict(item) for item in self.regioes_bloqueadas]
        self.planejar()
        self.assertEqual(confluencia_original, self.confluencia)
        self.assertEqual(regioes_originais, self.regioes_bloqueadas)

    def test_contrato_versionado_ausente_bloqueia(self) -> None:
        plano = self.planejar_sombra(schema_version=None)
        self.assertEqual(
            "CONTRATO_ENTRADA_AUSENTE_OU_INCOMPATIVEL",
            plano["motivo_bloqueio"],
        )

    def test_campo_superior_desconhecido_bloqueia(self) -> None:
        plano = self.planejar_sombra(campo_indevido=True)
        self.assertEqual(
            "CAMPO_SUPERIOR_DESCONHECIDO",
            plano["motivo_bloqueio"],
        )

    def test_payload_nao_controla_homologacao_sombra(self) -> None:
        entrada = self.entrada_sombra_valida()
        entrada["modo_sombra_homologado"] = True
        plano = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual(
            "CAMPO_SUPERIOR_DESCONHECIDO",
            plano["motivo_bloqueio"],
        )

    def test_payload_nao_controla_autorizacao_operacional(self) -> None:
        entrada = self.entrada_sombra_valida()
        entrada["autorizacao_operacional_externa"] = "LIBERADA"
        plano = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual(
            "CAMPO_SUPERIOR_DESCONHECIDO",
            plano["motivo_bloqueio"],
        )
        self.assertEqual("BLOQUEADA", plano["autorizacao"])

    def test_decisao_fiscal_ausente_bloqueia_e_preserva_status(self) -> None:
        plano = self.planejar_sombra(
            gate_fiscal={
                "status_tecnico_bruto": "CERTIFICADO",
            }
        )
        self.assertEqual(
            "DECISAO_FISCAL_AUSENTE",
            plano["motivo_bloqueio"],
        )
        self.assertEqual(
            "CERTIFICADO",
            plano["evidencias"]["gate_fiscal"][
                "status_tecnico_bruto"
            ],
        )

    def test_decisao_fiscal_reprovada_bloqueia(self) -> None:
        plano = self.planejar_sombra(
            gate_fiscal={
                "decisao": "REPROVADA",
                "status_tecnico_bruto": "REPROVADO",
            }
        )
        self.assertEqual(
            "DECISAO_FISCAL_NAO_APROVADA",
            plano["motivo_bloqueio"],
        )
        self.assertIsNone(plano["direcao"])

    def test_status_fiscal_bruto_ausente_bloqueia(self) -> None:
        plano = self.planejar_sombra(
            gate_fiscal={"decisao": "APROVADA"}
        )
        self.assertEqual(
            "STATUS_FISCAL_BRUTO_AUSENTE_OU_VAZIO",
            plano["motivo_bloqueio"],
        )

    def test_status_fiscal_bruto_vazio_bloqueia(self) -> None:
        plano = self.planejar_sombra(
            gate_fiscal={
                "decisao": "APROVADA",
                "status_tecnico_bruto": "   ",
            }
        )
        self.assertEqual(
            "STATUS_FISCAL_BRUTO_AUSENTE_OU_VAZIO",
            plano["motivo_bloqueio"],
        )

    def test_contrato_ativo_ausente_bloqueia(self) -> None:
        plano = self.planejar_sombra(contrato_ativo=None)
        self.assertEqual(
            "CONTRATO_ATIVO_NAO_CONFIRMADO",
            plano["motivo_bloqueio"],
        )

    def test_fonte_nao_saudavel_bloqueia(self) -> None:
        plano = self.planejar_sombra(fontes_saudaveis=False)
        self.assertEqual(
            "FONTES_NAO_SAUDAVEIS",
            plano["motivo_bloqueio"],
        )

    def test_saude_fontes_ausente_bloqueia(self) -> None:
        entrada = self.entrada_sombra_valida()
        entrada.pop("fontes_saudaveis")
        plano = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual(
            "SAUDE_FONTES_NAO_INFORMADA",
            plano["motivo_bloqueio"],
        )

    def test_alias_fontes_aninhado_e_rejeitado(self) -> None:
        entrada = self.entrada_sombra_valida()
        entrada.pop("fontes_saudaveis")
        entrada["fontes"] = {
            "saudaveis": True,
            "periodo_parcial": False,
        }
        plano = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual(
            "CAMPO_SUPERIOR_DESCONHECIDO",
            plano["motivo_bloqueio"],
        )

    def test_periodo_parcialidade_ausente_bloqueia(self) -> None:
        entrada = self.entrada_sombra_valida()
        entrada["identidade_snapshot"].pop("periodo_parcial")
        plano = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual(
            "PERIODO_PARCIALIDADE_NAO_INFORMADA",
            plano["motivo_bloqueio"],
        )

    def test_periodo_parcial_no_nivel_superior_e_rejeitado(self) -> None:
        entrada = self.entrada_sombra_valida()
        entrada["periodo_parcial"] = False
        plano = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual(
            "CAMPO_SUPERIOR_DESCONHECIDO",
            plano["motivo_bloqueio"],
        )

    def test_periodo_parcial_bloqueia(self) -> None:
        entrada = self.entrada_sombra_valida()
        entrada["identidade_snapshot"]["periodo_parcial"] = True
        plano = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual(
            "PERIODO_PARCIAL",
            plano["motivo_bloqueio"],
        )

    def test_periodo_parcial_nao_booleano_bloqueia(self) -> None:
        entrada = self.entrada_sombra_valida()
        entrada["identidade_snapshot"]["periodo_parcial"] = "false"
        plano = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual(
            "PERIODO_PARCIALIDADE_NAO_INFORMADA",
            plano["motivo_bloqueio"],
        )

    def test_regiao_inelegivel_bloqueia(self) -> None:
        plano = self.planejar_sombra(
            regioes_elegiveis=self.regioes_bloqueadas,
        )
        self.assertEqual(
            "REGIOES_SEM_ELEGIBILIDADE_OPERACIONAL",
            plano["motivo_bloqueio"],
        )

    def test_regiao_sem_chave_bloqueia(self) -> None:
        plano = self.planejar_sombra(
            regioes_elegiveis=[
                {
                    "status": "ATIVA",
                    "uso_operacional": "LIBERADO",
                }
            ],
        )
        self.assertEqual(
            "REGIOES_SEM_ELEGIBILIDADE_OPERACIONAL",
            plano["motivo_bloqueio"],
        )

    def test_confluencia_sem_schema_bloqueia(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia.pop("schema_version")
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual(
            "CONFLUENCIA_SEM_CONTRATO_VERSIONADO",
            plano["motivo_bloqueio"],
        )

    def test_score_ausente_bloqueia(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia.pop("score_confluencia")
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual(
            "CONFLUENCIA_SCORE_INVALIDO",
            plano["motivo_bloqueio"],
        )

    def test_score_booleano_bloqueia(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia["score_confluencia"] = True
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual(
            "CONFLUENCIA_SCORE_INVALIDO",
            plano["motivo_bloqueio"],
        )

    def test_score_fora_da_faixa_bloqueia(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia["score_confluencia"] = 10.01
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual(
            "CONFLUENCIA_SCORE_INVALIDO",
            plano["motivo_bloqueio"],
        )

    def test_score_nan_falha_fechado(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia["score_confluencia"] = math.nan
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual("ERRO_BLOQUEADO", plano["estado"])

    def test_score_infinito_falha_fechado(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia["score_confluencia"] = math.inf
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual("ERRO_BLOQUEADO", plano["estado"])

    def test_direcao_ausente_nao_e_inventada(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia["direcao"] = None
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual(
            "CONFLUENCIA_SEM_DIRECAO_ELEGIVEL",
            plano["motivo_bloqueio"],
        )
        self.assertIsNone(plano["direcao"])

    def test_qualidade_arbitraria_bloqueia(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia["qualidade"] = "EXCELENTE"
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual(
            "CONFLUENCIA_QUALIDADE_INVALIDA",
            plano["motivo_bloqueio"],
        )

    def test_confluencia_bloqueada_nao_forma_plano(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia["qualidade"] = "BLOQUEADO_POR_CERTIFICACAO"
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual(
            "CONFLUENCIA_BLOQUEADA",
            plano["motivo_bloqueio"],
        )
        self.assertIsNone(plano["hipotese_plano"])

    def test_evidencias_confluencia_ausentes_bloqueiam(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia.pop("evidencias")
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual(
            "CONFLUENCIA_EVIDENCIAS_AUSENTES",
            plano["motivo_bloqueio"],
        )

    def test_evidencias_confluencia_vazias_bloqueiam(self) -> None:
        confluencia = self.entrada_sombra_valida()[
            "confluencia_versionada"
        ]
        confluencia["evidencias"] = []
        plano = self.planejar_sombra(
            confluencia_versionada=confluencia,
        )
        self.assertEqual(
            "CONFLUENCIA_EVIDENCIAS_AUSENTES",
            plano["motivo_bloqueio"],
        )

    def test_origem_desconhecida_bloqueia(self) -> None:
        plano = self.planejar_sombra(
            origem_contexto="DESCONHECIDA",
        )
        self.assertEqual(
            "ORIGEM_CONTEXTO_DESCONHECIDA",
            plano["motivo_bloqueio"],
        )

    def test_timestamp_invalido_bloqueia(self) -> None:
        snapshot = self.entrada_sombra_valida()[
            "identidade_snapshot"
        ]
        snapshot["timestamp"] = "INVALIDO"
        plano = self.planejar_sombra(
            identidade_snapshot=snapshot,
        )
        self.assertEqual(
            "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            plano["motivo_bloqueio"],
        )

    def test_timestamp_sem_timezone_bloqueia(self) -> None:
        snapshot = self.entrada_sombra_valida()[
            "identidade_snapshot"
        ]
        snapshot["timestamp"] = "2026-07-20T10:00:00"
        plano = self.planejar_sombra(
            identidade_snapshot=snapshot,
        )
        self.assertEqual(
            "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            plano["motivo_bloqueio"],
        )

    def test_sequencia_booleana_bloqueia(self) -> None:
        snapshot = self.entrada_sombra_valida()[
            "identidade_snapshot"
        ]
        snapshot["sequencia"] = True
        plano = self.planejar_sombra(
            identidade_snapshot=snapshot,
        )
        self.assertEqual(
            "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            plano["motivo_bloqueio"],
        )

    def test_replay_com_look_ahead_bloqueia(self) -> None:
        plano = self.planejar_sombra(
            origem_contexto="REPLAY",
            identidade_snapshot={
                "evento_id": "REPLAY|10",
                "timestamp": "2026-07-20T10:00:00-03:00",
                "sequencia": 10,
                "periodo_parcial": False,
                "ordem_evento": 10,
                "janela_fim_ordem": 11,
            },
        )
        self.assertEqual(
            "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            plano["motivo_bloqueio"],
        )
        self.assertFalse(
            plano["rastreabilidade"]["look_ahead"]
        )

    def test_replay_sequencia_incoerente_bloqueia(self) -> None:
        plano = self.planejar_sombra(
            origem_contexto="REPLAY",
            identidade_snapshot={
                "evento_id": "REPLAY|10",
                "timestamp": "2026-07-20T10:00:00-03:00",
                "sequencia": 9,
                "periodo_parcial": False,
                "ordem_evento": 10,
                "janela_fim_ordem": 10,
            },
        )
        self.assertEqual(
            "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            plano["motivo_bloqueio"],
        )

    def test_modo_sombra_default_false_bloqueia(self) -> None:
        plano = self.planejador.planejar_sombra(
            self.entrada_sombra_valida()
        )
        self.assertEqual(
            "MODO_SOMBRA_NAO_HOMOLOGADO",
            plano["motivo_bloqueio"],
        )

    def test_entradas_favoraveis_formam_apenas_plano_sombra(self) -> None:
        plano = self.planejar_sombra()
        self.assertEqual(
            "PlanejamentoOperacionalSombraV1",
            plano["schema_version"],
        )
        self.assertEqual("SOMBRA", plano["modo"])
        self.assertEqual("PLANO_SOMBRA", plano["estado"])
        self.assertEqual("COMPRA", plano["direcao"])
        self.assertEqual("BLOQUEADA", plano["autorizacao"])
        self.assertEqual("BLOQUEADO", plano["uso_operacional"])
        self.assertIsNone(plano["ordem_corretora"])
        self.assertEqual(
            "MODO_SOMBRA_SEM_AUTORIZACAO_OPERACIONAL",
            plano["motivo_bloqueio"],
        )
        for campo in (
            "entrada_inferior",
            "entrada_superior",
            "invalidacao",
            "stop",
            "parcial",
            "alvo",
        ):
            self.assertIsNone(plano[campo])

    def test_replay_valido_forma_plano_sombra_sem_autorizar_ao_vivo(
        self,
    ) -> None:
        plano = self.planejar_sombra(
            origem_contexto="REPLAY",
            identidade_snapshot={
                "evento_id": "REPLAY|10",
                "timestamp": "2026-07-20T10:00:00-03:00",
                "sequencia": 10,
                "periodo_parcial": False,
                "ordem_evento": 10,
                "janela_fim_ordem": 10,
            },
        )
        self.assertEqual("PLANO_SOMBRA", plano["estado"])
        self.assertEqual("REPLAY", plano["origem_contexto"])
        self.assertEqual("BLOQUEADA", plano["autorizacao"])
        self.assertIsNone(plano["ordem_corretora"])

    def test_sombra_nao_altera_entradas_aninhadas(self) -> None:
        entrada = self.entrada_sombra_valida()
        original = deepcopy(entrada)
        self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual(original, entrada)

    def test_resultado_sombra_e_deterministico(self) -> None:
        entrada = self.entrada_sombra_valida()
        primeiro = self.planejador_sombra.planejar_sombra(entrada)
        segundo = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual(primeiro, segundo)

    def test_objeto_nao_serializavel_falha_fechado(self) -> None:
        entrada = self.entrada_sombra_valida()
        entrada["gate_fiscal"]["motivo"] = object()
        plano = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual("ERRO_BLOQUEADO", plano["estado"])
        self.assertEqual(
            "ERRO_INTERNO_PLANEJADOR",
            plano["motivo_bloqueio"],
        )

    def test_nan_em_metadado_falha_fechado(self) -> None:
        entrada = self.entrada_sombra_valida()
        entrada["gate_fiscal"]["motivo"] = math.nan
        plano = self.planejador_sombra.planejar_sombra(entrada)
        self.assertEqual("ERRO_BLOQUEADO", plano["estado"])

    def test_erro_interno_falha_fechado(self) -> None:
        plano = self.planejador_sombra.planejar_sombra(
            EntradaQueFalha()
        )
        self.assertEqual("ERRO_BLOQUEADO", plano["estado"])
        self.assertEqual("BLOQUEADA", plano["autorizacao"])
        self.assertEqual(
            "ERRO_INTERNO_PLANEJADOR",
            plano["motivo_bloqueio"],
        )
        self.assertIsNone(plano["ordem_corretora"])


    def test_contrato_ativo_numerico_bloqueia(self) -> None:
        plano = self.planejar_sombra(contrato_ativo=123)
        self.assertEqual(
            "CONTRATO_ATIVO_NAO_CONFIRMADO",
            plano["motivo_bloqueio"],
        )

    def test_contrato_ativo_booleano_bloqueia(self) -> None:
        plano = self.planejar_sombra(contrato_ativo=True)
        self.assertEqual(
            "CONTRATO_ATIVO_NAO_CONFIRMADO",
            plano["motivo_bloqueio"],
        )

    def test_evento_id_numerico_bloqueia(self) -> None:
        snapshot = self.entrada_sombra_valida()[
            "identidade_snapshot"
        ]
        snapshot["evento_id"] = 123
        plano = self.planejar_sombra(
            identidade_snapshot=snapshot,
        )
        self.assertEqual(
            "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            plano["motivo_bloqueio"],
        )

    def test_evento_id_booleano_bloqueia(self) -> None:
        snapshot = self.entrada_sombra_valida()[
            "identidade_snapshot"
        ]
        snapshot["evento_id"] = True
        plano = self.planejar_sombra(
            identidade_snapshot=snapshot,
        )
        self.assertEqual(
            "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            plano["motivo_bloqueio"],
        )

    def test_chave_regiao_numerica_bloqueia(self) -> None:
        plano = self.planejar_sombra(
            regioes_elegiveis=[
                {
                    "chave_regiao": 123,
                    "status": "ATIVA",
                    "uso_operacional": "LIBERADO",
                }
            ],
        )
        self.assertEqual(
            "REGIOES_SEM_ELEGIBILIDADE_OPERACIONAL",
            plano["motivo_bloqueio"],
        )

    def test_chave_regiao_booleana_bloqueia(self) -> None:
        plano = self.planejar_sombra(
            regioes_elegiveis=[
                {
                    "chave_regiao": True,
                    "status": "ATIVA",
                    "uso_operacional": "LIBERADO",
                }
            ],
        )
        self.assertEqual(
            "REGIOES_SEM_ELEGIBILIDADE_OPERACIONAL",
            plano["motivo_bloqueio"],
        )

    def test_snapshot_invalido_precede_regiao_invalida(self) -> None:
        snapshot = self.entrada_sombra_valida()[
            "identidade_snapshot"
        ]
        snapshot["timestamp"] = "INVALIDO"
        plano = self.planejar_sombra(
            identidade_snapshot=snapshot,
            regioes_elegiveis=self.regioes_bloqueadas,
        )
        self.assertEqual(
            "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            plano["motivo_bloqueio"],
        )

    def test_snapshot_invalido_precede_confluencia_invalida(self) -> None:
        snapshot = self.entrada_sombra_valida()[
            "identidade_snapshot"
        ]
        snapshot["timestamp"] = "INVALIDO"
        plano = self.planejar_sombra(
            identidade_snapshot=snapshot,
            confluencia_versionada={},
        )
        self.assertEqual(
            "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            plano["motivo_bloqueio"],
        )

    def test_periodo_parcial_precede_regiao_invalida(self) -> None:
        snapshot = self.entrada_sombra_valida()[
            "identidade_snapshot"
        ]
        snapshot["periodo_parcial"] = True
        plano = self.planejar_sombra(
            identidade_snapshot=snapshot,
            regioes_elegiveis=self.regioes_bloqueadas,
        )
        self.assertEqual(
            "PERIODO_PARCIAL",
            plano["motivo_bloqueio"],
        )

    def test_ordem_dos_gates_na_saida_e_exata(self) -> None:
        plano = self.planejar_sombra()
        self.assertEqual(
            [
                "CONTRATO_ENTRADA_VERSIONADO",
                "CAMPOS_SUPERIORES_PERMITIDOS",
                "DECISAO_FISCAL",
                "STATUS_FISCAL_BRUTO",
                "CONTRATO_ATIVO",
                "FONTES_SAUDAVEIS",
                "IDENTIDADE_TEMPORAL",
                "PERIODO_COMPLETO",
                "REGIOES_ELEGIVEIS",
                "CONFLUENCIA_VERSIONADA",
                "SCORE_CONFLUENCIA",
                "DIRECAO_CONFLUENCIA",
                "QUALIDADE_CONFLUENCIA",
                "CONFLUENCIA_NAO_BLOQUEADA",
                "EVIDENCIAS_CONFLUENCIA",
                "ORIGEM_CONTEXTO",
                "SEPARACAO_AO_VIVO_REPLAY",
                "MODO_SOMBRA_HOMOLOGADO",
                "AUTORIZACAO_OPERACIONAL_EXTERNA",
            ],
            [gate["id"] for gate in plano["gates"]],
        )



if __name__ == "__main__":
    unittest.main()
