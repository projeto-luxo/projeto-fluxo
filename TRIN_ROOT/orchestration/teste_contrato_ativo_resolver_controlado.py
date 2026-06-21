from pathlib import Path
from contrato_ativo_resolver import ContratoAtivoResolver


def criar_calendario_teste(caminho: Path):
    caminho.parent.mkdir(parents=True, exist_ok=True)

    caminho.write_text(
        "\n".join([
            "ativo_base;contrato_visual;contrato_rtd;ano;mes_vencimento;codigo_mes;data_vencimento_oficial;udn;lf;inicio_validade;fim_validade;fonte;fonte_data_revisao;status_confiabilidade;observacao",
            "WIN;WINM26;WINM26_F_0;2026;2026-06;M;2026-06-17;2026-06-17;2026-06-18;2026-04-16;2026-06-17;TESTE_CONTROLADO;2026-06-20;NAO_HOMOLOGADO;Linha sintetica para teste",
            "WIN;WINQ26;WINQ26_F_0;2026;2026-08;Q;2026-08-12;2026-08-12;2026-08-13;2026-06-18;2026-08-12;TESTE_CONTROLADO;2026-06-20;NAO_HOMOLOGADO;Linha sintetica para teste",
        ]),
        encoding="utf-8",
    )


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    calendario_teste = raiz / "config" / "calendarios" / "TESTE_calendario_contratos_b3_controlado.csv"

    criar_calendario_teste(calendario_teste)

    resolver = ContratoAtivoResolver(calendario_teste)

    resultado_antes = resolver.resolver("WIN", "2026-06-17")
    resultado_depois = resolver.resolver("WIN", "2026-06-20")
    resultado_fora = resolver.resolver("WIN", "2027-01-01")

    print("=== TESTE 1 — ANTES DA ROLAGEM ===")
    print(resultado_antes)

    print("\n=== TESTE 2 — DEPOIS DA ROLAGEM ===")
    print(resultado_depois)

    print("\n=== TESTE 3 — FORA DA COBERTURA ===")
    print(resultado_fora)

    assert resultado_antes.contrato_rtd_esperado == "WINM26_F_0"
    assert resultado_depois.contrato_rtd_esperado == "WINQ26_F_0"
    assert resultado_fora.status_resolucao == "DATA_FORA_DA_COBERTURA"

    print("\nTESTE_CONTROLADO_OK")
