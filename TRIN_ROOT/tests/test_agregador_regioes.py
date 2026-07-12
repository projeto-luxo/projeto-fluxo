import unittest

from core.agregador_regioes import AgregadorRegioesRG02B


def referencia(
    chave: str,
    origem: str,
    valor: float,
    *,
    status: str = "ATIVA",
    limite_superior: float | None = None,
) -> dict:
    return {
        "chave_referencia": chave,
        "ativo": "WIN",
        "contrato": "WINQ26",
        "data_referencia": "2026-07-13",
        "sessao_referencia": "REGULAR",
        "origem_tipo": origem,
        "fornecedor": f"FONTE_{origem}",
        "campo_origem": origem,
        "timeframe_origem": "SESSAO",
        "limite_inferior": valor,
        "limite_superior": valor if limite_superior is None else limite_superior,
        "status": status,
        "status_certificacao": "OFICIAL",
    }


class AgregadorRegioesRG02BTest(unittest.TestCase):
    def setUp(self) -> None:
        self.agregador = AgregadorRegioesRG02B()

    def test_niveis_iguais_sao_agrupados(self) -> None:
        regioes = self.agregador.agregar(
            [
                referencia("REF-MILHAR", "MILHAR", 180000),
                referencia("REF-VWAP", "VWAP_OFICIAL", 180000),
            ]
        )
        self.assertEqual(1, len(regioes))
        self.assertEqual(2, regioes[0]["quantidade_origens"])

    def test_niveis_diferentes_permanecem_separados(self) -> None:
        regioes = self.agregador.agregar(
            [
                referencia("REF-1", "MILHAR", 180000),
                referencia("REF-2", "VWAP_OFICIAL", 180000.01),
            ]
        )
        self.assertEqual(2, len(regioes))

    def test_referencia_bloqueada_nao_forma_regiao(self) -> None:
        regioes = self.agregador.agregar(
            [referencia("REF-B", "AJUSTE_DIARIO", 175049, status="BLOQUEADA")]
        )
        self.assertEqual([], regioes)

    def test_origens_sao_preservadas(self) -> None:
        regioes = self.agregador.agregar(
            [
                referencia("REF-1", "MILHAR", 180000),
                referencia("REF-2", "VWAP_OFICIAL", 180000),
            ]
        )
        chaves = {item["chave_referencia"] for item in regioes[0]["origens"]}
        self.assertEqual({"REF-1", "REF-2"}, chaves)

    def test_chave_independe_da_ordem(self) -> None:
        refs = [
            referencia("REF-1", "MILHAR", 180000),
            referencia("REF-2", "VWAP_OFICIAL", 180000),
        ]
        chave_a = self.agregador.agregar(refs)[0]["chave_regiao"]
        chave_b = self.agregador.agregar(list(reversed(refs)))[0]["chave_regiao"]
        self.assertEqual(chave_a, chave_b)

    def test_referencia_duplicada_nao_duplica_origem(self) -> None:
        item = referencia("REF-1", "MILHAR", 180000)
        regioes = self.agregador.agregar([item, item])
        self.assertEqual(1, regioes[0]["quantidade_origens"])

    def test_faixas_iguais_sao_agrupadas(self) -> None:
        regioes = self.agregador.agregar(
            [
                referencia("REF-1", "FAIXA_A", 179900, limite_superior=180100),
                referencia("REF-2", "FAIXA_B", 179900, limite_superior=180100),
            ]
        )
        self.assertEqual(1, len(regioes))
        self.assertEqual(2, regioes[0]["quantidade_origens"])

    def test_saida_nao_contem_campos_operacionais(self) -> None:
        regiao = self.agregador.agregar(
            [referencia("REF-1", "MILHAR", 180000)]
        )[0]
        proibidos = {"entrada", "stop", "parcial", "alvo", "direcao", "forca", "confianca"}
        self.assertTrue(proibidos.isdisjoint(regiao))
        self.assertEqual("BLOQUEADO", regiao["uso_operacional"])


if __name__ == "__main__":
    unittest.main()
