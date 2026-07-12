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
            "abertura_sessao": 180100,
            "abertura_fonte": "RTD_EXCEL_ABERTURA",
            "abertura_origem_confirmada": True,
            "maxima_sessao": 181250,
            "maxima_fonte": "RTD_EXCEL_MAXIMA",
            "maxima_origem_confirmada": True,
            "minima_sessao": 179500,
            "minima_fonte": "RTD_EXCEL_MINIMA",
            "minima_origem_confirmada": True,
            "volume": 123456,
        }

    def test_sete_provedores_estao_presentes(self) -> None:
        referencias = self.motor.localizar(
            self.payload_base(),
            self.contexto,
        )

        tipos = [item["origem_tipo"] for item in referencias]
        self.assertEqual(2, tipos.count("MILHAR"))
        self.assertIn("VWAP_OFICIAL", tipos)
        self.assertIn("AJUSTE_DIARIO", tipos)
        self.assertIn("PTAX", tipos)
        self.assertIn("ABERTURA_SESSAO", tipos)
        self.assertIn("MAXIMA_SESSAO", tipos)
        self.assertIn("MINIMA_SESSAO", tipos)

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


    def test_referencias_de_sessao_confirmadas_ficam_ativas(self) -> None:
        referencias = self.motor.localizar(
            self.payload_base(),
            self.contexto,
        )

        por_tipo = {
            item["origem_tipo"]: item
            for item in referencias
        }

        self.assertEqual("ATIVA", por_tipo["ABERTURA_SESSAO"]["status"])
        self.assertEqual("ATIVA", por_tipo["MAXIMA_SESSAO"]["status"])
        self.assertEqual("ATIVA", por_tipo["MINIMA_SESSAO"]["status"])
        self.assertEqual(
            180100.0,
            por_tipo["ABERTURA_SESSAO"]["limite_inferior"],
        )

    def test_abertura_sem_confirmacao_fica_bloqueada(self) -> None:
        payload = self.payload_base()
        payload["abertura_origem_confirmada"] = False

        referencias = self.motor.localizar(payload, self.contexto)
        abertura = next(
            item
            for item in referencias
            if item["origem_tipo"] == "ABERTURA_SESSAO"
        )

        self.assertEqual("BLOQUEADA", abertura["status"])
        self.assertEqual(
            "ABERTURA_SESSAO_ORIGEM_NAO_CONFIRMADA",
            abertura["motivo_status"],
        )

    def test_maxima_ou_minima_invalidas_ficam_bloqueadas(self) -> None:
        payload = self.payload_base()
        payload["maxima_sessao"] = None
        payload["minima_sessao"] = 0

        referencias = self.motor.localizar(payload, self.contexto)
        por_tipo = {
            item["origem_tipo"]: item
            for item in referencias
        }

        self.assertEqual("BLOQUEADA", por_tipo["MAXIMA_SESSAO"]["status"])
        self.assertEqual("BLOQUEADA", por_tipo["MINIMA_SESSAO"]["status"])

if __name__ == "__main__":
    unittest.main()
