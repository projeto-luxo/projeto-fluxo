from pathlib import Path
import pandas as pd


class HistoriadorAdapter:
    """
    Adapter oficial do Historiador para o Motor de Confluência v2.

    Responsabilidade:
    - Ler saídas já produzidas pelo Historiador.
    - Entregar um pacote padronizado ao Motor de Confluência.
    - Não altera arquivos.
    - Não certifica.
    - Não gera ordem.
    """

    def __init__(self):
        self.trin_root = Path(__file__).resolve().parents[1]
        self.conhecimento = self.trin_root / "TRIN_HISTORICO" / "00_CONHECIMENTO"

        self.arq_padroes = self.conhecimento / "catalogo_padroes_historiador.csv"
        self.arq_contexto = self.conhecimento / "contexto_historiador.csv"
        self.arq_cobertura = self.conhecimento / "cobertura_temporal.csv"
        self.arq_fractais = self.conhecimento / "distribuicao_fractais.csv"

    def _ler_csv(self, caminho):
        if not caminho.exists():
            return pd.DataFrame()

        try:
            return pd.read_csv(
                caminho,
                sep=";",
                encoding="utf-8-sig",
                dtype=str,
                keep_default_na=False,
            )
        except Exception:
            return pd.DataFrame()

    def _num(self, valor, default=0.0):
        try:
            if valor is None:
                return default

            texto = str(valor).strip()

            if texto == "" or texto.upper() in ["N/D", "NONE", "NAN"]:
                return default

            texto = texto.replace(".", "").replace(",", ".")
            return float(texto)

        except Exception:
            return default

    def consultar(self, ativo=None, fractal=None, contexto=None):
        padroes = self._ler_csv(self.arq_padroes)
        contextos = self._ler_csv(self.arq_contexto)
        cobertura = self._ler_csv(self.arq_cobertura)
        fractais = self._ler_csv(self.arq_fractais)

        resposta = {
            "padrao": "SEM_PADRAO",
            "score_historico": 0.0,
            "confianca": 0.0,
            "frequencia": 0,
            "episodio": "SEM_EPISODIO",
            "contexto": contexto or "DESCONHECIDO",
            "direcao": "NEUTRO",
            "fonte": "HistoriadorAdapter",
            "status": "SEM_CONHECIMENTO",
        }

        if not padroes.empty:
            linha = padroes.iloc[0]

            resposta["padrao"] = str(
                linha.get("padrao", linha.get("nome", "PADRAO_CATALOGADO"))
            )

            resposta["episodio"] = str(
                linha.get("descricao", linha.get("episodio", "PADRAO_CATALOGADO"))
            )

            resposta["status"] = "PADRAO_CATALOGADO"

            texto = (
                resposta["padrao"] + " " +
                resposta["episodio"]
            ).upper()

            if "COMPRA" in texto or "ALTA" in texto:
                resposta["direcao"] = "COMPRA"
            elif "VENDA" in texto or "BAIXA" in texto:
                resposta["direcao"] = "VENDA"

            resposta["score_historico"] = 0.25
            resposta["confianca"] = 0.25
            resposta["frequencia"] = len(padroes)

        if not contextos.empty:
            resposta["contexto"] = str(
                contextos.iloc[0].get("contexto", resposta["contexto"])
            )

        if not cobertura.empty:
            if ativo and "ativo" in cobertura.columns:
                cobertura = cobertura[
                    cobertura["ativo"].astype(str).str.upper() == str(ativo).upper()
                ]

            if fractal and "fractal" in cobertura.columns:
                cobertura = cobertura[
                    cobertura["fractal"].astype(str).str.upper() == str(fractal).upper()
                ]

            if not cobertura.empty:
                resposta["score_historico"] = max(resposta["score_historico"], 0.35)
                resposta["confianca"] = max(resposta["confianca"], 0.35)
                resposta["status"] = "COBERTURA_ENCONTRADA"

        if not fractais.empty:
            resposta["frequencia"] = max(resposta["frequencia"], len(fractais))

        return resposta


if __name__ == "__main__":
    adapter = HistoriadorAdapter()

    print("=" * 70)
    print("TESTE HISTORIADOR ADAPTER v1.0")
    print("=" * 70)

    pacote = adapter.consultar(
        ativo="WIN",
        fractal="5_MIN",
        contexto="ABERTURA"
    )

    print(pacote)
