from __future__ import annotations

import copy

import pytest
from jsonschema import Draft202012Validator

from intelligence.confluencia_replay.schema_generator import verificar_reproducao
from intelligence.confluencia_replay.schemas import carregar_schema, erros_schema
from intelligence.confluencia_replay.validador_semantico import validar_semantica

from .helpers import avaliar, consulta_padrao, experiencia


def test_schemas_draft_2020_12_meta_validos() -> None:
    Draft202012Validator.check_schema(carregar_schema("consulta"))
    Draft202012Validator.check_schema(carregar_schema("saida"))


def test_schema_grande_reproduzivel() -> None:
    resultado = verificar_reproducao()
    assert resultado["reproduzido"] is True
    assert resultado["sha256_gerado"] == resultado["sha256_esperado"]


def test_saida_real_valida_no_schema_grande() -> None:
    saida, _ = avaliar([experiencia(1), experiencia(2)], schema_saida=False)
    assert not erros_schema("saida", saida)


@pytest.mark.parametrize(
    "mutacao",
    [
        lambda q: q.update({"resultado": {"mfe": 100}}),
        lambda q: q["politica_universo"].update({"filtro_direcao": "COMPRA"}),
        lambda q: q["politica_universo"].update({"top_n": 5}),
        lambda q: q.update({"ids_escolhidos_manualmente": ["EXP-1"]}),
    ],
)
def test_consultas_de_cherry_picking_rejeitadas(mutacao) -> None:
    consulta = consulta_padrao()
    mutacao(consulta)
    assert erros_schema("consulta", consulta)


def test_quantidade_de_cada_classificacao_igual_lista() -> None:
    saida, _ = avaliar([experiencia(1), experiencia(2, ativo="WDOFUT"), experiencia(3, sessao_id=None)])
    for bloco in saida["classificacoes_evidencia"].values():
        assert bloco["quantidade"] == len(bloco["ids"])


def test_ids_classificacao_correspondem_evidencias() -> None:
    saida, _ = avaliar([experiencia(1), experiencia(2, ativo="WDOFUT")])
    ids = set(saida["ids_experiencias"])
    for bloco in saida["classificacoes_evidencia"].values():
        assert set(bloco["ids"]).issubset(ids)


def test_metricas_hipotese_coerentes_com_ids() -> None:
    saida, _ = avaliar([experiencia(1), experiencia(2, mfe="10.00", mae="50.00")])
    ids = set(saida["ids_experiencias"])
    total = 0
    for nome, bloco in saida["metricas_qualidade_hipotese"].items():
        if nome == "regra":
            continue
        assert bloco["quantidade"] == len(bloco["ids"])
        assert set(bloco["ids"]).issubset(ids)
        total += bloco["quantidade"]
    assert total == len(ids)


def test_estratificacoes_coerentes_com_ids() -> None:
    saida, _ = avaliar([experiencia(i) for i in range(1, 7)])
    ids = set(saida["ids_experiencias"])
    for nome in ("resultados_por_horario", "resultados_por_volatilidade", "resultados_por_contexto"):
        for estrato in saida[nome]:
            assert estrato["quantidade"] == len(estrato["ids_experiencias"])
            assert set(estrato["ids_experiencias"]).issubset(ids)


def test_criterios_exatamente_tres_campos_fixos() -> None:
    saida, _ = avaliar([experiencia(1)])
    assert [c["campo"] for c in saida["evidencias"][0]["criterios"]] == [
        "fato.evento.ativo",
        "contexto.regime",
        "contexto.sessao.sessao_id",
    ]


def test_prova_identificavel_e_separada_calibracao() -> None:
    saida, _ = avaliar([experiencia(i) for i in range(1, 5)])
    p = saida["particao_dados"]
    assert p["ids_calibracao"]
    assert p["ids_prova"]
    assert set(p["ids_calibracao"]).isdisjoint(p["ids_prova"])
    por_id = {e["experiencia_id"]: e["particao"] for e in saida["evidencias"]}
    assert all(por_id[i] == "CALIBRACAO" for i in p["ids_calibracao"])
    assert all(por_id[i] == "PROVA" for i in p["ids_prova"])


def test_duplicidade_exata_nao_duplica() -> None:
    item = experiencia(1)
    saida, _ = avaliar([item, copy.deepcopy(item)])
    assert saida["quantidade_experiencias"] == 1
    assert saida["universo"]["excluidos"][0]["motivo"] == "DUPLICIDADE_EXATA"


def test_mesmo_id_com_corpo_alterado_bloqueia_por_integridade() -> None:
    a = experiencia(1)
    b = copy.deepcopy(a)
    b["resultado"]["mfe_pontos"] = "999.00"
    saida, _ = avaliar([a, b])
    assert saida["status"] == "BLOQUEADO"
    assert any(
        x["codigo"] in {"EXPERIENCIA_ID_DIVERGENTE", "DUPLICIDADE_CONFLITANTE"}
        for x in saida["bloqueios"]
    )


def test_sem_estado_acumulado_entre_chamadas() -> None:
    a, _ = avaliar([experiencia(1)])
    b, _ = avaliar([experiencia(1)])
    assert a == b
    assert not validar_semantica(a)
