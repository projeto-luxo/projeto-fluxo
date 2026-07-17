from __future__ import annotations

from collections import Counter
from typing import Any, Mapping

from .canonico import sha256_canonico
from .erros import FalhaConfluenciaReplay
from .util import CAMPOS_FIXOS, parse_timestamp


def _ids(bloco: Mapping[str, Any]) -> list[str]:
    valores = bloco.get("ids", [])
    return list(valores) if isinstance(valores, list) else []


def validar_semantica(saida: Mapping[str, Any]) -> list[str]:
    erros: list[str] = []
    ids = list(saida.get("ids_experiencias", []))
    evidencias = list(saida.get("evidencias", []))
    quantidade = saida.get("quantidade_experiencias")

    if quantidade != len(ids) or quantidade != len(evidencias):
        erros.append("IS-01_QUANTIDADE_LISTAS_DIVERGENTE")
    if len(ids) != len(set(ids)):
        erros.append("IS-02_IDS_EXPERIENCIAS_NAO_UNICOS")
    ids_evidencias = [e.get("experiencia_id") for e in evidencias]
    if ids_evidencias != ids:
        erros.append("IS-03_IDS_EVIDENCIAS_ORDEM_DIVERGENTE")

    particao = saida.get("particao_dados", {})
    calibracao = list(particao.get("ids_calibracao", []))
    prova = list(particao.get("ids_prova", []))
    if set(calibracao) & set(prova):
        erros.append("IS-04_PARTICOES_INTERSECAO")
    if calibracao + prova != ids:
        erros.append("IS-05_PARTICOES_NAO_RECONSTROEM_IDS")

    universo = saida.get("universo", {})
    if universo.get("ids_incluidos") != ids:
        erros.append("IS-06_UNIVERSO_IDS_INCLUIDOS_DIVERGENTE")

    por_id = {e.get("experiencia_id"): e for e in evidencias}
    classificacoes = saida.get("classificacoes_evidencia", {})
    ids_classificados: list[str] = []
    for classe in ("NEUTRA", "FAVORAVEL", "CONTRARIA", "BLOQUEADORA"):
        bloco = classificacoes.get(classe, {})
        valores = _ids(bloco)
        if bloco.get("quantidade") != len(valores):
            erros.append(f"IS-07_CLASSIFICACAO_QUANTIDADE_{classe}")
        if any(item not in por_id for item in valores):
            erros.append(f"IS-08_CLASSIFICACAO_ID_DESCONHECIDO_{classe}")
        ids_classificados.extend(valores)
        for item in valores:
            if item in por_id and por_id[item].get("classificacao_evidencia") != classe:
                erros.append(f"IS-09_CLASSIFICACAO_EVIDENCIA_DIVERGENTE_{classe}")
    if Counter(ids_classificados) != Counter(ids):
        erros.append("IS-10_CLASSIFICACOES_NAO_PARTICIONAM_EVIDENCIAS")

    for evidencia in evidencias:
        criterios = evidencia.get("criterios", [])
        campos = [item.get("campo") for item in criterios]
        if tuple(campos) != CAMPOS_FIXOS:
            erros.append("IS-11_CRITERIOS_NAO_SAO_EXATAMENTE_TRES_FIXOS")
        if evidencia.get("direcao") not in (None, "COMPRA", "VENDA"):
            erros.append("IS-12_DIRECAO_INVALIDA")

    metricas = saida.get("metricas_qualidade_hipotese", {})
    ids_metricas: list[str] = []
    for categoria in (
        "ACERTO",
        "FALSO_POSITIVO",
        "FALSO_NEGATIVO",
        "ACERTO_NEGATIVO",
        "OPORTUNIDADE_PERDIDA",
        "NAO_AVALIAVEL",
    ):
        bloco = metricas.get(categoria, {})
        valores = _ids(bloco)
        if bloco.get("quantidade") != len(valores):
            erros.append(f"IS-13_METRICA_QUANTIDADE_{categoria}")
        if any(item not in por_id for item in valores):
            erros.append(f"IS-14_METRICA_ID_DESCONHECIDO_{categoria}")
        ids_metricas.extend(valores)
    if Counter(ids_metricas) != Counter(ids):
        erros.append("IS-15_METRICAS_NAO_PARTICIONAM_EVIDENCIAS")

    for nome in (
        "resultados_por_horario",
        "resultados_por_volatilidade",
        "resultados_por_contexto",
    ):
        for estrato in saida.get(nome, []):
            valores = estrato.get("ids_experiencias", [])
            if estrato.get("quantidade") != len(valores):
                erros.append(f"IS-16_ESTRATO_QUANTIDADE_{nome}")
            if any(item not in por_id for item in valores):
                erros.append(f"IS-17_ESTRATO_ID_DESCONHECIDO_{nome}")

    confianca = saida.get("confianca_diagnostica", {})
    comparaveis = list(confianca.get("ids_comparaveis", []))
    if confianca.get("quantidade_comparaveis") != len(comparaveis):
        erros.append("IS-18_CONFIANCA_QUANTIDADE_DIVERGENTE")
    if any(item not in por_id for item in comparaveis):
        erros.append("IS-19_CONFIANCA_ID_DESCONHECIDO")
    if not comparaveis and confianca.get("valor") is not None:
        erros.append("IS-20_CONFIANCA_COM_ZERO_COMPARAVEIS")

    status = saida.get("status")
    bloqueios = list(saida.get("bloqueios", []))
    if status == "COMPLETO" and (not ids or bloqueios):
        erros.append("IS-21_COMPLETO_INCOERENTE")
    if status == "SEM_EVIDENCIA" and ids:
        erros.append("IS-22_SEM_EVIDENCIA_COM_IDS")
    if status == "BLOQUEADO" and not bloqueios:
        erros.append("IS-23_BLOQUEADO_SEM_BLOQUEIO")
    if status != "BLOQUEADO" and bloqueios:
        erros.append("IS-24_BLOQUEIOS_FORA_DE_BLOQUEADO")

    if saida.get("peso") != 0 or saida.get("impacto_operacional") != 0:
        erros.append("IS-25_IMPACTO_OPERACIONAL_NAO_ZERO")
    proibidos = {
        "ordem",
        "compra",
        "venda",
        "entrada",
        "stop",
        "parcial",
        "alvo",
        "quantidade_contratos",
        "autorizacao_operacional",
    }
    if proibidos & set(saida):
        erros.append("IS-26_CAMPO_OPERACIONAL_PROIBIDO")

    hash_resultado = saida.get("hash_resultado")
    material = dict(saida)
    material.pop("hash_resultado", None)
    if isinstance(hash_resultado, str) and sha256_canonico(material) != hash_resultado:
        erros.append("IS-27_HASH_RESULTADO_DIVERGENTE")

    timestamp = saida.get("timestamp_calculo")
    timestamps = [e.get("timestamp_referencia") for e in evidencias]
    esperado = (
        max(
            timestamps,
            key=lambda valor: parse_timestamp(valor, "timestamp_referencia"),
        )
        if timestamps
        else None
    )
    if timestamp != esperado:
        erros.append("IS-28_TIMESTAMP_SEMANTICO_DIVERGENTE")

    return erros


def validar_semantica_ou_falhar(saida: Mapping[str, Any]) -> None:
    erros = validar_semantica(saida)
    if erros:
        raise FalhaConfluenciaReplay(
            "SAIDA_SEMANTICAMENTE_INVALIDA",
            " | ".join(erros),
        )
