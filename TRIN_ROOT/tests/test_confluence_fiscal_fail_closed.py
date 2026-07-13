from __future__ import annotations

import unittest

from core.confluence_engine import ConfluenceEngineV2


class ConfluenceFiscalFailClosedTest(unittest.TestCase):
    def setUp(self) -> None:
        self.motor = ConfluenceEngineV2()

    def test_status_desconhecido_bloqueia(self) -> None:
        qualidade = self.motor._qualidade(
            8.0,
            {"status": "DESCONHECIDO"},
        )
        self.assertEqual(qualidade, "BLOQUEADO_POR_CERTIFICACAO")

    def test_erro_fiscal_bloqueia(self) -> None:
        qualidade = self.motor._qualidade(
            8.0,
            {"status": "ERRO_FISCAL"},
        )
        self.assertEqual(qualidade, "BLOQUEADO_POR_CERTIFICACAO")

    def test_certificado_nao_bloqueia(self) -> None:
        qualidade = self.motor._qualidade(
            8.0,
            {"status": "CERTIFICADO"},
        )
        self.assertNotEqual(qualidade, "BLOQUEADO_POR_CERTIFICACAO")

    def test_ressalva_nao_bloqueia(self) -> None:
        qualidade = self.motor._qualidade(
            5.0,
            {"status": "APROVADO_COM_RESSALVAS"},
        )
        self.assertNotEqual(qualidade, "BLOQUEADO_POR_CERTIFICACAO")


if __name__ == "__main__":
    unittest.main()
