from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from intelligence.bernardo_ordens_fiscal import BernardoOrdensFiscal


class BernardoOrdensFiscalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.ordens = base / "ordens_para_bernardo.csv"
        self.respostas = base / "respostas_bernardo.csv"
        self.ponte = BernardoOrdensFiscal(self.ordens, self.respostas)

    def test_sem_ordens_gera_schema_vazio(self) -> None:
        self.ordens.write_text("", encoding="utf-8")
        resultado = self.ponte.processar(gravar=True)
        self.assertEqual(resultado["status"], "SEM_ORDENS_PENDENTES")
        frame = pd.read_csv(self.respostas, sep=";", encoding="utf-8-sig", dtype=str)
        self.assertEqual(list(frame.columns), BernardoOrdensFiscal.COLUNAS_RESPOSTA)

    def test_ordem_fica_em_analise(self) -> None:
        pd.DataFrame([{
            "id_ocorrencia": "FT-20260713-000001",
            "status_ordem": "PENDENTE",
        }]).to_csv(self.ordens, sep=";", index=False, encoding="utf-8-sig")
        resultado = self.ponte.processar(gravar=True)
        self.assertEqual(resultado["status"], "ORDENS_RECEBIDAS_EM_ANALISE")
        self.assertEqual(resultado["respostas"][0]["status_ordem"], "EM_ANALISE")
        self.assertNotIn(
            resultado["respostas"][0]["status_ordem"],
            {"CORRIGIDO", "RECERTIFICAR", "ENCERRADO"},
        )

    def test_schema_sem_id_e_rejeitado(self) -> None:
        pd.DataFrame([{"motivo": "ERRO"}]).to_csv(
            self.ordens, sep=";", index=False, encoding="utf-8-sig"
        )
        resultado = self.ponte.processar(gravar=False)
        self.assertEqual(resultado["status"], "SCHEMA_ORDENS_FISCAL_INVALIDO")


if __name__ == "__main__":
    unittest.main()
