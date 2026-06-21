from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import csv


@dataclass
class ResultadoContratoAtivo:
    ativo_base: str
    data_referencia: str
    contrato_visual_esperado: str | None
    contrato_rtd_esperado: str | None
    mes_vencimento: str | None
    data_udn: str | None
    data_lf: str | None
    criterio_usado: str
    status_resolucao: str
    motivo: str


class ContratoAtivoResolver:
    """
    Resolve qual contrato futuro deveria estar ativo para uma data operacional.

    Responsabilidade unica:
    - Ler calendario oficial de contratos.
    - Resolver contrato esperado.
    - Nao altera Excel.
    - Nao le Profit.
    - Nao libera operacao.
    - Nao substitui o Bastiao.
    """

    def __init__(self, caminho_calendario: str | Path):
        self.caminho_calendario = Path(caminho_calendario)

    def resolver(self, ativo_base: str, data_referencia: str | date | None = None) -> ResultadoContratoAtivo:
        ativo_base = str(ativo_base).upper().strip()

        data_ref = self._normalizar_data(data_referencia)

        if not self.caminho_calendario.exists():
            return ResultadoContratoAtivo(
                ativo_base=ativo_base,
                data_referencia=data_ref.isoformat(),
                contrato_visual_esperado=None,
                contrato_rtd_esperado=None,
                mes_vencimento=None,
                data_udn=None,
                data_lf=None,
                criterio_usado="calendario_ausente",
                status_resolucao="CALENDARIO_AUSENTE",
                motivo=f"Calendario nao encontrado: {self.caminho_calendario}",
            )

        linhas = self._ler_linhas()

        if not linhas:
            return ResultadoContratoAtivo(
                ativo_base=ativo_base,
                data_referencia=data_ref.isoformat(),
                contrato_visual_esperado=None,
                contrato_rtd_esperado=None,
                mes_vencimento=None,
                data_udn=None,
                data_lf=None,
                criterio_usado="calendario_sem_linhas",
                status_resolucao="CALENDARIO_INCOMPLETO",
                motivo="Calendario existe, mas nao possui contratos preenchidos.",
            )

        candidatos = [
            linha for linha in linhas
            if str(linha.get("ativo_base", "")).upper().strip() == ativo_base
        ]

        if not candidatos:
            return ResultadoContratoAtivo(
                ativo_base=ativo_base,
                data_referencia=data_ref.isoformat(),
                contrato_visual_esperado=None,
                contrato_rtd_esperado=None,
                mes_vencimento=None,
                data_udn=None,
                data_lf=None,
                criterio_usado="ativo_nao_encontrado",
                status_resolucao="NAO_RESOLVIDO",
                motivo=f"Nenhuma linha encontrada para ativo_base={ativo_base}.",
            )

        # Criterio oficial provisório:
        # usar inicio_validade/fim_validade quando preenchidos.
        # Calendario sem essas datas ainda nao deve ser usado para decisao operacional.
        for linha in candidatos:
            inicio = self._parse_data(linha.get("inicio_validade"))
            fim = self._parse_data(linha.get("fim_validade"))

            if inicio and fim and inicio <= data_ref <= fim:
                return ResultadoContratoAtivo(
                    ativo_base=ativo_base,
                    data_referencia=data_ref.isoformat(),
                    contrato_visual_esperado=linha.get("contrato_visual") or None,
                    contrato_rtd_esperado=linha.get("contrato_rtd") or None,
                    mes_vencimento=linha.get("mes_vencimento") or None,
                    data_udn=linha.get("udn") or None,
                    data_lf=linha.get("lf") or None,
                    criterio_usado="janela_inicio_fim_validade",
                    status_resolucao="RESOLVIDO",
                    motivo="Contrato resolvido por janela oficial de validade.",
                )

        return ResultadoContratoAtivo(
            ativo_base=ativo_base,
            data_referencia=data_ref.isoformat(),
            contrato_visual_esperado=None,
            contrato_rtd_esperado=None,
            mes_vencimento=None,
            data_udn=None,
            data_lf=None,
            criterio_usado="sem_janela_valida",
            status_resolucao="DATA_FORA_DA_COBERTURA",
            motivo="Nao ha contrato com inicio_validade/fim_validade cobrindo a data informada.",
        )

    def _ler_linhas(self) -> list[dict]:
        with self.caminho_calendario.open("r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=";")
            return list(leitor)

    @staticmethod
    def _normalizar_data(valor: str | date | None) -> date:
        if valor is None:
            return date.today()

        if isinstance(valor, date):
            return valor

        return datetime.strptime(str(valor), "%Y-%m-%d").date()

    @staticmethod
    def _parse_data(valor) -> date | None:
        if valor is None:
            return None

        texto = str(valor).strip()

        if not texto:
            return None

        try:
            return datetime.strptime(texto, "%Y-%m-%d").date()
        except ValueError:
            return None


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    calendario = raiz / "config" / "calendarios" / "calendario_contratos_b3.csv"

    resolver = ContratoAtivoResolver(calendario)
    resultado = resolver.resolver("WIN")

    print(resultado)
