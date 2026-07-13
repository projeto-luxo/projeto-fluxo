from __future__ import annotations

import unittest

from core.confluence_engine import ConfluenceEngineV2


class ConfluenciaRegioesDiagnosticasTest(unittest.TestCase):
    def setUp(self) -> None:
        self.motor = ConfluenceEngineV2()
        self.resultado_base = {
            "score_confluencia": 6.25,
            "direcao": "COMPRA",
            "qualidade": "MEDIA",
            "alerta": None,
            "evidencias": [
                {
                    "nome": "FLUXO_DELTA_SALDO",
                    "valor": {},
                    "peso": 2.0,
                    "impacto": 1.0,
                    "direcao": "COMPRA",
                    "justificativa": "teste",
                }
            ],
        }
        self.regioes = [
            {
                "chave_regiao": "REGIAO|WIN|180000",
                "limite_inferior": 180000.0,
                "limite_superior": 180000.0,
                "quantidade_origens": 2,
                "status": "CANDIDATA",
                "classificacao": "NAO_CLASSIFICADA",
                "uso_operacional": "BLOQUEADO",
            }
        ]

    def test_anexa_evidencia_neutra(self) -> None:
        resultado = self.motor.anexar_regioes_diagnosticas(
            self.resultado_base,
            self.regioes,
        )

        evidencia = next(
            item
            for item in resultado["evidencias"]
            if item["nome"] == "REGIOES_COMPOSTAS"
        )

        self.assertEqual(0.0, evidencia["peso"])
        self.assertEqual(0.0, evidencia["impacto"])
        self.assertEqual("NEUTRO", evidencia["direcao"])
        self.assertEqual(1, evidencia["valor"]["quantidade"])

    def test_nao_altera_resultado_operacional(self) -> None:
        resultado = self.motor.anexar_regioes_diagnosticas(
            self.resultado_base,
            self.regioes,
        )

        for campo in (
            "score_confluencia",
            "direcao",
            "qualidade",
            "alerta",
        ):
            self.assertEqual(
                self.resultado_base[campo],
                resultado[campo],
            )

    def test_chamada_repetida_nao_duplica_evidencia(self) -> None:
        primeira = self.motor.anexar_regioes_diagnosticas(
            self.resultado_base,
            self.regioes,
        )
        segunda = self.motor.anexar_regioes_diagnosticas(
            primeira,
            self.regioes,
        )

        evidencias = [
            item
            for item in segunda["evidencias"]
            if item["nome"] == "REGIOES_COMPOSTAS"
        ]

        self.assertEqual(1, len(evidencias))

    def test_uso_operacional_permanece_bloqueado(self) -> None:
        resultado = self.motor.anexar_regioes_diagnosticas(
            self.resultado_base,
            self.regioes,
        )

        evidencia = next(
            item
            for item in resultado["evidencias"]
            if item["nome"] == "REGIOES_COMPOSTAS"
        )

        regiao = evidencia["valor"]["regioes"][0]
        self.assertEqual("BLOQUEADO", regiao["uso_operacional"])
        self.assertEqual(
            "DIAGNOSTICO_SEM_IMPACTO",
            resultado["regioes_compostas_status"],
        )


if __name__ == "__main__":
    unittest.main()
