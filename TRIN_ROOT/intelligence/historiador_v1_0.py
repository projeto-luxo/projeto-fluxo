from pathlib import Path
from datetime import datetime

from historiador_estatistico import gerar_estatistica_biblioteca
from historiador_temporal import gerar_cobertura_temporal, gerar_distribuicao_fractais
from historiador_delta import gerar_estatistica_delta
from historiador_volume import gerar_estatistica_volume
from historiador_padroes import gerar_padroes_iniciais
from historiador_contextual import gerar_contexto_inicial, CONHECIMENTO


# ============================================================
# HISTORIADOR v1.0 — ORQUESTRADOR
# Missao: gerar conhecimento inicial a partir dos indices Bernardo.
# Nao altera biblioteca historica.
# ============================================================


def main():
    print("\n" + "=" * 60)
    print("HISTORIADOR v1.0 - CONHECIMENTO INICIAL")
    print("=" * 60)

    saidas = []
    saidas.append(gerar_estatistica_biblioteca())
    saidas.append(gerar_cobertura_temporal())
    saidas.append(gerar_distribuicao_fractais())
    saidas.append(gerar_estatistica_delta())
    saidas.append(gerar_estatistica_volume())
    saidas.append(gerar_padroes_iniciais())
    saidas.append(gerar_contexto_inicial())

    relatorio = CONHECIMENTO / "relatorio_historiador.txt"
    texto = [
        "HISTORIADOR v1.0 - RELATORIO OFICIAL",
        "=" * 60,
        f"Data/hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "Status: CONCLUIDO",
        "Missao: transformar indices do Bernardo em conhecimento inicial.",
        "Arquivos gerados:",
    ]
    for caminho in saidas:
        texto.append(f"- {caminho}")
    texto.append("=" * 60)
    relatorio.write_text("\n".join(texto), encoding="utf-8")

    print("Arquivos gerados:")
    for caminho in saidas:
        print(caminho)
    print(relatorio)
    print("=" * 60)


if __name__ == "__main__":
    main()
