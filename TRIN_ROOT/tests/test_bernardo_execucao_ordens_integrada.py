from __future__ import annotations

import inspect
import unittest

from intelligence import bernardo_bibliotecario_v4_0


class BernardoExecucaoOrdensIntegradaTest(unittest.TestCase):
    def test_main_processa_ordens_do_fiscal(self) -> None:
        fonte = inspect.getsource(
            bernardo_bibliotecario_v4_0.main
        )

        self.assertIn(
            "BernardoOrdensFiscal().processar",
            fonte,
        )
        self.assertIn(
            "gravar=True",
            fonte,
        )


if __name__ == "__main__":
    unittest.main()
