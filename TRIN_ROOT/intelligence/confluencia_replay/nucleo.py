from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping

from .canonico import sha256_canonico
from .criterios import avaliar_criterios, violacoes_bloqueadoras
from .erros import FalhaConfluenciaReplay
from .estatisticas import estatisticas_metricas
from .gps import (
    classificar_qualidade_hipotese,
    metricas_qualidade,
    resultados_por_contexto,
    resultados_por_horario,
    resultados_por_volatilidade,
)
from .modelos import ExperienciaProjetada, validar_experiencia_minima
from .porta_historiador import PortaHistoriadorConfluenciaV1
from .schemas import validar_schema
from .util import CAMPOS_FIXOS, copia_profunda, parse_timestamp
from .validador_semantico import validar_semantica_ou_falhar

BASE_COMMIT = "be7714c16d0031b87bebcc1ef905b4daf5bba478"
VERSAO_ALGORITMO = "CONFLUENCIA_REPLAY_ALGORITMO_V1"
CRITERIO = "CRITERIO_CONFLUENCIA_REPLAY_V1"
MAX_UNIVERSO = 1000


def _bloqueio(codigo: str, motivo: str, experiencia_id: str | None = None) -> dict[str, Any]:
    return {
        "codigo": codigo,
        "motivo": motivo,
        "experiencia_id": experiencia_id,
    }


def _motivo_exclusao(exc: FalhaConfluenciaReplay) -> str:
    if "ORIGEM" in exc.codigo:
        return "ORIGEM_INVALIDA"
    if "RASTREABILIDADE" in exc.codigo or "HASH" in exc.codigo:
        return "RASTREABILIDADE_INCOMPLETA"
    return "SCHEMA_INVALIDO"


def _metric_ids(ids: list[str]) -> dict[str, Any]:
    return {"quantidade": len(ids), "ids": ids}


def _estatistica_vazia() -> dict[str, Any]:
    return {
        "quantidade": 0,
        "minimo": None,
        "maximo": None,
        "media": None,
        "mediana": None,
        "percentil_25": None,
        "percentil_75": None,
        "ids_incluidos": [],
        "excluidos": [],
        "outliers_removidos": 0,
    }


def _hash_universo(experiencias: list[ExperienciaProjetada]) -> str:
    material = [
        {
            "experiencia_id": item.experiencia_id,
            "experiencia_sha256": item.experiencia_sha256,
            "timestamp_referencia": item.timestamp_referencia,
            "ordinal_referencia": item.ordinal_referencia,
        }
        for item in experiencias
    ]
    return sha256_canonico(material)


def _particionar(ids: list[str]) -> tuple[list[str], list[str], str]:
    corte = len(ids) // 2
    calibracao = ids[:corte]
    prova = ids[corte:]
    material = {
        "metodo": "CORTE_TEMPORAL_50_50_V1_PROVISORIO",
        "ids_calibracao": calibracao,
        "ids_prova": prova,
    }
    return calibracao, prova, sha256_canonico(material)


def _identidade(
    *,
    hash_consulta: str,
    hash_universo: str,
    hash_particao: str,
    ids: list[str],
) -> str:
    material = {
        "versao_schema": "1.0.0",
        "versao_algoritmo": VERSAO_ALGORITMO,
        "hash_consulta": hash_consulta,
        "hash_universo": hash_universo,
        "hash_particao": hash_particao,
        "ids_incluidos": ids,
    }
    return "CFR-" + sha256_canonico(material)[:32].upper()


def _garantia_fiscal() -> dict[str, Any]:
    return {
        "modelo": "HERDADA_DO_INGRESSO_HISTORIADOR_HOMOLOGADO",
        "fronteira_homologada": "RepositorioExperiencias",
        "certificado_individual_exigido_na_confluencia": False,
        "campos_rastreabilidade_exigidos": [
            "solicitacao_id",
            "origem_id",
            "origem_hash",
        ],
    }


class NucleoConfluenciaReplay:
    def __init__(
        self,
        porta: PortaHistoriadorConfluenciaV1,
        *,
        validar_schema_saida: bool = True,
    ) -> None:
        self._porta = porta
        self._validar_schema_saida = validar_schema_saida

    def avaliar(self, consulta: Mapping[str, Any]) -> dict[str, Any]:
        consulta_copia = copia_profunda(dict(consulta))
        validar_schema("consulta", consulta_copia)
        hash_consulta = sha256_canonico(consulta_copia)

        retorno = self._porta.consultar(consulta_copia["origem_id"])
        total_retornado = len(retorno.experiencias)
        bloqueios: list[dict[str, Any]] = []
        motivos: list[str] = []
        excluidos: list[dict[str, str]] = []
        validas: list[ExperienciaProjetada] = []

        for indice, experiencia in enumerate(retorno.experiencias):
            try:
                projetada = validar_experiencia_minima(experiencia)
                validas.append(projetada)
            except FalhaConfluenciaReplay as exc:
                identidade = str(experiencia.get("experiencia_id") or f"ITEM-{indice:06d}")
                motivo = _motivo_exclusao(exc)
                excluidos.append(
                    {"experiencia_id": identidade, "motivo": motivo}
                )
                bloqueios.append(
                    _bloqueio(exc.codigo, str(exc), identidade)
                )

        validas.sort(key=lambda item: item.chave_ordenacao)
        deduplicadas: list[ExperienciaProjetada] = []
        por_id: dict[str, ExperienciaProjetada] = {}
        conflito = False
        for item in validas:
            anterior = por_id.get(item.experiencia_id)
            if anterior is None:
                por_id[item.experiencia_id] = item
                deduplicadas.append(item)
            elif anterior.experiencia_sha256 == item.experiencia_sha256:
                excluidos.append(
                    {
                        "experiencia_id": item.experiencia_id,
                        "motivo": "DUPLICIDADE_EXATA",
                    }
                )
            else:
                conflito = True
                excluidos.append(
                    {
                        "experiencia_id": item.experiencia_id,
                        "motivo": "DUPLICIDADE_CONFLITANTE",
                    }
                )
                bloqueios.append(
                    _bloqueio(
                        "DUPLICIDADE_CONFLITANTE",
                        "Mesmo experiencia_id com hashes diferentes.",
                        item.experiencia_id,
                    )
                )

        if len(deduplicadas) > MAX_UNIVERSO:
            bloqueios.append(
                _bloqueio(
                    "UNIVERSO_ACIMA_LIMITE_SEGURANCA",
                    f"{len(deduplicadas)} > {MAX_UNIVERSO}",
                )
            )
            motivos.append("UNIVERSO_ACIMA_LIMITE_SEGURANCA")
            deduplicadas = []

        hash_universo = _hash_universo(deduplicadas)
        ids = [item.experiencia_id for item in deduplicadas]
        calibracao, prova, hash_particao = _particionar(ids)
        particao_por_id = {item: "CALIBRACAO" for item in calibracao}
        particao_por_id.update({item: "PROVA" for item in prova})

        evidencias_internas: list[dict[str, Any]] = []
        concordancias: list[dict[str, Any]] = []
        divergencias: list[dict[str, Any]] = []
        classificacoes: dict[str, list[str]] = {
            "NEUTRA": [],
            "FAVORAVEL": [],
            "CONTRARIA": [],
            "BLOQUEADORA": [],
        }

        for item in deduplicadas:
            experiencia = copia_profunda(item.experiencia)
            criterios, conc, div, classe = avaliar_criterios(experiencia, consulta_copia)
            violacoes = violacoes_bloqueadoras(experiencia)
            if violacoes:
                classe = "BLOQUEADORA"
                for motivo in violacoes:
                    bloqueios.append(
                        _bloqueio(
                            motivo,
                            motivo,
                            item.experiencia_id,
                        )
                    )
            classificacoes[classe].append(item.experiencia_id)
            for registro in conc:
                concordancias.append(
                    {"experiencia_id": item.experiencia_id, **registro}
                )
            for registro in div:
                divergencias.append(
                    {"experiencia_id": item.experiencia_id, **registro}
                )
            hipotese = experiencia["hipotese"]
            resultado = experiencia["resultado"]
            qualidade = classificar_qualidade_hipotese(experiencia)
            evidencia = {
                "experiencia_id": item.experiencia_id,
                "experiencia_sha256": item.experiencia_sha256,
                "origem_tipo": "ORIGEM_REPLAY",
                "origem_id": item.origem_id,
                "origem_hash": item.origem_hash,
                "timestamp_referencia": item.timestamp_referencia,
                "ordinal_referencia": item.ordinal_referencia,
                "classificacao_evidencia": classe,
                "criterios": criterios,
                "direcao": hipotese.get("direcao"),
                "mfe_pontos": resultado.get("mfe_pontos"),
                "mae_pontos": resultado.get("mae_pontos"),
                "particao": particao_por_id[item.experiencia_id],
                "motivos": violacoes,
                # Campos internos removidos antes da serialização.
                "experiencia_fonte": experiencia,
                "qualidade_hipotese": qualidade,
            }
            evidencias_internas.append(evidencia)

        ids_publicos = [e["experiencia_id"] for e in evidencias_internas]
        evidencias_publicas = [
            {
                chave: valor
                for chave, valor in evidencia.items()
                if chave not in {"experiencia_fonte", "qualidade_hipotese"}
            }
            for evidencia in evidencias_internas
        ]

        mfe = estatisticas_metricas(evidencias_publicas, "mfe_pontos")
        mae = estatisticas_metricas(evidencias_publicas, "mae_pontos")
        qualidade = metricas_qualidade(evidencias_internas)
        por_horario = resultados_por_horario(evidencias_internas)
        por_volatilidade = resultados_por_volatilidade(evidencias_internas)
        por_contexto = resultados_por_contexto(evidencias_internas)

        comparaveis = classificacoes["FAVORAVEL"] + classificacoes["CONTRARIA"]
        total_criterios = len(evidencias_internas) * len(CAMPOS_FIXOS)
        avaliados = sum(
            1
            for evidencia in evidencias_internas
            for criterio in evidencia["criterios"]
            if criterio["resultado"] != "NAO_AVALIADO"
        )
        cobertura = (avaliados / total_criterios) if total_criterios else 0.0
        if comparaveis:
            taxa_favoravel = len(classificacoes["FAVORAVEL"]) / len(comparaveis)
            confianca_valor: float | None = taxa_favoravel * cobertura
            confianca_estado = "DESCRITIVA_NAO_CALIBRADA"
        else:
            confianca_valor = None
            confianca_estado = "NAO_CALCULAVEL"

        if bloqueios:
            status = "BLOQUEADO"
            confianca_valor = None
            confianca_estado = "BLOQUEADA"
        elif not evidencias_internas:
            status = "SEM_EVIDENCIA"
            motivos.append("UNIVERSO_VAZIO")
        elif not comparaveis:
            status = "INSUFICIENTE"
            motivos.append("ZERO_EVIDENCIAS_COMPARAVEIS")
        elif classificacoes["NEUTRA"]:
            status = "PARCIAL"
        else:
            status = "COMPLETO"

        timestamp_calculo = (
            max(
                (e["timestamp_referencia"] for e in evidencias_internas),
                key=lambda valor: parse_timestamp(valor, "timestamp_referencia"),
            )
            if evidencias_internas
            else None
        )
        id_confluencia = _identidade(
            hash_consulta=hash_consulta,
            hash_universo=hash_universo,
            hash_particao=hash_particao,
            ids=ids_publicos,
        )

        saida: dict[str, Any] = {
            "versao_schema": "1.0.0",
            "id_confluencia": id_confluencia,
            "timestamp_calculo": timestamp_calculo,
            "origem_tipo": "ORIGEM_REPLAY",
            "status": status,
            "modo": "SOMBRA",
            "garantia_fiscal": _garantia_fiscal(),
            "criterios_consulta": consulta_copia,
            "universo": {
                "quantidade_total_retornada": total_retornado,
                "ids_universo_ordenados": ids,
                "hash_universo": hash_universo,
                "ids_incluidos": ids_publicos,
                "excluidos": excluidos,
                "regra_top_n": "DESABILITADO_USAR_UNIVERSO_COMPLETO",
                "filtros_permitidos": ["origem_id"],
                "filtros_proibidos": [
                    "direcao",
                    "resultado",
                    "mfe_pontos",
                    "mae_pontos",
                    "desfecho",
                    "ids_escolhidos_manualmente",
                ],
            },
            "particao_dados": {
                "metodo": "CORTE_TEMPORAL_50_50_V1_PROVISORIO",
                "provisorio": True,
                "ids_calibracao": calibracao,
                "ids_prova": prova,
                "hash_particao": hash_particao,
                "intersecao": [],
            },
            "quantidade_experiencias": len(evidencias_publicas),
            "ids_experiencias": ids_publicos,
            "evidencias": evidencias_publicas,
            "classificacoes_evidencia": {
                classe: _metric_ids(classificacoes[classe])
                for classe in (
                    "NEUTRA",
                    "FAVORAVEL",
                    "CONTRARIA",
                    "BLOQUEADORA",
                )
            },
            "concordancias": concordancias,
            "divergencias": divergencias,
            "estatisticas_mfe": mfe,
            "estatisticas_mae": mae,
            "metricas_qualidade_hipotese": qualidade,
            "resultados_por_horario": por_horario,
            "resultados_por_volatilidade": por_volatilidade,
            "resultados_por_contexto": por_contexto,
            "confianca_diagnostica": {
                "estado": confianca_estado,
                "valor": confianca_valor,
                "formula": "taxa_favoravel * cobertura",
                "quantidade_comparaveis": len(comparaveis),
                "ids_comparaveis": comparaveis,
                "cobertura": cobertura,
                "nao_calibrada": True,
                "faixas_classificatorias": None,
            },
            "peso": 0,
            "impacto_operacional": 0,
            "bloqueios": bloqueios,
            "motivos": list(dict.fromkeys(motivos)),
            "rastreabilidade": {
                "commit_base": BASE_COMMIT,
                "versao_algoritmo": VERSAO_ALGORITMO,
                "serializacao_canonica": "RFC8785_JCS_UTF8",
                "hash_consulta": hash_consulta,
                "hash_universo": hash_universo,
                "hash_particao": hash_particao,
                "hashes_experiencias": [
                    item.experiencia_sha256 for item in deduplicadas
                ],
                "idempotencia": {
                    "estado_interno_mutado": False,
                    "saida_canonica_repetivel": True,
                },
            },
        }
        saida["hash_resultado"] = sha256_canonico(saida)
        validar_semantica_ou_falhar(saida)
        if self._validar_schema_saida:
            validar_schema("saida", saida)
        return saida


def avaliar_confluencia_replay(
    *,
    consulta: Mapping[str, Any],
    repositorio: Any,
    validar_schema_saida: bool = True,
) -> dict[str, Any]:
    porta = PortaHistoriadorConfluenciaV1(repositorio)
    return NucleoConfluenciaReplay(
        porta,
        validar_schema_saida=validar_schema_saida,
    ).avaliar(consulta)
