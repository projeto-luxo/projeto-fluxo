from __future__ import annotations

import copy

from intelligence.confluencia_replay.canonico import sha256_canonico
from intelligence.confluencia_replay.validador_semantico import validar_semantica

from .helpers import avaliar, experiencia


def _base():
    saida, _ = avaliar([experiencia(1), experiencia(2)])
    return saida


def _rehash(saida):
    saida.pop("hash_resultado", None)
    saida["hash_resultado"] = sha256_canonico(saida)
    return saida


def test_is_01_quantidade_coerente_com_listas() -> None:
    saida = _base()
    saida["quantidade_experiencias"] = 99
    _rehash(saida)
    assert "IS-01_QUANTIDADE_LISTAS_DIVERGENTE" in validar_semantica(saida)


def test_is_02_ids_unicos() -> None:
    saida = _base()
    saida["ids_experiencias"][1] = saida["ids_experiencias"][0]
    _rehash(saida)
    assert "IS-02_IDS_EXPERIENCIAS_NAO_UNICOS" in validar_semantica(saida)


def test_is_03_ids_evidencias_mesma_ordem() -> None:
    saida = _base()
    saida["evidencias"].reverse()
    _rehash(saida)
    assert "IS-03_IDS_EVIDENCIAS_ORDEM_DIVERGENTE" in validar_semantica(saida)


def test_is_04_particoes_sem_intersecao() -> None:
    saida = _base()
    saida["particao_dados"]["ids_prova"].append(saida["particao_dados"]["ids_calibracao"][0])
    _rehash(saida)
    assert "IS-04_PARTICOES_INTERSECAO" in validar_semantica(saida)


def test_is_05_uniao_particoes_reconstroi_ids() -> None:
    saida = _base()
    saida["particao_dados"]["ids_prova"] = []
    _rehash(saida)
    assert "IS-05_PARTICOES_NAO_RECONSTROEM_IDS" in validar_semantica(saida)


def test_is_06_universo_ids_incluidos_corresponde() -> None:
    saida = _base()
    saida["universo"]["ids_incluidos"] = []
    _rehash(saida)
    assert "IS-06_UNIVERSO_IDS_INCLUIDOS_DIVERGENTE" in validar_semantica(saida)


def test_is_07_quantidade_classificacao() -> None:
    saida = _base()
    saida["classificacoes_evidencia"]["FAVORAVEL"]["quantidade"] = 99
    _rehash(saida)
    assert "IS-07_CLASSIFICACAO_QUANTIDADE_FAVORAVEL" in validar_semantica(saida)


def test_is_08_id_classificacao_conhecido() -> None:
    saida = _base()
    saida["classificacoes_evidencia"]["FAVORAVEL"]["ids"].append("EXP-INEXISTENTE")
    saida["classificacoes_evidencia"]["FAVORAVEL"]["quantidade"] += 1
    _rehash(saida)
    assert "IS-08_CLASSIFICACAO_ID_DESCONHECIDO_FAVORAVEL" in validar_semantica(saida)


def test_is_09_classe_corresponde_evidencia() -> None:
    saida = _base()
    saida["evidencias"][0]["classificacao_evidencia"] = "CONTRARIA"
    _rehash(saida)
    assert "IS-09_CLASSIFICACAO_EVIDENCIA_DIVERGENTE_FAVORAVEL" in validar_semantica(saida)


def test_is_10_classificacoes_particionam_ids() -> None:
    saida = _base()
    saida["classificacoes_evidencia"]["FAVORAVEL"]["ids"] = []
    saida["classificacoes_evidencia"]["FAVORAVEL"]["quantidade"] = 0
    _rehash(saida)
    assert "IS-10_CLASSIFICACOES_NAO_PARTICIONAM_EVIDENCIAS" in validar_semantica(saida)


def test_is_11_tres_criterios_fixos() -> None:
    saida = _base()
    saida["evidencias"][0]["criterios"] = []
    _rehash(saida)
    assert "IS-11_CRITERIOS_NAO_SAO_EXATAMENTE_TRES_FIXOS" in validar_semantica(saida)


def test_is_12_direcao_valida() -> None:
    saida = _base()
    saida["evidencias"][0]["direcao"] = "NEUTRO"
    _rehash(saida)
    assert "IS-12_DIRECAO_INVALIDA" in validar_semantica(saida)


def test_is_13_quantidade_metrica_hipotese() -> None:
    saida = _base()
    saida["metricas_qualidade_hipotese"]["ACERTO"]["quantidade"] = 99
    _rehash(saida)
    assert "IS-13_METRICA_QUANTIDADE_ACERTO" in validar_semantica(saida)


def test_is_14_id_metrica_conhecido() -> None:
    saida = _base()
    saida["metricas_qualidade_hipotese"]["ACERTO"]["ids"].append("EXP-INEXISTENTE")
    saida["metricas_qualidade_hipotese"]["ACERTO"]["quantidade"] += 1
    _rehash(saida)
    assert "IS-14_METRICA_ID_DESCONHECIDO_ACERTO" in validar_semantica(saida)


def test_is_15_metricas_particionam_ids() -> None:
    saida = _base()
    saida["metricas_qualidade_hipotese"]["ACERTO"]["ids"] = []
    saida["metricas_qualidade_hipotese"]["ACERTO"]["quantidade"] = 0
    _rehash(saida)
    assert "IS-15_METRICAS_NAO_PARTICIONAM_EVIDENCIAS" in validar_semantica(saida)


def test_is_16_estrato_quantidade() -> None:
    saida = _base()
    saida["resultados_por_horario"][0]["quantidade"] = 99
    _rehash(saida)
    assert "IS-16_ESTRATO_QUANTIDADE_resultados_por_horario" in validar_semantica(saida)


def test_is_17_estrato_id_conhecido() -> None:
    saida = _base()
    saida["resultados_por_contexto"][0]["ids_experiencias"].append("EXP-INEXISTENTE")
    saida["resultados_por_contexto"][0]["quantidade"] += 1
    _rehash(saida)
    assert "IS-17_ESTRATO_ID_DESCONHECIDO_resultados_por_contexto" in validar_semantica(saida)


def test_is_18_quantidade_comparaveis() -> None:
    saida = _base()
    saida["confianca_diagnostica"]["quantidade_comparaveis"] = 99
    _rehash(saida)
    assert "IS-18_CONFIANCA_QUANTIDADE_DIVERGENTE" in validar_semantica(saida)


def test_is_19_id_comparavel_conhecido() -> None:
    saida = _base()
    saida["confianca_diagnostica"]["ids_comparaveis"].append("EXP-INEXISTENTE")
    saida["confianca_diagnostica"]["quantidade_comparaveis"] += 1
    _rehash(saida)
    assert "IS-19_CONFIANCA_ID_DESCONHECIDO" in validar_semantica(saida)


def test_is_20_zero_comparaveis_implica_null() -> None:
    saida, _ = avaliar([experiencia(1, sessao_id=None)])
    saida["confianca_diagnostica"]["valor"] = 1.0
    _rehash(saida)
    assert "IS-20_CONFIANCA_COM_ZERO_COMPARAVEIS" in validar_semantica(saida)


def test_is_21_estado_completo_coerente() -> None:
    saida, _ = avaliar([])
    saida["status"] = "COMPLETO"
    _rehash(saida)
    assert "IS-21_COMPLETO_INCOERENTE" in validar_semantica(saida)


def test_is_22_estado_sem_evidencia_coerente() -> None:
    saida = _base()
    saida["status"] = "SEM_EVIDENCIA"
    _rehash(saida)
    assert "IS-22_SEM_EVIDENCIA_COM_IDS" in validar_semantica(saida)
