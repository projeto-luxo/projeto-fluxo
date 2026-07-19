from __future__ import annotations

import copy
import json
import threading
import time
from pathlib import Path

from backend.confluencia_replay_backend import (
    ExecutorDiagnosticoLimitado,
    anexar_confluencia_replay_backend,
)
from tests.p04b_backend.helpers import RepositorioFake, env_config, payload_fiscal_aprovado, saida_p04a_valida


def test_idempotencia_n_chamadas_sem_acumulo(tmp_path):
    p04a = saida_p04a_valida()
    base = payload_fiscal_aprovado({"x": [1, 2]})
    snapshot = copy.deepcopy(base)
    resultados = []
    for _ in range(8):
        resultados.append(
            anexar_confluencia_replay_backend(
                base,
                replay_ativo=True,
                replay_status={"data_pregao": "2026-01-21"},
                environ=env_config(tmp_path),
                repositorio_factory=lambda _p: RepositorioFake([]),
                avaliador=lambda *_: p04a,
            )
        )
    assert base == snapshot
    canonicos = [json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for r in resultados]
    assert len(set(canonicos)) == 1


def test_classificacoes_quantidade_igual_ids_e_ids_existentes(tmp_path):
    p04a = saida_p04a_valida()
    campo = anexar_confluencia_replay_backend(
        payload_fiscal_aprovado(),
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
        repositorio_factory=lambda _p: RepositorioFake([]),
        avaliador=lambda *_: p04a,
    )["confluencia_replay"]
    ids_evidencias = set(p04a["ids_experiencias"])
    for item in campo["classificacoes"].values():
        assert item["quantidade"] == len(item["ids"])
        assert set(item["ids"]).issubset(ids_evidencias)


def test_metricas_e_estratos_coerentes_com_ids(tmp_path):
    p04a = saida_p04a_valida()
    campo = anexar_confluencia_replay_backend(
        payload_fiscal_aprovado(),
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
        repositorio_factory=lambda _p: RepositorioFake([]),
        avaliador=lambda *_: p04a,
    )["confluencia_replay"]
    universo = set(p04a["ids_experiencias"])
    qualidade = campo["metricas"]["qualidade_hipotese"]
    for nome, item in qualidade.items():
        if nome == "regra":
            continue
        assert item["quantidade"] == len(item["ids"])
        assert set(item["ids"]).issubset(universo)
    for chave in ("resultados_por_horario", "resultados_por_volatilidade", "resultados_por_contexto"):
        for estrato in campo["metricas"][chave]:
            assert estrato["quantidade"] == len(estrato["ids_experiencias"])
            assert set(estrato["ids_experiencias"]).issubset(universo)


def test_repositorio_nao_mutado(tmp_path):
    p04a = saida_p04a_valida()
    env = env_config(tmp_path)
    path = Path(env["TRIN_CONFLUENCIA_REPLAY_REPOSITORIO_JSONL"])
    before = path.read_bytes()
    anexar_confluencia_replay_backend(
        payload_fiscal_aprovado(), replay_ativo=True, replay_status={"data_pregao": "2026-01-21"},
        environ=env, repositorio_factory=lambda _p: RepositorioFake([]), avaliador=lambda *_: p04a,
    )
    assert path.read_bytes() == before


def test_mutacao_do_repositorio_durante_consulta_bloqueia(tmp_path):
    p04a = saida_p04a_valida()
    env = env_config(tmp_path)
    path = Path(env["TRIN_CONFLUENCIA_REPLAY_REPOSITORIO_JSONL"])

    def mutante(*_):
        path.write_text("mutado", encoding="utf-8")
        return p04a

    campo = anexar_confluencia_replay_backend(
        payload_fiscal_aprovado(), replay_ativo=True, replay_status={"data_pregao": "2026-01-21"},
        environ=env, repositorio_factory=lambda _p: RepositorioFake([]), avaliador=mutante,
    )["confluencia_replay"]
    assert campo["status"] == "BLOQUEADO"
    assert campo["bloqueios"][0]["codigo"] == "P04B_REPOSITORIO_MUTADO_DURANTE_CONSULTA"


def test_arquivos_protegidos_nao_mutados():
    root = Path(__file__).resolve().parents[2]
    protegidos = [
        root / "intelligence/confluencia_replay/nucleo.py",
        root / "intelligence/historiador_replay/repositorio_experiencias.py",
    ]
    antes = {str(p): p.read_bytes() for p in protegidos if p.exists()}
    anexar_confluencia_replay_backend({}, replay_ativo=False)
    depois = {str(p): p.read_bytes() for p in protegidos if p.exists()}
    assert antes == depois


def test_timeout_isola_repositorio_e_descarta_mutacao_tardia(tmp_path):
    p04a = saida_p04a_valida()
    env = env_config(tmp_path)
    caminho_oficial = Path(
        env["TRIN_CONFLUENCIA_REPLAY_REPOSITORIO_JSONL"]
    )
    bytes_oficiais = caminho_oficial.read_bytes()
    executor = ExecutorDiagnosticoLimitado()
    liberar = threading.Event()
    capturado: dict[str, Path] = {}

    class RepositorioComCaminho:
        def __init__(self, caminho: Path) -> None:
            self.caminho = caminho

        def consultar_experiencias(self, origem_id=None, direcao=None):
            return []

    def fabrica(caminho: Path):
        capturado["caminho"] = caminho
        return RepositorioComCaminho(caminho)

    def mutacao_tardia(_consulta, repositorio):
        liberar.wait()
        repositorio.caminho.write_text(
            "mutacao_apenas_na_copia",
            encoding="utf-8",
        )
        return p04a

    campo = anexar_confluencia_replay_backend(
        payload_fiscal_aprovado(),
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env,
        repositorio_factory=fabrica,
        avaliador=mutacao_tardia,
        executor_diagnostico=executor,
        timeout_segundos=0.01,
    )["confluencia_replay"]

    assert campo["status"] == "INDISPONIVEL"
    assert campo["bloqueios"][0]["codigo"] == "P04B_TIMEOUT"
    caminho_isolado = capturado["caminho"]
    assert caminho_isolado != caminho_oficial
    assert caminho_isolado.read_bytes() == bytes_oficiais
    assert caminho_oficial.read_bytes() == bytes_oficiais

    liberar.set()
    limite = time.monotonic() + 5.0
    while executor.quantidade_trabalhos_ativos() and time.monotonic() < limite:
        time.sleep(0.01)

    assert executor.quantidade_trabalhos_ativos() == 0
    assert caminho_oficial.read_bytes() == bytes_oficiais
    assert not caminho_isolado.parent.exists()
