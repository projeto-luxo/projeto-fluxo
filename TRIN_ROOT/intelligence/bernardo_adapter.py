from pathlib import Path
import pandas as pd


class BernardoAdapter:
    """
    Adapter oficial do Bernardo para o Motor de Confluência v2.

    Responsabilidade:
    - Consultar saídas cognitivas já produzidas pelo Bernardo.
    - Entregar pacote padronizado ao Motor.
    - Não altera memória.
    - Não escreve arquivos.
    - Não certifica.
    - Não gera sinais.
    """

    def __init__(self):
        self.trin_root = Path(__file__).resolve().parents[1]
        self.historico = self.trin_root / "TRIN_HISTORICO"
        self.indices = self.historico / "00_INDICES"
        self.conhecimento = self.historico / "00_CONHECIMENTO"

        self.arq_pacote_historiador = self.indices / "pacote_historiador.csv"
        self.arq_contexto = self.conhecimento / "contexto_historiador.csv"
        self.arq_padroes = self.conhecimento / "catalogo_padroes_historiador.csv"

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

    def consultar(self, ativo=None, fractal=None, contexto=None, padrao=None):
        pacote = self._ler_csv(self.arq_pacote_historiador)
        contextos = self._ler_csv(self.arq_contexto)
        padroes = self._ler_csv(self.arq_padroes)

        resposta = {
            "episodio_semelhante": False,
            "similaridade": 0.0,
            "ocorrencias": 0,
            "resultado_medio": "DESCONHECIDO",
            "confianca": 0.0,
            "direcao": "NEUTRO",
            "contexto": contexto or "DESCONHECIDO",
            "padrao": padrao or "SEM_PADRAO",
            "fonte": "BernardoAdapter",
            "status": "SEM_MEMORIA_COMPATIVEL",
        }

        if not pacote.empty:
            df = pacote.copy()

            if ativo and "ativo" in df.columns:
                df = df[df["ativo"].astype(str).str.upper() == str(ativo).upper()]

            if fractal and "fractal" in df.columns:
                df = df[df["fractal"].astype(str).str.upper() == str(fractal).upper()]

            if not df.empty:
                resposta["episodio_semelhante"] = True
                resposta["ocorrencias"] = len(df)
                resposta["similaridade"] = min(0.95, 0.40 + (len(df) / 100))
                resposta["confianca"] = min(0.90, 0.30 + (len(df) / 120))
                resposta["status"] = "MEMORIA_ENCONTRADA"

        if not padroes.empty:
            linha = padroes.iloc[0]

            resposta["padrao"] = str(
                linha.get("padrao", linha.get("nome", resposta["padrao"]))
            )

            descricao = str(
                linha.get("descricao", linha.get("episodio", ""))
            ).upper()

            texto = (resposta["padrao"] + " " + descricao).upper()

            if "COMPRA" in texto or "ALTA" in texto:
                resposta["direcao"] = "COMPRA"
                resposta["resultado_medio"] = "CONTINUIDADE_COMPRADORA"
            elif "VENDA" in texto or "BAIXA" in texto:
                resposta["direcao"] = "VENDA"
                resposta["resultado_medio"] = "CONTINUIDADE_VENDEDORA"
            else:
                resposta["direcao"] = "NEUTRO"
                resposta["resultado_medio"] = "PADRAO_CATALOGADO"

            resposta["episodio_semelhante"] = True
            resposta["ocorrencias"] = max(resposta["ocorrencias"], len(padroes))
            resposta["similaridade"] = max(resposta["similaridade"], 0.35)
            resposta["confianca"] = max(resposta["confianca"], 0.35)

            if resposta["status"] == "SEM_MEMORIA_COMPATIVEL":
                resposta["status"] = "PADRAO_COGNITIVO_ENCONTRADO"

        if not contextos.empty:
            resposta["contexto"] = str(
                contextos.iloc[0].get("contexto", resposta["contexto"])
            )

        return resposta


if __name__ == "__main__":
    adapter = BernardoAdapter()

    print("=" * 70)
    print("TESTE BERNARDO ADAPTER v1.0")
    print("=" * 70)

    pacote = adapter.consultar(
        ativo="WIN",
        fractal="5_MIN",
        contexto="ABERTURA",
        padrao="REVERSAO_VWAP",
    )

    print(pacote)
