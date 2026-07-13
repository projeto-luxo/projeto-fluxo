from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from intelligence.fiscal_adapter import FiscalAdapter


class FiscalAdapterTest(unittest.TestCase):
    def adapter_com_laudo(self, conteudo: str) -> FiscalAdapter:
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)

        arquivo = Path(pasta.name) / "laudo_temporal.txt"
        arquivo.write_text(conteudo, encoding="utf-8")

        adapter = FiscalAdapter()
        adapter.arquivo = arquivo
        return adapter

    def test_le_status_final_exato(self) -> None:
        adapter = self.adapter_com_laudo(
            "FISCAL TEMPORAL\nSTATUS FINAL:\nREPROVADO_COM_PENDENCIAS\n"
        )

        resultado = adapter.consultar()

        self.assertEqual(resultado["status"], "REPROVADO_COM_PENDENCIAS")
        self.assertFalse(resultado["aprovado_operacional"])
        self.assertTrue(resultado["bloqueio_operacional"])

    def test_nome_certificado_temporal_nao_gera_falso_certificado(self) -> None:
        adapter = self.adapter_com_laudo(
            "ARQUIVOS GERADOS:\n- certificado_temporal.csv\n"
        )

        resultado = adapter.consultar()

        self.assertEqual(resultado["status"], "DESCONHECIDO")
        self.assertTrue(resultado["bloqueio_operacional"])

    def test_ressalva_mantem_aprovacao_controlada(self) -> None:
        adapter = self.adapter_com_laudo(
            "STATUS FINAL:\nAPROVADO_COM_RESSALVAS\n"
        )

        resultado = adapter.consultar()

        self.assertEqual(resultado["status"], "APROVADO_COM_RESSALVAS")
        self.assertTrue(resultado["aprovado_operacional"])
        self.assertFalse(resultado["bloqueio_operacional"])

    def test_laudo_ausente_falha_fechado(self) -> None:
        adapter = FiscalAdapter()
        adapter.arquivo = Path(tempfile.gettempdir()) / "trin_laudo_inexistente.txt"
        adapter.arquivo.unlink(missing_ok=True)

        resultado = adapter.consultar()

        self.assertEqual(resultado["status"], "DESCONHECIDO")
        self.assertFalse(resultado["aprovado_operacional"])
        self.assertTrue(resultado["bloqueio_operacional"])


if __name__ == "__main__":
    unittest.main()
