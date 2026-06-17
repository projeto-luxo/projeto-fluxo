# -*- coding: utf-8 -*-
# ============================================================
# ZÉ DO EUCRÁZIO 4.0 — OFICIAL / TESTE CONTROLADO
# ENGENHEIRO TEMPORAL DO TRIN
#
# Metodologia aplicada:
# ETAPA 0 — Análise de Necessidade Evolutiva
# ETAPA 1 — Auditoria Arquitetural
# ETAPA 2 — Contrato do Módulo
# ETAPA 3 — Implementação Conservadora
# ETAPA 4 — Teste Controlado
#
# REGRA DE OURO:
# Zé do Eucrázio gera fractais determinísticos.
# Fiscal Temporal certifica a integridade final.
#
# O Zé NÃO:
# - interpreta mercado
# - gera sinais
# - calcula score
# - homologa memória
# - substitui o Bernardo
# - substitui o Fiscal Temporal
#
# O Zé SIM:
# - lê histórico 1 minuto
# - normaliza campos
# - agrupa por sessão
# - gera fractais derivados
# - registra parciais
# - gera logs e manifesto
# - preserva rastreabilidade
# ============================================================

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd


# ============================================================
# CONFIGURAÇÃO OFICIAL
# ============================================================

BASE_PATH = Path(r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO")

ATIVO_PASTA = "win"
ATIVO_PREFIXO_ARQUIVO = "WIN"

PASTA_ORIGEM = BASE_PATH / "01_1_MIN" / ATIVO_PASTA

TIMEZONE_OFICIAL = "America/Sao_Paulo"

# Primeira execução oficial deve ser teste controlado.
# Para processar tudo, mude para False depois do teste.
MODO_TESTE_CONTROLADO = True
MAX_ARQUIVOS_TESTE = 1

# Segurança contra sobrescrita acidental.
# Se False, arquivo existente não será sobrescrito.
SOBRESCREVER_SAIDA = False

# Política oficial de candle parcial:
# - manter no arquivo de saída com status_candle = PARCIAL
# - registrar também em relatório separado
MANTER_CANDLES_PARCIAIS_NA_SAIDA = True

# Fractais oficiais em minutos.
FRACTAIS_MINUTOS = [
    2, 3, 4, 5, 6, 7, 8, 9, 10, 12,
    15, 20, 30, 45, 60, 90, 120, 180, 240,
]

# Pastas oficiais.
# Mantém padrão legível e evita ambiguidade.
def pasta_fractal(minutos: int) -> str:
    return f"{minutos:02d}_{minutos}_MIN"


PASTA_LOGS = BASE_PATH / "00_LOGS" / "ze_do_eucrazio"
PASTA_RELATORIOS = BASE_PATH / "00_RELATORIOS" / "ze_do_eucrazio"
PASTA_MANIFESTOS = BASE_PATH / "00_MANIFESTOS" / "ze_do_eucrazio"


# Contrato oficial de saída.
COLUNAS_SAIDA = [
    "ativo",
    "data",
    "hora",
    "timestamp",
    "timezone",
    "sessao",
    "fractal_minutos",
    "status_candle",
    "qtd_candles_origem",
    "abertura",
    "maximo",
    "minimo",
    "ultimo",
    "volume",
    "volume_quantidade",
    "delta",
    "saldo",
    "agressao_compra",
    "agressao_saldo",
    "agressao_venda",
    "vwap",
]


# ============================================================
# MODELOS DE LOG
# ============================================================

@dataclass
class ResultadoFractal:
    fractal_minutos: int
    status: str
    arquivo_saida: Optional[str]
    hash_saida: Optional[str]
    linhas_saida: int
    candles_completos: int
    candles_parciais: int
    relatorio_parciais: Optional[str]
    motivo: Optional[str] = None


@dataclass
class ResultadoArquivo:
    arquivo_origem: str
    hash_origem: str
    tipo_detectado: Optional[str]
    linhas_origem: int
    status: str
    alertas: List[str]
    erros: List[str]
    fractais: List[ResultadoFractal]


# ============================================================
# UTILITÁRIOS
# ============================================================

def garantir_pastas() -> None:
    PASTA_LOGS.mkdir(parents=True, exist_ok=True)
    PASTA_RELATORIOS.mkdir(parents=True, exist_ok=True)
    PASTA_MANIFESTOS.mkdir(parents=True, exist_ok=True)

    for minutos in FRACTAIS_MINUTOS:
        (BASE_PATH / pasta_fractal(minutos) / ATIVO_PASTA).mkdir(parents=True, exist_ok=True)


def agora_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def hash_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()

    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)

    return h.hexdigest()


def limpar_numero(valor) -> float:
    """
    Conversão conservadora para números vindos do Profit/CSV brasileiro.

    Regras:
    - "1.234,56" -> 1234.56
    - "1234,56"  -> 1234.56
    - "1234.56"  -> 1234.56
    - "1.234"    -> 1234.0 se parecer milhar
    - vazio/NaN  -> 0.0
    """
    if pd.isna(valor):
        return 0.0

    texto = str(valor).strip().replace(" ", "")

    if texto == "":
        return 0.0

    # Remove caracteres comuns indesejados, preservando sinais e separadores.
    texto = texto.replace("\ufeff", "")

    try:
        if "," in texto and "." in texto:
            # Formato BR com milhar e decimal.
            texto = texto.replace(".", "").replace(",", ".")
        elif "," in texto:
            # Decimal BR.
            texto = texto.replace(",", ".")
        elif "." in texto:
            # Pode ser decimal internacional ou milhar.
            partes = texto.split(".")
            if len(partes) > 1 and all(len(p) == 3 for p in partes[1:]) and len(partes[-1]) == 3:
                texto = texto.replace(".", "")
            # Caso contrário, mantém ponto decimal.
        return float(texto)
    except Exception:
        return 0.0


def listar_csvs_origem() -> List[Path]:
    if not PASTA_ORIGEM.exists():
        raise FileNotFoundError(f"Pasta de origem não encontrada: {PASTA_ORIGEM}")

    arquivos = sorted([
        p for p in PASTA_ORIGEM.iterdir()
        if p.is_file() and p.suffix.lower() == ".csv"
    ])

    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV encontrado em: {PASTA_ORIGEM}")

    if MODO_TESTE_CONTROLADO:
        return arquivos[:MAX_ARQUIVOS_TESTE]

    return arquivos


def detectar_header(df_raw: pd.DataFrame) -> bool:
    if df_raw.empty:
        return False

    primeira_linha = [str(x).strip().lower() for x in df_raw.iloc[0].tolist()]
    marcadores = {"ativo", "timestamp_pc", "data", "hora", "abertura", "ultimo"}

    return any(x in marcadores for x in primeira_linha)


def caminho_saida_para(caminho_origem: Path, minutos: int) -> Path:
    nome = caminho_origem.name

    substituicoes = [
        ("1min", f"{minutos}min"),
        ("1MIN", f"{minutos}MIN"),
        ("1_Min", f"{minutos}_Min"),
        ("1_MIN", f"{minutos}_MIN"),
        ("1_min", f"{minutos}_min"),
    ]

    nome_novo = nome
    for antigo, novo in substituicoes:
        nome_novo = nome_novo.replace(antigo, novo)

    if nome_novo == nome:
        nome_novo = f"{ATIVO_PREFIXO_ARQUIVO}_{minutos}min_{nome}"

    return BASE_PATH / pasta_fractal(minutos) / ATIVO_PASTA / nome_novo


def salvar_csv_padrao(df: pd.DataFrame, caminho: Path) -> None:
    df.to_csv(
        caminho,
        sep=";",
        index=False,
        header=True,
        encoding="utf-8-sig",
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )


# ============================================================
# LEITURA E NORMALIZAÇÃO
# ============================================================

def carregar_csv(caminho_csv: Path) -> Tuple[pd.DataFrame, str, List[str]]:
    alertas: List[str] = []

    df = pd.read_csv(
        caminho_csv,
        sep=";",
        header=None,
        engine="python",
        encoding="utf-8-sig",
        dtype=str,
    )

    if df.empty:
        raise ValueError("Arquivo vazio.")

    if detectar_header(df):
        df = df.iloc[1:].reset_index(drop=True)
        alertas.append("Header detectado e removido na leitura.")

    qtd_colunas = df.shape[1]

    if qtd_colunas >= 15:
        tipo = "MEMORIA_VIVA_TRIN"
        df = df.iloc[:, :15]
        df.columns = [
            "timestamp_pc",
            "ativo",
            "data",
            "hora",
            "ultimo",
            "abertura",
            "maximo",
            "minimo",
            "volume",
            "delta",
            "saldo",
            "agressao_compra",
            "agressao_saldo",
            "agressao_venda",
            "vwap",
        ]
        df["volume_quantidade"] = 0.0

    elif qtd_colunas >= 9:
        tipo = "HISTORICO_PROFIT"
        df = df.iloc[:, :9]
        df.columns = [
            "ativo",
            "data",
            "hora",
            "abertura",
            "maximo",
            "minimo",
            "ultimo",
            "volume",
            "volume_quantidade",
        ]
        df["delta"] = 0.0
        df["saldo"] = 0.0
        df["agressao_compra"] = 0.0
        df["agressao_saldo"] = 0.0
        df["agressao_venda"] = 0.0
        df["vwap"] = df["ultimo"]

    elif qtd_colunas >= 8:
        tipo = "HISTORICO_PROFIT_REDUZIDO"
        df = df.iloc[:, :8]
        df.columns = [
            "ativo",
            "data",
            "hora",
            "abertura",
            "maximo",
            "minimo",
            "ultimo",
            "volume",
        ]
        df["volume_quantidade"] = 0.0
        df["delta"] = 0.0
        df["saldo"] = 0.0
        df["agressao_compra"] = 0.0
        df["agressao_saldo"] = 0.0
        df["agressao_venda"] = 0.0
        df["vwap"] = df["ultimo"]

    else:
        raise ValueError(f"Arquivo com colunas insuficientes: {qtd_colunas}")

    df["datetime"] = pd.to_datetime(
        df["data"].astype(str).str.strip() + " " + df["hora"].astype(str).str.strip(),
        dayfirst=True,
        errors="coerce",
    )

    linhas_antes = len(df)
    df = df.dropna(subset=["datetime"]).copy()
    removidas = linhas_antes - len(df)

    if removidas > 0:
        alertas.append(f"{removidas} linhas removidas por data/hora inválida.")

    campos_numericos = [
        "ultimo",
        "abertura",
        "maximo",
        "minimo",
        "volume",
        "volume_quantidade",
        "delta",
        "saldo",
        "agressao_compra",
        "agressao_saldo",
        "agressao_venda",
        "vwap",
    ]

    for campo in campos_numericos:
        df[campo] = df[campo].apply(limpar_numero)

    df["ordem_original"] = range(len(df))
    df = df.sort_values(["datetime", "ordem_original"]).reset_index(drop=True)

    # Sessão oficial inicial: data do pregão.
    # O Fiscal Temporal deverá evoluir para calendário real B3, feriados e horários especiais.
    df["sessao"] = df["datetime"].dt.strftime("%Y-%m-%d")

    return df, tipo, alertas


# ============================================================
# VALIDAÇÃO BÁSICA DO ZÉ
# ============================================================

def validar_origem_basico(df: pd.DataFrame) -> List[str]:
    alertas: List[str] = []

    if df.empty:
        alertas.append("Origem vazia após normalização.")
        return alertas

    duplicados = int(df["datetime"].duplicated().sum())
    if duplicados > 0:
        alertas.append(f"{duplicados} timestamps duplicados encontrados na origem.")

    ohlc_invalido = df[
        (df["maximo"] < df["minimo"]) |
        (df["abertura"] > df["maximo"]) |
        (df["abertura"] < df["minimo"]) |
        (df["ultimo"] > df["maximo"]) |
        (df["ultimo"] < df["minimo"])
    ]

    if len(ohlc_invalido) > 0:
        alertas.append(f"{len(ohlc_invalido)} candles origem com OHLC inconsistente.")

    sessoes = df["sessao"].nunique()
    if sessoes <= 0:
        alertas.append("Nenhuma sessão identificada.")

    return alertas


# ============================================================
# AGREGAÇÃO DETERMINÍSTICA
# ============================================================

def calcular_vwap_agregado(bloco: pd.DataFrame) -> float:
    """
    VWAP agregada por ponderação de volume quando possível.
    Caso volume total seja zero, usa o último VWAP disponível.
    """
    volume_total = float(bloco["volume"].sum())

    if volume_total > 0:
        return float((bloco["vwap"] * bloco["volume"]).sum() / volume_total)

    return float(bloco.iloc[-1]["vwap"])


def agregar_fractal(df: pd.DataFrame, minutos: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    linhas = []
    linhas_parciais = []

    for sessao, grupo_sessao in df.groupby("sessao", sort=True):
        grupo_sessao = grupo_sessao.sort_values(["datetime", "ordem_original"]).reset_index(drop=True)

        # Agrupamento por contador dentro da sessão.
        # Isso impede cruzar pregões e torna o resultado determinístico.
        grupo_sessao["grupo_fractal"] = grupo_sessao.index // minutos

        for _, bloco in grupo_sessao.groupby("grupo_fractal", sort=True):
            qtd = int(len(bloco))
            status_candle = "COMPLETO" if qtd == minutos else "PARCIAL"

            if status_candle == "PARCIAL" and not MANTER_CANDLES_PARCIAIS_NA_SAIDA:
                continue

            primeiro = bloco.iloc[0]
            ultimo = bloco.iloc[-1]
            dt = primeiro["datetime"]

            linha = {
                "ativo": primeiro["ativo"],
                "data": dt.strftime("%d/%m/%Y"),
                "hora": dt.strftime("%H:%M:%S"),
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": TIMEZONE_OFICIAL,
                "sessao": sessao,
                "fractal_minutos": minutos,
                "status_candle": status_candle,
                "qtd_candles_origem": qtd,
                "abertura": float(primeiro["abertura"]),
                "maximo": float(bloco["maximo"].max()),
                "minimo": float(bloco["minimo"].min()),
                "ultimo": float(ultimo["ultimo"]),
                "volume": float(bloco["volume"].sum()),
                "volume_quantidade": float(bloco["volume_quantidade"].sum()),
                "delta": float(bloco["delta"].sum()),
                "saldo": float(ultimo["saldo"]),
                "agressao_compra": float(bloco["agressao_compra"].sum()),
                "agressao_saldo": float(bloco["agressao_saldo"].sum()),
                "agressao_venda": float(bloco["agressao_venda"].sum()),
                "vwap": calcular_vwap_agregado(bloco),
            }

            linhas.append(linha)

            if status_candle == "PARCIAL":
                linhas_parciais.append(linha)

    saida = pd.DataFrame(linhas, columns=COLUNAS_SAIDA)
    parciais = pd.DataFrame(linhas_parciais, columns=COLUNAS_SAIDA)

    return saida, parciais


# ============================================================
# PROCESSAMENTO
# ============================================================

def processar_fractal(caminho_origem: Path, df: pd.DataFrame, minutos: int) -> ResultadoFractal:
    caminho_saida = caminho_saida_para(caminho_origem, minutos)

    if caminho_saida.exists() and not SOBRESCREVER_SAIDA:
        return ResultadoFractal(
            fractal_minutos=minutos,
            status="PULADO_ARQUIVO_EXISTENTE",
            arquivo_saida=str(caminho_saida),
            hash_saida=hash_arquivo(caminho_saida),
            linhas_saida=0,
            candles_completos=0,
            candles_parciais=0,
            relatorio_parciais=None,
            motivo="Arquivo já existe e SOBRESCREVER_SAIDA=False.",
        )

    saida, parciais = agregar_fractal(df, minutos)

    salvar_csv_padrao(saida, caminho_saida)

    relatorio_parciais = None
    if len(parciais) > 0:
        nome_relatorio = caminho_saida.stem + "_CANDLES_PARCIAIS.csv"
        caminho_parciais = PASTA_RELATORIOS / nome_relatorio
        salvar_csv_padrao(parciais, caminho_parciais)
        relatorio_parciais = str(caminho_parciais)

    completos = int((saida["status_candle"] == "COMPLETO").sum()) if not saida.empty else 0
    qtd_parciais = int((saida["status_candle"] == "PARCIAL").sum()) if not saida.empty else 0

    return ResultadoFractal(
        fractal_minutos=minutos,
        status="GERADO",
        arquivo_saida=str(caminho_saida),
        hash_saida=hash_arquivo(caminho_saida),
        linhas_saida=int(len(saida)),
        candles_completos=completos,
        candles_parciais=qtd_parciais,
        relatorio_parciais=relatorio_parciais,
        motivo="Gerado pelo Zé. Certificação final pertence ao Fiscal Temporal.",
    )


def processar_arquivo(caminho_origem: Path) -> ResultadoArquivo:
    alertas: List[str] = []
    erros: List[str] = []
    fractais: List[ResultadoFractal] = []
    tipo: Optional[str] = None
    linhas_origem = 0

    hash_origem = hash_arquivo(caminho_origem)

    try:
        df, tipo, alertas_leitura = carregar_csv(caminho_origem)
        alertas.extend(alertas_leitura)
        linhas_origem = int(len(df))

        alertas.extend(validar_origem_basico(df))

        if df.empty:
            raise ValueError("Arquivo sem linhas válidas após normalização.")

        for minutos in FRACTAIS_MINUTOS:
            try:
                resultado = processar_fractal(caminho_origem, df, minutos)
                fractais.append(resultado)
            except Exception as erro_fractal:
                erros.append(f"Fractal {minutos} min: {erro_fractal}")

        status = "CONCLUIDO"
        if erros:
            status = "CONCLUIDO_COM_ERROS"
        elif alertas:
            status = "CONCLUIDO_COM_ALERTAS"

    except Exception as erro:
        status = "ERRO"
        erros.append(str(erro))

    return ResultadoArquivo(
        arquivo_origem=str(caminho_origem),
        hash_origem=hash_origem,
        tipo_detectado=tipo,
        linhas_origem=linhas_origem,
        status=status,
        alertas=alertas,
        erros=erros,
        fractais=fractais,
    )


def salvar_manifesto(resultados: List[ResultadoArquivo], inicio: datetime, fim: datetime) -> Path:
    manifesto = {
        "modulo": "ZE_DO_EUCRAZIO",
        "versao": "4.0",
        "status_arquitetural": "TESTE_CONTROLADO",
        "regra_oficial": "Zé gera fractais determinísticos. Fiscal Temporal certifica.",
        "base_path": str(BASE_PATH),
        "pasta_origem": str(PASTA_ORIGEM),
        "timezone_oficial": TIMEZONE_OFICIAL,
        "modo_teste_controlado": MODO_TESTE_CONTROLADO,
        "max_arquivos_teste": MAX_ARQUIVOS_TESTE,
        "sobrescrever_saida": SOBRESCREVER_SAIDA,
        "manter_candles_parciais_na_saida": MANTER_CANDLES_PARCIAIS_NA_SAIDA,
        "fractais_minutos": FRACTAIS_MINUTOS,
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "duracao_segundos": round((fim - inicio).total_seconds(), 2),
        "resultados": [
            {
                **asdict(r),
                "fractais": [asdict(f) for f in r.fractais],
            }
            for r in resultados
        ],
    }

    caminho = PASTA_MANIFESTOS / f"manifesto_ze_eucrazio_4_0_{agora_tag()}.json"

    with caminho.open("w", encoding="utf-8") as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=2)

    return caminho


def salvar_log_texto(resultados: List[ResultadoArquivo], manifesto: Path) -> Path:
    caminho = PASTA_LOGS / f"log_ze_eucrazio_4_0_{agora_tag()}.txt"

    linhas = []
    linhas.append("=" * 80)
    linhas.append("ZÉ DO EUCRÁZIO 4.0 — LOG OPERACIONAL")
    linhas.append("=" * 80)
    linhas.append("Regra oficial: Zé gera. Fiscal Temporal certifica.")
    linhas.append(f"Base: {BASE_PATH}")
    linhas.append(f"Origem: {PASTA_ORIGEM}")
    linhas.append(f"Manifesto: {manifesto}")
    linhas.append("")

    for r in resultados:
        linhas.append("-" * 80)
        linhas.append(f"Origem: {r.arquivo_origem}")
        linhas.append(f"Tipo: {r.tipo_detectado}")
        linhas.append(f"Linhas origem: {r.linhas_origem}")
        linhas.append(f"Status: {r.status}")

        if r.alertas:
            linhas.append("Alertas:")
            for alerta in r.alertas:
                linhas.append(f"  - {alerta}")

        if r.erros:
            linhas.append("Erros:")
            for erro in r.erros:
                linhas.append(f"  - {erro}")

        linhas.append("Fractais:")
        for f in r.fractais:
            linhas.append(
                f"  {f.fractal_minutos:>3} min | {f.status:<24} | "
                f"linhas={f.linhas_saida:<8} completos={f.candles_completos:<8} "
                f"parciais={f.candles_parciais:<8}"
            )

    caminho.write_text("\n".join(linhas), encoding="utf-8")
    return caminho


def processar() -> None:
    garantir_pastas()

    print("\n" + "=" * 80)
    print("🌽 ZÉ DO EUCRÁZIO 4.0 — TESTE CONTROLADO")
    print("=" * 80)
    print("Regra oficial: Zé gera. Fiscal Temporal certifica.")
    print(f"Base: {BASE_PATH}")
    print(f"Origem: {PASTA_ORIGEM}")
    print(f"Timezone oficial: {TIMEZONE_OFICIAL}")
    print(f"Modo teste controlado: {MODO_TESTE_CONTROLADO}")
    print(f"Sobrescrever saída: {SOBRESCREVER_SAIDA}")
    print("=" * 80)

    inicio = datetime.now()

    try:
        arquivos = listar_csvs_origem()
    except Exception as erro:
        print(f"ERRO AO LISTAR ORIGEM: {erro}")
        sys.exit(1)

    print(f"\nArquivos selecionados: {len(arquivos)}")

    resultados: List[ResultadoArquivo] = []

    for caminho in arquivos:
        print("\nProcessando origem:")
        print(caminho)

        resultado = processar_arquivo(caminho)
        resultados.append(resultado)

        print(f"Status: {resultado.status}")
        print(f"Tipo detectado: {resultado.tipo_detectado}")
        print(f"Linhas origem: {resultado.linhas_origem}")

        if resultado.alertas:
            print("Alertas:")
            for alerta in resultado.alertas:
                print(f"  - {alerta}")

        if resultado.erros:
            print("Erros:")
            for erro in resultado.erros:
                print(f"  - {erro}")

        for fractal in resultado.fractais:
            print(
                f"  {fractal.fractal_minutos:>3} min | "
                f"{fractal.status:<24} | "
                f"linhas={fractal.linhas_saida:<7} "
                f"completos={fractal.candles_completos:<7} "
                f"parciais={fractal.candles_parciais:<7}"
            )

    fim = datetime.now()

    manifesto = salvar_manifesto(resultados, inicio, fim)
    log_txt = salvar_log_texto(resultados, manifesto)

    print("\n" + "=" * 80)
    print("PROCESSAMENTO FINALIZADO")
    print(f"Manifesto: {manifesto}")
    print(f"Log texto: {log_txt}")
    print("Observação: a certificação final pertence ao Fiscal Temporal.")
    print("=" * 80)


if __name__ == "__main__":
    processar()
