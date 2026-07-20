from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import hashlib
import json
import math
from typing import Any, Iterable, Mapping


class PlanejadorOperacional:
    """Planejador seguro: legado bloqueado e contrato sombra versionado."""

    VERSAO_REGRA = "1.0"
    VERSAO_REGRA_SOMBRA = "1.0-EC1"
    SCHEMA_ENTRADA_SOMBRA = "PlanejamentoOperacionalSombraEntradaV1"
    SCHEMA_SAIDA_SOMBRA = "PlanejamentoOperacionalSombraV1"
    SCHEMA_CONFLUENCIA = "ConfluenciaOperacionalV1"

    CAMPOS_ENTRADA_SOMBRA = frozenset(
        {
            "schema_version",
            "gate_fiscal",
            "contrato_ativo",
            "fontes_saudaveis",
            "regioes_elegiveis",
            "confluencia_versionada",
            "origem_contexto",
            "identidade_snapshot",
        }
    )
    QUALIDADES_CONFLUENCIA_V1 = frozenset(
        {
            "FORTE",
            "MEDIA",
            "FRACA",
            "NEUTRA",
            "BLOQUEADO_POR_CERTIFICACAO",
        }
    )

    def __init__(
        self,
        *,
        modo_sombra_homologado: bool = False,
    ) -> None:
        self._modo_sombra_homologado = (
            modo_sombra_homologado is True
        )

    def planejar(
        self,
        *,
        confluencia: Mapping[str, Any] | None,
        regioes: Iterable[Mapping[str, Any]] | None,
        fiscal_aprovado: bool,
        contrato_ativo: str | None,
        fontes_saudaveis: bool,
    ) -> dict[str, Any]:
        """Compatibilidade segura até a integração versionada do backend."""
        confluencia_recebida = dict(confluencia or {})
        regioes_recebidas = [
            dict(regiao)
            for regiao in (regioes or [])
            if isinstance(regiao, Mapping)
        ]

        motivo = self._motivo_bloqueio(
            confluencia=confluencia_recebida,
            regioes=regioes_recebidas,
            fiscal_aprovado=bool(fiscal_aprovado),
            contrato_ativo=contrato_ativo,
            fontes_saudaveis=bool(fontes_saudaveis),
        )

        return {
            "id_plano": "PO-DIAGNOSTICO-BLOQUEADO",
            "estado": "SEM_OPERACAO",
            "direcao": "NEUTRA",
            "entrada_inferior": None,
            "entrada_superior": None,
            "invalidacao": None,
            "stop": None,
            "parcial": None,
            "alvo": None,
            "autorizacao": "BLOQUEADA",
            "motivo_bloqueio": motivo,
            "uso_operacional": "BLOQUEADO",
            "diagnostico": {
                "contrato_ativo": str(contrato_ativo or "").strip() or None,
                "fiscal_aprovado": bool(fiscal_aprovado),
                "fontes_saudaveis": bool(fontes_saudaveis),
                "regioes_recebidas": len(regioes_recebidas),
                "direcao_confluencia": confluencia_recebida.get("direcao"),
                "score_confluencia": confluencia_recebida.get(
                    "score_confluencia"
                ),
                "qualidade_confluencia": confluencia_recebida.get("qualidade"),
            },
            "versao_regra": self.VERSAO_REGRA,
        }

    def planejar_sombra(
        self,
        entrada: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        """Avalia o contrato EC1 sem produzir autorização ou ordem real."""
        try:
            return self._planejar_sombra(entrada)
        except Exception as erro:
            return self._saida_erro_bloqueado(erro)

    def _planejar_sombra(
        self,
        entrada: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        if not isinstance(entrada, Mapping):
            dados: dict[str, Any] = {}
        else:
            dados = deepcopy(dict(entrada))

        campos_desconhecidos = sorted(
            set(dados) - self.CAMPOS_ENTRADA_SOMBRA
        )

        gate_fiscal = self._mapping(dados.get("gate_fiscal"))
        confluencia = self._mapping(
            dados.get("confluencia_versionada")
        )
        snapshot = self._mapping(dados.get("identidade_snapshot"))
        regioes = self._regioes(
            dados.get("regioes_elegiveis")
        )

        schema_valido = (
            dados.get("schema_version")
            == self.SCHEMA_ENTRADA_SOMBRA
        )

        decisao_fiscal = str(
            gate_fiscal.get("decisao") or ""
        ).strip().upper()
        status_fiscal_bruto = gate_fiscal.get(
            "status_tecnico_bruto"
        )
        status_fiscal_valido = (
            isinstance(status_fiscal_bruto, str)
            and bool(status_fiscal_bruto.strip())
        )

        contrato_valor = dados.get("contrato_ativo")
        contrato_ativo_valido = (
            isinstance(contrato_valor, str)
            and bool(contrato_valor.strip())
        )
        contrato_ativo = (
            contrato_valor.strip()
            if contrato_ativo_valido
            else ""
        )

        fontes_valor = dados.get("fontes_saudaveis")
        fontes_declaradas = isinstance(fontes_valor, bool)
        fontes_saudaveis = fontes_valor is True

        periodo_valor = snapshot.get("periodo_parcial")
        periodo_declarado = isinstance(periodo_valor, bool)
        periodo_parcial = periodo_valor is True

        regioes_aptas = [
            regiao
            for regiao in regioes
            if isinstance(regiao.get("chave_regiao"), str)
            and bool(regiao["chave_regiao"].strip())
            and regiao.get("status") == "ATIVA"
            and regiao.get("uso_operacional") == "LIBERADO"
        ]

        schema_confluencia_valido = (
            confluencia.get("schema_version")
            == self.SCHEMA_CONFLUENCIA
        )
        score_confluencia = confluencia.get(
            "score_confluencia"
        )
        score_valido = self._score_confluencia_valido(
            score_confluencia
        )

        direcao_confluencia = confluencia.get("direcao")
        direcao_valida = direcao_confluencia in {
            "COMPRA",
            "VENDA",
        }

        qualidade_confluencia = str(
            confluencia.get("qualidade") or ""
        ).strip().upper()
        qualidade_valida = (
            qualidade_confluencia
            in self.QUALIDADES_CONFLUENCIA_V1
        )
        confluencia_bloqueada = (
            qualidade_confluencia.startswith("BLOQUEADO")
        )

        evidencias_confluencia = confluencia.get("evidencias")
        evidencias_validas = (
            isinstance(evidencias_confluencia, list)
            and bool(evidencias_confluencia)
        )

        origem = str(
            dados.get("origem_contexto") or ""
        ).strip().upper()
        origem_valida = origem in {"AO_VIVO", "REPLAY"}

        snapshot_basico_valido = self._snapshot_basico_valido(
            snapshot=snapshot,
        )
        origem_sem_lookahead_valida = (
            self._origem_sem_lookahead_valida(
                snapshot=snapshot,
                origem=origem,
            )
        )

        gates_formacao = [
            self._gate(
                "CONTRATO_ENTRADA_VERSIONADO",
                schema_valido,
                "CONTRATO_ENTRADA_AUSENTE_OU_INCOMPATIVEL",
            ),
            self._gate(
                "CAMPOS_SUPERIORES_PERMITIDOS",
                not campos_desconhecidos,
                "CAMPO_SUPERIOR_DESCONHECIDO",
            ),
            self._gate(
                "DECISAO_FISCAL",
                decisao_fiscal == "APROVADA",
                (
                    "DECISAO_FISCAL_AUSENTE"
                    if not decisao_fiscal
                    else "DECISAO_FISCAL_NAO_APROVADA"
                ),
            ),
            self._gate(
                "STATUS_FISCAL_BRUTO",
                status_fiscal_valido,
                "STATUS_FISCAL_BRUTO_AUSENTE_OU_VAZIO",
            ),
            self._gate(
                "CONTRATO_ATIVO",
                contrato_ativo_valido,
                "CONTRATO_ATIVO_NAO_CONFIRMADO",
            ),
            self._gate(
                "FONTES_SAUDAVEIS",
                fontes_saudaveis,
                (
                    "SAUDE_FONTES_NAO_INFORMADA"
                    if not fontes_declaradas
                    else "FONTES_NAO_SAUDAVEIS"
                ),
            ),
            self._gate(
                "IDENTIDADE_TEMPORAL",
                snapshot_basico_valido,
                "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            ),
            self._gate(
                "PERIODO_COMPLETO",
                periodo_declarado and not periodo_parcial,
                (
                    "PERIODO_PARCIALIDADE_NAO_INFORMADA"
                    if not periodo_declarado
                    else "PERIODO_PARCIAL"
                ),
            ),
            self._gate(
                "REGIOES_ELEGIVEIS",
                bool(regioes_aptas),
                "REGIOES_SEM_ELEGIBILIDADE_OPERACIONAL",
            ),
            self._gate(
                "CONFLUENCIA_VERSIONADA",
                schema_confluencia_valido,
                "CONFLUENCIA_SEM_CONTRATO_VERSIONADO",
            ),
            self._gate(
                "SCORE_CONFLUENCIA",
                score_valido,
                "CONFLUENCIA_SCORE_INVALIDO",
            ),
            self._gate(
                "DIRECAO_CONFLUENCIA",
                direcao_valida,
                "CONFLUENCIA_SEM_DIRECAO_ELEGIVEL",
            ),
            self._gate(
                "QUALIDADE_CONFLUENCIA",
                qualidade_valida,
                "CONFLUENCIA_QUALIDADE_INVALIDA",
            ),
            self._gate(
                "CONFLUENCIA_NAO_BLOQUEADA",
                qualidade_valida and not confluencia_bloqueada,
                "CONFLUENCIA_BLOQUEADA",
            ),
            self._gate(
                "EVIDENCIAS_CONFLUENCIA",
                evidencias_validas,
                "CONFLUENCIA_EVIDENCIAS_AUSENTES",
            ),
            self._gate(
                "ORIGEM_CONTEXTO",
                origem_valida,
                "ORIGEM_CONTEXTO_DESCONHECIDA",
            ),
            self._gate(
                "SEPARACAO_AO_VIVO_REPLAY",
                origem_sem_lookahead_valida,
                "SNAPSHOT_AUSENTE_INCOERENTE_OU_COM_LOOK_AHEAD",
            ),
            self._gate(
                "MODO_SOMBRA_HOMOLOGADO",
                self._modo_sombra_homologado,
                "MODO_SOMBRA_NAO_HOMOLOGADO",
            ),
        ]

        primeiro_bloqueio = next(
            (
                gate["motivo_reprovacao"]
                for gate in gates_formacao
                if not gate["aprovado"]
            ),
            None,
        )
        plano_formado = primeiro_bloqueio is None

        gates = [
            *gates_formacao,
            {
                "id": "AUTORIZACAO_OPERACIONAL_EXTERNA",
                "aprovado": False,
                "motivo_reprovacao":
                    "MODO_SOMBRA_SEM_AUTORIZACAO_OPERACIONAL",
                "efeito": "MANTER_BLOQUEIO_OPERACIONAL",
            },
        ]

        entrada_hash = self._hash_deterministico(dados)
        direcao = (
            str(direcao_confluencia)
            if plano_formado
            else None
        )
        estado = "PLANO_SOMBRA" if plano_formado else "BLOQUEADO"
        motivo = (
            "MODO_SOMBRA_SEM_AUTORIZACAO_OPERACIONAL"
            if plano_formado
            else str(primeiro_bloqueio)
        )
        prefixo = "PO-SOMBRA" if plano_formado else "PO-BLOQUEADO"

        niveis = {
            "entrada_inferior": None,
            "entrada_superior": None,
            "invalidacao": None,
            "stop": None,
            "parcial": None,
            "alvo": None,
        }

        return {
            "schema_version": self.SCHEMA_SAIDA_SOMBRA,
            "id_plano": f"{prefixo}-{entrada_hash[:16].upper()}",
            "modo": "SOMBRA",
            "origem_contexto": origem or "DESCONHECIDA",
            "estado": estado,
            "autorizacao": "BLOQUEADA",
            "uso_operacional": "BLOQUEADO",
            "motivo_bloqueio": motivo,
            "direcao": direcao,
            **niveis,
            "ordem_corretora": None,
            "entradas_recebidas": dados,
            "gates": gates,
            "evidencias": {
                "gate_fiscal": {
                    "decisao": decisao_fiscal or None,
                    "status_tecnico_bruto": status_fiscal_bruto,
                    "motivo": gate_fiscal.get("motivo"),
                    "fonte": gate_fiscal.get("fonte"),
                },
                "confluencia": deepcopy(confluencia),
                "fontes_saudaveis": (
                    fontes_valor if fontes_declaradas else None
                ),
                "periodo_parcial": (
                    periodo_valor if periodo_declarado else None
                ),
                "regioes_recebidas": len(regioes),
                "regioes_elegiveis": len(regioes_aptas),
                "campos_superiores_desconhecidos":
                    campos_desconhecidos,
            },
            "hipotese_plano": (
                {
                    "natureza": "DIAGNOSTICA",
                    "direcao": direcao,
                    "niveis": deepcopy(niveis),
                    "ordem_corretora": None,
                }
                if plano_formado
                else None
            ),
            "rastreabilidade": {
                "identidade_snapshot": deepcopy(snapshot),
                "hash_entrada": entrada_hash,
                "versao_regra": self.VERSAO_REGRA_SOMBRA,
                "look_ahead": False,
            },
        }

    @staticmethod
    def _mapping(valor: Any) -> dict[str, Any]:
        if not isinstance(valor, Mapping):
            return {}
        return deepcopy(dict(valor))

    @staticmethod
    def _regioes(valor: Any) -> list[dict[str, Any]]:
        if isinstance(valor, (str, bytes)) or not isinstance(
            valor,
            Iterable,
        ):
            return []
        return [
            deepcopy(dict(regiao))
            for regiao in valor
            if isinstance(regiao, Mapping)
        ]

    @staticmethod
    def _gate(
        identificador: str,
        aprovado: bool,
        motivo_reprovacao: str,
    ) -> dict[str, Any]:
        return {
            "id": identificador,
            "aprovado": bool(aprovado),
            "motivo_reprovacao": (
                None if aprovado else motivo_reprovacao
            ),
        }

    @staticmethod
    def _score_confluencia_valido(valor: Any) -> bool:
        return (
            isinstance(valor, (int, float))
            and not isinstance(valor, bool)
            and math.isfinite(valor)
            and -10 <= valor <= 10
        )

    @staticmethod
    def _snapshot_basico_valido(
        *,
        snapshot: Mapping[str, Any],
    ) -> bool:
        evento_id = snapshot.get("evento_id")
        timestamp = snapshot.get("timestamp")
        sequencia = snapshot.get("sequencia")

        if not (
            isinstance(evento_id, str)
            and bool(evento_id.strip())
        ):
            return False
        if not (
            isinstance(timestamp, str)
            and bool(timestamp.strip())
        ):
            return False
        if not PlanejadorOperacional._timestamp_com_timezone(
            timestamp.strip()
        ):
            return False
        return PlanejadorOperacional._inteiro_nao_negativo(
            sequencia
        )

    @staticmethod
    def _origem_sem_lookahead_valida(
        *,
        snapshot: Mapping[str, Any],
        origem: str,
    ) -> bool:
        if origem == "AO_VIVO":
            return True
        if origem != "REPLAY":
            return False

        sequencia = snapshot.get("sequencia")
        ordem_evento = snapshot.get("ordem_evento")
        janela_fim_ordem = snapshot.get(
            "janela_fim_ordem"
        )

        return (
            PlanejadorOperacional._inteiro_nao_negativo(
                sequencia
            )
            and PlanejadorOperacional._inteiro_nao_negativo(
                ordem_evento
            )
            and PlanejadorOperacional._inteiro_nao_negativo(
                janela_fim_ordem
            )
            and sequencia == ordem_evento
            and ordem_evento == janela_fim_ordem
        )

    @staticmethod
    def _inteiro_nao_negativo(valor: Any) -> bool:
        return (
            isinstance(valor, int)
            and not isinstance(valor, bool)
            and valor >= 0
        )

    @staticmethod
    def _timestamp_com_timezone(valor: str) -> bool:
        try:
            normalizado = (
                valor[:-1] + "+00:00"
                if valor.endswith("Z")
                else valor
            )
            instante = datetime.fromisoformat(normalizado)
        except (TypeError, ValueError):
            return False

        return (
            instante.tzinfo is not None
            and instante.utcoffset() is not None
        )

    @staticmethod
    def _hash_deterministico(dados: Mapping[str, Any]) -> str:
        serializado = json.dumps(
            dados,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        return hashlib.sha256(
            serializado.encode("utf-8")
        ).hexdigest()

    def _saida_erro_bloqueado(
        self,
        erro: Exception,
    ) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_SAIDA_SOMBRA,
            "id_plano": "PO-ERRO-BLOQUEADO",
            "modo": "SOMBRA",
            "origem_contexto": "DESCONHECIDA",
            "estado": "ERRO_BLOQUEADO",
            "autorizacao": "BLOQUEADA",
            "uso_operacional": "BLOQUEADO",
            "motivo_bloqueio": "ERRO_INTERNO_PLANEJADOR",
            "direcao": None,
            "entrada_inferior": None,
            "entrada_superior": None,
            "invalidacao": None,
            "stop": None,
            "parcial": None,
            "alvo": None,
            "ordem_corretora": None,
            "entradas_recebidas": None,
            "gates": [],
            "evidencias": {
                "erro_tipo": type(erro).__name__,
            },
            "hipotese_plano": None,
            "rastreabilidade": {
                "identidade_snapshot": {},
                "hash_entrada": None,
                "versao_regra": self.VERSAO_REGRA_SOMBRA,
                "look_ahead": False,
            },
        }

    @staticmethod
    def _motivo_bloqueio(
        *,
        confluencia: Mapping[str, Any],
        regioes: list[dict[str, Any]],
        fiscal_aprovado: bool,
        contrato_ativo: str | None,
        fontes_saudaveis: bool,
    ) -> str:
        if not fiscal_aprovado:
            return "FISCAL_NAO_APROVADO"

        if not str(contrato_ativo or "").strip():
            return "CONTRATO_ATIVO_NAO_CONFIRMADO"

        if not fontes_saudaveis:
            return "FONTES_NAO_SAUDAVEIS"

        regioes_elegiveis = [
            regiao
            for regiao in regioes
            if regiao.get("status") == "ATIVA"
            and regiao.get("uso_operacional") == "LIBERADO"
        ]
        if not regioes_elegiveis:
            return "REGIOES_SEM_ELEGIBILIDADE_OPERACIONAL"

        if confluencia.get("direcao") not in {"COMPRA", "VENDA"}:
            return "CONFLUENCIA_SEM_DIRECAO_ELEGIVEL"

        qualidade = str(confluencia.get("qualidade") or "")
        if qualidade.startswith("BLOQUEADO"):
            return "CONFLUENCIA_BLOQUEADA"

        return "PLANEJADOR_NAO_HOMOLOGADO"
