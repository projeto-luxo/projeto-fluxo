from __future__ import annotations

import copy

import pytest

from intelligence.confluencia_replay.canonico import sha256_canonico
from intelligence.confluencia_replay.erros import FalhaConfluenciaReplay
from intelligence.confluencia_replay.porta_historiador import PortaHistoriadorConfluenciaV1
from intelligence.confluencia_replay.schemas import erros_schema

from .helpers import RepositorioFake, avaliar, consulta_padrao, experiencia, hash_objeto


def test_cf_01_entrada_somente_api_oficial() -> None:
    saida, repo = avaliar([experiencia(1)])
    assert repo.chamadas == [("WINFUT_REPLAY_SELADO_001", None)]
    assert saida["universo"]["filtros_permitidos"] == ["origem_id"]


def test_cf_02_garantia_fiscal_herdada() -> None:
    saida, _ = avaliar([experiencia(1)])
    assert saida["garantia_fiscal"]["modelo"] == "HERDADA_DO_INGRESSO_HISTORIADOR_HOMOLOGADO"
    assert saida["garantia_fiscal"]["certificado_individual_exigido_na_confluencia"] is False


def test_cf_03_origem_invalida_bloqueia() -> None:
    saida, _ = avaliar([experiencia(1, origem_tipo="OUTRA")])
    assert saida["status"] == "BLOQUEADO"
    assert saida["confianca_diagnostica"]["valor"] is None


def test_cf_04_origem_replay_preservada() -> None:
    saida, _ = avaliar([experiencia(1)])
    assert saida["origem_tipo"] == "ORIGEM_REPLAY"
    assert saida["evidencias"][0]["origem_tipo"] == "ORIGEM_REPLAY"


def test_cf_05_resultado_nao_participa_da_classificacao_contextual() -> None:
    a = experiencia(1, mfe="120.00", mae="50.00")
    b = experiencia(2, mfe="10.00", mae="300.00")
    saida_a, _ = avaliar([a])
    saida_b, _ = avaliar([b])
    assert saida_a["quantidade_experiencias"] == 1
    assert saida_b["quantidade_experiencias"] == 1
    assert saida_a["evidencias"][0]["classificacao_evidencia"] == saida_b["evidencias"][0]["classificacao_evidencia"]
    assert saida_a["evidencias"][0]["classificacao_evidencia"] == "FAVORAVEL"


def test_cf_06_sem_experiencias_estado_seguro() -> None:
    saida, _ = avaliar([])
    assert saida["status"] == "SEM_EVIDENCIA"
    assert saida["quantidade_experiencias"] == 0
    assert saida["confianca_diagnostica"]["valor"] is None


def test_cf_07_direcao_ausente_permanece_ausente() -> None:
    saida, _ = avaliar([experiencia(1, direcao=None, origem_direcao=None, mfe=None, mae=None)])
    assert saida["evidencias"][0]["direcao"] is None


def test_cf_08_peso_zero() -> None:
    saida, _ = avaliar([experiencia(1)])
    assert saida["peso"] == 0


def test_cf_09_impacto_zero() -> None:
    saida, _ = avaliar([experiencia(1)])
    assert saida["impacto_operacional"] == 0


def test_cf_10_nenhuma_ordem_produzida() -> None:
    saida, _ = avaliar([experiencia(1)])
    proibidos = {"ordem", "entrada", "stop", "parcial", "alvo", "compra", "venda"}
    assert not proibidos.intersection(saida)


def test_cf_11_historiador_nao_mutado() -> None:
    itens = [experiencia(1), experiencia(2)]
    antes = hash_objeto(itens)
    _, repo = avaliar(itens)
    assert hash_objeto(itens) == antes
    assert repo.escritas == 0


def test_cf_12_memoria_ao_vivo_nao_recebida() -> None:
    saida, _ = avaliar([experiencia(1)])
    assert "memoria" not in saida
    assert "memoria_operacional" not in saida


def test_cf_13_biblioteca_historica_nao_e_entrada() -> None:
    consulta = consulta_padrao()
    consulta["TRIN_HISTORICO"] = "proibido"
    assert erros_schema("consulta", consulta)


def test_cf_14_saida_deterministica() -> None:
    itens = [experiencia(2), experiencia(1)]
    a, _ = avaliar(itens)
    b, _ = avaliar(list(reversed(itens)))
    assert a == b


def test_cf_15_ids_rastreaveis() -> None:
    saida, _ = avaliar([experiencia(1), experiencia(2)])
    assert saida["ids_experiencias"] == [e["experiencia_id"] for e in saida["evidencias"]]
    assert len(saida["rastreabilidade"]["hashes_experiencias"]) == 2


def test_cf_16_mfe_mae_agregados_com_ids() -> None:
    saida, _ = avaliar([experiencia(1, mfe="120.00", mae="50.00"), experiencia(2, mfe="80.00", mae="20.00")])
    assert saida["estatisticas_mfe"]["media"] == "100.00"
    assert saida["estatisticas_mae"]["media"] == "35.00"
    assert saida["estatisticas_mfe"]["ids_incluidos"] == saida["ids_experiencias"]


def test_cf_17_schema_experiencia_invalido_bloqueia() -> None:
    item = experiencia(1)
    del item["contexto"]
    saida, _ = avaliar([item])
    assert saida["status"] == "BLOQUEADO"


def test_cf_18_porta_nao_exige_modificar_consumidor() -> None:
    saida, _ = avaliar([experiencia(1)])
    assert saida["modo"] == "SOMBRA"


def test_cf_19_rollback_e_responsabilidade_do_aplicador() -> None:
    # Contrato funcional não contém mecanismo de Git/rollback.
    saida, _ = avaliar([experiencia(1)])
    assert "rollback" not in saida


def test_cf_20_commit_nao_e_responsabilidade_do_nucleo() -> None:
    saida, _ = avaliar([experiencia(1)])
    assert "commit" not in saida and "push" not in saida


@pytest.mark.parametrize(
    ("item", "classe"),
    [
        (experiencia(1), "FAVORAVEL"),
        (experiencia(2, ativo="WDOFUT"), "CONTRARIA"),
        (experiencia(3, sessao_id=None), "NEUTRA"),
    ],
)
def test_cf_21_classificacoes_diagnosticas(item, classe) -> None:
    saida, _ = avaliar([item])
    assert saida["evidencias"][0]["classificacao_evidencia"] == classe


def test_cf_22_matriz_qualidade_hipotese() -> None:
    itens = [
        experiencia(1, mfe="120.00", mae="50.00"),
        experiencia(2, mfe="10.00", mae="50.00"),
        experiencia(3, direcao=None, origem_direcao="HIPOTESE_NEGATIVA_EXPLICITA", mfe="120.00", mae="50.00"),
        experiencia(4, direcao=None, origem_direcao="ABSTENCAO_DELIBERADA", mfe="120.00", mae="50.00"),
    ]
    saida, _ = avaliar(itens)
    metricas = saida["metricas_qualidade_hipotese"]
    assert metricas["ACERTO"]["quantidade"] == 1
    assert metricas["FALSO_POSITIVO"]["quantidade"] == 1
    assert metricas["FALSO_NEGATIVO"]["quantidade"] == 1
    assert metricas["OPORTUNIDADE_PERDIDA"]["quantidade"] == 1


def test_cf_23_resultados_por_horario() -> None:
    saida, _ = avaliar([
        experiencia(1, timestamp="2026-01-21T09:01:00-03:00"),
        experiencia(2, timestamp="2026-01-21T10:01:00-03:00"),
    ])
    assert [x["chave"] for x in saida["resultados_por_horario"]] == ["09:00-09:59", "10:00-10:59"]


def test_cf_24_resultados_por_volatilidade() -> None:
    itens = [
        experiencia(1, maximo="10010", minimo="10000"),
        experiencia(2, maximo="10020", minimo="10000"),
        experiencia(3, maximo="10030", minimo="10000"),
        experiencia(4, maximo="10040", minimo="10000"),
        experiencia(5, maximo="10050", minimo="10000"),
        experiencia(6, maximo="10060", minimo="10000"),
    ]
    saida, _ = avaliar(itens)
    chaves = {x["chave"] for x in saida["resultados_por_volatilidade"]}
    assert {"BAIXA", "MEDIA", "ALTA"}.issubset(chaves)


def test_cf_25_resultados_por_contexto() -> None:
    saida, _ = avaliar([experiencia(1), experiencia(2, sessao_id="2026-01-22")])
    assert len(saida["resultados_por_contexto"]) == 2


def test_cf_26_particao_sem_intersecao() -> None:
    saida, _ = avaliar([experiencia(i) for i in range(1, 7)])
    p = saida["particao_dados"]
    assert not set(p["ids_calibracao"]).intersection(p["ids_prova"])
    assert p["ids_calibracao"] + p["ids_prova"] == saida["ids_experiencias"]


@pytest.mark.parametrize("campo", ["resultado", "direcao", "ids_escolhidos_manualmente"])
def test_cf_27_cherry_picking_rejeitado(campo: str) -> None:
    consulta = consulta_padrao()
    consulta[campo] = "proibido"
    assert erros_schema("consulta", consulta)


def test_cf_28_top_n_desabilitado() -> None:
    consulta = consulta_padrao()
    consulta["politica_universo"]["top_n"] = 10
    assert erros_schema("consulta", consulta)


def test_cf_29_hash_universo_reproduzivel() -> None:
    itens = [experiencia(1), experiencia(2)]
    a, _ = avaliar(itens)
    b, _ = avaliar(copy.deepcopy(itens))
    assert a["universo"]["hash_universo"] == b["universo"]["hash_universo"]


def test_cf_30_idempotencia_n_chamadas() -> None:
    repo = RepositorioFake([experiencia(1), experiencia(2)])
    porta = PortaHistoriadorConfluenciaV1(repo)
    from intelligence.confluencia_replay.nucleo import NucleoConfluenciaReplay
    nucleo = NucleoConfluenciaReplay(porta, validar_schema_saida=False)
    resultados = [nucleo.avaliar(consulta_padrao()) for _ in range(5)]
    assert all(item == resultados[0] for item in resultados)
    assert len(resultados[0]["ids_experiencias"]) == 2


def test_cf_31_id_confluencia_deterministico() -> None:
    a, _ = avaliar([experiencia(1)])
    b, _ = avaliar([experiencia(1)])
    assert a["id_confluencia"] == b["id_confluencia"]


def test_cf_32_hash_resultado_sem_autorreferencia() -> None:
    saida, _ = avaliar([experiencia(1)])
    esperado = saida["hash_resultado"]
    material = dict(saida)
    material.pop("hash_resultado")
    assert sha256_canonico(material) == esperado


def test_cf_33_completo_zero_rejeitado_pelo_schema() -> None:
    saida, _ = avaliar([])
    saida["status"] = "COMPLETO"
    assert erros_schema("saida", saida)


def test_cf_34_quantidade_lista_divergente_rejeitada() -> None:
    saida, _ = avaliar([])
    saida["quantidade_experiencias"] = 3
    assert erros_schema("saida", saida)


def test_cf_35_confianca_com_zero_rejeitada() -> None:
    saida, _ = avaliar([])
    saida["confianca_diagnostica"]["estado"] = "DESCRITIVA_NAO_CALIBRADA"
    saida["confianca_diagnostica"]["valor"] = 1.0
    assert erros_schema("saida", saida)


def test_cf_36_campos_comparacao_exatamente_fixos() -> None:
    consulta = consulta_padrao()
    consulta["campos_comparacao"] = []
    assert erros_schema("consulta", consulta)
