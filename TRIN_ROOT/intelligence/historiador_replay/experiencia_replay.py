from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .erros import FalhaReplay
from .util.hash_sha256 import sha256_bytes
from .util.json_canonico import json_canonico_bytes

ORIGEM_REPLAY = "ORIGEM_REPLAY"
_DIRECOES = {"COMPRA", "VENDA"}
_QUANT = Decimal("0.01")


def _decimal(valor: Any, campo: str) -> Decimal:
    try:
        return Decimal(str(valor)).quantize(_QUANT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise FalhaReplay("VALOR_EXPERIENCIA_INVALIDO", campo) from exc


def _texto_decimal(valor: Decimal) -> str:
    return f"{valor.quantize(_QUANT, rounding=ROUND_HALF_UP):.2f}"


def _direcao_explicita(hipotese: Mapping[str, Any] | None) -> str | None:
    if not hipotese:
        return None
    valor = hipotese.get("direcao")
    if valor is None:
        valor = hipotese.get("direcao_fornecida")
    if valor is None or str(valor).strip() == "":
        return None
    normalizada = str(valor).strip().upper()
    if normalizada not in _DIRECOES:
        raise FalhaReplay("DIRECAO_EXPLICITA_INVALIDA", normalizada)
    return normalizada


@dataclass(frozen=True)
class ExperienciaReplayV1:
    experiencia_id: str
    contrato: str
    versao: str
    origem_tipo: str
    solicitacao_id: str
    origem_id: str
    origem_hash: str
    timestamp_referencia: str
    ordinal_referencia: int
    fato: dict[str, Any]
    contexto: dict[str, Any]
    hipotese: dict[str, Any]
    resultado: dict[str, Any]

    def como_dict(self) -> dict[str, Any]:
        return deepcopy(asdict(self))

    def verificar_integridade(self) -> None:
        dados = self.como_dict()
        recebido = dados.pop("experiencia_id")
        esperado = sha256_bytes(json_canonico_bytes(dados))
        if recebido != esperado:
            raise FalhaReplay("EXPERIENCIA_ID_DIVERGENTE")
        if self.origem_tipo != ORIGEM_REPLAY:
            raise FalhaReplay("ORIGEM_REPLAY_OBRIGATORIA")
        if not all(isinstance(getattr(self, nome), dict) for nome in ("fato", "contexto", "hipotese", "resultado")):
            raise FalhaReplay("COMPARTIMENTOS_EXPERIENCIA_INVALIDOS")
        if self.hipotese.get("direcao") not in {None, "COMPRA", "VENDA"}:
            raise FalhaReplay("DIRECAO_EXPERIENCIA_INVALIDA")


def construir_experiencia_replay(
    contextos: Sequence[Mapping[str, Any]],
    *,
    ordinal_referencia: int,
    hipotese: Mapping[str, Any] | None,
    tamanho_janela_posterior: int,
) -> ExperienciaReplayV1:
    """Constrói experiência determinística sem mutar contextos nem integrar motores.

    A hipótese é entrada explícita. Direção ausente permanece ``None`` e, nesse
    caso, MFE/MAE não são fabricados. A janela posterior é definida somente por
    ordinais imediatamente posteriores ao evento de referência.
    """

    if tamanho_janela_posterior < 1:
        raise FalhaReplay("JANELA_POSTERIOR_INVALIDA")
    if not contextos:
        raise FalhaReplay("CONTEXTOS_REPLAY_AUSENTES")

    copia = [deepcopy(dict(item)) for item in contextos]
    por_ordinal = {int(item["ordinal_evento"]): item for item in copia}
    referencia = por_ordinal.get(ordinal_referencia)
    if referencia is None:
        raise FalhaReplay("ORDINAL_REFERENCIA_AUSENTE", str(ordinal_referencia))

    ordinais = list(range(ordinal_referencia + 1, ordinal_referencia + 1 + tamanho_janela_posterior))
    posteriores = [por_ordinal[o] for o in ordinais if o in por_ordinal]
    janela_completa = len(posteriores) == tamanho_janela_posterior

    direcao = _direcao_explicita(hipotese)
    hipotese_saida = deepcopy(dict(hipotese or {}))
    hipotese_saida["direcao"] = direcao
    hipotese_saida.setdefault("origem_direcao", None)
    hipotese_saida["direcao_inventada"] = False

    evento = deepcopy(referencia["evento_atual"])
    preco = _decimal(evento["ultimo"], "evento_atual.ultimo")

    resultado: dict[str, Any] = {
        "regra_janela_posterior": f"{tamanho_janela_posterior}_EVENTOS_IMEDIATAMENTE_POSTERIORES",
        "janela_posterior_ordinais": [int(item["ordinal_evento"]) for item in posteriores],
        "janela_posterior_completa": janela_completa,
        "mfe_pontos": None,
        "mae_pontos": None,
        "status_metricas": "SEM_DIRECAO" if direcao is None else "JANELA_INCOMPLETA",
    }

    if direcao is not None and janela_completa:
        maximos = [_decimal(item["evento_atual"]["maximo"], "janela.maximo") for item in posteriores]
        minimos = [_decimal(item["evento_atual"]["minimo"], "janela.minimo") for item in posteriores]
        if direcao == "COMPRA":
            mfe = max(maximos) - preco
            mae = preco - min(minimos)
        else:
            mfe = preco - min(minimos)
            mae = max(maximos) - preco
        resultado.update(
            {
                "mfe_pontos": _texto_decimal(mfe),
                "mae_pontos": _texto_decimal(mae),
                "status_metricas": "CALCULADO",
            }
        )

    fato = {
        "timestamp": referencia["timestamp_evento"],
        "ordinal": ordinal_referencia,
        "evento": evento,
    }
    contexto = {
        "origem_id": referencia["origem_id"],
        "origem_hash": referencia["origem_hash"],
        "periodo_solicitado": deepcopy(referencia["periodo_solicitado"]),
        "sessao": deepcopy(referencia["sessao"]),
        "janela_anterior": deepcopy(referencia["janela_anterior"]),
        "tamanho_janela_posterior": tamanho_janela_posterior,
    }

    corpo = {
        "contrato": "ExperienciaReplayV1",
        "versao": "1.0.0",
        "origem_tipo": ORIGEM_REPLAY,
        "solicitacao_id": referencia["solicitacao_id"],
        "origem_id": referencia["origem_id"],
        "origem_hash": referencia["origem_hash"],
        "timestamp_referencia": referencia["timestamp_evento"],
        "ordinal_referencia": ordinal_referencia,
        "fato": fato,
        "contexto": contexto,
        "hipotese": hipotese_saida,
        "resultado": resultado,
    }
    experiencia = ExperienciaReplayV1(
        experiencia_id=sha256_bytes(json_canonico_bytes(corpo)),
        **corpo,
    )
    experiencia.verificar_integridade()
    return experiencia


class RepositorioExperiencias:
    """Repositório aditivo e consultável, sem integração automática externa.

    Sem ``caminho_jsonl`` funciona apenas em memória. Quando um caminho é
    informado, cada experiência inédita é anexada como JSON canônico em uma
    linha. O chamador escolhe explicitamente o destino controlado.
    """

    def __init__(self, caminho_jsonl: Path | str | None = None) -> None:
        self._caminho = Path(caminho_jsonl).resolve() if caminho_jsonl is not None else None
        self._itens: dict[str, dict[str, Any]] = {}
        if self._caminho is not None and self._caminho.exists():
            for numero, linha in enumerate(self._caminho.read_text(encoding="utf-8").splitlines(), start=1):
                if not linha.strip():
                    continue
                try:
                    item = json.loads(linha)
                    self._itens[item["experiencia_id"]] = item
                except Exception as exc:
                    raise FalhaReplay("REPOSITORIO_EXPERIENCIAS_CORROMPIDO", str(numero)) from exc

    def registrar_experiencia(self, experiencia: ExperienciaReplayV1 | Mapping[str, Any]) -> dict[str, Any]:
        if isinstance(experiencia, ExperienciaReplayV1):
            experiencia.verificar_integridade()
            dados = experiencia.como_dict()
        else:
            dados = deepcopy(dict(experiencia))
            identificador = dados.get("experiencia_id")
            if not isinstance(identificador, str):
                raise FalhaReplay("EXPERIENCIA_ID_AUSENTE")
            corpo = deepcopy(dados)
            corpo.pop("experiencia_id", None)
            if identificador != sha256_bytes(json_canonico_bytes(corpo)):
                raise FalhaReplay("EXPERIENCIA_ID_DIVERGENTE")

        identificador = dados["experiencia_id"]
        existente = self._itens.get(identificador)
        if existente is not None:
            if existente != dados:
                raise FalhaReplay("EXPERIENCIA_ID_COLISAO")
            return deepcopy(existente)

        self._itens[identificador] = deepcopy(dados)
        if self._caminho is not None:
            self._caminho.parent.mkdir(parents=True, exist_ok=True)
            with self._caminho.open("ab") as destino:
                destino.write(json_canonico_bytes(dados) + b"\n")
        return deepcopy(dados)

    def consultar_experiencia(self, experiencia_id: str) -> dict[str, Any] | None:
        item = self._itens.get(experiencia_id)
        return deepcopy(item) if item is not None else None

    def consultar_experiencias(
        self,
        *,
        origem_id: str | None = None,
        direcao: str | None = None,
    ) -> list[dict[str, Any]]:
        resultado: list[dict[str, Any]] = []
        for item in self._itens.values():
            if origem_id is not None and item["origem_id"] != origem_id:
                continue
            if direcao is not None and item["hipotese"].get("direcao") != direcao:
                continue
            resultado.append(deepcopy(item))
        return sorted(resultado, key=lambda x: (x["timestamp_referencia"], x["experiencia_id"]))


def registrar_experiencia(
    repositorio: RepositorioExperiencias,
    experiencia: ExperienciaReplayV1 | Mapping[str, Any],
) -> dict[str, Any]:
    return repositorio.registrar_experiencia(experiencia)


def consultar_experiencia(
    repositorio: RepositorioExperiencias,
    experiencia_id: str,
) -> dict[str, Any] | None:
    return repositorio.consultar_experiencia(experiencia_id)


def consultar_experiencias(
    repositorio: RepositorioExperiencias,
    *,
    origem_id: str | None = None,
    direcao: str | None = None,
) -> list[dict[str, Any]]:
    return repositorio.consultar_experiencias(origem_id=origem_id, direcao=direcao)
