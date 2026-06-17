# -*- coding: utf-8 -*-
# ============================================================
# ZÉ DO EUCRÁZIO 4.2 — OFICIAL / TESTE CONTROLADO
# ENGENHEIRO TEMPORAL DO TRIN
#
# Evolução de fechamento antes do congelamento arquitetural.
#
# Missão:
# - organizar biblioteca temporal sem apagar dados;
# - gerar fractais determinísticos a partir do 1 minuto;
# - registrar logs, manifesto, auditoria e parciais;
# - entregar ao Fiscal Temporal com status explícito.
#
# O Zé NÃO:
# - certifica integridade final;
# - interpreta mercado;
# - calcula score;
# - substitui Bernardo;
# - substitui Fiscal Temporal.
# ============================================================

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


# ============================================================
# IDENTIDADE INSTITUCIONAL
# ============================================================

VERSAO_MOTOR = "4.2"
VERSAO_CONTRATO_SAIDA = "1.0"
VERSAO_CONFIGURACAO_ESPERADA = "1.2"

NOME_MODULO = "ZE_DO_EUCRAZIO"
STATUS_CERTIFICACAO_PADRAO = "AGUARDANDO_FISCAL_TEMPORAL"
REGRA_OFICIAL = "Zé gera fractais determinísticos. Fiscal Temporal certifica."


# ============================================================
# CONFIGURAÇÃO PADRÃO
# ============================================================

BASE_PATH_PADRAO = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"
ATIVO_PASTA_PADRAO = "win"
ATIVO_PREFIXO_ARQUIVO_PADRAO = "WIN"

CONFIG_DIR_PADRAO = "00_CONFIG"
CONFIG_ARQUIVO_PADRAO = "ze_config.json"

REGISTRO_OFICIAL_FRACTAIS_PADRAO: Dict[str, Any] = {
    "001_1_MIN": 1,
    "002_2_MIN": 2,
    "003_3_MIN": 3,
    "004_4_MIN": 4,
    "005_5_MIN": 5,
    "006_6_MIN": 6,
    "007_7_MIN": 7,
    "008_8_MIN": 8,
    "009_9_MIN": 9,
    "010_10_MIN": 10,
    "012_12_MIN": 12,
    "015_15_MIN": 15,
    "020_20_MIN": 20,
    "030_30_MIN": 30,
    "045_45_MIN": 45,
    "060_60_MIN": 60,
    "090_90_MIN": 90,
    "120_120_MIN": 120,
    "180_180_MIN": 180,
    "240_240_MIN": 240,
    "D01_DIARIO": "DIARIO",
    "S01_SEMANAL": "SEMANAL",
    "M01_MENSAL": "MENSAL",
}

FRACTAIS_INTRADIARIOS_PADRAO = [
    2, 3, 4, 5, 6, 7, 8, 9, 10, 12,
    15, 20, 30, 45, 60, 90, 120, 180, 240,
]

CONFIG_PADRAO: Dict[str, Any] = {
    "versao_configuracao": VERSAO_CONFIGURACAO_ESPERADA,
    "base_path": BASE_PATH_PADRAO,
    "ativo_pasta": ATIVO_PASTA_PADRAO,
    "ativo_prefixo_arquivo": ATIVO_PREFIXO_ARQUIVO_PADRAO,
    "pasta_origem_relativa": "001_1_MIN/win",
    "timezone_oficial": "America/Sao_Paulo",

    "modo_teste_controlado": True,
    "max_arquivos_teste": 1,
    "sobrescrever_saida": False,

    "manter_candles_parciais_na_saida": True,
    "modo_auditor": True,

    # Auditoria estrutural da Biblioteca Histórica.
    # MODO SEGURO: move pastas irregulares/duplicadas para quarentena,
    # nunca apaga dados.
    "organizar_duplicidades_fractais": True,
    "mover_irregulares_para_quarentena": True,

    "encoding_saida": "utf-8-sig",
    "separador_saida": ";",
    "header_saida": True,

    "status_certificacao": STATUS_CERTIFICACAO_PADRAO,
    "registro_oficial_fractais": REGISTRO_OFICIAL_FRACTAIS_PADRAO,
    "fractais_minutos": FRACTAIS_INTRADIARIOS_PADRAO,
    "alinhamento_sessao": "POR_SESSAO_CONTADOR_SEQUENCIAL",
}


# ============================================================
# CONTRATO OFICIAL DE SAÍDA
# ============================================================

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
# MODELOS
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
    relatorio_auditor: Optional[str]
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

def agora_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def hash_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def normalizar_caminho_relativo(valor: str) -> Path:
    partes = [p for p in str(valor).replace("\\", "/").split("/") if p]
    return Path(*partes)


def limpar_numero(valor) -> float:
    if pd.isna(valor):
        return 0.0

    texto = str(valor).strip().replace(" ", "").replace("\ufeff", "")
    if texto == "":
        return 0.0

    try:
        if "," in texto and "." in texto:
            texto = texto.replace(".", "").replace(",", ".")
        elif "," in texto:
            texto = texto.replace(",", ".")
        elif "." in texto:
            partes = texto.split(".")
            if len(partes) > 1 and all(len(p) == 3 for p in partes[1:]) and len(partes[-1]) == 3:
                texto = texto.replace(".", "")
        return float(texto)
    except Exception:
        return 0.0


def caminho_config_padrao() -> Path:
    return Path(BASE_PATH_PADRAO) / CONFIG_DIR_PADRAO / CONFIG_ARQUIVO_PADRAO


def corrigir_caminhos_antigos_config(config: Dict[str, Any]) -> bool:
    """
    Corrige automaticamente versões antigas do config, sem depender de edição manual.
    """
    alterou = False
    origem = str(config.get("pasta_origem_relativa", "")).replace("\\", "/")

    if origem in {"01_1_MIN/win", "0001_1_MIN/win", "1_1_MIN/win"}:
        config["pasta_origem_relativa"] = "001_1_MIN/win"
        alterou = True

    if config.get("versao_configuracao") != VERSAO_CONFIGURACAO_ESPERADA:
        config["versao_configuracao"] = VERSAO_CONFIGURACAO_ESPERADA
        alterou = True

    return alterou


def garantir_config_padrao() -> Path:
    caminho = caminho_config_padrao()
    caminho.parent.mkdir(parents=True, exist_ok=True)

    if not caminho.exists():
        with caminho.open("w", encoding="utf-8") as f:
            json.dump(CONFIG_PADRAO, f, ensure_ascii=False, indent=2)

    return caminho


def carregar_config() -> Tuple[Dict[str, Any], Path, str]:
    caminho = garantir_config_padrao()

    with caminho.open("r", encoding="utf-8-sig") as f:
        config = json.load(f)

    alterou = False
    for chave, valor in CONFIG_PADRAO.items():
        if chave not in config:
            config[chave] = valor
            alterou = True

    # Garante que o registro oficial tenha todas as chaves novas.
    registro = config.get("registro_oficial_fractais", {})
    for pasta, valor in REGISTRO_OFICIAL_FRACTAIS_PADRAO.items():
        if pasta not in registro:
            registro[pasta] = valor
            alterou = True
    config["registro_oficial_fractais"] = registro

    if corrigir_caminhos_antigos_config(config):
        alterou = True

    if alterou:
        with caminho.open("w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    return config, caminho, hash_arquivo(caminho)


# ============================================================
# REGISTRO OFICIAL DE FRACTAIS
# ============================================================

def registro_fractais_intradiarios(config: Dict[str, Any]) -> Dict[int, str]:
    registro = config.get("registro_oficial_fractais", {})
    mapa: Dict[int, str] = {}

    for pasta, valor in registro.items():
        if isinstance(valor, int):
            mapa[int(valor)] = str(pasta)

    return mapa


def registro_fractais_calendario(config: Dict[str, Any]) -> Dict[str, str]:
    registro = config.get("registro_oficial_fractais", {})
    mapa: Dict[str, str] = {}

    for pasta, valor in registro.items():
        if isinstance(valor, str):
            mapa[str(valor).upper()] = str(pasta)

    return mapa


def fractais_habilitados(config: Dict[str, Any]) -> List[int]:
    mapa = registro_fractais_intradiarios(config)
    lista = config.get("fractais_minutos", sorted(mapa.keys()))

    resultado = []
    for item in lista:
        item_int = int(item)
        if item_int in mapa:
            resultado.append(item_int)

    return resultado


def pasta_fractal(config: Dict[str, Any], minutos: int) -> str:
    mapa = registro_fractais_intradiarios(config)
    if int(minutos) not in mapa:
        raise ValueError(f"Fractal {minutos} sem pasta oficial no registro_oficial_fractais.")
    return mapa[int(minutos)]


def validar_config(config: Dict[str, Any]) -> None:
    fractais = fractais_habilitados(config)
    mapa = registro_fractais_intradiarios(config)

    if not fractais:
        raise ValueError("Configuração inválida: nenhum fractal intradiário habilitado.")

    for item in fractais:
        if item not in mapa:
            raise ValueError(f"Fractal sem pasta oficial: {item}")

    origem = str(config.get("pasta_origem_relativa", ""))
    if not origem:
        raise ValueError("Configuração inválida: pasta_origem_relativa ausente.")

    if bool(config.get("sobrescrever_saida", False)):
        print("ATENÇÃO: sobrescrever_saida=True. Arquivos existentes poderão ser substituídos.")


# ============================================================
# CAMINHOS E PASTAS
# ============================================================

def obter_caminhos(config: Dict[str, Any]) -> Dict[str, Path]:
    base_path = Path(config["base_path"])
    pasta_origem_relativa = normalizar_caminho_relativo(
        config.get("pasta_origem_relativa", "001_1_MIN/win")
    )

    return {
        "base_path": base_path,
        "pasta_origem": base_path / pasta_origem_relativa,
        "pasta_logs": base_path / "00_LOGS" / "ze_do_eucrazio",
        "pasta_relatorios": base_path / "00_RELATORIOS" / "ze_do_eucrazio",
        "pasta_manifestos": base_path / "00_MANIFESTOS" / "ze_do_eucrazio",
        "pasta_auditor": base_path / "00_AUDITORIA" / "ze_do_eucrazio",
        "pasta_quarentena": base_path / "00_DUPLICIDADES_FRACTAIS",
    }


def garantir_pastas(config: Dict[str, Any], caminhos: Dict[str, Path]) -> None:
    for chave in [
        "pasta_logs",
        "pasta_relatorios",
        "pasta_manifestos",
        "pasta_auditor",
        "pasta_quarentena",
    ]:
        caminhos[chave].mkdir(parents=True, exist_ok=True)

    ativo_pasta = config.get("ativo_pasta", ATIVO_PASTA_PADRAO)

    for minutos in fractais_habilitados(config):
        (caminhos["base_path"] / pasta_fractal(config, minutos) / ativo_pasta).mkdir(
            parents=True,
            exist_ok=True,
        )

    for pasta_cal in registro_fractais_calendario(config).values():
        (caminhos["base_path"] / pasta_cal).mkdir(parents=True, exist_ok=True)


# ============================================================
# AUDITORIA E ORGANIZAÇÃO DE PASTAS TEMPORAIS
# ============================================================

def detectar_fractal_por_nome(nome: str) -> Optional[int]:
    """
    Detecta fractais intradiários em nomes como:
    - 008_8_MIN  -> 8
    - 08_8_MIN   -> 8
    - 008_15_MIN -> 15  (caso histórico irregular)
    - 15_15_MIN  -> 15
    """
    m = re.match(r"^0*(\d+)_0*(\d+)_MIN$", nome, re.IGNORECASE)
    if not m:
        return None
    return int(m.group(2))


def mover_com_seguranca(origem: Path, destino_base: Path) -> Path:
    destino = destino_base
    if destino.exists():
        destino = destino_base.with_name(f"{destino_base.name}__{agora_tag()}")
    shutil.move(str(origem), str(destino))
    return destino


def auditar_e_organizar_pastas(config: Dict[str, Any], caminhos: Dict[str, Path]) -> Path:
    """
    Detecta:
    - pastas oficiais;
    - pastas antigas;
    - pastas com nomenclatura histórica incorreta;
    - duplicidades.

    Nunca apaga dados.
    Em modo seguro, move irregularidades para quarentena.
    """
    base = caminhos["base_path"]
    quarentena = caminhos["pasta_quarentena"]
    mapa_oficial = registro_fractais_intradiarios(config)
    pasta_por_fractal = mapa_oficial
    oficiais = set(pasta_por_fractal.values())

    mover = bool(config.get("mover_irregulares_para_quarentena", True))
    organizar = bool(config.get("organizar_duplicidades_fractais", True))

    registros = []
    tag = agora_tag()

    for item in sorted(base.iterdir()):
        if not item.is_dir():
            continue

        nome = item.name

        # ignora pastas institucionais
        if nome.startswith("00_"):
            continue

        # ignora calendário oficial
        if nome in registro_fractais_calendario(config).values():
            registros.append({
                "tipo": "CALENDARIO",
                "fractal_detectado": "",
                "pasta_encontrada": nome,
                "pasta_oficial": nome,
                "acao": "OFICIAL_MANTIDA",
                "destino": "",
                "observacao": "Pasta de calendário oficial.",
            })
            continue

        fractal = detectar_fractal_por_nome(nome)
        if fractal is None:
            registros.append({
                "tipo": "DESCONHECIDA",
                "fractal_detectado": "",
                "pasta_encontrada": nome,
                "pasta_oficial": "",
                "acao": "IGNORADA",
                "destino": "",
                "observacao": "Nome não reconhecido como fractal intradiário.",
            })
            continue

        pasta_oficial = pasta_por_fractal.get(fractal)
        if not pasta_oficial:
            registros.append({
                "tipo": "FRACTAL_NAO_REGISTRADO",
                "fractal_detectado": fractal,
                "pasta_encontrada": nome,
                "pasta_oficial": "",
                "acao": "IGNORADA",
                "destino": "",
                "observacao": "Fractal não consta no registro oficial.",
            })
            continue

        if nome == pasta_oficial:
            registros.append({
                "tipo": "INTRADIARIO",
                "fractal_detectado": fractal,
                "pasta_encontrada": nome,
                "pasta_oficial": pasta_oficial,
                "acao": "OFICIAL_MANTIDA",
                "destino": "",
                "observacao": "Pasta oficial.",
            })
            continue

        acao = "IRREGULAR_DETECTADA"
        destino_txt = ""
        observacao = "Nome de pasta não corresponde ao padrão oficial."

        if organizar and mover:
            destino = mover_com_seguranca(item, quarentena / nome)
            acao = "MOVIDA_PARA_QUARENTENA"
            destino_txt = str(destino)

        registros.append({
            "tipo": "INTRADIARIO_IRREGULAR",
            "fractal_detectado": fractal,
            "pasta_encontrada": nome,
            "pasta_oficial": pasta_oficial,
            "acao": acao,
            "destino": destino_txt,
            "observacao": observacao,
        })

    relatorio = caminhos["pasta_auditor"] / f"auditoria_pastas_temporais_{tag}.csv"
    pd.DataFrame(registros).to_csv(
        relatorio,
        sep=";",
        index=False,
        header=True,
        encoding="utf-8-sig",
        lineterminator="\n",
    )

    return relatorio


# ============================================================
# LEITURA DE ORIGEM
# ============================================================

def listar_csvs_origem(config: Dict[str, Any], pasta_origem: Path) -> List[Path]:
    if not pasta_origem.exists():
        raise FileNotFoundError(f"Pasta de origem não encontrada: {pasta_origem}")

    arquivos = sorted([
        p for p in pasta_origem.iterdir()
        if p.is_file() and p.suffix.lower() == ".csv"
    ])

    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV encontrado em: {pasta_origem}")

    if bool(config.get("modo_teste_controlado", True)):
        return arquivos[:int(config.get("max_arquivos_teste", 1))]

    return arquivos


def detectar_header(df_raw: pd.DataFrame) -> bool:
    if df_raw.empty:
        return False

    primeira_linha = [str(x).strip().lower() for x in df_raw.iloc[0].tolist()]
    marcadores = {"ativo", "timestamp_pc", "data", "hora", "abertura", "ultimo"}
    return any(x in marcadores for x in primeira_linha)


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
    df["sessao"] = df["datetime"].dt.strftime("%Y-%m-%d")

    return df, tipo, alertas


# ============================================================
# VALIDAÇÃO BÁSICA
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

    if df["sessao"].nunique() <= 0:
        alertas.append("Nenhuma sessão identificada.")

    return alertas


# ============================================================
# AGREGAÇÃO DETERMINÍSTICA
# ============================================================

def calcular_vwap_agregado(bloco: pd.DataFrame) -> float:
    volume_total = float(bloco["volume"].sum())

    if volume_total > 0:
        return float((bloco["vwap"] * bloco["volume"]).sum() / volume_total)

    return float(bloco.iloc[-1]["vwap"])


def agregar_fractal(config: Dict[str, Any], df: pd.DataFrame, minutos: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    linhas = []
    linhas_parciais = []
    auditoria_sessoes = []

    manter_parciais = bool(config.get("manter_candles_parciais_na_saida", True))
    timezone = str(config.get("timezone_oficial", "America/Sao_Paulo"))

    for sessao, grupo_sessao in df.groupby("sessao", sort=True):
        grupo_sessao = grupo_sessao.sort_values(["datetime", "ordem_original"]).reset_index(drop=True)
        grupo_sessao["grupo_fractal"] = grupo_sessao.index // minutos

        total_blocos = 0
        completos = 0
        parciais = 0
        qtd_sobra = 0

        for _, bloco in grupo_sessao.groupby("grupo_fractal", sort=True):
            total_blocos += 1
            qtd = int(len(bloco))
            status_candle = "COMPLETO" if qtd == minutos else "PARCIAL"

            if status_candle == "COMPLETO":
                completos += 1
            else:
                parciais += 1
                qtd_sobra = qtd

            if status_candle == "PARCIAL" and not manter_parciais:
                continue

            primeiro = bloco.iloc[0]
            ultimo = bloco.iloc[-1]
            dt = primeiro["datetime"]

            linha = {
                "ativo": primeiro["ativo"],
                "data": dt.strftime("%d/%m/%Y"),
                "hora": dt.strftime("%H:%M:%S"),
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": timezone,
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

        motivo = "SEM_SOBRA" if parciais == 0 else f"SOBRARAM_{qtd_sobra}_CANDLES"

        auditoria_sessoes.append({
            "sessao": sessao,
            "fractal_minutos": minutos,
            "total_candles_origem": int(len(grupo_sessao)),
            "blocos_gerados": int(total_blocos),
            "candles_completos": int(completos),
            "candles_parciais": int(parciais),
            "motivo_parcial": motivo,
        })

    saida = pd.DataFrame(linhas, columns=COLUNAS_SAIDA)
    parciais = pd.DataFrame(linhas_parciais, columns=COLUNAS_SAIDA)
    auditoria = pd.DataFrame(auditoria_sessoes)

    return saida, parciais, auditoria


# ============================================================
# PROCESSAMENTO
# ============================================================

def caminho_saida_para(config: Dict[str, Any], caminhos: Dict[str, Path], caminho_origem: Path, minutos: int) -> Path:
    nome = caminho_origem.name
    nome_novo = nome

    substituicoes = [
        ("1min", f"{minutos}min"),
        ("1MIN", f"{minutos}MIN"),
        ("1_Min", f"{minutos}_Min"),
        ("1_MIN", f"{minutos}_MIN"),
        ("1_min", f"{minutos}_min"),
    ]

    for antigo, novo in substituicoes:
        nome_novo = nome_novo.replace(antigo, novo)

    if nome_novo == nome:
        nome_novo = f"{config.get('ativo_prefixo_arquivo', 'WIN')}_{minutos}min_{nome}"

    return caminhos["base_path"] / pasta_fractal(config, minutos) / config.get("ativo_pasta", "win") / nome_novo


def salvar_csv_padrao(config: Dict[str, Any], df: pd.DataFrame, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        caminho,
        sep=str(config.get("separador_saida", ";")),
        index=False,
        header=bool(config.get("header_saida", True)),
        encoding=str(config.get("encoding_saida", "utf-8-sig")),
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\n",
    )


def processar_fractal(config: Dict[str, Any], caminhos: Dict[str, Path], caminho_origem: Path, df: pd.DataFrame, minutos: int) -> ResultadoFractal:
    caminho_saida = caminho_saida_para(config, caminhos, caminho_origem, minutos)

    if caminho_saida.exists() and not bool(config.get("sobrescrever_saida", False)):
        return ResultadoFractal(
            fractal_minutos=minutos,
            status="PULADO_ARQUIVO_EXISTENTE",
            arquivo_saida=str(caminho_saida),
            hash_saida=hash_arquivo(caminho_saida),
            linhas_saida=0,
            candles_completos=0,
            candles_parciais=0,
            relatorio_parciais=None,
            relatorio_auditor=None,
            motivo="Arquivo já existe e sobrescrever_saida=False.",
        )

    saida, parciais, auditoria_df = agregar_fractal(config, df, minutos)

    salvar_csv_padrao(config, saida, caminho_saida)

    relatorio_parciais = None
    if len(parciais) > 0:
        caminho_parciais = caminhos["pasta_relatorios"] / (caminho_saida.stem + "_CANDLES_PARCIAIS.csv")
        salvar_csv_padrao(config, parciais, caminho_parciais)
        relatorio_parciais = str(caminho_parciais)

    relatorio_auditor = None
    if bool(config.get("modo_auditor", True)):
        caminho_auditor = caminhos["pasta_auditor"] / (caminho_saida.stem + "_AUDITOR_SESSOES.csv")
        salvar_csv_padrao(config, auditoria_df, caminho_auditor)
        relatorio_auditor = str(caminho_auditor)

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
        relatorio_auditor=relatorio_auditor,
        motivo="Gerado pelo Zé. Certificação final pertence ao Fiscal Temporal.",
    )


def processar_arquivo(config: Dict[str, Any], caminhos: Dict[str, Path], caminho_origem: Path) -> ResultadoArquivo:
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

        for minutos in fractais_habilitados(config):
            try:
                fractais.append(processar_fractal(config, caminhos, caminho_origem, df, int(minutos)))
            except Exception as erro_fractal:
                erros.append(f"Fractal {minutos} min: {erro_fractal}")

        if erros:
            status = "CONCLUIDO_COM_ERROS"
        elif alertas:
            status = "CONCLUIDO_COM_ALERTAS"
        else:
            status = "CONCLUIDO"

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


# ============================================================
# MANIFESTO E LOG
# ============================================================

def salvar_manifesto(
    config: Dict[str, Any],
    caminhos: Dict[str, Path],
    resultados: List[ResultadoArquivo],
    inicio: datetime,
    fim: datetime,
    caminho_config: Path,
    hash_config: str,
    id_execucao: str,
    relatorio_auditoria_pastas: Optional[Path],
) -> Path:
    manifesto = {
        "modulo": NOME_MODULO,
        "versao_motor": VERSAO_MOTOR,
        "versao_contrato_saida": VERSAO_CONTRATO_SAIDA,
        "versao_configuracao": str(config.get("versao_configuracao", VERSAO_CONFIGURACAO_ESPERADA)),
        "hash_configuracao": hash_config,
        "arquivo_configuracao": str(caminho_config),
        "id_execucao": id_execucao,
        "status_arquitetural": "TESTE_CONTROLADO" if config.get("modo_teste_controlado", True) else "PROCESSAMENTO_COMPLETO",
        "status_certificacao": str(config.get("status_certificacao", STATUS_CERTIFICACAO_PADRAO)),
        "regra_oficial": REGRA_OFICIAL,
        "base_path": str(caminhos["base_path"]),
        "pasta_origem": str(caminhos["pasta_origem"]),
        "relatorio_auditoria_pastas": str(relatorio_auditoria_pastas) if relatorio_auditoria_pastas else None,
        "timezone_oficial": str(config.get("timezone_oficial", "America/Sao_Paulo")),
        "modo_teste_controlado": bool(config.get("modo_teste_controlado", True)),
        "max_arquivos_teste": int(config.get("max_arquivos_teste", 1)),
        "sobrescrever_saida": bool(config.get("sobrescrever_saida", False)),
        "manter_candles_parciais_na_saida": bool(config.get("manter_candles_parciais_na_saida", True)),
        "modo_auditor": bool(config.get("modo_auditor", True)),
        "organizar_duplicidades_fractais": bool(config.get("organizar_duplicidades_fractais", True)),
        "mover_irregulares_para_quarentena": bool(config.get("mover_irregulares_para_quarentena", True)),
        "fractais_minutos": fractais_habilitados(config),
        "registro_oficial_fractais": config.get("registro_oficial_fractais", {}),
        "alinhamento_sessao": str(config.get("alinhamento_sessao", "POR_SESSAO_CONTADOR_SEQUENCIAL")),
        "inicio": inicio.isoformat(),
        "fim": fim.isoformat(),
        "data_execucao": fim.strftime("%Y-%m-%d %H:%M:%S"),
        "duracao_segundos": round((fim - inicio).total_seconds(), 2),
        "resultados": [
            {
                **asdict(r),
                "fractais": [asdict(f) for f in r.fractais],
            }
            for r in resultados
        ],
    }

    caminho = caminhos["pasta_manifestos"] / f"manifesto_ze_do_eucrazio_v{VERSAO_MOTOR.replace('.', '_')}_{id_execucao}.json"

    with caminho.open("w", encoding="utf-8") as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=2)

    return caminho


def salvar_log_texto(
    config: Dict[str, Any],
    caminhos: Dict[str, Path],
    resultados: List[ResultadoArquivo],
    manifesto: Path,
    id_execucao: str,
    relatorio_auditoria_pastas: Optional[Path],
) -> Path:
    caminho = caminhos["pasta_logs"] / f"log_ze_do_eucrazio_v{VERSAO_MOTOR.replace('.', '_')}_{id_execucao}.txt"

    linhas = [
        "=" * 80,
        f"ZÉ DO EUCRÁZIO {VERSAO_MOTOR} — LOG OPERACIONAL",
        "=" * 80,
        f"Regra oficial: {REGRA_OFICIAL}",
        f"Status certificação: {config.get('status_certificacao', STATUS_CERTIFICACAO_PADRAO)}",
        f"Base: {caminhos['base_path']}",
        f"Origem: {caminhos['pasta_origem']}",
        f"Manifesto: {manifesto}",
        f"Auditoria de pastas: {relatorio_auditoria_pastas}",
        "",
    ]

    for r in resultados:
        linhas.extend([
            "-" * 80,
            f"Origem: {r.arquivo_origem}",
            f"Hash origem: {r.hash_origem}",
            f"Tipo: {r.tipo_detectado}",
            f"Linhas origem: {r.linhas_origem}",
            f"Status: {r.status}",
        ])

        if r.alertas:
            linhas.append("Alertas:")
            linhas.extend([f"  - {a}" for a in r.alertas])

        if r.erros:
            linhas.append("Erros:")
            linhas.extend([f"  - {e}" for e in r.erros])

        linhas.append("Fractais:")
        for f in r.fractais:
            linhas.append(
                f"  {f.fractal_minutos:>3} min | {f.status:<24} | "
                f"linhas={f.linhas_saida:<8} completos={f.candles_completos:<8} "
                f"parciais={f.candles_parciais:<8}"
            )

    caminho.write_text("\n".join(linhas), encoding="utf-8")
    return caminho


# ============================================================
# EXECUÇÃO
# ============================================================

def processar() -> None:
    id_execucao = agora_tag()

    config, caminho_config, hash_config = carregar_config()
    validar_config(config)

    caminhos = obter_caminhos(config)
    garantir_pastas(config, caminhos)

    relatorio_auditoria_pastas = auditar_e_organizar_pastas(config, caminhos)

    print("\n" + "=" * 80)
    print(f"🌽 ZÉ DO EUCRÁZIO {VERSAO_MOTOR} — TESTE CONTROLADO")
    print("=" * 80)
    print(f"Regra oficial: {REGRA_OFICIAL}")
    print(f"Base: {caminhos['base_path']}")
    print(f"Origem: {caminhos['pasta_origem']}")
    print(f"Timezone oficial: {config.get('timezone_oficial')}")
    print(f"Modo teste controlado: {config.get('modo_teste_controlado')}")
    print(f"Sobrescrever saída: {config.get('sobrescrever_saida')}")
    print(f"Modo auditor: {config.get('modo_auditor')}")
    print(f"Config: {caminho_config}")
    print(f"Auditoria de pastas: {relatorio_auditoria_pastas}")
    print("=" * 80)

    inicio = datetime.now()

    try:
        arquivos = listar_csvs_origem(config, caminhos["pasta_origem"])
    except Exception as erro:
        print(f"ERRO AO LISTAR ORIGEM: {erro}")
        sys.exit(1)

    print(f"\nArquivos selecionados: {len(arquivos)}")

    resultados: List[ResultadoArquivo] = []

    for caminho in arquivos:
        print("\nProcessando origem:")
        print(caminho)

        resultado = processar_arquivo(config, caminhos, caminho)
        resultados.append(resultado)

        print(f"Status: {resultado.status}")
        print(f"Tipo detectado: {resultado.tipo_detectado}")
        print(f"Linhas origem: {resultado.linhas_origem}")

        for alerta in resultado.alertas:
            print(f"  ALERTA: {alerta}")

        for erro in resultado.erros:
            print(f"  ERRO: {erro}")

        for fractal in resultado.fractais:
            print(
                f"  {fractal.fractal_minutos:>3} min | "
                f"{fractal.status:<24} | "
                f"linhas={fractal.linhas_saida:<7} "
                f"completos={fractal.candles_completos:<7} "
                f"parciais={fractal.candles_parciais:<7}"
            )

    fim = datetime.now()

    manifesto = salvar_manifesto(
        config=config,
        caminhos=caminhos,
        resultados=resultados,
        inicio=inicio,
        fim=fim,
        caminho_config=caminho_config,
        hash_config=hash_config,
        id_execucao=id_execucao,
        relatorio_auditoria_pastas=relatorio_auditoria_pastas,
    )

    log_txt = salvar_log_texto(
        config=config,
        caminhos=caminhos,
        resultados=resultados,
        manifesto=manifesto,
        id_execucao=id_execucao,
        relatorio_auditoria_pastas=relatorio_auditoria_pastas,
    )

    print("\n" + "=" * 80)
    print("PROCESSAMENTO FINALIZADO")
    print(f"Manifesto: {manifesto}")
    print(f"Log texto: {log_txt}")
    print(f"Auditoria de pastas: {relatorio_auditoria_pastas}")
    print(f"Status certificação: {config.get('status_certificacao', STATUS_CERTIFICACAO_PADRAO)}")
    print("Observação: a certificação final pertence ao Fiscal Temporal.")
    print("=" * 80)


if __name__ == "__main__":
    processar()
