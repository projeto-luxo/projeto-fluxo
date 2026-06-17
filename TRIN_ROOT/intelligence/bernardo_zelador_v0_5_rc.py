import os
import pandas as pd
from pathlib import Path
from datetime import datetime


# ============================================================
# BERNARDO v0.5 RC
# ZELADOR DA BIBLIOTECA HISTORICA
# Ajustado para TRIN_ROOT
# Missao: auditar nomes e estrutura da biblioteca historica
# NAO MOVE
# NAO RENOMEIA
# NAO APAGA
# ============================================================

TRIN_ROOT = Path(__file__).resolve().parents[1]

BASE_PATH = TRIN_ROOT / "TRIN_HISTORICO"
PASTA_INDICES = BASE_PATH / "00_INDICES"

ARQUIVO_RELATORIO = PASTA_INDICES / "relatorio_zelador_biblioteca.csv"

IGNORAR = {
    "00_INDICES",
    "00_LOGS",
    "00_MANIFESTOS",
    "00_RELATORIOS",
    "00_AUDITORIA",
    "00_CONFIG",
    "00_DUPLICIDADES_FRACTAIS",
    "00_MEMORIA_PROCESSADA",
}


def detectar_ativo_nome(nome):
    texto = str(nome).upper()

    if "WIN" in texto:
        return "WIN"

    if "WDO" in texto:
        return "WDO"

    return "DESCONHECIDO"


def detectar_fractal_pasta(pasta):
    texto = str(pasta).upper()

    if "DIARIO" in texto:
        return "DIARIO"

    if "SEMANAL" in texto:
        return "SEMANAL"

    if "MENSAL" in texto:
        return "MENSAL"

    partes = texto.split("_")

    for parte in partes:
        if parte.isdigit():
            return f"{int(parte)}_MIN"

    return "DESCONHECIDO"


def main():
    print("\n" + "=" * 60)
    print("BERNARDO v0.5 RC - ZELADOR DA BIBLIOTECA")
    print("=" * 60)

    print(f"Pasta historico: {BASE_PATH}")
    print(f"Pasta indices  : {PASTA_INDICES}")

    if not BASE_PATH.exists():
        print("ERRO: pasta TRIN_HISTORICO nao encontrada.")
        return

    PASTA_INDICES.mkdir(parents=True, exist_ok=True)

    registros = []

    for pasta in sorted(os.listdir(BASE_PATH)):
        if pasta in IGNORAR:
            continue

        caminho_pasta = BASE_PATH / pasta

        if not caminho_pasta.is_dir():
            continue

        fractal_pasta = detectar_fractal_pasta(pasta)

        for raiz, _, arquivos in os.walk(caminho_pasta):
            for arquivo in sorted(arquivos):
                if not arquivo.lower().endswith(".csv"):
                    continue

                caminho = Path(raiz) / arquivo
                ativo_nome = detectar_ativo_nome(arquivo)

                problemas = []

                if ativo_nome == "DESCONHECIDO":
                    problemas.append("ATIVO_NAO_IDENTIFICADO_NO_NOME")

                if fractal_pasta == "DESCONHECIDO":
                    problemas.append("FRACTAL_NAO_IDENTIFICADO_NA_PASTA")

                if " " in arquivo:
                    problemas.append("NOME_COM_ESPACO")

                if arquivo != arquivo.strip():
                    problemas.append("NOME_COM_ESPACO_NAS_EXTREMIDADES")

                status = "OK" if not problemas else "VERIFICAR"

                registros.append({
                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "pasta_base": pasta,
                    "fractal_pasta": fractal_pasta,
                    "arquivo": arquivo,
                    "ativo_nome": ativo_nome,
                    "caminho": str(caminho),
                    "status": status,
                    "problemas": " | ".join(problemas) if problemas else "NENHUM",
                })

                print(
                    f"{status} | "
                    f"{ativo_nome} | "
                    f"{fractal_pasta} | "
                    f"{arquivo}"
                )

    df = pd.DataFrame(registros)

    df.to_csv(
        ARQUIVO_RELATORIO,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("RESUMO ZELADOR BIBLIOTECA")
    print("=" * 60)
    print(f"Arquivos analisados : {len(df)}")

    if len(df) > 0:
        print(f"OK                  : {len(df[df['status'] == 'OK'])}")
        print(f"Verificar           : {len(df[df['status'] == 'VERIFICAR'])}")

    print(f"Relatorio salvo em  : {ARQUIVO_RELATORIO}")
    print("=" * 60)


if __name__ == "__main__":
    main()