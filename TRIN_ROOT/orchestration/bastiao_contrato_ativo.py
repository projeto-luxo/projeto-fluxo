from dataclasses import dataclass


@dataclass
class ResultadoValidacaoContrato:
    contrato_esperado_rtd: str | None
    contrato_excel_rtd: str | None
    contrato_backend_rtd: str | None
    status_validacao: str
    motivo: str
    bloqueio_operacional: bool


class BastiaoContratoAtivo:
    """
    Validador institucional do contrato ativo TRIN.

    Responsabilidade unica:
    - Validar se o contrato esperado bate com Excel e Backend.
    - Nao resolve calendario.
    - Nao altera Excel.
    - Nao le Profit.
    - Nao gera sinal.
    """

    def validar(
        self,
        contrato_esperado_rtd: str | None,
        contrato_excel_rtd: str | None,
        contrato_backend_rtd: str | None,
    ) -> ResultadoValidacaoContrato:

        if not contrato_esperado_rtd:
            return ResultadoValidacaoContrato(
                contrato_esperado_rtd=contrato_esperado_rtd,
                contrato_excel_rtd=contrato_excel_rtd,
                contrato_backend_rtd=contrato_backend_rtd,
                status_validacao="BLOQUEADO",
                motivo="Contrato esperado ausente. Resolver nao forneceu contrato valido.",
                bloqueio_operacional=True,
            )

        if not contrato_excel_rtd:
            return ResultadoValidacaoContrato(
                contrato_esperado_rtd=contrato_esperado_rtd,
                contrato_excel_rtd=contrato_excel_rtd,
                contrato_backend_rtd=contrato_backend_rtd,
                status_validacao="BLOQUEADO",
                motivo="Contrato aplicado no Excel ausente.",
                bloqueio_operacional=True,
            )

        if contrato_excel_rtd != contrato_esperado_rtd:
            return ResultadoValidacaoContrato(
                contrato_esperado_rtd=contrato_esperado_rtd,
                contrato_excel_rtd=contrato_excel_rtd,
                contrato_backend_rtd=contrato_backend_rtd,
                status_validacao="REPROVADO",
                motivo="Contrato do Excel diverge do contrato esperado pelo Resolver.",
                bloqueio_operacional=True,
            )

        if contrato_backend_rtd and contrato_backend_rtd != contrato_esperado_rtd:
            return ResultadoValidacaoContrato(
                contrato_esperado_rtd=contrato_esperado_rtd,
                contrato_excel_rtd=contrato_excel_rtd,
                contrato_backend_rtd=contrato_backend_rtd,
                status_validacao="REPROVADO",
                motivo="Contrato lido pelo Backend diverge do contrato esperado.",
                bloqueio_operacional=True,
            )

        if not contrato_backend_rtd:
            return ResultadoValidacaoContrato(
                contrato_esperado_rtd=contrato_esperado_rtd,
                contrato_excel_rtd=contrato_excel_rtd,
                contrato_backend_rtd=contrato_backend_rtd,
                status_validacao="APROVADO_COM_RESSALVA",
                motivo="Excel esta correto, mas Backend ainda nao informou contrato.",
                bloqueio_operacional=False,
            )

        return ResultadoValidacaoContrato(
            contrato_esperado_rtd=contrato_esperado_rtd,
            contrato_excel_rtd=contrato_excel_rtd,
            contrato_backend_rtd=contrato_backend_rtd,
            status_validacao="APROVADO",
            motivo="Contrato esperado, Excel e Backend estao alinhados.",
            bloqueio_operacional=False,
        )


if __name__ == "__main__":
    bastiao = BastiaoContratoAtivo()

    testes = [
        ("WINQ26_F_0", "WINQ26_F_0", "WINQ26_F_0"),
        ("WINQ26_F_0", "WINM26_F_0", "WINM26_F_0"),
        ("WINQ26_F_0", "WINQ26_F_0", None),
        (None, "WINQ26_F_0", "WINQ26_F_0"),
    ]

    for teste in testes:
        print(bastiao.validar(*teste))
