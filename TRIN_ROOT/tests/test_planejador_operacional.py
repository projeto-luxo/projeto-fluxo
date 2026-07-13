from __future__ import annotations

import unittest

from core.planejador_operacional import PlanejadorOperacional


class PlanejadorOperacionalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.planejador = PlanejadorOperacional()
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

    def test_fiscal_bloqueado_impede_operacao(self) -> None:
        plano = self.planejar()

        self.assertEqual("SEM_OPERACAO", plano["estado"])
        self.assertEqual("BLOQUEADA", plano["autorizacao"])
        self.assertEqual("FISCAL_NAO_APROVADO", plano["motivo_bloqueio"])

    def test_regioes_diagnosticas_nao_viram_plano(self) -> None:
        plano = self.planejar(fiscal_aprovado=True)

        self.assertEqual(
            "REGIOES_SEM_ELEGIBILIDADE_OPERACIONAL",
            plano["motivo_bloqueio"],
        )
        self.assertEqual("BLOQUEADO", plano["uso_operacional"])

    def test_niveis_operacionais_permanecem_nulos(self) -> None:
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

    def test_mesmo_com_entradas_favoraveis_permanece_bloqueado(self) -> None:
        regiao_liberada = [
            {
                "chave_regiao": "REGIAO|WIN|180000",
                "status": "ATIVA",
                "uso_operacional": "LIBERADO",
            }
        ]

        plano = self.planejar(
            fiscal_aprovado=True,
            regioes=regiao_liberada,
        )

        self.assertEqual(
            "PLANEJADOR_NAO_HOMOLOGADO",
            plano["motivo_bloqueio"],
        )
        self.assertEqual("SEM_OPERACAO", plano["estado"])
        self.assertEqual("BLOQUEADA", plano["autorizacao"])

    def test_nao_altera_entradas_recebidas(self) -> None:
        confluencia_original = dict(self.confluencia)
        regioes_originais = [dict(item) for item in self.regioes_bloqueadas]

        self.planejar()

        self.assertEqual(confluencia_original, self.confluencia)
        self.assertEqual(regioes_originais, self.regioes_bloqueadas)


if __name__ == "__main__":
    unittest.main()
