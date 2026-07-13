from __future__ import annotations

import unittest

import pandas as pd

from intelligence.bernardo_bibliotecario_v4_0 import (
    PASTAS_BIBLIOTECA_OFICIAL,
    ler_datas,
)


class BernardoEscopoTemporalTest(unittest.TestCase):
    def test_pastas_administrativas_nao_entram_na_biblioteca(self) -> None:
        proibidas = {
            "000_TT_BRUTO",
            "00_AUDITORIA",
            "00_CERTIFICACOES",
            "00_CONFIG",
            "00_CONHECIMENTO",
            "00_DUPLICIDADES_FRACTAIS",
            "00_INDICES",
            "00_LOGS",
            "00_PROCESSAMENTO_TT",
            "00_RECUPERACAO_PROFIT",
            "00_RELATORIOS",
        }

        self.assertTrue(
            proibidas.isdisjoint(PASTAS_BIBLIOTECA_OFICIAL)
        )

    def test_data_iso_nao_inverte_mes_e_dia(self) -> None:
        df = pd.DataFrame(
            [
                ["WIN", "2026-07-09 09:00:00"],
                ["WIN", "2026-07-09 18:00:00"],
            ]
        )

        inicio, fim, status = ler_datas(df)

        self.assertEqual(inicio, "09/07/2026")
        self.assertEqual(fim, "09/07/2026")
        self.assertEqual(status, "OK")

    def test_datas_absurdas_sao_rejeitadas(self) -> None:
        df = pd.DataFrame(
            [
                ["WIN", "01/01/1000"],
                ["WIN", "01/01/1940"],
            ]
        )

        inicio, fim, status = ler_datas(df)

        self.assertEqual(inicio, "N/D")
        self.assertEqual(fim, "N/D")
        self.assertEqual(status, "DATA_INVALIDA")


if __name__ == "__main__":
    unittest.main()
