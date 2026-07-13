from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


class BernardoAdapter:
    """Interface oficial de leitura do Bernardo."""

    COLUNAS_PACOTE_MOTOR = {
        "tipo", "nome", "categoria", "maturidade",
        "peso_inicial_sugerido", "uso",
    }

    def __init__(self) -> None:
        self.trin_root = Path(__file__).resolve().parents[1]
        self.historico = self.trin_root / "TRIN_HISTORICO"
        self.indices = self.historico / "00_INDICES"
        self.arq_pacote_motor = self.indices / "pacote_motor_confluencia.csv"
        self.arq_indice_geral = self.indices / "indice_geral.csv"

    def _ler_csv(self, caminho: Path) -> tuple[pd.DataFrame, str | None]:
        if not caminho.exists():
            return pd.DataFrame(), "ARQUIVO_INDISPONIVEL"
        try:
            return pd.read_csv(
                caminho, sep=";", encoding="utf-8-sig",
                dtype=str, keep_default_na=False,
            ), None
        except Exception as erro:
            return pd.DataFrame(), str(erro)

    @staticmethod
    def _base(contexto: str | None, padrao: str | None) -> dict[str, Any]:
        return {
            "episodio_semelhante": False,
            "similaridade": 0.0,
            "ocorrencias": 0,
            "resultado_medio": "CONHECIMENTO_NAO_DIRECIONAL",
            "confianca": 0.0,
            "direcao": "NEUTRO",
            "contexto": contexto or "DESCONHECIDO",
            "padrao": padrao or "SEM_PADRAO",
            "fonte": "BERNARDO_PACOTE_MOTOR_CONFLUENCIA",
            "status": "PACOTE_BERNARDO_INDISPONIVEL",
            "item_canonico": None,
        }

    @staticmethod
    def _filtrar(pacote: pd.DataFrame, contexto: str | None, padrao: str | None) -> pd.DataFrame:
        termos = [
            str(v).strip().upper()
            for v in (contexto, padrao)
            if v and str(v).strip()
        ]
        if not termos:
            return pacote
        cols = [c for c in ["tipo", "nome", "categoria", "uso"] if c in pacote.columns]
        if not cols:
            return pacote.iloc[0:0]
        texto = pacote[cols].astype(str).agg(" ".join, axis=1).str.upper()
        mask = pd.Series(False, index=pacote.index)
        for termo in termos:
            mask = mask | texto.str.contains(termo, regex=False, na=False)
        return pacote[mask]

    def consultar(
        self,
        ativo: str | None = None,
        fractal: str | None = None,
        contexto: str | None = None,
        padrao: str | None = None,
    ) -> dict[str, Any]:
        resposta = self._base(contexto, padrao)
        resposta["ativo_consultado"] = ativo or "NAO_INFORMADO"
        resposta["fractal_consultado"] = fractal or "NAO_INFORMADO"

        pacote, erro = self._ler_csv(self.arq_pacote_motor)
        if erro:
            resposta["status"] = (
                "PACOTE_BERNARDO_INDISPONIVEL"
                if erro == "ARQUIVO_INDISPONIVEL"
                else "ERRO_LEITURA_PACOTE_BERNARDO"
            )
            resposta["erro"] = erro
            return resposta

        ausentes = sorted(self.COLUNAS_PACOTE_MOTOR - set(pacote.columns))
        if ausentes:
            resposta["status"] = "SCHEMA_PACOTE_BERNARDO_INVALIDO"
            resposta["colunas_ausentes"] = ausentes
            return resposta
        if pacote.empty:
            resposta["status"] = "PACOTE_BERNARDO_VAZIO"
            return resposta

        compativeis = self._filtrar(pacote, contexto, padrao)
        selecionado = compativeis if not compativeis.empty else pacote
        linha = selecionado.iloc[0]

        resposta.update({
            "ocorrencias": int(len(selecionado)),
            "padrao": str(linha.get("nome", resposta["padrao"])),
            "status": (
                "PACOTE_COGNITIVO_COMPATIVEL"
                if not compativeis.empty
                else "PACOTE_COGNITIVO_DISPONIVEL"
            ),
            "item_canonico": {
                "tipo": str(linha.get("tipo", "")),
                "nome": str(linha.get("nome", "")),
                "categoria": str(linha.get("categoria", "")),
                "maturidade": str(linha.get("maturidade", "")),
                "peso_inicial_sugerido": str(linha.get("peso_inicial_sugerido", "")),
                "uso": str(linha.get("uso", "")),
            },
        })
        return resposta

    def consultar_indice(
        self,
        ativo: str | None = None,
        fractal: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        indice, erro = self._ler_csv(self.arq_indice_geral)
        if erro:
            return {
                "status": (
                    "INDICE_BERNARDO_INDISPONIVEL"
                    if erro == "ARQUIVO_INDISPONIVEL"
                    else "ERRO_LEITURA_INDICE_BERNARDO"
                ),
                "fonte": "BERNARDO_INDICE_GERAL",
                "registros": [],
                "erro": erro,
            }

        resultado = indice.copy()
        for coluna, valor in {"ativo": ativo, "fractal": fractal, "status": status}.items():
            if valor and coluna in resultado.columns:
                resultado = resultado[
                    resultado[coluna].astype(str).str.upper() == str(valor).upper()
                ]

        return {
            "status": "INDICE_BERNARDO_DISPONIVEL",
            "fonte": "BERNARDO_INDICE_GERAL",
            "quantidade": int(len(resultado)),
            "registros": resultado.to_dict(orient="records"),
        }


if __name__ == "__main__":
    print(BernardoAdapter().consultar())
