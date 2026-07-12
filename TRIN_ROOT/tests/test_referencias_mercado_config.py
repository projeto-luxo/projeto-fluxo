import tempfile
import unittest
from pathlib import Path

from data.referencias_mercado_config import ReferenciasMercadoConfig


CABECALHO = (
    "data_referencia;ativo;contrato;preco_ajuste;ptax_referencia;"
    "fonte_primaria;fonte_operacional;status_referencia;observacao\n"
)


class ReferenciasMercadoConfigTest(unittest.TestCase):
    def criar_config(self, linhas: str) -> ReferenciasMercadoConfig:
        diretorio = tempfile.TemporaryDirectory()
        self.addCleanup(diretorio.cleanup)

        arquivo = Path(diretorio.name) / "referencias.csv"
        arquivo.write_text(CABECALHO + linhas, encoding="utf-8-sig")
        return ReferenciasMercadoConfig(arquivo)

    def test_ajuste_win_oficial_fica_confirmado(self) -> None:
        config = self.criar_config(
            "2026-07-12;WIN;WINQ26;180250;;B3;ARQUIVO_OPERACIONAL;"
            "OFICIAL;ajuste oficial\n"
        )

        dados = config.carregar(
            ativo="WIN",
            contrato="WINQ26",
            data_referencia="2026-07-12",
        )

        self.assertTrue(dados["ajuste_origem_confirmada"])
        self.assertEqual(180250.0, dados["ajuste_diario"])
        self.assertFalse(dados["ptax_aplicavel_ao_ativo"])

    def test_ptax_wdo_oficial_fica_confirmada(self) -> None:
        config = self.criar_config(
            "2026-07-12;WDO;WDOQ26;5500.5;5.48;B3|BCB;"
            "ARQUIVO_OPERACIONAL;OFICIAL;referencias oficiais\n"
        )

        dados = config.carregar(
            ativo="WDO",
            contrato="WDOQ26",
            data_referencia="2026-07-12",
        )

        self.assertTrue(dados["ajuste_origem_confirmada"])
        self.assertTrue(dados["ptax_origem_confirmada"])
        self.assertTrue(dados["ptax_aplicavel_ao_ativo"])

    def test_status_pendente_bloqueia(self) -> None:
        config = self.criar_config(
            "2026-07-12;WIN;WINQ26;180250;;B3;MANUAL;"
            "PENDENTE_HOMOLOGACAO;pendente\n"
        )

        dados = config.carregar(
            ativo="WIN",
            contrato="WINQ26",
            data_referencia="2026-07-12",
        )

        self.assertFalse(dados["ajuste_origem_confirmada"])
        self.assertEqual("BLOQUEADA", dados["referencias_diarias_status"])

    def test_data_antiga_nao_e_reutilizada(self) -> None:
        config = self.criar_config(
            "2026-07-11;WIN;WINQ26;180250;;B3;MANUAL;"
            "OFICIAL;dia anterior\n"
        )

        dados = config.carregar(
            ativo="WIN",
            contrato="WINQ26",
            data_referencia="2026-07-12",
        )

        self.assertFalse(dados["ajuste_origem_confirmada"])
        self.assertEqual(
            "REFERENCIA_DIARIA_NAO_ENCONTRADA",
            dados["referencias_diarias_motivo"],
        )

    def test_contrato_diferente_nao_recebe_ajuste(self) -> None:
        config = self.criar_config(
            "2026-07-12;WIN;WINQ26;180250;;B3;MANUAL;"
            "OFICIAL;contrato correto\n"
        )

        dados = config.carregar(
            ativo="WIN",
            contrato="WINV26",
            data_referencia="2026-07-12",
        )

        self.assertFalse(dados["ajuste_origem_confirmada"])


if __name__ == "__main__":
    unittest.main()
