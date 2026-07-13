from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from intelligence import bernardo_bibliotecario_v4_0 as bernardo


class BernardoPacoteZeRastreavelTest(unittest.TestCase):
    def test_pacote_e_manifesto_possuem_rastreabilidade(self) -> None:
        with tempfile.TemporaryDirectory() as pasta:
            base = Path(pasta)

            originais = {
                "ARQ_INDICE": bernardo.ARQ_INDICE,
                "ARQ_AUTOINSPECAO": bernardo.ARQ_AUTOINSPECAO,
                "ARQ_PACOTE_HISTORIADOR": bernardo.ARQ_PACOTE_HISTORIADOR,
                "ARQ_PACOTE_ZE_EUCRAZIO": bernardo.ARQ_PACOTE_ZE_EUCRAZIO,
                "ARQ_PACOTE_MOTOR_CONFLUENCIA": bernardo.ARQ_PACOTE_MOTOR_CONFLUENCIA,
                "ARQ_MANIFESTO_PACOTE_ZE": bernardo.ARQ_MANIFESTO_PACOTE_ZE,
            }

            try:
                bernardo.ARQ_INDICE = str(base / "indice_geral.csv")
                bernardo.ARQ_AUTOINSPECAO = str(base / "autoinspecao_bernardo.csv")
                bernardo.ARQ_PACOTE_HISTORIADOR = str(base / "pacote_historiador.csv")
                bernardo.ARQ_PACOTE_ZE_EUCRAZIO = str(base / "pacote_ze_eucrazio.csv")
                bernardo.ARQ_PACOTE_MOTOR_CONFLUENCIA = str(base / "pacote_motor_confluencia.csv")
                bernardo.ARQ_MANIFESTO_PACOTE_ZE = str(base / "manifesto_pacote_ze_bernardo.json")

                indice = pd.DataFrame([{"fractal": "1_MIN", "ativo": "WIN"}])
                indice.to_csv(
                    bernardo.ARQ_INDICE,
                    sep=";",
                    index=False,
                    encoding="utf-8-sig",
                )

                pd.DataFrame(
                    [{"item": "PACOTE", "status": "OK", "gravidade": "BAIXA"}]
                ).to_csv(
                    bernardo.ARQ_AUTOINSPECAO,
                    sep=";",
                    index=False,
                    encoding="utf-8-sig",
                )

                vazio = pd.DataFrame()

                bernardo.gerar_pacotes_modulos_futuros(
                    indice=indice,
                    relatorio_memoria_estatistica=vazio,
                    ranking_historico=vazio,
                    banco_reversoes=pd.DataFrame(
                        columns=["elegivel_para_historiador"]
                    ),
                    memoria_por_assunto=pd.DataFrame(
                        columns=["assunto", "categoria", "maturidade_assunto"]
                    ),
                    rede_semantica=vazio,
                    biblioteca_conceitual=pd.DataFrame(
                        columns=["tipo", "nome", "categoria", "maturidade"]
                    ),
                )

                pacote = pd.read_csv(
                    bernardo.ARQ_PACOTE_ZE_EUCRAZIO,
                    sep=";",
                    encoding="utf-8-sig",
                    dtype=str,
                )

                obrigatorias = {
                    "versao_bernardo",
                    "id_execucao_bernardo",
                    "hash_indice_bernardo",
                    "status_autoinspecao_bernardo",
                    "manifesto_rastreabilidade",
                }

                self.assertTrue(obrigatorias.issubset(pacote.columns))
                self.assertEqual(
                    set(pacote["status_autoinspecao_bernardo"]),
                    {"APROVADA"},
                )

                manifesto = json.loads(
                    Path(bernardo.ARQ_MANIFESTO_PACOTE_ZE).read_text(
                        encoding="utf-8"
                    )
                )

                hash_real = hashlib.sha256(
                    Path(bernardo.ARQ_PACOTE_ZE_EUCRAZIO).read_bytes()
                ).hexdigest()

                self.assertEqual(
                    manifesto["hash_sha256_pacote_ze_bernardo"],
                    hash_real,
                )
                self.assertEqual(manifesto["quantidade_itens"], len(pacote))
                self.assertEqual(
                    manifesto["status_autoinspecao_bernardo"],
                    "APROVADA",
                )
            finally:
                for nome, valor in originais.items():
                    setattr(bernardo, nome, valor)


if __name__ == "__main__":
    unittest.main()
