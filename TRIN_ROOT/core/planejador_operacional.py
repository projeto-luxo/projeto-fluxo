from __future__ import annotations

from typing import Any, Iterable, Mapping


class PlanejadorOperacional:
    """Primeira versão segura: consome evidências, mas não cria operação."""

    VERSAO_REGRA = "1.0"

    def planejar(
        self,
        *,
        confluencia: Mapping[str, Any] | None,
        regioes: Iterable[Mapping[str, Any]] | None,
        fiscal_aprovado: bool,
        contrato_ativo: str | None,
        fontes_saudaveis: bool,
    ) -> dict[str, Any]:
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
