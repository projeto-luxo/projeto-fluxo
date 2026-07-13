from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from intelligence.bernardo_adapter import BernardoAdapter


class BernardoAdapterCanonicoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.adapter = BernardoAdapter()
        self.adapter.arq_pacote_motor = base / "pacote_motor_confluencia.csv"
        self.adapter.arq_indice_geral = base / "indice_geral.csv"

    def gravar_pacote(self) -> None:
        pd.DataFrame([{
            "tipo": "ASSUNTO",
            "nome": "REVERSAO",
            "categoria": "ESTRUTURA",
            "maturidade": "ALTA",
            "peso_inicial_sugerido": "3",
            "uso": "Contexto para motor",
        }]).to_csv(
            self.adapter.arq_pacote_motor,
            sep=";", index=False, encoding="utf-8-sig",
        )

    def test_pacote_canonico_sem_inventar_direcao(self) -> None:
        self.gravar_pacote()
        resposta = self.adapter.consultar(contexto="REVERSAO", padrao="REVERSAO")
        self.assertEqual(resposta["fonte"], "BERNARDO_PACOTE_MOTOR_CONFLUENCIA")
        self.assertEqual(resposta["direcao"], "NEUTRO")
        self.assertEqual(resposta["similaridade"], 0.0)
        self.assertEqual(resposta["confianca"], 0.0)
        self.assertFalse(resposta["episodio_semelhante"])
        self.assertEqual(resposta["status"], "PACOTE_COGNITIVO_COMPATIVEL")

    def test_pacote_ausente_nao_usa_historiador(self) -> None:
        resposta = self.adapter.consultar()
        self.assertEqual(resposta["status"], "PACOTE_BERNARDO_INDISPONIVEL")
        self.assertEqual(resposta["fonte"], "BERNARDO_PACOTE_MOTOR_CONFLUENCIA")

    def test_schema_invalido(self) -> None:
        pd.DataFrame([{"nome": "REVERSAO"}]).to_csv(
            self.adapter.arq_pacote_motor,
            sep=";", index=False, encoding="utf-8-sig",
        )
        resposta = self.adapter.consultar()
        self.assertEqual(resposta["status"], "SCHEMA_PACOTE_BERNARDO_INVALIDO")
        self.assertIn("tipo", resposta["colunas_ausentes"])

    def test_api_indice_filtra(self) -> None:
        pd.DataFrame([
            {"ativo": "WIN", "fractal": "5_MIN", "status": "OK"},
            {"ativo": "WDO", "fractal": "5_MIN", "status": "OK"},
        ]).to_csv(
            self.adapter.arq_indice_geral,
            sep=";", index=False, encoding="utf-8-sig",
        )
        resposta = self.adapter.consultar_indice(ativo="WIN", fractal="5_MIN")
        self.assertEqual(resposta["quantidade"], 1)
        self.assertEqual(resposta["registros"][0]["ativo"], "WIN")


if __name__ == "__main__":
    unittest.main()
