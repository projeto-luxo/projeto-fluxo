import os
import csv
import hashlib
from pathlib import Path
from datetime import datetime, timedelta, time

import pandas as pd


# ============================================================
# FISCAL TEMPORAL v5.0 — CARTÓRIO OFICIAL DO TEMPO DO TRIN
#
# MISSÃO:
# - Certificar integridade temporal.
# - Classificar lacunas com calendário B3.
# - Gerar ordens oficiais para Bernardo, Zé e Operador.
# - Assinar SHA256.
# - Manter protocolo estável.
#
# NÃO FAZ:
# - Não corrige dados.
# - Não gera fractais.
# - Não move arquivos.
# - Não interpreta mercado.
# - Não chama Bernardo/Zé diretamente.
# ============================================================


TRIN_ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = TRIN_ROOT / "TRIN_HISTORICO"

PASTA_CERTIFICACOES = BASE_PATH / "00_CERTIFICACOES"
PASTA_CERTIFICACOES.mkdir(parents=True, exist_ok=True)

ARQUIVO_CERTIFICADO = PASTA_CERTIFICACOES / "certificado_temporal.csv"
ARQUIVO_ALERTAS = PASTA_CERTIFICACOES / "alertas_temporais.csv"
ARQUIVO_BERNARDO = PASTA_CERTIFICACOES / "ordens_para_bernardo.csv"
ARQUIVO_ZE = PASTA_CERTIFICACOES / "ordens_para_ze.csv"
ARQUIVO_OPERADOR = PASTA_CERTIFICACOES / "ordens_operador.csv"
ARQUIVO_HASH = PASTA_CERTIFICACOES / "certificado_sha256.csv"
ARQUIVO_LAUDO = PASTA_CERTIFICACOES / "laudo_temporal.txt"
ARQUIVO_RESUMO_MOTIVOS = PASTA_CERTIFICACOES / "resumo_por_motivo.csv"
ARQUIVO_RESUMO_ARQUIVOS = PASTA_CERTIFICACOES / "resumo_por_arquivo.csv"
ARQUIVO_PROTOCOLOS = PASTA_CERTIFICACOES / "registro_protocolos_fiscal.csv"

RESPOSTA_BERNARDO = PASTA_CERTIFICACOES / "respostas_bernardo.csv"
RESPOSTA_ZE = PASTA_CERTIFICACOES / "respostas_ze.csv"
RESPOSTA_OPERADOR = PASTA_CERTIFICACOES / "respostas_operador.csv"


IGNORAR = {
    "00_INDICES",
    "00_LOGS",
    "00_MANIFESTOS",
    "00_RELATORIOS",
    "00_AUDITORIA",
    "00_CONFIG",
    "00_CONHECIMENTO",
    "00_CERTIFICACOES",
    "00_DUPLICIDADES_FRACTAIS",
    "00_MEMORIA_PROCESSADA",
}


# ============================================================
# CONFIGURAÇÃO B3 / TRIN
# ============================================================

# Ajustável. Se a B3 mudar o horário, altere aqui.
SESSOES_PADRAO = {
    "WIN": ("09:00", "18:30"),
    "WDO": ("09:00", "18:30"),
    "IND": ("09:00", "18:30"),
    "DOL": ("09:00", "18:30"),
}

FERIADOS_B3_2026 = {
    "2026-01-01": "Confraternizacao Universal",
    "2026-02-16": "Carnaval",
    "2026-02-17": "Carnaval",
    "2026-04-03": "Sexta-feira Santa",
    "2026-04-21": "Tiradentes",
    "2026-05-01": "Dia do Trabalho",
    "2026-06-04": "Corpus Christi",
    "2026-09-07": "Independencia do Brasil",
    "2026-10-12": "Nossa Senhora Aparecida",
    "2026-11-02": "Finados",
    "2026-11-20": "Consciencia Negra",
    "2026-12-24": "Vespera de Natal",
    "2026-12-25": "Natal",
    "2026-12-31": "Vespera de Ano Novo",
}

HORARIOS_ESPECIAIS_2026 = {
    "2026-02-18": {
        "inicio": "13:00",
        "fim": "18:30",
        "motivo": "Quarta-feira de Cinzas",
    }
}

FRACTAIS_GERADOS_PELO_ZE = {
    2, 3, 4, 6, 7, 8, 9, 12, 20, 45, 90, 120, 180, 240
}


# ============================================================
# UTILITÁRIOS
# ============================================================

def hora(hhmm):
    h, m = hhmm.split(":")
    return time(int(h), int(m))


def data_iso(dt):
    return dt.strftime("%Y-%m-%d")


def sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def normalizar_nome_coluna(nome):
    texto = str(nome).strip().lower()
    troca = {
        "á": "a", "à": "a", "ã": "a", "â": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    for a, b in troca.items():
        texto = texto.replace(a, b)
    texto = texto.replace(" ", "_")
    texto = texto.replace("-", "_")
    return texto


def normalizar_colunas(df):
    return [normalizar_nome_coluna(c) for c in df.columns]


def numero(valor):
    if valor is None:
        return None

    texto = str(valor).strip()

    if texto == "" or texto.lower() in {"nan", "none", "#n/d", "#valor!"}:
        return None

    try:
        return float(texto)
    except Exception:
        pass

    try:
        texto = texto.replace(".", "")
        texto = texto.replace(",", ".")
        return float(texto)
    except Exception:
        return None


def serie_numerica(s):
    return s.apply(numero)


def detectar_ativo(nome_arquivo, df=None):
    nome = str(nome_arquivo).upper()

    if nome.startswith("WIN"):
        return "WIN"
    if nome.startswith("WDO"):
        return "WDO"
    if nome.startswith("IND"):
        return "IND"
    if nome.startswith("DOL"):
        return "DOL"

    if df is not None and len(df) > 0:
        colunas = normalizar_colunas(df)
        if "ativo" in colunas:
            col = df.columns[colunas.index("ativo")]
            valor = str(df[col].dropna().iloc[0]).upper()
            if valor.startswith("WIN"):
                return "WIN"
            if valor.startswith("WDO"):
                return "WDO"
            if valor.startswith("IND"):
                return "IND"
            if valor.startswith("DOL"):
                return "DOL"

    return "DESCONHECIDO"


def detectar_tipo_fractal(pasta, arquivo):
    texto = f"{pasta} {arquivo}".upper()

    if "DIARIO" in texto or "DIÁRIO" in texto:
        return "DIARIO", None

    if "SEMANAL" in texto:
        return "SEMANAL", None

    if "MENSAL" in texto:
        return "MENSAL", None

    for pedaco in texto.replace("-", "_").split("_"):
        if pedaco.isdigit():
            valor = int(pedaco)
            if valor > 0:
                return "INTRADAY", valor

    return "DESCONHECIDO", None


def origem_fractal(minutos):
    if minutos in FRACTAIS_GERADOS_PELO_ZE:
        return "ZE_DO_EUCRAZIO"
    return "PROFIT_ORIGINAL"


# ============================================================
# CALENDÁRIO B3
# ============================================================

def eh_fim_de_semana(dt):
    return dt.weekday() >= 5


def eh_feriado_b3(dt):
    return data_iso(dt) in FERIADOS_B3_2026


def obter_sessao(ativo, dt):
    dia = data_iso(dt)

    if dia in HORARIOS_ESPECIAIS_2026:
        regra = HORARIOS_ESPECIAIS_2026[dia]
        return (
            hora(regra["inicio"]),
            hora(regra["fim"]),
            "HORARIO_ESPECIAL_B3",
            regra["motivo"],
        )

    ini, fim = SESSOES_PADRAO.get(ativo, SESSOES_PADRAO["WIN"])
    return hora(ini), hora(fim), "SESSAO_PADRAO_B3", "Sessao normal"


def classificar_instante_b3(ativo, dt):
    dia = data_iso(dt)

    if eh_fim_de_semana(dt):
        return {
            "dentro_sessao": False,
            "tipo": "FIM_DE_SEMANA",
            "motivo": "Fim de semana sem pregao",
        }

    if eh_feriado_b3(dt):
        return {
            "dentro_sessao": False,
            "tipo": "FERIADO_B3",
            "motivo": FERIADOS_B3_2026[dia],
        }

    inicio, fim, tipo, motivo = obter_sessao(ativo, dt)

    if inicio <= dt.time() <= fim:
        return {
            "dentro_sessao": True,
            "tipo": tipo,
            "motivo": motivo,
        }

    return {
        "dentro_sessao": False,
        "tipo": "FORA_DA_SESSAO",
        "motivo": "Horario fora da sessao oficial",
    }


def existem_candles_esperados_dentro_sessao(ativo, inicio, fim, minutos):
    """
    Verifica se, entre dois timestamps existentes, haveria candles esperados
    dentro da sessão oficial. Se sim, lacuna é problema real.
    """
    atual = inicio + timedelta(minutes=minutos)
    qtd = 0
    exemplos = []

    while atual < fim:
        regra = classificar_instante_b3(ativo, atual)
        if regra["dentro_sessao"]:
            qtd += 1
            if len(exemplos) < 3:
                exemplos.append(atual.strftime("%d/%m/%Y %H:%M:%S"))
        atual += timedelta(minutes=minutos)

    return qtd, exemplos


# ============================================================
# LEITURA CSV ROBUSTA
# ============================================================

def linha_parece_header(valores):
    texto = ";".join(str(v).lower() for v in valores)
    palavras = [
        "ativo", "data", "hora", "ultimo", "abertura",
        "maximo", "minimo", "volume", "delta", "saldo",
        "vwap", "timestamp",
    ]
    return sum(1 for p in palavras if p in texto) >= 2


def atribuir_colunas_sem_header(df):
    qtd = len(df.columns)

    # Memória Viva TRIN oficial
    if qtd >= 15:
        nomes = [
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
        extras = [f"extra_{i}" for i in range(qtd - len(nomes))]
        df.columns = nomes + extras
        return df

    # Exportação Profit histórica comum:
    # ativo;data;hora;abertura;maximo;minimo;ultimo;volume;...
    if qtd >= 9:
        nomes = [
            "ativo",
            "data",
            "hora",
            "abertura",
            "maximo",
            "minimo",
            "ultimo",
            "volume",
            "delta",
        ]
        extras = [f"extra_{i}" for i in range(qtd - len(nomes))]
        df.columns = nomes + extras
        return df

    if qtd >= 8:
        nomes = [
            "ativo",
            "data",
            "hora",
            "abertura",
            "maximo",
            "minimo",
            "ultimo",
            "volume",
        ]
        extras = [f"extra_{i}" for i in range(qtd - len(nomes))]
        df.columns = nomes + extras
        return df

    nomes = [f"col_{i}" for i in range(qtd)]
    df.columns = nomes
    return df


def ler_csv_trin(caminho):
    bruto = pd.read_csv(
        caminho,
        sep=";",
        engine="python",
        header=None,
        dtype=str,
        encoding="utf-8-sig",
        on_bad_lines="skip",
    )

    if len(bruto) == 0:
        return bruto

    primeira = list(bruto.iloc[0].values)

    if linha_parece_header(primeira):
        bruto.columns = [normalizar_nome_coluna(v) for v in primeira]
        bruto = bruto.iloc[1:].reset_index(drop=True)
    else:
        bruto = atribuir_colunas_sem_header(bruto)

    return bruto


# ============================================================
# TIMESTAMP
# ============================================================

def parse_datas(serie):
    serie = serie.astype(str).str.strip()

    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y",
    ]

    resultado = pd.Series(pd.NaT, index=serie.index, dtype="datetime64[ns]")

    for fmt in formatos:
        faltantes = resultado.isna()
        if not faltantes.any():
            break

        tentativa = pd.to_datetime(
            serie.loc[faltantes],
            format=fmt,
            errors="coerce",
        )

        resultado.loc[faltantes] = tentativa

    return resultado


def montar_timestamp(df, tipo_fractal):
    colunas = normalizar_colunas(df)

    if "timestamp" in colunas:
        col = df.columns[colunas.index("timestamp")]
        return parse_datas(df[col])

    if "timestamp_pc" in colunas:
        col = df.columns[colunas.index("timestamp_pc")]
        ts_pc = parse_datas(df[col])

        if ts_pc.notna().sum() > 0:
            return ts_pc

    if "data" in colunas:
        col_data = df.columns[colunas.index("data")]

        if tipo_fractal == "INTRADAY" and "hora" in colunas:
            col_hora = df.columns[colunas.index("hora")]
            return parse_datas(
                df[col_data].astype(str) + " " + df[col_hora].astype(str)
            )

        return parse_datas(df[col_data])

    return pd.Series(pd.NaT, index=df.index, dtype="datetime64[ns]")


# ============================================================
# PROTOCOLOS
# ============================================================

def carregar_protocolos():
    if not ARQUIVO_PROTOCOLOS.exists():
        return {}, 0

    mapa = {}
    maior = 0

    try:
        df = pd.read_csv(ARQUIVO_PROTOCOLOS, sep=";", engine="python", dtype=str)

        for _, row in df.iterrows():
            chave = str(row.get("chave_ocorrencia", ""))
            protocolo = str(row.get("id_ocorrencia", ""))

            if chave:
                mapa[chave] = protocolo

            try:
                seq = int(protocolo.split("-")[-1])
                maior = max(maior, seq)
            except Exception:
                pass

    except Exception:
        pass

    return mapa, maior


def salvar_protocolos(mapa):
    linhas = []

    for chave, protocolo in sorted(mapa.items(), key=lambda x: x[1]):
        linhas.append({
            "id_ocorrencia": protocolo,
            "chave_ocorrencia": chave,
            "data_registro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })

    pd.DataFrame(linhas).to_csv(
        ARQUIVO_PROTOCOLOS,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )


PROTOCOLOS, ULTIMO_PROTOCOLO = carregar_protocolos()


def obter_id_ocorrencia(chave):
    global ULTIMO_PROTOCOLO

    if chave in PROTOCOLOS:
        return PROTOCOLOS[chave]

    ULTIMO_PROTOCOLO += 1
    hoje = datetime.now().strftime("%Y%m%d")
    protocolo = f"FT-{hoje}-{ULTIMO_PROTOCOLO:06d}"
    PROTOCOLOS[chave] = protocolo
    return protocolo


def chave_ocorrencia(caminho, motivo, inicio=None, fim=None):
    base = f"{Path(caminho).as_posix()}|{motivo}|{inicio}|{fim}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def carregar_respostas():
    respostas = {}

    for arquivo in [RESPOSTA_BERNARDO, RESPOSTA_ZE, RESPOSTA_OPERADOR]:
        if not arquivo.exists():
            continue

        try:
            df = pd.read_csv(arquivo, sep=";", engine="python", dtype=str)

            if "id_ocorrencia" not in df.columns or "status_ordem" not in df.columns:
                continue

            for _, row in df.iterrows():
                respostas[str(row["id_ocorrencia"])] = str(row["status_ordem"]).upper()

        except Exception:
            pass

    return respostas


def status_ordem(id_ocorrencia, respostas):
    status = respostas.get(id_ocorrencia, "PENDENTE")

    permitidos = {
        "PENDENTE",
        "EM_ANALISE",
        "EM_CORRECAO",
        "CORRIGIDO",
        "RECERTIFICAR",
        "ENCERRADO",
    }

    if status not in permitidos:
        return "PENDENTE"

    return status


def criticidade(motivo):
    criticas = {
        "SEM_TIMESTAMP_VALIDO",
        "TIMESTAMP_DUPLICADO",
        "ORDEM_TEMPORAL_MISTA",
        "OHLC_INVALIDO",
        "ARQUIVO_VAZIO",
    }

    altas = {
        "TIMESTAMP_INVALIDO",
        "HEADER_SEM_DATA",
        "INTRADAY_SEM_HORA",
        "LACUNA_DENTRO_DA_SESSAO",
        "VOLUME_NEGATIVO",
        "ERRO_LEITURA",
    }

    medias = {
        "LACUNA_TRANSICAO_SESSAO",
        "LACUNA_ROLAGEM_OU_CORTE",
    }

    informativas = {
        "ORDEM_DECRESCENTE_ORIGEM_PROFIT",
        "LACUNA_FORA_DA_SESSAO",
        "LACUNA_FIM_SEMANA",
        "LACUNA_FERIADO_B3",
        "LACUNA_ENTRE_PREGOES",
    }

    if motivo in criticas:
        return "CRITICA"
    if motivo in altas:
        return "ALTA"
    if motivo in medias:
        return "MEDIA"
    if motivo in informativas:
        return "INFORMATIVA"

    return "BAIXA"


def dependencia(motivo, responsavel):
    if motivo == "LACUNA_DENTRO_DA_SESSAO":
        return "BERNARDO_VERIFICAR_ORIGEM -> ZE_REGENERAR_SE_DERIVADO -> FISCAL_RECERTIFICAR"

    if responsavel == "BERNARDO":
        return "BERNARDO_CORRIGIR_OU_REINDEXAR -> FISCAL_RECERTIFICAR"

    if responsavel == "ZE_DO_EUCRAZIO":
        return "ZE_REGERAR_OU_RECALCULAR -> FISCAL_RECERTIFICAR"

    if responsavel == "OPERADOR_CALENDARIO_B3":
        return "OPERADOR_VALIDAR_CONTEXTO -> FISCAL_RECERTIFICAR"

    return "NENHUMA"


def criar_ocorrencia(
    caminho,
    arquivo,
    status_certificacao,
    motivo,
    descricao,
    responsavel,
    acao,
    certificacao,
    respostas,
    inicio=None,
    fim=None,
):
    chave = chave_ocorrencia(caminho, motivo, inicio, fim)
    protocolo = obter_id_ocorrencia(chave)

    return {
        "id_ocorrencia": protocolo,
        "arquivo": arquivo,
        "caminho": str(caminho),
        "status_certificacao": status_certificacao,
        "status_ordem": status_ordem(protocolo, respostas),
        "criticidade": criticidade(motivo),
        "motivo": motivo,
        "descricao": descricao,
        "responsavel": responsavel,
        "acao_recomendada": acao,
        "dependencia": dependencia(motivo, responsavel),
        "certificacao": certificacao,
        "inicio_lacuna": inicio or "",
        "fim_lacuna": fim or "",
        "data_emissao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "fiscal_temporal": "v5.0",
    }


# ============================================================
# VALIDAÇÕES
# ============================================================

def verificar_ohlc(df):
    colunas = normalizar_colunas(df)

    mapa = {
        "abertura": ["abertura", "open"],
        "maximo": ["maximo", "maximo", "high"],
        "minimo": ["minimo", "minimo", "low"],
        "ultimo": ["ultimo", "close", "fechamento"],
    }

    achados = {}

    for chave, opcoes in mapa.items():
        achados[chave] = None
        for opcao in opcoes:
            if opcao in colunas:
                achados[chave] = df.columns[colunas.index(opcao)]
                break

    if not all(achados.values()):
        return "NAO_VERIFICADO", 0

    abertura = serie_numerica(df[achados["abertura"]])
    maximo = serie_numerica(df[achados["maximo"]])
    minimo = serie_numerica(df[achados["minimo"]])
    ultimo = serie_numerica(df[achados["ultimo"]])

    invalido = (
        (maximo < minimo) |
        (abertura > maximo) |
        (abertura < minimo) |
        (ultimo > maximo) |
        (ultimo < minimo)
    )

    qtd = int(invalido.fillna(False).sum())

    if qtd > 0:
        return "ERRO", qtd

    return "OK", 0


def verificar_nao_negativo(df, nome_coluna):
    colunas = normalizar_colunas(df)

    if nome_coluna not in colunas:
        return "NAO_VERIFICADO", 0

    col = df.columns[colunas.index(nome_coluna)]
    valores = serie_numerica(df[col])
    qtd = int((valores < 0).fillna(False).sum())

    if qtd > 0:
        return "ERRO", qtd

    return "OK", 0


def classificar_lacunas(timestamps, minutos, arquivo, caminho, ativo, respostas):
    ts = timestamps.dropna().sort_values()

    if len(ts) <= 1 or not minutos:
        return [], {
            "lacunas_total": 0,
            "lacunas_normais": 0,
            "lacunas_reais": 0,
            "lacunas_ressalva": 0,
        }

    esperado = minutos * 60
    ocorrencias = []

    contagem = {
        "lacunas_total": 0,
        "lacunas_normais": 0,
        "lacunas_reais": 0,
        "lacunas_ressalva": 0,
    }

    anterior = None

    for atual in ts:
        if anterior is None:
            anterior = atual
            continue

        segundos = (atual - anterior).total_seconds()

        if segundos <= esperado:
            anterior = atual
            continue

        contagem["lacunas_total"] += 1

        qtd_esperados, exemplos = existem_candles_esperados_dentro_sessao(
            ativo,
            anterior,
            atual,
            minutos,
        )

        inicio_txt = anterior.strftime("%d/%m/%Y %H:%M:%S")
        fim_txt = atual.strftime("%d/%m/%Y %H:%M:%S")
        horas = segundos / 3600

        regra_inicio = classificar_instante_b3(ativo, anterior)
        regra_fim = classificar_instante_b3(ativo, atual)

        if qtd_esperados == 0:
            contagem["lacunas_normais"] += 1
            anterior = atual
            continue

        origem = origem_fractal(minutos)

        if origem == "ZE_DO_EUCRAZIO":
            responsavel = "ZE_DO_EUCRAZIO"
            acao = "REGENERAR_FRACTAL_A_PARTIR_DA_BASE_1_MIN"
        else:
            responsavel = "BERNARDO"
            acao = "VERIFICAR_ORIGEM_PROFIT_EXPORTACAO_E_INDEXACAO"

        descricao = (
            f"Lacuna de {horas:.2f} horas entre {inicio_txt} e {fim_txt}. "
            f"Foram identificados {qtd_esperados} candles esperados dentro da sessão B3. "
            f"Exemplos esperados: {', '.join(exemplos)}. "
            f"Inicio: {regra_inicio['tipo']} / Fim: {regra_fim['tipo']}."
        )

        ocorrencias.append(criar_ocorrencia(
            caminho=caminho,
            arquivo=arquivo,
            status_certificacao="REPROVADO",
            motivo="LACUNA_DENTRO_DA_SESSAO",
            descricao=descricao,
            responsavel=responsavel,
            acao=acao,
            certificacao="NEGADA",
            respostas=respostas,
            inicio=inicio_txt,
            fim=fim_txt,
        ))

        contagem["lacunas_reais"] += 1
        anterior = atual

    return ocorrencias, contagem


# ============================================================
# ANÁLISE DE ARQUIVO
# ============================================================

def analisar_arquivo(caminho, pasta, respostas):
    tipo_fractal, minutos = detectar_tipo_fractal(pasta, caminho.name)

    registro = {
        "arquivo": caminho.name,
        "pasta": pasta,
        "caminho": str(caminho),
        "ativo": "N/D",
        "tipo_fractal": tipo_fractal,
        "fractal_minutos": minutos if minutos else "N/D",
        "origem_fractal": origem_fractal(minutos) if minutos else "N/D",
        "sha256": "N/D",
        "linhas": 0,
        "colunas": 0,
        "data_inicio": "N/D",
        "data_fim": "N/D",
        "ordem_temporal": "N/D",
        "timestamps_invalidos": 0,
        "duplicados": 0,
        "lacunas_total": 0,
        "lacunas_normais": 0,
        "lacunas_reais": 0,
        "lacunas_ressalva": 0,
        "ohlc_status": "N/D",
        "ohlc_problemas": 0,
        "volume_status": "N/D",
        "volume_negativo": 0,
        "status": "CERTIFICADO",
        "maior_criticidade": "NENHUMA",
        "motivos": "NENHUM",
        "responsavel": "NENHUM",
        "acao_recomendada": "NENHUMA",
        "certificacao": "CONCEDIDA",
    }

    ocorrencias = []

    try:
        registro["sha256"] = sha256_arquivo(caminho)

        df = ler_csv_trin(caminho)
        registro["linhas"] = len(df)
        registro["colunas"] = len(df.columns)

        ativo = detectar_ativo(caminho.name, df)
        registro["ativo"] = ativo

        colunas = normalizar_colunas(df)

        if len(df) == 0:
            ocorrencias.append(criar_ocorrencia(
                caminho, caminho.name, "REPROVADO",
                "ARQUIVO_VAZIO",
                "Arquivo CSV sem registros.",
                "BERNARDO",
                "VERIFICAR_ORIGEM_E_REINDEXAR_BIBLIOTECA",
                "NEGADA",
                respostas,
            ))

        if "data" not in colunas and "timestamp" not in colunas and "timestamp_pc" not in colunas:
            ocorrencias.append(criar_ocorrencia(
                caminho, caminho.name, "REPROVADO",
                "HEADER_SEM_DATA",
                "Arquivo não possui data ou timestamp identificável.",
                "BERNARDO",
                "CORRIGIR_ESTRUTURA_OU_LOCALIZAR_ORIGEM_CORRETA",
                "NEGADA",
                respostas,
            ))

        if tipo_fractal == "INTRADAY":
            if "hora" not in colunas and "timestamp" not in colunas and "timestamp_pc" not in colunas:
                ocorrencias.append(criar_ocorrencia(
                    caminho, caminho.name, "REPROVADO",
                    "INTRADAY_SEM_HORA",
                    "Arquivo intraday não possui hora ou timestamp identificável.",
                    "BERNARDO",
                    "CORRIGIR_HEADER_OU_REEXPORTAR_ARQUIVO",
                    "NEGADA",
                    respostas,
                ))

        timestamps = montar_timestamp(df, tipo_fractal)

        invalidos = int(timestamps.isna().sum())
        registro["timestamps_invalidos"] = invalidos

        if invalidos > 0:
            ocorrencias.append(criar_ocorrencia(
                caminho, caminho.name, "REPROVADO",
                "TIMESTAMP_INVALIDO",
                f"Foram encontrados {invalidos} timestamps inválidos.",
                "BERNARDO",
                "CORRIGIR_DATA_HORA_OU_REINDEXAR_ARQUIVO",
                "NEGADA",
                respostas,
            ))

        ts_validos = timestamps.dropna()

        if len(ts_validos) == 0:
            ocorrencias.append(criar_ocorrencia(
                caminho, caminho.name, "REPROVADO",
                "SEM_TIMESTAMP_VALIDO",
                "Nenhum timestamp válido foi encontrado.",
                "BERNARDO",
                "LOCALIZAR_ORIGEM_CORRETA_OU_REEXPORTAR",
                "NEGADA",
                respostas,
            ))

        else:
            registro["data_inicio"] = ts_validos.min().strftime("%d/%m/%Y %H:%M:%S")
            registro["data_fim"] = ts_validos.max().strftime("%d/%m/%Y %H:%M:%S")

            duplicados = int(ts_validos.duplicated().sum())
            registro["duplicados"] = duplicados

            if duplicados > 0:
                ocorrencias.append(criar_ocorrencia(
                    caminho, caminho.name, "REPROVADO",
                    "TIMESTAMP_DUPLICADO",
                    f"Foram encontrados {duplicados} timestamps duplicados.",
                    "BERNARDO",
                    "REINDEXAR_E_REMOVER_DUPLICIDADE_DE_ORIGEM",
                    "NEGADA",
                    respostas,
                ))

            diffs = ts_validos.diff().dt.total_seconds().dropna()
            negativos = int((diffs < 0).sum())
            positivos = int((diffs > 0).sum())

            if negativos > 0 and positivos == 0:
                registro["ordem_temporal"] = "DECRESCENTE"
                # Não gera ordem. Exportação Profit costuma vir assim.
            elif negativos > 0 and positivos > 0:
                registro["ordem_temporal"] = "MISTA"
                ocorrencias.append(criar_ocorrencia(
                    caminho, caminho.name, "REPROVADO",
                    "ORDEM_TEMPORAL_MISTA",
                    "Arquivo possui ordem temporal misturada.",
                    "BERNARDO",
                    "REINDEXAR_ARQUIVO_E_VALIDAR_ORIGEM",
                    "NEGADA",
                    respostas,
                ))
            else:
                registro["ordem_temporal"] = "CRESCENTE"

            if tipo_fractal == "INTRADAY" and minutos:
                ocorr_lacunas, contagem = classificar_lacunas(
                    timestamps=ts_validos,
                    minutos=minutos,
                    arquivo=caminho.name,
                    caminho=caminho,
                    ativo=ativo,
                    respostas=respostas,
                )

                ocorrencias.extend(ocorr_lacunas)
                registro.update(contagem)

        ohlc_status, ohlc_qtd = verificar_ohlc(df)
        registro["ohlc_status"] = ohlc_status
        registro["ohlc_problemas"] = ohlc_qtd

        if ohlc_status == "ERRO":
            responsavel = "ZE_DO_EUCRAZIO" if minutos in FRACTAIS_GERADOS_PELO_ZE else "BERNARDO"
            acao = "RECALCULAR_CANDLES_DERIVADOS" if responsavel == "ZE_DO_EUCRAZIO" else "VERIFICAR_EXPORTACAO_ORIGEM"

            ocorrencias.append(criar_ocorrencia(
                caminho, caminho.name, "REPROVADO",
                "OHLC_INVALIDO",
                f"Foram encontrados {ohlc_qtd} candles com OHLC inválido.",
                responsavel,
                acao,
                "NEGADA",
                respostas,
            ))

        volume_status, volume_qtd = verificar_nao_negativo(df, "volume")
        registro["volume_status"] = volume_status
        registro["volume_negativo"] = volume_qtd

        if volume_status == "ERRO":
            responsavel = "ZE_DO_EUCRAZIO" if minutos in FRACTAIS_GERADOS_PELO_ZE else "BERNARDO"
            ocorrencias.append(criar_ocorrencia(
                caminho, caminho.name, "REPROVADO",
                "VOLUME_NEGATIVO",
                f"Foram encontrados {volume_qtd} registros com volume negativo.",
                responsavel,
                "VERIFICAR_VOLUME_ORIGEM_OU_AGREGACAO",
                "NEGADA",
                respostas,
            ))

    except Exception as erro:
        ocorrencias.append(criar_ocorrencia(
            caminho, caminho.name, "REPROVADO",
            "ERRO_LEITURA",
            f"Erro ao ler arquivo: {erro}",
            "BERNARDO",
            "VERIFICAR_ENCODING_E_ESTRUTURA_DO_ARQUIVO",
            "NEGADA",
            respostas,
        ))

    ocorrencias_reais = [
        o for o in ocorrencias
        if o["status_certificacao"] != "INFORMATIVO"
    ]

    if any(o["status_certificacao"] == "REPROVADO" for o in ocorrencias_reais):
        registro["status"] = "REPROVADO"
        registro["certificacao"] = "NEGADA"
    elif any(o["status_certificacao"] == "APROVADO_COM_RESSALVAS" for o in ocorrencias_reais):
        registro["status"] = "APROVADO_COM_RESSALVAS"
        registro["certificacao"] = "MANTIDA_COM_JUSTIFICATIVA"
    else:
        registro["status"] = "CERTIFICADO"
        registro["certificacao"] = "CONCEDIDA"

    if ocorrencias:
        registro["motivos"] = " | ".join(sorted(set(o["motivo"] for o in ocorrencias)))
        registro["responsavel"] = " | ".join(sorted(set(o["responsavel"] for o in ocorrencias)))
        registro["acao_recomendada"] = " | ".join(sorted(set(o["acao_recomendada"] for o in ocorrencias)))

        ordem = ["CRITICA", "ALTA", "MEDIA", "BAIXA", "INFORMATIVA"]
        existentes = [o["criticidade"] for o in ocorrencias]
        for p in ordem:
            if p in existentes:
                registro["maior_criticidade"] = p
                break

    return registro, ocorrencias


# ============================================================
# SALVAMENTO
# ============================================================

def salvar_csv(lista, caminho):
    df = pd.DataFrame(lista)
    df.to_csv(caminho, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_resumo_motivos(ocorrencias):
    if not ocorrencias:
        return salvar_csv([], ARQUIVO_RESUMO_MOTIVOS)

    df = pd.DataFrame(ocorrencias)

    resumo = (
        df.groupby(["motivo", "responsavel", "criticidade", "status_certificacao"])
        .size()
        .reset_index(name="quantidade")
        .sort_values(["criticidade", "quantidade"], ascending=[True, False])
    )

    resumo.to_csv(ARQUIVO_RESUMO_MOTIVOS, sep=";", index=False, encoding="utf-8-sig")
    return resumo


def gerar_resumo_arquivos(registros):
    if not registros:
        return salvar_csv([], ARQUIVO_RESUMO_ARQUIVOS)

    df = pd.DataFrame(registros)

    colunas = [
        "arquivo",
        "ativo",
        "tipo_fractal",
        "fractal_minutos",
        "origem_fractal",
        "status",
        "maior_criticidade",
        "lacunas_total",
        "lacunas_normais",
        "lacunas_reais",
        "timestamps_invalidos",
        "duplicados",
        "ohlc_status",
        "ohlc_problemas",
        "motivos",
        "responsavel",
        "acao_recomendada",
    ]

    colunas = [c for c in colunas if c in df.columns]
    resumo = df[colunas].copy()
    resumo.to_csv(ARQUIVO_RESUMO_ARQUIVOS, sep=";", index=False, encoding="utf-8-sig")
    return resumo


# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "=" * 72)
    print("FISCAL TEMPORAL v5.0 - CARTORIO OFICIAL DO TEMPO DO TRIN")
    print("=" * 72)

    if not BASE_PATH.exists():
        print(f"ERRO: TRIN_HISTORICO nao encontrado em: {BASE_PATH}")
        return

    respostas = carregar_respostas()

    registros = []
    ocorrencias = []

    for pasta in sorted(os.listdir(BASE_PATH)):
        if pasta in IGNORAR:
            continue

        caminho_pasta = BASE_PATH / pasta

        if not caminho_pasta.is_dir():
            continue

        for raiz, _, arquivos in os.walk(caminho_pasta):
            for arquivo in sorted(arquivos):
                if not arquivo.lower().endswith(".csv"):
                    continue

                caminho = Path(raiz) / arquivo
                registro, ocorrs = analisar_arquivo(caminho, pasta, respostas)

                registros.append(registro)
                ocorrencias.extend(ocorrs)

    df_certificado = salvar_csv(registros, ARQUIVO_CERTIFICADO)
    salvar_csv(ocorrencias, ARQUIVO_ALERTAS)

    salvar_csv(
        [o for o in ocorrencias if o["responsavel"] == "BERNARDO"],
        ARQUIVO_BERNARDO,
    )

    salvar_csv(
        [o for o in ocorrencias if o["responsavel"] == "ZE_DO_EUCRAZIO"],
        ARQUIVO_ZE,
    )

    salvar_csv(
        [o for o in ocorrencias if o["responsavel"] == "OPERADOR_CALENDARIO_B3"],
        ARQUIVO_OPERADOR,
    )

    salvar_csv(
        [
            {
                "arquivo": r["arquivo"],
                "caminho": r["caminho"],
                "sha256": r["sha256"],
                "status": r["status"],
                "certificacao": r["certificacao"],
                "data_certificacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "fiscal_temporal": "v5.0",
            }
            for r in registros
        ],
        ARQUIVO_HASH,
    )

    gerar_resumo_motivos(ocorrencias)
    gerar_resumo_arquivos(registros)
    salvar_protocolos(PROTOCOLOS)

    total = len(df_certificado)
    certificados = len(df_certificado[df_certificado["status"] == "CERTIFICADO"])
    ressalvas = len(df_certificado[df_certificado["status"] == "APROVADO_COM_RESSALVAS"])
    reprovados = len(df_certificado[df_certificado["status"] == "REPROVADO"])

    criticas = len([o for o in ocorrencias if o["criticidade"] == "CRITICA"])
    altas = len([o for o in ocorrencias if o["criticidade"] == "ALTA"])
    medias = len([o for o in ocorrencias if o["criticidade"] == "MEDIA"])
    baixas = len([o for o in ocorrencias if o["criticidade"] == "BAIXA"])
    informativas = len([o for o in ocorrencias if o["criticidade"] == "INFORMATIVA"])

    lacunas_normais = int(df_certificado["lacunas_normais"].sum()) if total else 0
    lacunas_reais = int(df_certificado["lacunas_reais"].sum()) if total else 0

    if reprovados > 0:
        status_final = "REPROVADO_COM_PENDENCIAS"
    elif ressalvas > 0:
        status_final = "APROVADO_COM_RESSALVAS"
    else:
        status_final = "CERTIFICADO"

    laudo = f"""
============================================================
FISCAL TEMPORAL v5.0 - LAUDO OFICIAL DO TRIN
============================================================

Data/hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

Arquivos analisados        : {total}
Certificados               : {certificados}
Aprovados com ressalvas    : {ressalvas}
Reprovados                 : {reprovados}

Criticas                   : {criticas}
Altas                      : {altas}
Medias                     : {medias}
Baixas                     : {baixas}
Informativas               : {informativas}

Lacunas normais ignoradas  : {lacunas_normais}
Lacunas reais detectadas   : {lacunas_reais}

STATUS FINAL:
{status_final}

ARQUIVOS GERADOS:
- certificado_temporal.csv
- alertas_temporais.csv
- ordens_para_bernardo.csv
- ordens_para_ze.csv
- ordens_operador.csv
- certificado_sha256.csv
- resumo_por_motivo.csv
- resumo_por_arquivo.csv
- registro_protocolos_fiscal.csv

REGRA OFICIAL:
O Fiscal Temporal nao corrige.
O Fiscal Temporal identifica, explica, classifica, prioriza, protocola e certifica.

REGRA DE LACUNAS:
- Fora da sessao B3: nao gera pendencia.
- Fim de semana/feriado B3: nao gera pendencia.
- Dentro da sessao B3: reprova e emite ordem.
- Fractal gerado pelo Ze: ordem para Ze.
- Arquivo original Profit: ordem para Bernardo.
- Ordem decrescente Profit: nao derruba certificacao.

CICLO:
Fiscal emite protocolo
Modulo responsavel responde em respostas_*.csv
Fiscal recertifica
Arquivo recebe selo SHA256

============================================================
"""

    ARQUIVO_LAUDO.write_text(laudo, encoding="utf-8")

    print("\n" + "=" * 72)
    print("RESUMO FISCAL TEMPORAL v5.0")
    print("=" * 72)
    print(f"Arquivos analisados        : {total}")
    print(f"Certificados               : {certificados}")
    print(f"Aprovados com ressalvas    : {ressalvas}")
    print(f"Reprovados                 : {reprovados}")
    print(f"Criticas                   : {criticas}")
    print(f"Altas                      : {altas}")
    print(f"Medias                     : {medias}")
    print(f"Baixas                     : {baixas}")
    print(f"Informativas               : {informativas}")
    print(f"Lacunas normais ignoradas  : {lacunas_normais}")
    print(f"Lacunas reais detectadas   : {lacunas_reais}")
    print(f"Status final               : {status_final}")
    print("=" * 72)
    print(f"Laudo                      : {ARQUIVO_LAUDO}")
    print(f"Resumo arquivos            : {ARQUIVO_RESUMO_ARQUIVOS}")
    print(f"Resumo motivos             : {ARQUIVO_RESUMO_MOTIVOS}")
    print(f"Ordens Bernardo            : {ARQUIVO_BERNARDO}")
    print(f"Ordens Ze                  : {ARQUIVO_ZE}")
    print(f"Ordens Operador            : {ARQUIVO_OPERADOR}")
    print("=" * 72)


if __name__ == "__main__":
    main()