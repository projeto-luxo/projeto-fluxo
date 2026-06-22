import os
import hashlib
from pathlib import Path
from datetime import datetime
import pandas as pd

try:
    from calendario_b3 import CalendarioB3
except ImportError:
    from intelligence.calendario_b3 import CalendarioB3
# ============================================================
# FISCAL TEMPORAL v4.2.2 — CARTÓRIO TEMPORAL DO TRIN
#
# BASEADO NO v4.2 COM PATCH CONTROLADO v4.2.2.
#
# MELHORIAS v4.2:
# - ID de ocorrência estável e persistente
# - Informativo não derruba certificação
# - Ordem decrescente do Profit não vira ressalva
# - Ordens só para pendências reais
# - Resumo por motivo
# - Resumo por arquivo
# - Registro persistente de protocolos
# - Consulta CalendarioB3 externo para justificar lacunas
# - Calendario nao pertence ao Fiscal; Fiscal apenas consulta
#
# NÃO FAZ:
# - Não corrige dados
# - Não gera fractais
# - Não move arquivos
# - Não cria calendário novo
# - Não chama Bernardo/Zé diretamente
# ============================================================

TRIN_ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = TRIN_ROOT / "TRIN_HISTORICO"

PASTA_CERTIFICACOES = BASE_PATH / "00_CERTIFICACOES"
PASTA_CERTIFICACOES.mkdir(parents=True, exist_ok=True)

ARQUIVO_CERTIFICADO = PASTA_CERTIFICACOES / "certificado_temporal.csv"
ARQUIVO_ALERTAS = PASTA_CERTIFICACOES / "alertas_temporais.csv"
ARQUIVO_LAUDO = PASTA_CERTIFICACOES / "laudo_temporal.txt"
ARQUIVO_BERNARDO = PASTA_CERTIFICACOES / "ordens_para_bernardo.csv"
ARQUIVO_ZE = PASTA_CERTIFICACOES / "ordens_para_ze.csv"
ARQUIVO_OPERADOR = PASTA_CERTIFICACOES / "ordens_operador.csv"
ARQUIVO_HASH = PASTA_CERTIFICACOES / "certificado_sha256.csv"
ARQUIVO_TRILHA = PASTA_CERTIFICACOES / "trilha_auditoria_temporal.csv"
ARQUIVO_PROTOCOLos = PASTA_CERTIFICACOES / "registro_protocolos_fiscal.csv"
ARQUIVO_RESUMO_MOTIVO = PASTA_CERTIFICACOES / "resumo_por_motivo.csv"
ARQUIVO_RESUMO_ARQUIVO = PASTA_CERTIFICACOES / "resumo_por_arquivo.csv"

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

CALENDARIO_B3 = None


def obter_calendario_b3():
    global CALENDARIO_B3

    if CALENDARIO_B3 is None:
        try:
            CALENDARIO_B3 = CalendarioB3()
        except Exception as erro:
            print(f"AVISO: CalendarioB3 nao carregado. Fiscal seguira regra conservadora. Erro: {erro}")
            CALENDARIO_B3 = False

    return CALENDARIO_B3 if CALENDARIO_B3 is not False else None


def sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def normalizar_coluna(nome):
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
    return texto


def normalizar_colunas(df):
    return [normalizar_coluna(c) for c in df.columns]


def ler_csv(caminho):
    return pd.read_csv(
        caminho,
        sep=";",
        engine="python",
        encoding="utf-8-sig",
        on_bad_lines="skip",
    )


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


def detectar_tipo_fractal(pasta, arquivo):
    texto = f"{pasta} {arquivo}".upper()

    if "DIARIO" in texto or "DIÁRIO" in texto:
        return "DIARIO", None
    if "SEMANAL" in texto:
        return "SEMANAL", None
    if "MENSAL" in texto:
        return "MENSAL", None

    partes = str(pasta).upper().split("_")

    for parte in partes:
        if parte.isdigit():
            return "INTRADAY", int(parte)

    return "DESCONHECIDO", None


def montar_timestamp(df, tipo_fractal):
    colunas = normalizar_colunas(df)

    if "timestamp" in colunas:
        col = df.columns[colunas.index("timestamp")]
        return parse_datas(df[col])

    if "timestamp_pc" in colunas:
        col = df.columns[colunas.index("timestamp_pc")]
        return parse_datas(df[col])

    if "data" in colunas:
        col_data = df.columns[colunas.index("data")]

        if tipo_fractal == "INTRADAY" and "hora" in colunas:
            col_hora = df.columns[colunas.index("hora")]
            return parse_datas(
                df[col_data].astype(str) + " " + df[col_hora].astype(str)
            )

        return parse_datas(df[col_data])

    if tipo_fractal == "INTRADAY" and len(df.columns) >= 3:
        return parse_datas(
            df.iloc[:, 1].astype(str) + " " + df.iloc[:, 2].astype(str)
        )

    if len(df.columns) >= 2:
        return parse_datas(df.iloc[:, 1])

    return pd.Series([pd.NaT] * len(df))


def carregar_protocolos():
    if not ARQUIVO_PROTOCOLos.exists():
        return {}, 0

    try:
        df = pd.read_csv(ARQUIVO_PROTOCOLos, sep=";", engine="python", dtype=str)
    except Exception:
        return {}, 0

    mapa = {}
    maior = 0

    for _, row in df.iterrows():
        chave = str(row.get("chave_ocorrencia", ""))
        protocolo = str(row.get("id_ocorrencia", ""))

        if chave and protocolo:
            mapa[chave] = protocolo

        try:
            seq = int(protocolo.split("-")[-1])
            maior = max(maior, seq)
        except Exception:
            pass

    return mapa, maior


PROTOCOLOS, ULTIMO_PROTOCOLO = carregar_protocolos()


def chave_ocorrencia(caminho, motivo, descricao):
    base = f"{Path(caminho).as_posix()}|{motivo}|{descricao}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def obter_id_ocorrencia(caminho, motivo, descricao):
    global ULTIMO_PROTOCOLO

    chave = chave_ocorrencia(caminho, motivo, descricao)

    if chave in PROTOCOLOS:
        return PROTOCOLOS[chave]

    ULTIMO_PROTOCOLO += 1
    data = datetime.now().strftime("%Y%m%d")
    protocolo = f"FT-{data}-{ULTIMO_PROTOCOLO:06d}"

    PROTOCOLOS[chave] = protocolo
    return protocolo


def salvar_protocolos():
    linhas = []

    for chave, protocolo in sorted(PROTOCOLOS.items(), key=lambda x: x[1]):
        linhas.append({
            "id_ocorrencia": protocolo,
            "chave_ocorrencia": chave,
            "data_registro": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })

    pd.DataFrame(linhas).to_csv(
        ARQUIVO_PROTOCOLos,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )



def definir_criticidade(motivo):
    criticas = {
        "TIMESTAMP_DUPLICADO",
        "SEM_TIMESTAMP_VALIDO",
        "ORDEM_TEMPORAL_MISTA",
        "OHLC_INVALIDO",
        "ARQUIVO_VAZIO",
    }

    altas = {
        "TIMESTAMP_INVALIDO",
        "HEADER_SEM_DATA",
        "INTRADAY_SEM_HORA",
        "LACUNA_CANDLE_AUSENTE",
        "VOLUME_NEGATIVO",
        "ERRO_LEITURA",
        "CALENDARIO_B3_INDISPONIVEL",
        "LACUNA_LONGA_SEM_CALENDARIO",
    }

    medias = {
        "LACUNA_SESSAO_OU_CORTE_ARQUIVO",
        "LACUNA_CRUZA_CALENDARIO_B3",
        "LACUNA_EM_HORARIO_ESPECIAL_B3",
        "LACUNA_LONGA_SEM_JUSTIFICATIVA_CALENDARIO",
    }

    informativas = {
        "ORDEM_DECRESCENTE_ORIGEM_PROFIT",
        "LACUNA_FIM_SEMANA_OU_FERIADO",
        "LACUNA_ENTRE_SESSOES",
        "LACUNA_JUSTIFICADA_FIM_DE_SEMANA",
        "LACUNA_JUSTIFICADA_FERIADO_B3",
        "LACUNA_JUSTIFICADA_CALENDARIO_B3",
        "LACUNA_LONGA_ENTRE_SESSOES",
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


def definir_dependencia(motivo, responsavel):
    if motivo == "LACUNA_CANDLE_AUSENTE":
        return "BERNARDO_LOCALIZAR_ORIGEM -> ZE_REGENERAR_FRACTAL -> FISCAL_RECERTIFICAR"

    if responsavel == "BERNARDO":
        return "BERNARDO_CORRIGIR_OU_REINDEXAR -> FISCAL_RECERTIFICAR"

    if responsavel == "ZE_DO_EUCRAZIO":
        return "ZE_REGENERAR_OU_RECALCULAR -> FISCAL_RECERTIFICAR"

    if responsavel == "OPERADOR_CALENDARIO_B3":
        return "OPERADOR_ATUALIZAR_CALENDARIO_B3 -> FISCAL_RECERTIFICAR"

    return "NENHUMA"


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


def status_ordem_por_resposta(id_ocorrencia, respostas):
    status = respostas.get(id_ocorrencia, "PENDENTE")

    permitidos = {
        "PENDENTE",
        "EM_ANALISE",
        "EM_CORRECAO",
        "CORRIGIDO",
        "RECERTIFICAR",
        "ENCERRADO",
    }

    if status in permitidos:
        return status

    return "PENDENTE"


def criar_ocorrencia(
    arquivo,
    caminho,
    status,
    motivo,
    descricao,
    responsavel,
    acao,
    certificacao,
    respostas
):
    id_ocorrencia = obter_id_ocorrencia(caminho, motivo, descricao)
    criticidade = definir_criticidade(motivo)

    return {
        "id_ocorrencia": id_ocorrencia,
        "arquivo": arquivo,
        "caminho": str(caminho),
        "status_certificacao": status,
        "status_ordem": status_ordem_por_resposta(id_ocorrencia, respostas),
        "criticidade": criticidade,
        "motivo": motivo,
        "descricao": descricao,
        "responsavel": responsavel,
        "acao_recomendada": acao,
        "dependencia": definir_dependencia(motivo, responsavel),
        "certificacao": certificacao,
        "data_emissao": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "fiscal_temporal": "v4.2.2",
    }


def verificar_ohlc(df):
    colunas = normalizar_colunas(df)

    mapa = {
        "abertura": ["abertura", "open"],
        "maximo": ["maximo", "máximo", "high"],
        "minimo": ["minimo", "mínimo", "low"],
        "ultimo": ["ultimo", "último", "close", "fechamento"],
    }

    achados = {}

    for chave, nomes in mapa.items():
        achados[chave] = None

        for nome in nomes:
            nome_norm = normalizar_coluna(nome)

            if nome_norm in colunas:
                achados[chave] = df.columns[colunas.index(nome_norm)]
                break

    if not all(achados.values()):
        return "NAO_VERIFICADO", 0

    abertura = pd.to_numeric(df[achados["abertura"]], errors="coerce")
    maximo = pd.to_numeric(df[achados["maximo"]], errors="coerce")
    minimo = pd.to_numeric(df[achados["minimo"]], errors="coerce")
    ultimo = pd.to_numeric(df[achados["ultimo"]], errors="coerce")

    invalido = (
        (maximo < minimo) |
        (abertura > maximo) |
        (abertura < minimo) |
        (ultimo > maximo) |
        (ultimo < minimo)
    )

    qtd = int(invalido.fillna(False).sum())

    return ("ERRO", qtd) if qtd > 0 else ("OK", 0)


def verificar_nao_negativo(df, nome_coluna):
    colunas = normalizar_colunas(df)

    if nome_coluna not in colunas:
        return "NAO_VERIFICADO", 0

    col = df.columns[colunas.index(nome_coluna)]
    valores = pd.to_numeric(df[col], errors="coerce")
    qtd = int((valores < 0).fillna(False).sum())

    return ("ERRO", qtd) if qtd > 0 else ("OK", 0)



def data_b3(dt):
    return dt.strftime("%Y-%m-%d")


def intervalo_datas(inicio, fim):
    datas = pd.date_range(inicio.date(), fim.date(), freq="D")
    return [d.strftime("%Y-%m-%d") for d in datas]


def fim_de_semana(dt):
    return dt.weekday() >= 5


def hora_em_janela(dt, inicio_txt, fim_txt):
    if not inicio_txt or not fim_txt:
        return False

    try:
        h_ini = datetime.strptime(str(inicio_txt), "%H:%M").time()
        h_fim = datetime.strptime(str(fim_txt), "%H:%M").time()
        return h_ini <= dt.time() <= h_fim
    except Exception:
        return False


def avaliar_lacuna_com_calendario(inicio, fim, minutos):
    calendario = obter_calendario_b3()

    if calendario is None:
        return {
            "tem_calendario": False,
            "status": None,
            "motivo": None,
            "responsavel": None,
            "acao": None,
            "certificacao": None,
            "justificativa": "Calendario B3 indisponivel. Fiscal aplicara regra conservadora v4.2.2.",
        }

    datas = intervalo_datas(inicio, fim)
    feriados = []
    horarios_especiais = []
    nao_negociaveis = []
    negociaveis = []

    for data in datas:
        try:
            if calendario.eh_feriado(data):
                feriados.append(data)

            especial = calendario.horario_especial(data)
            if especial:
                horarios_especiais.append((data, especial))

            if calendario.eh_negociavel(data):
                negociaveis.append(data)
            else:
                nao_negociaveis.append(data)
        except Exception:
            negociaveis.append(data)

    # Fim de semana puro: justifica lacuna automaticamente.
    if all(pd.Timestamp(d).weekday() >= 5 for d in datas):
        return {
            "tem_calendario": True,
            "status": "INFORMATIVO",
            "motivo": "LACUNA_JUSTIFICADA_FIM_DE_SEMANA",
            "responsavel": "CALENDARIO_B3",
            "acao": "NENHUMA_ACAO_OPERACIONAL",
            "certificacao": "JUSTIFICADA",
            "justificativa": "Lacuna ocorreu em fim de semana. Nao havia pregao esperado.",
        }

    # Todos os dias do intervalo sao nao negociaveis segundo calendario.
    if datas and len(nao_negociaveis) == len(datas):
        motivo = "LACUNA_JUSTIFICADA_FERIADO_B3" if feriados else "LACUNA_JUSTIFICADA_CALENDARIO_B3"
        return {
            "tem_calendario": True,
            "status": "INFORMATIVO",
            "motivo": motivo,
            "responsavel": "CALENDARIO_B3",
            "acao": "NENHUMA_ACAO_OPERACIONAL",
            "certificacao": "JUSTIFICADA",
            "justificativa": f"Lacuna justificada pelo calendario B3. Datas nao negociaveis: {', '.join(nao_negociaveis)}.",
        }

    # Se a lacuna cruza feriado/fim de semana mas tambem tem dia negociavel,
    # o Fiscal nao reprova diretamente: manda como ressalva para analise de origem.
    if feriados or any(pd.Timestamp(d).weekday() >= 5 for d in datas):
        return {
            "tem_calendario": True,
            "status": "APROVADO_COM_RESSALVAS",
            "motivo": "LACUNA_CRUZA_CALENDARIO_B3",
            "responsavel": "BERNARDO",
            "acao": "VERIFICAR_ORIGEM_ARQUIVO_E_CONTEXTO_TEMPORAL",
            "certificacao": "PENDENTE_DE_JUSTIFICATIVA",
            "justificativa": (
                "Lacuna cruza dias nao negociaveis do calendario B3, "
                "mas tambem envolve janela potencialmente negociavel."
            ),
        }

    # Horario especial no mesmo intervalo: ressalva, nao reprova direta.
    if horarios_especiais:
        detalhes = []
        for data, especial in horarios_especiais:
            detalhes.append(f"{data} {especial.get('inicio','')}->{especial.get('fim','')} {especial.get('motivo','')}")

        return {
            "tem_calendario": True,
            "status": "APROVADO_COM_RESSALVAS",
            "motivo": "LACUNA_EM_HORARIO_ESPECIAL_B3",
            "responsavel": "BERNARDO",
            "acao": "VERIFICAR_HORARIO_ESPECIAL_E_ORIGEM_DO_ARQUIVO",
            "certificacao": "PENDENTE_DE_JUSTIFICATIVA",
            "justificativa": "Lacuna envolve horario especial B3: " + " | ".join(detalhes),
        }

    return {
        "tem_calendario": True,
        "status": None,
        "motivo": None,
        "responsavel": None,
        "acao": None,
        "certificacao": None,
        "justificativa": "Calendario B3 nao justificou a lacuna.",
    }




def classificar_lacunas(timestamps, minutos, arquivo, caminho, respostas):
    ts = timestamps.dropna().sort_values()

    if len(ts) <= 1 or not minutos:
        return []

    esperado = minutos * 60
    lacunas = []
    lacunas_longas_consolidadas = {}
    anterior = None

    for atual in ts:
        if anterior is None:
            anterior = atual
            continue

        segundos = (atual - anterior).total_seconds()

        if segundos <= esperado:
            anterior = atual
            continue

        horas = segundos / 3600
        contexto = avaliar_lacuna_com_calendario(anterior, atual, minutos)

        inicio_txt = anterior.strftime("%d/%m/%Y %H:%M:%S")
        fim_txt = atual.strftime("%d/%m/%Y %H:%M:%S")

        # Calendario indisponivel: nao jogar culpa em Bernardo ou Ze.
        if contexto.get("tem_calendario") is False:
            motivo = "LACUNA_LONGA_SEM_CALENDARIO" if horas >= 12 else "CALENDARIO_B3_INDISPONIVEL"
            descricao = (
                f"Lacuna de {horas:.2f} horas entre {inicio_txt} e {fim_txt}. "
                "Calendario B3 indisponivel; nao e possivel concluir se a lacuna e de mercado, sessao ou arquivo."
            )

            lacunas.append(criar_ocorrencia(
                arquivo,
                caminho,
                "APROVADO_COM_RESSALVAS",
                motivo,
                descricao,
                "OPERADOR_CALENDARIO_B3",
                "CARREGAR_OU_CORRIGIR_CALENDARIO_B3",
                "PENDENTE_DE_INFRAESTRUTURA",
                respostas
            ))

            anterior = atual
            continue

        # Lacunas longas informativas ficam consolidadas por arquivo/motivo.
        # Regra v4.2.2: o Fiscal registra o contexto, mas nao abre uma ocorrencia por cada vao longo.
        if horas >= 12:
            if contexto.get("status") == "INFORMATIVO":
                motivo = contexto.get("motivo") or "LACUNA_LONGA_ENTRE_SESSOES"
                responsavel = contexto.get("responsavel") or "CALENDARIO_B3"
                acao = contexto.get("acao") or "NENHUMA_ACAO_OPERACIONAL"
                certificacao = contexto.get("certificacao") or "JUSTIFICADA"
                justificativa = contexto.get("justificativa", "")
            else:
                motivo = "LACUNA_LONGA_ENTRE_SESSOES"
                responsavel = "CALENDARIO_B3"
                acao = "NENHUMA_ACAO_OPERACIONAL"
                certificacao = "JUSTIFICADA_COM_RESSALVA"
                justificativa = "Registrada como contexto temporal longo entre sessoes/arquivos."

            chave = (motivo, responsavel, acao, certificacao)
            resumo = lacunas_longas_consolidadas.setdefault(chave, {
                "qtd": 0,
                "horas_total": 0.0,
                "maior_horas": 0.0,
                "primeira": inicio_txt,
                "ultima": fim_txt,
                "justificativas": [],
            })

            resumo["qtd"] += 1
            resumo["horas_total"] += horas
            resumo["maior_horas"] = max(resumo["maior_horas"], horas)
            resumo["ultima"] = fim_txt

            if justificativa and len(resumo["justificativas"]) < 3:
                resumo["justificativas"].append(justificativa)

            anterior = atual
            continue

        # Lacuna justificada pelo calendario: registra, mas nao derruba certificacao nem gera ordem.
        if contexto.get("status") == "INFORMATIVO":
            descricao = (
                f"Lacuna de {horas:.2f} horas entre {inicio_txt} e {fim_txt}. "
                f"{contexto.get('justificativa', '')}"
            )

            lacunas.append(criar_ocorrencia(
                arquivo,
                caminho,
                "INFORMATIVO",
                contexto.get("motivo") or "LACUNA_JUSTIFICADA_CALENDARIO_B3",
                descricao,
                contexto.get("responsavel") or "CALENDARIO_B3",
                contexto.get("acao") or "NENHUMA_ACAO_OPERACIONAL",
                contexto.get("certificacao") or "JUSTIFICADA",
                respostas
            ))

            anterior = atual
            continue

        # Contextos especiais do calendario viram ressalva controlada se forem lacunas curtas.
        if contexto.get("status") == "APROVADO_COM_RESSALVAS" and horas < 2:
            descricao = (
                f"Lacuna de {horas:.2f} horas entre {inicio_txt} e {fim_txt}. "
                f"{contexto.get('justificativa', '')}"
            )

            lacunas.append(criar_ocorrencia(
                arquivo,
                caminho,
                "APROVADO_COM_RESSALVAS",
                contexto["motivo"],
                descricao,
                contexto["responsavel"],
                contexto["acao"],
                contexto["certificacao"],
                respostas
            ))

            anterior = atual
            continue

        # Lacuna media: possivel corte de sessao/arquivo.
        if horas >= 2:
            descricao = (
                f"Lacuna de {horas:.2f} horas entre {inicio_txt} e {fim_txt}. "
                "Janela sensivel. Pode indicar corte de sessao ou arquivo."
            )

            lacunas.append(criar_ocorrencia(
                arquivo,
                caminho,
                "APROVADO_COM_RESSALVAS",
                "LACUNA_SESSAO_OU_CORTE_ARQUIVO",
                descricao,
                "BERNARDO",
                "VERIFICAR_ORIGEM_ARQUIVO_E_CONTEXTO_TEMPORAL",
                "PENDENTE_DE_JUSTIFICATIVA",
                respostas
            ))

        # Lacuna curta: possivel candle ausente dentro do pregao/fractal.
        else:
            descricao = (
                f"Lacuna de {horas:.2f} horas entre {inicio_txt} e {fim_txt}. "
                "Possivel candle ausente dentro da sequencia temporal."
            )

            lacunas.append(criar_ocorrencia(
                arquivo,
                caminho,
                "REPROVADO",
                "LACUNA_CANDLE_AUSENTE",
                descricao,
                "ZE_DO_EUCRAZIO",
                "REGENERAR_FRACTAL_A_PARTIR_DO_1_MIN",
                "NEGADA",
                respostas
            ))

        anterior = atual

    for (motivo, responsavel, acao, certificacao), resumo in lacunas_longas_consolidadas.items():
        detalhes = " | ".join(resumo["justificativas"]) if resumo["justificativas"] else "Contexto temporal longo consolidado."
        descricao = (
            f"{resumo['qtd']} lacunas longas consolidadas neste arquivo. "
            f"Primeira: {resumo['primeira']}. Ultima: {resumo['ultima']}. "
            f"Horas totais aproximadas: {resumo['horas_total']:.2f}. "
            f"Maior lacuna: {resumo['maior_horas']:.2f} horas. "
            f"{detalhes}"
        )

        lacunas.append(criar_ocorrencia(
            arquivo,
            caminho,
            "INFORMATIVO",
            motivo,
            descricao,
            responsavel,
            acao,
            certificacao,
            respostas
        ))

    return lacunas


def analisar_arquivo(caminho, pasta, respostas):
    tipo_fractal, minutos = detectar_tipo_fractal(pasta, caminho.name)

    registro = {
        "arquivo": caminho.name,
        "pasta": pasta,
        "caminho": str(caminho),
        "tipo_fractal": tipo_fractal,
        "fractal_minutos": minutos if minutos else "N/D",
        "sha256": "N/D",
        "linhas": 0,
        "colunas": 0,
        "data_inicio": "N/D",
        "data_fim": "N/D",
        "ordem_temporal": "N/D",
        "timestamps_invalidos": 0,
        "duplicados": 0,
        "lacunas": 0,
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
        df = ler_csv(caminho)

        registro["linhas"] = len(df)
        registro["colunas"] = len(df.columns)

        colunas = normalizar_colunas(df)

        if len(df) == 0:
            ocorrencias.append(criar_ocorrencia(
                caminho.name, caminho, "REPROVADO",
                "ARQUIVO_VAZIO",
                "Arquivo CSV sem registros.",
                "BERNARDO",
                "VERIFICAR_ORIGEM_E_REINDEXAR_BIBLIOTECA",
                "NEGADA",
                respostas
            ))

        if "data" not in colunas and len(df.columns) < 2:
            ocorrencias.append(criar_ocorrencia(
                caminho.name, caminho, "REPROVADO",
                "HEADER_SEM_DATA",
                "Arquivo não possui coluna de data identificável.",
                "BERNARDO",
                "CORRIGIR_ESTRUTURA_OU_LOCALIZAR_ORIGEM_CORRETA",
                "NEGADA",
                respostas
            ))

        if tipo_fractal == "INTRADAY" and "hora" not in colunas and len(df.columns) < 3:
            ocorrencias.append(criar_ocorrencia(
                caminho.name, caminho, "REPROVADO",
                "INTRADAY_SEM_HORA",
                "Arquivo intraday não possui hora identificável.",
                "BERNARDO",
                "CORRIGIR_HEADER_OU_REEXPORTAR_ARQUIVO",
                "NEGADA",
                respostas
            ))

        timestamps = montar_timestamp(df, tipo_fractal)
        invalidos = int(timestamps.isna().sum())
        registro["timestamps_invalidos"] = invalidos

        if invalidos > 0:
            ocorrencias.append(criar_ocorrencia(
                caminho.name, caminho, "REPROVADO",
                "TIMESTAMP_INVALIDO",
                f"Foram encontrados {invalidos} timestamps inválidos.",
                "BERNARDO",
                "CORRIGIR_DATA_HORA_OU_REINDEXAR_ARQUIVO",
                "NEGADA",
                respostas
            ))

        ts_validos = timestamps.dropna()

        if len(ts_validos) == 0:
            ocorrencias.append(criar_ocorrencia(
                caminho.name, caminho, "REPROVADO",
                "SEM_TIMESTAMP_VALIDO",
                "Nenhum timestamp válido foi encontrado no arquivo.",
                "BERNARDO",
                "LOCALIZAR_ORIGEM_CORRETA_OU_REEXPORTAR",
                "NEGADA",
                respostas
            ))

        else:
            registro["data_inicio"] = ts_validos.min().strftime("%d/%m/%Y %H:%M:%S")
            registro["data_fim"] = ts_validos.max().strftime("%d/%m/%Y %H:%M:%S")

            duplicados = int(ts_validos.duplicated().sum())
            registro["duplicados"] = duplicados

            if duplicados > 0:
                ocorrencias.append(criar_ocorrencia(
                    caminho.name, caminho, "REPROVADO",
                    "TIMESTAMP_DUPLICADO",
                    f"Foram encontrados {duplicados} timestamps duplicados.",
                    "BERNARDO",
                    "REINDEXAR_E_REMOVER_DUPLICIDADE_DE_ORIGEM",
                    "NEGADA",
                    respostas
                ))

            diffs = ts_validos.diff().dt.total_seconds().dropna()
            negativos = int((diffs < 0).sum())
            positivos = int((diffs > 0).sum())

            if negativos > 0 and positivos == 0:
                registro["ordem_temporal"] = "DECRESCENTE"
                # Exportação do Profit pode vir decrescente.
                # Não gera ocorrência nem ressalva.
            elif negativos > 0 and positivos > 0:
                registro["ordem_temporal"] = "MISTA"
                ocorrencias.append(criar_ocorrencia(
                    caminho.name, caminho, "REPROVADO",
                    "ORDEM_TEMPORAL_MISTA",
                    "Arquivo possui ordem temporal misturada.",
                    "BERNARDO",
                    "REINDEXAR_ARQUIVO_E_VALIDAR_ORIGEM",
                    "NEGADA",
                    respostas
                ))
            else:
                registro["ordem_temporal"] = "CRESCENTE"

            if tipo_fractal == "INTRADAY":
                lacunas = classificar_lacunas(
                    ts_validos,
                    minutos,
                    caminho.name,
                    caminho,
                    respostas
                )

                registro["lacunas"] = len(lacunas)
                ocorrencias.extend(lacunas)

        ohlc_status, ohlc_qtd = verificar_ohlc(df)
        registro["ohlc_status"] = ohlc_status
        registro["ohlc_problemas"] = ohlc_qtd

        if ohlc_status == "ERRO":
            ocorrencias.append(criar_ocorrencia(
                caminho.name, caminho, "REPROVADO",
                "OHLC_INVALIDO",
                f"Foram encontrados {ohlc_qtd} candles com OHLC inválido.",
                "ZE_DO_EUCRAZIO",
                "REGERAR_OU_RECALCULAR_CANDLES_DERIVADOS",
                "NEGADA",
                respostas
            ))

        volume_status, volume_qtd = verificar_nao_negativo(df, "volume")
        registro["volume_status"] = volume_status
        registro["volume_negativo"] = volume_qtd

        if volume_status == "ERRO":
            ocorrencias.append(criar_ocorrencia(
                caminho.name, caminho, "REPROVADO",
                "VOLUME_NEGATIVO",
                f"Foram encontrados {volume_qtd} registros com volume negativo.",
                "ZE_DO_EUCRAZIO",
                "RECALCULAR_AGREGACAO_DE_VOLUME",
                "NEGADA",
                respostas
            ))

    except Exception as erro:
        ocorrencias.append(criar_ocorrencia(
            caminho.name, caminho, "REPROVADO",
            "ERRO_LEITURA",
            f"Erro ao ler arquivo: {erro}",
            "BERNARDO",
            "VERIFICAR_ARQUIVO_ORIGEM_ENCODING_E_ESTRUTURA",
            "NEGADA",
            respostas
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

        prioridade_ordem = ["CRITICA", "ALTA", "MEDIA", "BAIXA", "INFORMATIVA"]
        existentes = [o["criticidade"] for o in ocorrencias]

        for p in prioridade_ordem:
            if p in existentes:
                registro["maior_criticidade"] = p
                break

    return registro, ocorrencias


def salvar_csv(lista, caminho):
    df = pd.DataFrame(lista)
    df.to_csv(caminho, sep=";", index=False, encoding="utf-8-sig")
    return df


def salvar_resumos(registros, ocorrencias):
    df_reg = pd.DataFrame(registros)
    df_oc = pd.DataFrame(ocorrencias)

    if len(df_reg):
        colunas = [
            "arquivo",
            "pasta",
            "tipo_fractal",
            "fractal_minutos",
            "status",
            "maior_criticidade",
            "motivos",
            "responsavel",
            "acao_recomendada",
            "linhas",
            "colunas",
            "data_inicio",
            "data_fim",
            "ordem_temporal",
            "timestamps_invalidos",
            "duplicados",
            "lacunas",
            "ohlc_status",
            "ohlc_problemas",
            "volume_status",
            "volume_negativo",
        ]

        colunas = [c for c in colunas if c in df_reg.columns]

        df_reg[colunas].to_csv(
            ARQUIVO_RESUMO_ARQUIVO,
            sep=";",
            index=False,
            encoding="utf-8-sig"
        )

    if len(df_oc):
        resumo = (
            df_oc.groupby([
                "status_certificacao",
                "criticidade",
                "motivo",
                "responsavel"
            ])
            .size()
            .reset_index(name="quantidade")
            .sort_values(
                by=["status_certificacao", "criticidade", "quantidade"],
                ascending=[True, True, False]
            )
        )

        resumo.to_csv(
            ARQUIVO_RESUMO_MOTIVO,
            sep=";",
            index=False,
            encoding="utf-8-sig"
        )
    else:
        pd.DataFrame().to_csv(
            ARQUIVO_RESUMO_MOTIVO,
            sep=";",
            index=False,
            encoding="utf-8-sig"
        )


def main():
    print("\n" + "=" * 70)
    print("FISCAL TEMPORAL v4.2.2 - CARTORIO TEMPORAL DO TRIN")
    print("=" * 70)

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

    ocorrencias_reais = [
        o for o in ocorrencias
        if o["status_certificacao"] != "INFORMATIVO"
    ]

    salvar_csv(
        [o for o in ocorrencias_reais if o["responsavel"] == "BERNARDO"],
        ARQUIVO_BERNARDO
    )

    salvar_csv(
        [o for o in ocorrencias_reais if o["responsavel"] == "ZE_DO_EUCRAZIO"],
        ARQUIVO_ZE
    )

    salvar_csv(
        [o for o in ocorrencias_reais if o["responsavel"] == "OPERADOR_CALENDARIO_B3"],
        ARQUIVO_OPERADOR
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
                "fiscal_temporal": "v4.2.2",
            }
            for r in registros
        ],
        ARQUIVO_HASH
    )

    trilha = []
    for o in ocorrencias:
        trilha.append({
            "id_ocorrencia": o["id_ocorrencia"],
            "evento": "CONTEXTO_REGISTRADO" if o["status_certificacao"] == "INFORMATIVO" else "ORDEM_EMITIDA",
            "arquivo": o["arquivo"],
            "responsavel": o["responsavel"],
            "status_ordem": o["status_ordem"],
            "criticidade": o["criticidade"],
            "motivo": o["motivo"],
            "data_evento": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "fiscal_temporal": "v4.2.2",
        })

    salvar_csv(trilha, ARQUIVO_TRILHA)
    salvar_resumos(registros, ocorrencias)
    salvar_protocolos()

    total = len(df_certificado)
    certificados = len(df_certificado[df_certificado["status"] == "CERTIFICADO"])
    ressalvas = len(df_certificado[df_certificado["status"] == "APROVADO_COM_RESSALVAS"])
    reprovados = len(df_certificado[df_certificado["status"] == "REPROVADO"])

    criticas = len([o for o in ocorrencias if o["criticidade"] == "CRITICA"])
    altas = len([o for o in ocorrencias if o["criticidade"] == "ALTA"])
    medias = len([o for o in ocorrencias if o["criticidade"] == "MEDIA"])
    baixas = len([o for o in ocorrencias if o["criticidade"] == "BAIXA"])
    informativas = len([o for o in ocorrencias if o["criticidade"] == "INFORMATIVA"])

    if reprovados > 0:
        status_final = "REPROVADO_COM_PENDENCIAS"
    elif ressalvas > 0:
        status_final = "APROVADO_COM_RESSALVAS"
    else:
        status_final = "CERTIFICADO"

    laudo = f"""
============================================================
FISCAL TEMPORAL v4.2.2 - LAUDO OFICIAL
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

STATUS FINAL:
{status_final}

ARQUIVOS GERADOS:
- certificado_temporal.csv
- alertas_temporais.csv
- ordens_para_bernardo.csv
- ordens_para_ze.csv
- ordens_operador.csv
- certificado_sha256.csv
- trilha_auditoria_temporal.csv
- registro_protocolos_fiscal.csv
- resumo_por_motivo.csv
- resumo_por_arquivo.csv

REGRA v4.2.2:
- O Fiscal nao corrige.
- O Fiscal nao cria calendario; apenas consulta CalendarioB3 externo.
- Lacunas justificadas pelo calendario B3 viram informativo e nao geram ordem.
- Horarios especiais ou cruzamento de calendario viram ressalva controlada.
- Ordem decrescente do Profit nao derruba certificacao.
- Informativo nao derruba certificacao.
- Ordens sao emitidas apenas para pendencias reais.
- IDs de ocorrencia sao persistidos em registro_protocolos_fiscal.csv.

============================================================
"""

    ARQUIVO_LAUDO.write_text(laudo, encoding="utf-8")

    print("\n" + "=" * 70)
    print("RESUMO FISCAL TEMPORAL v4.2.2")
    print("=" * 70)
    print(f"Arquivos analisados     : {total}")
    print(f"Certificados            : {certificados}")
    print(f"Aprovados com ressalvas : {ressalvas}")
    print(f"Reprovados              : {reprovados}")
    print(f"Criticas                : {criticas}")
    print(f"Altas                   : {altas}")
    print(f"Medias                  : {medias}")
    print(f"Baixas                  : {baixas}")
    print(f"Informativas            : {informativas}")
    print(f"Status final            : {status_final}")
    print("=" * 70)
    print(f"Laudo                   : {ARQUIVO_LAUDO}")
    print(f"Resumo por arquivo      : {ARQUIVO_RESUMO_ARQUIVO}")
    print(f"Resumo por motivo       : {ARQUIVO_RESUMO_MOTIVO}")
    print(f"Ordens Bernardo         : {ARQUIVO_BERNARDO}")
    print(f"Ordens Ze               : {ARQUIVO_ZE}")
    print(f"Ordens Operador         : {ARQUIVO_OPERADOR}")
    print("=" * 70)


if __name__ == "__main__":
    main()