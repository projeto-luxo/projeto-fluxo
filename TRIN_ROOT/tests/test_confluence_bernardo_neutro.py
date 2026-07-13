from __future__ import annotations

import unittest

from core.confluence_engine import ConfluenceEngineV2


class ConfluenceBernardoNeutroTest(unittest.TestCase):
    def test_evidencia_preserva_item_sem_impacto(self) -> None:
        motor = ConfluenceEngineV2()

        evidencia = motor._evidencia_bernardo(
            {
                "status": "PACOTE_COGNITIVO_COMPATIVEL",
                "fonte": "BERNARDO_PACOTE_MOTOR_CONFLUENCIA",
                "ocorrencias": 30,
                "item_canonico": {
                    "tipo": "ASSUNTO",
                    "nome": "REVERSAO",
                    "categoria": "ESTRUTURA",
                    "maturidade": "ALTA",
                    "peso_inicial_sugerido": "3",
                    "uso": "Contexto para motor",
                },
            }
        )

        self.assertEqual(evidencia.nome, "BERNARDO")
        self.assertEqual(evidencia.peso, 0.0)
        self.assertEqual(evidencia.impacto, 0.0)
        self.assertEqual(evidencia.direcao, "NEUTRO")
        self.assertEqual(
            evidencia.valor["fonte"],
            "BERNARDO_PACOTE_MOTOR_CONFLUENCIA",
        )
        self.assertEqual(evidencia.valor["nome"], "REVERSAO")
        self.assertEqual(evidencia.valor["maturidade"], "ALTA")
        self.assertEqual(
            evidencia.valor["uso_operacional"],
            "DIAGNOSTICO_SEM_IMPACTO",
        )


if __name__ == "__main__":
    unittest.main()
