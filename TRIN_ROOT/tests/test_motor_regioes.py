import unittest

from core.motor_regioes import ContextoReferencia, MotorRegioes


class MotorRegioesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.motor = MotorRegioes()
        self.contexto = ContextoReferencia(
            ativo="WIN",
            contrato="WINQ26",
            data_referencia="2026-07-12",
            sessao_referencia="REGULAR",
            modo_dados="AO_VIVO",
            timestamp_fonte="2026-07-12T10:00:00-03:00",
            timestamp_processamento="2026-07-12T10:00:01-03:00",
            qualidade_dados="QUALIFICADO",
            status_certificacao="FONTE_QUALIFICADA",
        )

    def payload_base(self) -> dict:
        return {
            "preco_atual": 178553,
            "preco_qualificado": True,
            "vwap_oficial": 178400,
            "vwap_fonte": "RTD_EXCEL_VWAP_REAL",
            "vwap_origem_confirmada": True,
            "ajuste_diario": 178120,
            "ajuste_fonte": "FONTE_EXPLICITA_AJUSTE",
            "ajuste_origem_confirmada": True,
            "ptax": 5.48,
            "ptax_fonte": "FONTE_EXPLICITA_PTAX",
            "ptax_origem_confirmada": True,
            "ptax_aplicavel_ao_ativo": False,
            "volume": 123456,
        }

    def test_quatro_provedores_estao_presentes(self) -> None:
        referencias = self.motor.localizar(
            self.payload_base(),
            self.contexto,
        )

        tipos = [item["origem_tipo"] for item in referencias]
        self.assertEqual(2, tipos.count("MILHAR"))
        self.assertIn("VWAP_OFICIAL", tipos)
        self.assertIn("AJUSTE_DIARIO", tipos)
        self.assertIn("PTAX", tipos)

    def test_vwap_engine_calculada_fica_bloqueada(self) -> None:
        payload = self.payload_base()
        payload["vwap_fonte"] = "VWAP_ENGINE_CALCULADA"

        referencias = self.motor.localizar(payload, self.contexto)
        vwap = next(
            item
            for item in referencias
            if item["origem_tipo"] == "VWAP_OFICIAL"
        )

        self.assertEqual("BLOQUEADA", vwap["status"])
        self.assertEqual(
            "VWAP_FONTE_NAO_HOMOLOGADA",
            vwap["motivo_status"],
        )

    def test_ajuste_diario_valido_fica_ativo(self) -> None:
        referencias = self.motor.localizar(
            self.payload_base(),
            self.contexto,
        )
        ajuste = next(
            item
            for item in referencias
            if item["origem_tipo"] == "AJUSTE_DIARIO"
        )

        self.assertEqual("ATIVA", ajuste["status"])
        self.assertEqual(178120.0, ajuste["limite_inferior"])

    def test_ptax_nao_aplicavel_fica_bloqueada(self) -> None:
        referencias = self.motor.localizar(
            self.payload_base(),
            self.contexto,
        )
        ptax = next(
            item
            for item in referencias
            if item["origem_tipo"] == "PTAX"
        )

        self.assertEqual("BLOQUEADA", ptax["status"])
        self.assertEqual(
            "PTAX_NAO_APLICAVEL_AO_ATIVO",
            ptax["motivo_status"],
        )

    def test_ptax_aplicavel_e_confirmada_fica_ativa(self) -> None:
        payload = self.payload_base()
        payload["ptax_aplicavel_ao_ativo"] = True

        referencias = self.motor.localizar(payload, self.contexto)
        ptax = next(
            item
            for item in referencias
            if item["origem_tipo"] == "PTAX"
        )

        self.assertEqual("ATIVA", ptax["status"])
        self.assertEqual(5.48, ptax["limite_inferior"])

    def test_timestamp_processamento_nao_muda_chave(self) -> None:
        referencias_1 = self.motor.localizar(
            self.payload_base(),
            self.contexto,
        )

        contexto_2 = ContextoReferencia(
            **{
                **self.contexto.__dict__,
                "timestamp_processamento": "2026-07-12T10:05:00-03:00",
            }
        )
        referencias_2 = self.motor.localizar(
            self.payload_base(),
            contexto_2,
        )

        chaves_1 = {
            item["origem_tipo"] + item["campo_origem"]:
            item["chave_referencia"]
            for item in referencias_1
        }
        chaves_2 = {
            item["origem_tipo"] + item["campo_origem"]:
            item["chave_referencia"]
            for item in referencias_2
        }

        self.assertEqual(chaves_1, chaves_2)

    def test_volume_bruto_nao_cria_referencia(self) -> None:
        referencias = self.motor.localizar(
            self.payload_base(),
            self.contexto,
        )
        tipos = {item["origem_tipo"] for item in referencias}

        self.assertNotIn("VOLUME", tipos)
        self.assertNotIn("PERFIL_VOLUME", tipos)

    def test_saida_nao_possui_campos_operacionais(self) -> None:
        referencias = self.motor.localizar(
            self.payload_base(),
            self.contexto,
        )
        proibidos = {
            "entrada",
            "stop",
            "parcial",
            "alvo",
            "direcao_provavel",
            "forca",
            "confianca",
        }

        for item in referencias:
            self.assertTrue(proibidos.isdisjoint(item))
            self.assertEqual("BLOQUEADO", item["uso_operacional"])


if __name__ == "__main__":
    unittest.main()
