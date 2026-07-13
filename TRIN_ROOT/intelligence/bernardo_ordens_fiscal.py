from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


class BernardoOrdensFiscal:
    """Recebe ordens do Fiscal e registra somente o recebimento seguro."""

    COLUNAS_RESPOSTA = [
        "id_ocorrencia", "status_ordem", "responsavel",
        "acao_executada", "observacao", "data_resposta",
    ]

    def __init__(
        self,
        arquivo_ordens: Path | None = None,
        arquivo_respostas: Path | None = None,
    ) -> None:
        root = Path(__file__).resolve().parents[1]
        cert = root / "TRIN_HISTORICO" / "00_CERTIFICACOES"
        self.arquivo_ordens = arquivo_ordens or cert / "ordens_para_bernardo.csv"
        self.arquivo_respostas = arquivo_respostas or cert / "respostas_bernardo.csv"

    def _ler_ordens(self) -> tuple[pd.DataFrame, str | None]:
        if not self.arquivo_ordens.exists():
            return pd.DataFrame(), "ARQUIVO_ORDENS_INDISPONIVEL"
        try:
            return pd.read_csv(
                self.arquivo_ordens, sep=";", encoding="utf-8-sig",
                dtype=str, keep_default_na=False,
            ), None
        except pd.errors.EmptyDataError:
            return pd.DataFrame(), None
        except Exception as erro:
            return pd.DataFrame(), str(erro)

    def processar(self, gravar: bool = True) -> dict[str, Any]:
        ordens, erro = self._ler_ordens()
        if erro:
            return {
                "status": "ERRO_LEITURA_ORDENS_FISCAL",
                "erro": erro,
                "quantidade": 0,
                "respostas": [],
            }

        respostas: list[dict[str, str]] = []
        if not ordens.empty:
            if "id_ocorrencia" not in ordens.columns:
                return {
                    "status": "SCHEMA_ORDENS_FISCAL_INVALIDO",
                    "colunas_ausentes": ["id_ocorrencia"],
                    "quantidade": 0,
                    "respostas": [],
                }
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            for _, ordem in ordens.iterrows():
                identificador = str(ordem.get("id_ocorrencia", "")).strip()
                if not identificador:
                    continue
                respostas.append({
                    "id_ocorrencia": identificador,
                    "status_ordem": "EM_ANALISE",
                    "responsavel": "BERNARDO",
                    "acao_executada": "ORDEM_RECEBIDA_PARA_ANALISE",
                    "observacao": (
                        "Nenhuma correcao, recertificacao ou encerramento "
                        "foi declarado automaticamente."
                    ),
                    "data_resposta": agora,
                })

        frame = pd.DataFrame(respostas, columns=self.COLUNAS_RESPOSTA)
        if gravar:
            self.arquivo_respostas.parent.mkdir(parents=True, exist_ok=True)
            frame.to_csv(
                self.arquivo_respostas, sep=";", index=False,
                encoding="utf-8-sig",
            )

        return {
            "status": "ORDENS_RECEBIDAS_EM_ANALISE" if respostas else "SEM_ORDENS_PENDENTES",
            "quantidade": len(respostas),
            "respostas": respostas,
            "arquivo_respostas": str(self.arquivo_respostas),
        }


if __name__ == "__main__":
    print(BernardoOrdensFiscal().processar())
