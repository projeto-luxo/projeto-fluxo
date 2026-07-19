from __future__ import annotations

import threading
import time

import pytest

import backend.confluencia_replay_backend as modulo_p04b
from intelligence.fiscal_adapter import FiscalAdapter

from backend.confluencia_replay_backend import (
    ExecutorDiagnosticoLimitado,
    anexar_confluencia_replay_backend,
)
from tests.p04b_backend.helpers import RepositorioFake, env_config, payload_fiscal_aprovado, saida_p04a_valida


def executar(tmp_path, avaliador, **kwargs):
    return anexar_confluencia_replay_backend(
        payload_fiscal_aprovado(),
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
        repositorio_factory=lambda _p: RepositorioFake([]),
        avaliador=avaliador,
        **kwargs,
    )["confluencia_replay"]


def test_modo_ao_vivo_nao_consulta():
    chamado = []
    out = anexar_confluencia_replay_backend({}, replay_ativo=False, avaliador=lambda *_: chamado.append(1))
    assert not chamado
    assert out["confluencia_replay"]["status"] == "INDISPONIVEL"


def test_config_ausente_indisponivel():
    out = anexar_confluencia_replay_backend(payload_fiscal_aprovado(), replay_ativo=True, environ={})
    assert out["confluencia_replay"]["status"] == "INDISPONIVEL"


def test_regime_nao_e_fabricado(tmp_path):
    env = env_config(tmp_path)
    env.pop("TRIN_CONFLUENCIA_REPLAY_REGIME")
    campo = anexar_confluencia_replay_backend(payload_fiscal_aprovado(), replay_ativo=True, replay_status={"data_pregao": "2026-01-21"}, environ=env)["confluencia_replay"]
    assert campo["status"] == "INDISPONIVEL"
    assert campo["bloqueios"][0]["codigo"] == "P04B_REGIME_OFICIAL_INDISPONIVEL"
    assert "CERTIFICADO_SEM_INFERENCIA" not in str(campo)


def test_fonte_regime_nao_homologada_bloqueia(tmp_path):
    env = env_config(tmp_path)
    env["TRIN_CONFLUENCIA_REPLAY_REGIME_FONTE"] = "FONTE_INVENTADA"
    campo = anexar_confluencia_replay_backend(payload_fiscal_aprovado(), replay_ativo=True, replay_status={"data_pregao": "2026-01-21"}, environ=env)["confluencia_replay"]
    assert campo["status"] == "BLOQUEADO"
    assert campo["bloqueios"][0]["codigo"] == "P04B_FONTE_REGIME_NAO_HOMOLOGADA"


@pytest.mark.parametrize("mutacao,codigo", [
    (lambda x: x.update(versao_schema="9.9.9"), "P04B_VERSAO_P04A_DESCONHECIDA"),
    (lambda x: x.update(origem_tipo="OUTRA"), "P04B_ORIGEM_P04A_DIVERGENTE"),
    (lambda x: x.update(peso=1), "P04B_INVARIANTES_OPERACIONAIS_VIOLADAS"),
    (lambda x: x.update(quantidade_experiencias=99), "P04B_QUANTIDADE_P04A_INCOERENTE"),
    (lambda x: x.update(hash_resultado="0" * 64), "P04B_HASH_P04A_DIVERGENTE"),
])
def test_saida_invalida_bloqueia(tmp_path, mutacao, codigo):
    saida = saida_p04a_valida(); mutacao(saida)
    campo = executar(tmp_path, lambda *_: saida)
    assert campo["status"] == "BLOQUEADO"
    assert campo["bloqueios"][0]["codigo"] == codigo
    assert campo["operacional"] is False and campo["peso"] == 0


def test_excecao_interna_nao_derruba_backend(tmp_path):
    campo = executar(tmp_path, lambda *_: (_ for _ in ()).throw(RuntimeError("boom")))
    assert campo["status"] == "ERRO_DIAGNOSTICO"


def test_timeout_nao_acumula_trabalhos(tmp_path):
    executor = ExecutorDiagnosticoLimitado()
    release = threading.Event()

    def bloqueado(*_):
        release.wait()
        return saida_p04a_valida()

    try:
        primeiro = executar(
            tmp_path,
            bloqueado,
            timeout_segundos=0.01,
            executor_diagnostico=executor,
        )
        assert primeiro["bloqueios"][0]["codigo"] == "P04B_TIMEOUT"
        for _ in range(20):
            campo = executar(
                tmp_path,
                bloqueado,
                timeout_segundos=0.01,
                executor_diagnostico=executor,
            )
            assert campo["bloqueios"][0]["codigo"] == "P04B_AVALIADOR_OCUPADO"
            assert executor.quantidade_trabalhos_ativos() == 1
        threads = [
            t
            for t in threading.enumerate()
            if t.name.startswith(executor.thread_prefix)
        ]
        assert len(threads) <= 1
        assert all(t.daemon for t in threads)
    finally:
        release.set()

    limite = time.monotonic() + 5.0
    while executor.quantidade_trabalhos_ativos() and time.monotonic() < limite:
        time.sleep(0.01)
    assert executor.quantidade_trabalhos_ativos() == 0


def test_repositorio_em_trin_historico_bloqueia(tmp_path):
    proibido = tmp_path / "TRIN_HISTORICO" / "x.jsonl"; proibido.parent.mkdir(); proibido.write_text("")
    env = env_config(tmp_path); env["TRIN_CONFLUENCIA_REPLAY_REPOSITORIO_JSONL"] = str(proibido)
    campo = anexar_confluencia_replay_backend(payload_fiscal_aprovado(), replay_ativo=True, replay_status={"data_pregao": "2026-01-21"}, environ=env)["confluencia_replay"]
    assert campo["status"] == "BLOQUEADO"
    assert campo["bloqueios"][0]["codigo"] == "P04B_REPOSITORIO_PROIBIDO"


def test_fiscal_ausente_bloqueia_antes_do_p04a(tmp_path):
    campo = anexar_confluencia_replay_backend(
        {"contrato_ativo": {"ativo_base": "WINFUT"}},
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
    )["confluencia_replay"]
    assert campo["status"] == "BLOQUEADO"
    assert campo["bloqueios"][0]["codigo"] == "P04B_FISCAL_NAO_APROVADO"
    assert campo["gate_fiscal"]["aprovado_operacional"] is False


def test_fiscal_fonte_divergente_bloqueia(tmp_path):
    payload = payload_fiscal_aprovado()
    payload["fiscal"]["fonte"] = "FONTE_INVENTADA"
    campo = anexar_confluencia_replay_backend(
        payload, replay_ativo=True, replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
    )["confluencia_replay"]
    assert campo["status"] == "BLOQUEADO"
    assert campo["bloqueios"][0]["codigo"] == "P04B_FISCAL_FONTE_DIVERGENTE"


def test_fiscal_bloqueado_impede_avaliador(tmp_path):
    payload = payload_fiscal_aprovado()
    payload["fiscal"].update(aprovado_operacional=False, bloqueio_operacional=True, status="REPROVADO_COM_PENDENCIAS")
    chamado = []
    campo = anexar_confluencia_replay_backend(
        payload, replay_ativo=True, replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path), avaliador=lambda *_: chamado.append(1),
    )["confluencia_replay"]
    assert not chamado
    assert campo["status"] == "BLOQUEADO"
    assert campo["gate_fiscal"]["bloqueio_operacional"] is True


@pytest.mark.parametrize(
    "status",
    ["REPROVADO", "REPROVADO_COM_PENDENCIAS", "DESCONHECIDO", "ERRO_FISCAL"],
)
def test_fiscal_status_contraditorio_com_booleanos_favoraveis_bloqueia(
    tmp_path,
    status,
):
    payload = payload_fiscal_aprovado()
    payload["fiscal"].update(
        status=status,
        aprovado_operacional=True,
        bloqueio_operacional=False,
        motivo=None,
    )
    chamado = []

    campo = anexar_confluencia_replay_backend(
        payload,
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
        repositorio_factory=lambda _p: RepositorioFake([]),
        avaliador=lambda *_: chamado.append(1),
    )["confluencia_replay"]

    assert not chamado
    assert campo["status"] == "BLOQUEADO"
    assert campo["bloqueios"][0]["codigo"] == "P04B_FISCAL_STATUS_INCOMPATIVEL"
    assert campo["gate_fiscal"]["status"] == status
    assert campo["gate_fiscal"]["aprovado_operacional"] is False
    assert campo["gate_fiscal"]["bloqueio_operacional"] is True
    assert campo["gate_fiscal"]["motivo"] == "P04B_FISCAL_STATUS_INCOMPATIVEL"


@pytest.mark.parametrize(
    "status",
    sorted(FiscalAdapter.STATUS_LIBERADOS),
)
def test_fiscal_status_aprovado_coerente_permite_avaliacao(tmp_path, status):
    payload = payload_fiscal_aprovado()
    payload["fiscal"]["status"] = status
    chamado = []
    saida_p04a = saida_p04a_valida()

    campo = anexar_confluencia_replay_backend(
        payload,
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
        repositorio_factory=lambda _p: RepositorioFake([]),
        avaliador=lambda *_: chamado.append(1) or saida_p04a,
    )["confluencia_replay"]

    assert chamado == [1]
    assert campo["gate_fiscal"]["status"] == status
    assert campo["gate_fiscal"]["aprovado_operacional"] is True
    assert campo["gate_fiscal"]["bloqueio_operacional"] is False

    # O gate Fiscal apenas autoriza a consulta. A decisão diagnóstica,
    # inclusive status, bloqueios e motivos, continua pertencendo ao P04A.
    assert campo["status"] == saida_p04a["status"]
    assert campo["bloqueios"] == saida_p04a["bloqueios"]
    assert campo["motivos"] == saida_p04a["motivos"]
    assert all(
        item.get("codigo") != "P04B_FISCAL_STATUS_INCOMPATIVEL"
        for item in campo["bloqueios"]
    )


def test_p04b_nao_declara_lista_local_de_status_fiscais():
    assert not hasattr(modulo_p04b, "STATUS_FISCAL_APROVADOS")


def test_fiscal_ressalva_da_autoridade_vigente_permite_avaliacao(tmp_path):
    assert "RESSALVA" in FiscalAdapter.STATUS_LIBERADOS
    payload = payload_fiscal_aprovado()
    payload["fiscal"]["status"] = "RESSALVA"
    chamado = []
    saida_p04a = saida_p04a_valida()

    campo = anexar_confluencia_replay_backend(
        payload,
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
        repositorio_factory=lambda _p: RepositorioFake([]),
        avaliador=lambda *_: chamado.append(1) or saida_p04a,
    )["confluencia_replay"]

    assert chamado == [1]
    assert campo["gate_fiscal"]["status"] == "RESSALVA"
    assert campo["gate_fiscal"]["aprovado_operacional"] is True
    assert campo["gate_fiscal"]["bloqueio_operacional"] is False


def test_fiscal_status_ausente_bloqueia(tmp_path):
    payload = payload_fiscal_aprovado()
    payload["fiscal"].pop("status")
    chamado = []

    campo = anexar_confluencia_replay_backend(
        payload,
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
        repositorio_factory=lambda _p: RepositorioFake([]),
        avaliador=lambda *_: chamado.append(1),
    )["confluencia_replay"]

    assert not chamado
    assert campo["status"] == "BLOQUEADO"
    assert campo["gate_fiscal"]["status"] == "DESCONHECIDO"
    assert campo["bloqueios"][0]["codigo"] == "P04B_FISCAL_STATUS_INCOMPATIVEL"


def test_fiscal_status_desconhecido_bloqueia(tmp_path):
    payload = payload_fiscal_aprovado()
    payload["fiscal"]["status"] = "STATUS_NAO_RECONHECIDO"
    chamado = []

    campo = anexar_confluencia_replay_backend(
        payload,
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
        repositorio_factory=lambda _p: RepositorioFake([]),
        avaliador=lambda *_: chamado.append(1),
    )["confluencia_replay"]

    assert not chamado
    assert campo["status"] == "BLOQUEADO"
    assert campo["bloqueios"][0]["codigo"] == "P04B_FISCAL_STATUS_INCOMPATIVEL"


@pytest.mark.parametrize(
    ("aprovado_operacional", "bloqueio_operacional"),
    [
        (False, False),
        (True, True),
    ],
)
def test_fiscal_booleanos_contraditorios_bloqueiam(
    tmp_path,
    aprovado_operacional,
    bloqueio_operacional,
):
    payload = payload_fiscal_aprovado()
    payload["fiscal"].update(
        status="CERTIFICADO",
        aprovado_operacional=aprovado_operacional,
        bloqueio_operacional=bloqueio_operacional,
    )
    chamado = []

    campo = anexar_confluencia_replay_backend(
        payload,
        replay_ativo=True,
        replay_status={"data_pregao": "2026-01-21"},
        environ=env_config(tmp_path),
        repositorio_factory=lambda _p: RepositorioFake([]),
        avaliador=lambda *_: chamado.append(1),
    )["confluencia_replay"]

    assert not chamado
    assert campo["status"] == "BLOQUEADO"
    assert campo["gate_fiscal"]["aprovado_operacional"] is False
    assert campo["gate_fiscal"]["bloqueio_operacional"] is True
