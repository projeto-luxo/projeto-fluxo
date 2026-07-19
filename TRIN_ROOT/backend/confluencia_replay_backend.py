from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import tempfile
import threading
from concurrent.futures import Future, TimeoutError as FutureTimeoutError
from pathlib import Path
from typing import Any, Callable, Mapping

from jsonschema import Draft202012Validator, FormatChecker

from intelligence.fiscal_adapter import FiscalAdapter

CONTRATO_BACKEND = "ConfluenciaReplayBackendV1"
VERSAO_BACKEND = "1.0.0"
ORIGEM_REPLAY = "ORIGEM_REPLAY"
MODO_SOMBRA = "SOMBRA"
PESO_ZERO = 0
IMPACTO_ZERO = 0
OPERACIONAL = False
STATUS_P04A = {"COMPLETO", "PARCIAL", "SEM_EVIDENCIA", "INSUFICIENTE", "BLOQUEADO"}
STATUS_BACKEND = STATUS_P04A | {"INDISPONIVEL", "ERRO_DIAGNOSTICO"}
P04A_SCHEMA_HEAD_BLOB_SHA1 = "576a858ffd8522263dcabb7154413ab30f4e8c90"
P04A_SCHEMA_SHA256_ALLOWED = frozenset({
    "4ab9eacce02720649c8016af052904ed57ea17b20f7013c4d6bc3aa8f654661a",  # blob/checkout LF
    "ae3073a30edf260bc7f04afcbd486b7a5b183783c43e33d7b8afef2f1bcd2835",  # checkout/sandbox CRLF comprovado no Windows
})
FONTE_FISCAL_OFICIAL = "FISCAL_TEMPORAL_LAUDO_OFICIAL"
FONTE_REGIME_OFICIAL = "HISTORIADOR_REPLAY_CONTEXTO_OFICIAL"


class FalhaIntegracaoP04B(RuntimeError):
    def __init__(self, codigo: str, detalhe: str = "") -> None:
        self.codigo = codigo
        self.detalhe = detalhe
        super().__init__(f"{codigo}: {detalhe}" if detalhe else codigo)


class ExecutorDiagnosticoLimitado:
    _contador_instancias = 0
    """No máximo uma avaliação em thread daemon, sem fila e sem acúmulo.

    Timeout não cria outro trabalhador. Se a avaliação ficar bloqueada para
    sempre, chamadas seguintes falham fechado com P04B_AVALIADOR_OCUPADO e
    nenhuma nova thread é criada. A thread é daemon para não impedir o
    encerramento controlado do processo do backend.
    """

    def __init__(self) -> None:
        type(self)._contador_instancias += 1
        self.thread_prefix = f"trin-p04b-{type(self)._contador_instancias}"
        self._lock = threading.Lock()
        self._future: Future[dict[str, Any]] | None = None
        self._thread: threading.Thread | None = None

    def _limpar_concluido(self) -> None:
        if self._thread is not None and not self._thread.is_alive():
            self._thread = None
            self._future = None

    def executar(
        self,
        funcao: Callable[[], dict[str, Any]],
        timeout_segundos: float,
    ) -> dict[str, Any]:
        if timeout_segundos <= 0:
            raise FalhaIntegracaoP04B("P04B_TIMEOUT_INVALIDO", str(timeout_segundos))

        with self._lock:
            self._limpar_concluido()
            if self._thread is not None and self._thread.is_alive():
                raise FalhaIntegracaoP04B(
                    "P04B_AVALIADOR_OCUPADO",
                    "Uma avaliação anterior continua em execução; nenhuma nova tarefa foi criada.",
                )
            future: Future[dict[str, Any]] = Future()

            def alvo() -> None:
                try:
                    future.set_result(funcao())
                except BaseException as exc:  # preserva a exceção para a chamada solicitante
                    future.set_exception(exc)

            thread = threading.Thread(
                target=alvo,
                name=self.thread_prefix,
                daemon=True,
            )
            self._future = future
            self._thread = thread
            thread.start()

        try:
            return future.result(timeout=timeout_segundos)
        except FutureTimeoutError as exc:
            raise FalhaIntegracaoP04B("P04B_TIMEOUT", f"{timeout_segundos:.3f}s") from exc
        finally:
            with self._lock:
                self._limpar_concluido()

    def quantidade_trabalhos_ativos(self) -> int:
        with self._lock:
            self._limpar_concluido()
            return int(self._thread is not None and self._thread.is_alive())


_EXECUTOR_DIAGNOSTICO = ExecutorDiagnosticoLimitado()


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _schema_backend_path() -> Path:
    return _root() / "governance" / "08_CONTRATOS" / "CONFLUENCIA_REPLAY_BACKEND_V1.schema.json"


def _schema_p04a_path() -> Path:
    return _root() / "governance" / "08_CONTRATOS" / "CONFLUENCIA_REPLAY_V1.schema.json"


def _sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _snapshot_arquivo(path: Path) -> dict[str, Any]:
    return {
        "sha256": _sha256_path(path),
        "tamanho": path.stat().st_size,
    }


def _criar_copia_repositorio_isolada(caminho: Path) -> tuple[Path, Path]:
    diretorio = Path(tempfile.mkdtemp(prefix="trin_p04b_repositorio_"))
    copia = diretorio / caminho.name
    try:
        shutil.copy2(caminho, copia)
        if _snapshot_arquivo(copia) != _snapshot_arquivo(caminho):
            raise FalhaIntegracaoP04B(
                "P04B_COPIA_REPOSITORIO_DIVERGENTE",
                f"origem={caminho} copia={copia}",
            )
        return diretorio, copia
    except Exception:
        shutil.rmtree(diretorio, ignore_errors=True)
        raise


def _executar_avaliacao_isolada(
    *,
    caminho: Path,
    consulta: Mapping[str, Any],
    fabrica: Callable[[Path], Any],
    funcao: Callable[[Mapping[str, Any], Any], dict[str, Any]],
    executor: ExecutorDiagnosticoLimitado,
    timeout_segundos: float,
) -> dict[str, Any]:
    snapshot_antes = _snapshot_arquivo(caminho)
    diretorio_isolado, caminho_isolado = _criar_copia_repositorio_isolada(caminho)

    try:
        repositorio = fabrica(caminho_isolado)
    except Exception:
        shutil.rmtree(diretorio_isolado, ignore_errors=True)
        raise

    def tarefa_isolada() -> dict[str, Any]:
        try:
            return funcao(consulta, repositorio)
        finally:
            shutil.rmtree(diretorio_isolado, ignore_errors=True)

    try:
        return executor.executar(tarefa_isolada, timeout_segundos)
    finally:
        try:
            snapshot_depois = _snapshot_arquivo(caminho)
        except Exception as exc:
            raise FalhaIntegracaoP04B(
                "P04B_REPOSITORIO_MUTADO_DURANTE_CONSULTA",
                f"arquivo_oficial_indisponivel={caminho}: {type(exc).__name__}: {exc}",
            ) from exc
        if snapshot_depois != snapshot_antes:
            raise FalhaIntegracaoP04B(
                "P04B_REPOSITORIO_MUTADO_DURANTE_CONSULTA",
                f"antes={snapshot_antes} depois={snapshot_depois}",
            )


def _carregar_schema_backend() -> dict[str, Any]:
    try:
        schema = json.loads(_schema_backend_path().read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        return schema
    except Exception as exc:
        raise FalhaIntegracaoP04B("P04B_SCHEMA_BACKEND_INDISPONIVEL", str(exc)) from exc


def _validar_schema_backend(documento: Mapping[str, Any]) -> None:
    validator = Draft202012Validator(_carregar_schema_backend(), format_checker=FormatChecker())
    erros = sorted(validator.iter_errors(documento), key=lambda e: tuple(map(str, e.absolute_path)))
    if erros:
        primeiro = erros[0]
        caminho = ".".join(map(str, primeiro.absolute_path)) or "$"
        raise FalhaIntegracaoP04B(
            "P04B_CAMPO_DIAGNOSTICO_INVALIDO",
            f"{caminho}: {primeiro.message}",
        )


def _metric_ids_vazio() -> dict[str, Any]:
    return {"quantidade": 0, "ids": []}


def _metricas_vazias() -> dict[str, Any]:
    return {
        "estatisticas_mfe": None,
        "estatisticas_mae": None,
        "qualidade_hipotese": None,
        "resultados_por_horario": [],
        "resultados_por_volatilidade": [],
        "resultados_por_contexto": [],
    }


def campo_seguro(
    status: str,
    codigo: str,
    motivo: str,
    *,
    gate_fiscal: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if status not in STATUS_BACKEND:
        status = "ERRO_DIAGNOSTICO"
    campo = {
        "contrato": CONTRATO_BACKEND,
        "versao": VERSAO_BACKEND,
        "status": status,
        "modo": MODO_SOMBRA,
        "origem_tipo": ORIGEM_REPLAY,
        "gate_fiscal": copy.deepcopy(dict(gate_fiscal or {
            "fonte": FONTE_FISCAL_OFICIAL,
            "status": "DESCONHECIDO",
            "aprovado_operacional": False,
            "bloqueio_operacional": True,
            "motivo": codigo,
        })),
        "id_confluencia": None,
        "hash_resultado": None,
        "timestamp_referencia": None,
        "quantidade_experiencias": 0,
        "quantidade_comparaveis": 0,
        "classificacoes": {
            "NEUTRA": _metric_ids_vazio(),
            "FAVORAVEL": _metric_ids_vazio(),
            "CONTRARIA": _metric_ids_vazio(),
            "BLOQUEADORA": _metric_ids_vazio(),
        },
        "metricas": _metricas_vazias(),
        "confianca_diagnostica": None,
        "bloqueios": [{"codigo": codigo, "motivo": motivo}],
        "motivos": [codigo],
        "peso": PESO_ZERO,
        "impacto_operacional": IMPACTO_ZERO,
        "operacional": OPERACIONAL,
    }
    _validar_schema_backend(campo)
    return campo


def _get(documento: Mapping[str, Any], *caminho: Any) -> Any:
    atual: Any = documento
    for parte in caminho:
        if isinstance(parte, int):
            if not isinstance(atual, list) or not atual:
                return None
            try:
                atual = atual[parte]
            except IndexError:
                return None
            continue
        if not isinstance(atual, Mapping):
            return None
        atual = atual.get(parte)
    return atual


def _primeiro_texto(*valores: Any) -> str | None:
    for valor in valores:
        if valor is not None and str(valor).strip():
            return str(valor).strip()
    return None



def _obter_gate_fiscal(payload: Mapping[str, Any]) -> dict[str, Any]:
    fiscal = payload.get("fiscal")
    if not isinstance(fiscal, Mapping):
        return {
            "fonte": FONTE_FISCAL_OFICIAL,
            "status": "DESCONHECIDO",
            "aprovado_operacional": False,
            "bloqueio_operacional": True,
            "motivo": "P04B_FISCAL_CONTEXTO_AUSENTE",
        }
    fonte = _primeiro_texto(fiscal.get("fonte")) or ""
    status = (_primeiro_texto(fiscal.get("status")) or "DESCONHECIDO").upper()
    aprovado = fiscal.get("aprovado_operacional") is True
    bloqueio = fiscal.get("bloqueio_operacional") is not False
    motivo = _primeiro_texto(fiscal.get("motivo"))
    if fonte != FONTE_FISCAL_OFICIAL:
        return {
            "fonte": fonte or FONTE_FISCAL_OFICIAL,
            "status": status,
            "aprovado_operacional": False,
            "bloqueio_operacional": True,
            "motivo": "P04B_FISCAL_FONTE_DIVERGENTE",
        }
    if not aprovado or bloqueio:
        return {
            "fonte": fonte,
            "status": status,
            "aprovado_operacional": False,
            "bloqueio_operacional": True,
            "motivo": motivo or "P04B_FISCAL_NAO_APROVADO",
        }
    if status not in FiscalAdapter.STATUS_LIBERADOS:
        return {
            "fonte": fonte,
            "status": status,
            "aprovado_operacional": False,
            "bloqueio_operacional": True,
            "motivo": "P04B_FISCAL_STATUS_INCOMPATIVEL",
        }
    return {
        "fonte": fonte,
        "status": status,
        "aprovado_operacional": True,
        "bloqueio_operacional": False,
        "motivo": motivo,
    }


def _exigir_gate_fiscal(gate: Mapping[str, Any]) -> None:
    if gate.get("fonte") != FONTE_FISCAL_OFICIAL:
        raise FalhaIntegracaoP04B(
            "P04B_FISCAL_FONTE_DIVERGENTE",
            str(gate.get("fonte")),
        )
    if gate.get("motivo") == "P04B_FISCAL_STATUS_INCOMPATIVEL":
        raise FalhaIntegracaoP04B(
            "P04B_FISCAL_STATUS_INCOMPATIVEL",
            str(gate.get("status")),
        )
    if gate.get("aprovado_operacional") is not True or gate.get("bloqueio_operacional") is not False:
        raise FalhaIntegracaoP04B(
            "P04B_FISCAL_NAO_APROVADO",
            f"status={gate.get('status')} motivo={gate.get('motivo')}",
        )
    if str(gate.get("status") or "").upper() not in FiscalAdapter.STATUS_LIBERADOS:
        raise FalhaIntegracaoP04B(
            "P04B_FISCAL_STATUS_INCOMPATIVEL",
            str(gate.get("status")),
        )


def _configuracao(
    payload: Mapping[str, Any],
    replay_status: Mapping[str, Any] | None,
    environ: Mapping[str, str],
) -> tuple[dict[str, Any], Path]:
    origem_id = _primeiro_texto(environ.get("TRIN_CONFLUENCIA_REPLAY_ORIGEM_ID"))
    repositorio_texto = _primeiro_texto(
        environ.get("TRIN_CONFLUENCIA_REPLAY_REPOSITORIO_JSONL")
    )
    ativo = _primeiro_texto(
        environ.get("TRIN_CONFLUENCIA_REPLAY_ATIVO"),
        _get(payload, "contrato_ativo", "ativo_base"),
        _get(payload, "contrato_ativo", "ativo"),
        _get(payload, "historico", -1, "ativo"),
    )
    sessao_id = _primeiro_texto(
        environ.get("TRIN_CONFLUENCIA_REPLAY_SESSAO_ID"),
        (replay_status or {}).get("data_pregao"),
        (replay_status or {}).get("sessao_id"),
    )
    regime = _primeiro_texto(environ.get("TRIN_CONFLUENCIA_REPLAY_REGIME"))
    fonte_regime = _primeiro_texto(
        environ.get("TRIN_CONFLUENCIA_REPLAY_REGIME_FONTE")
    )

    if not regime or not fonte_regime:
        raise FalhaIntegracaoP04B(
            "P04B_REGIME_OFICIAL_INDISPONIVEL",
            "TRIN_CONFLUENCIA_REPLAY_REGIME e TRIN_CONFLUENCIA_REPLAY_REGIME_FONTE são obrigatórios; nenhum regime é fabricado.",
        )
    if fonte_regime != FONTE_REGIME_OFICIAL:
        raise FalhaIntegracaoP04B(
            "P04B_FONTE_REGIME_NAO_HOMOLOGADA",
            fonte_regime,
        )

    faltantes = [
        nome
        for nome, valor in (
            ("origem_id", origem_id),
            ("repositorio_jsonl", repositorio_texto),
            ("ativo", ativo),
            ("sessao_id", sessao_id),
        )
        if not valor
    ]
    if faltantes:
        raise FalhaIntegracaoP04B("P04B_CONFIGURACAO_INCOMPLETA", ",".join(faltantes))

    repositorio = Path(str(repositorio_texto)).expanduser().resolve()
    partes = {parte.casefold() for parte in repositorio.parts}
    if "trin_root" in partes or "trin_historico" in partes:
        raise FalhaIntegracaoP04B("P04B_REPOSITORIO_PROIBIDO", str(repositorio))
    if repositorio.suffix.casefold() != ".jsonl":
        raise FalhaIntegracaoP04B("P04B_REPOSITORIO_EXTENSAO_INVALIDA", str(repositorio))
    if not repositorio.is_file():
        raise FalhaIntegracaoP04B("P04B_REPOSITORIO_INDISPONIVEL", str(repositorio))

    consulta = {
        "contrato_consulta": "ConsultaConfluenciaReplayV1",
        "versao": "1.0.0",
        "modo_analise": "RETROSPECTIVO_SELADO",
        "origem_id": origem_id,
        "perfil_criterio": "CRITERIO_CONFLUENCIA_REPLAY_V1",
        "campos_comparacao": [
            "fato.evento.ativo",
            "contexto.regime",
            "contexto.sessao.sessao_id",
        ],
        "contexto_alvo": {
            "ativo": ativo,
            "regime": regime,
            "sessao_id": sessao_id,
        },
        "particao_dados": {
            "metodo": "CORTE_TEMPORAL_50_50_V1_PROVISORIO",
            "percentual_calibracao": 50,
            "percentual_prova": 50,
        },
        "politica_universo": {
            "usar_universo_completo": True,
            "top_n": None,
            "limite_seguranca": 1000,
            "ordem": "timestamp_referencia_ordinal_referencia_experiencia_id_ASC",
            "filtro_direcao": None,
        },
    }
    return consulta, repositorio


def _repositorio_oficial(caminho: Path) -> Any:
    try:
        from intelligence.historiador_replay import RepositorioExperiencias
    except Exception as exc:
        raise FalhaIntegracaoP04B("P04B_HISTORIADOR_NAO_IMPORTAVEL", str(exc)) from exc
    try:
        repositorio = RepositorioExperiencias(caminho)
    except Exception as exc:
        raise FalhaIntegracaoP04B("P04B_REPOSITORIO_NAO_ABERTO", str(exc)) from exc
    if not callable(getattr(repositorio, "consultar_experiencias", None)):
        raise FalhaIntegracaoP04B(
            "P04B_HISTORIADOR_API_DIVERGENTE",
            "RepositorioExperiencias.consultar_experiencias ausente.",
        )
    return repositorio


def _avaliar_p04a(consulta: Mapping[str, Any], repositorio: Any) -> dict[str, Any]:
    try:
        from intelligence.confluencia_replay import (
            avaliar_confluencia_replay,
            validar_semantica_ou_falhar,
        )
    except Exception as exc:
        raise FalhaIntegracaoP04B("P04B_P04A_NAO_IMPORTAVEL", str(exc)) from exc

    schema = _schema_p04a_path()
    if not schema.is_file():
        raise FalhaIntegracaoP04B("P04B_SCHEMA_P04A_AUSENTE", str(schema))
    atual = _sha256_path(schema)
    if atual not in P04A_SCHEMA_SHA256_ALLOWED:
        raise FalhaIntegracaoP04B(
            "P04B_SCHEMA_P04A_DIVERGENTE",
            f"atual={atual} permitidos={sorted(P04A_SCHEMA_SHA256_ALLOWED)}",
        )
    try:
        saida = avaliar_confluencia_replay(
            consulta=consulta,
            repositorio=repositorio,
            validar_schema_saida=True,
        )
        validar_semantica_ou_falhar(saida)
        return saida
    except Exception as exc:
        raise FalhaIntegracaoP04B("P04B_P04A_FALHOU", str(exc)) from exc


def _validar_saida_p04a(saida: Mapping[str, Any]) -> None:
    if not isinstance(saida, Mapping):
        raise FalhaIntegracaoP04B("P04B_SAIDA_P04A_NAO_MAPEAMENTO")
    if saida.get("versao_schema") != "1.0.0":
        raise FalhaIntegracaoP04B(
            "P04B_VERSAO_P04A_DESCONHECIDA",
            str(saida.get("versao_schema")),
        )
    if saida.get("origem_tipo") != ORIGEM_REPLAY:
        raise FalhaIntegracaoP04B(
            "P04B_ORIGEM_P04A_DIVERGENTE",
            str(saida.get("origem_tipo")),
        )
    if (
        saida.get("modo") != MODO_SOMBRA
        or saida.get("peso") != 0
        or saida.get("impacto_operacional") != 0
    ):
        raise FalhaIntegracaoP04B("P04B_INVARIANTES_OPERACIONAIS_VIOLADAS")
    if saida.get("status") not in STATUS_P04A:
        raise FalhaIntegracaoP04B(
            "P04B_STATUS_P04A_DESCONHECIDO",
            str(saida.get("status")),
        )
    quantidade = saida.get("quantidade_experiencias")
    ids = saida.get("ids_experiencias")
    evidencias = saida.get("evidencias")
    if not isinstance(quantidade, int) or not isinstance(ids, list) or not isinstance(evidencias, list):
        raise FalhaIntegracaoP04B("P04B_QUANTIDADE_P04A_INVALIDA")
    if quantidade != len(ids) or quantidade != len(evidencias):
        raise FalhaIntegracaoP04B("P04B_QUANTIDADE_P04A_INCOERENTE")
    hash_atual = saida.get("hash_resultado")
    if not isinstance(hash_atual, str) or len(hash_atual) != 64:
        raise FalhaIntegracaoP04B("P04B_HASH_P04A_INVALIDO")
    try:
        from intelligence.confluencia_replay.canonico import sha256_canonico
    except Exception as exc:
        raise FalhaIntegracaoP04B("P04B_CANONICO_P04A_INDISPONIVEL", str(exc)) from exc
    material = copy.deepcopy(dict(saida))
    material.pop("hash_resultado", None)
    esperado = sha256_canonico(material)
    if esperado != hash_atual:
        raise FalhaIntegracaoP04B(
            "P04B_HASH_P04A_DIVERGENTE",
            f"atual={hash_atual} esperado={esperado}",
        )


def _projetar(saida: Mapping[str, Any], gate_fiscal: Mapping[str, Any]) -> dict[str, Any]:
    _validar_saida_p04a(saida)
    classificacoes_p04a = saida.get("classificacoes_evidencia") or {}
    if not isinstance(classificacoes_p04a, Mapping):
        raise FalhaIntegracaoP04B("P04B_CLASSIFICACOES_P04A_INVALIDAS")
    classificacoes: dict[str, dict[str, Any]] = {}
    for classe in ("NEUTRA", "FAVORAVEL", "CONTRARIA", "BLOQUEADORA"):
        item = classificacoes_p04a.get(classe)
        if not isinstance(item, Mapping):
            raise FalhaIntegracaoP04B("P04B_CLASSIFICACOES_P04A_INCOERENTES", classe)
        quantidade_classe = item.get("quantidade")
        ids_classificacao = item.get("ids")
        if (
            not isinstance(quantidade_classe, int)
            or not isinstance(ids_classificacao, list)
            or quantidade_classe != len(ids_classificacao)
        ):
            raise FalhaIntegracaoP04B("P04B_CLASSIFICACOES_P04A_INCOERENTES", classe)
        classificacoes[classe] = {
            "quantidade": quantidade_classe,
            "ids": copy.deepcopy(ids_classificacao),
        }
    confianca = copy.deepcopy(saida.get("confianca_diagnostica"))
    quantidade_comparaveis = 0
    if isinstance(confianca, Mapping):
        quantidade_comparaveis = int(confianca.get("quantidade_comparaveis") or 0)
    campo = {
        "contrato": CONTRATO_BACKEND,
        "versao": VERSAO_BACKEND,
        "status": str(saida["status"]),
        "modo": MODO_SOMBRA,
        "origem_tipo": ORIGEM_REPLAY,
        "gate_fiscal": copy.deepcopy(dict(gate_fiscal)),
        "id_confluencia": saida.get("id_confluencia"),
        "hash_resultado": saida.get("hash_resultado"),
        "timestamp_referencia": saida.get("timestamp_calculo"),
        "quantidade_experiencias": int(saida["quantidade_experiencias"]),
        "quantidade_comparaveis": quantidade_comparaveis,
        "classificacoes": classificacoes,
        "metricas": {
            "estatisticas_mfe": copy.deepcopy(saida.get("estatisticas_mfe")),
            "estatisticas_mae": copy.deepcopy(saida.get("estatisticas_mae")),
            "qualidade_hipotese": copy.deepcopy(saida.get("metricas_qualidade_hipotese")),
            "resultados_por_horario": copy.deepcopy(saida.get("resultados_por_horario") or []),
            "resultados_por_volatilidade": copy.deepcopy(
                saida.get("resultados_por_volatilidade") or []
            ),
            "resultados_por_contexto": copy.deepcopy(saida.get("resultados_por_contexto") or []),
        },
        "confianca_diagnostica": confianca,
        "bloqueios": copy.deepcopy(saida.get("bloqueios") or []),
        "motivos": copy.deepcopy(saida.get("motivos") or []),
        "peso": PESO_ZERO,
        "impacto_operacional": IMPACTO_ZERO,
        "operacional": OPERACIONAL,
    }
    _validar_schema_backend(campo)
    return campo


def anexar_confluencia_replay_backend(
    payload: Mapping[str, Any],
    *,
    replay_ativo: bool,
    replay_status: Mapping[str, Any] | None = None,
    environ: Mapping[str, str] | None = None,
    timeout_segundos: float = 0.75,
    avaliador: Callable[[Mapping[str, Any], Any], dict[str, Any]] | None = None,
    repositorio_factory: Callable[[Path], Any] | None = None,
    executor_diagnostico: ExecutorDiagnosticoLimitado | None = None,
) -> dict[str, Any]:
    """Retorna cópia aditiva; nunca altera payload, P04A ou repositório."""
    saida_payload = copy.deepcopy(dict(payload))
    if not replay_ativo:
        saida_payload["confluencia_replay"] = campo_seguro(
            "INDISPONIVEL",
            "P04B_MODO_AO_VIVO_NAO_CONSULTA_REPLAY",
            "A integração replay permanece inativa no modo AO_VIVO.",
            gate_fiscal=_obter_gate_fiscal(saida_payload),
        )
        return saida_payload

    ambiente = dict(os.environ if environ is None else environ)
    gate_fiscal = _obter_gate_fiscal(saida_payload)
    try:
        _exigir_gate_fiscal(gate_fiscal)
        consulta, caminho = _configuracao(saida_payload, replay_status, ambiente)
        fabrica = repositorio_factory or _repositorio_oficial
        funcao = avaliador or _avaliar_p04a
        executor = executor_diagnostico or _EXECUTOR_DIAGNOSTICO
        resultado = _executar_avaliacao_isolada(
            caminho=caminho,
            consulta=consulta,
            fabrica=fabrica,
            funcao=funcao,
            executor=executor,
            timeout_segundos=timeout_segundos,
        )
        saida_payload["confluencia_replay"] = _projetar(resultado, gate_fiscal)
    except FalhaIntegracaoP04B as exc:
        indisponiveis = {
            "P04B_CONFIGURACAO_INCOMPLETA",
            "P04B_REGIME_OFICIAL_INDISPONIVEL",
            "P04B_REPOSITORIO_INDISPONIVEL",
            "P04B_HISTORIADOR_NAO_IMPORTAVEL",
            "P04B_P04A_NAO_IMPORTAVEL",
            "P04B_SCHEMA_P04A_AUSENTE",
            "P04B_TIMEOUT",
            "P04B_AVALIADOR_OCUPADO",
        }
        status = "INDISPONIVEL" if exc.codigo in indisponiveis else "BLOQUEADO"
        saida_payload["confluencia_replay"] = campo_seguro(
            status,
            exc.codigo,
            exc.detalhe or str(exc),
            gate_fiscal=gate_fiscal,
        )
    except Exception as exc:
        saida_payload["confluencia_replay"] = campo_seguro(
            "ERRO_DIAGNOSTICO",
            "P04B_EXCECAO_NAO_CLASSIFICADA",
            f"{type(exc).__name__}: {exc}",
            gate_fiscal=gate_fiscal,
        )
    return saida_payload
