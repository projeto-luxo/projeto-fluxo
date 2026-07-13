import os
import hashlib
import json
import shutil
import re
import pandas as pd
from datetime import datetime
from pathlib import Path


TRIN_ROOT = Path(__file__).resolve().parents[1]
BASE = str(TRIN_ROOT / "TRIN_HISTORICO")
INDICES = os.path.join(BASE, "00_INDICES")
VERSOES = os.path.join(INDICES, "VERSOES")
RECUPERACAO = os.path.join(INDICES, "RECUPERACAO")

os.makedirs(INDICES, exist_ok=True)
os.makedirs(VERSOES, exist_ok=True)
os.makedirs(RECUPERACAO, exist_ok=True)

PASTAS_BIBLIOTECA_OFICIAL = {
    "001_1_MIN",
    "002_2_MIN",
    "003_3_MIN",
    "004_4_MIN",
    "005_5_MIN",
    "006_6_MIN",
    "007_7_MIN",
    "008_8_MIN",
    "009_9_MIN",
    "010_10_MIN",
    "012_12_MIN",
    "015_15_MIN",
    "020_20_MIN",
    "030_30_MIN",
    "045_45_MIN",
    "060_60_MIN",
    "090_90_MIN",
    "120_120_MIN",
    "180_180_MIN",
    "240_240_MIN",
    "M01_MENSAL",
    "S01_SEMANAL",
}

ARQ_INDICE = os.path.join(INDICES, "indice_geral.csv")
ARQ_WIN = os.path.join(INDICES, "indice_win.csv")
ARQ_WDO = os.path.join(INDICES, "indice_wdo.csv")
ARQ_INTEGRIDADE = os.path.join(INDICES, "relatorio_integridade.csv")
ARQ_STATUS = os.path.join(INDICES, "biblioteca_status.txt")
ARQ_LOG = os.path.join(INDICES, "log_bernardo.csv")
ARQ_DIAGNOSTICO = os.path.join(INDICES, "bernardo_diagnostico.txt")
ARQ_ALERTAS = os.path.join(INDICES, "central_alertas.csv")
ARQ_DUPLICADOS = os.path.join(INDICES, "hash_duplicados.csv")
ARQ_USO = os.path.join(INDICES, "memoria_uso.csv")
ARQ_TIMELINE = os.path.join(INDICES, "linha_do_tempo.csv")
ARQ_ESTATISTICAS = os.path.join(INDICES, "estatisticas_biblioteca.csv")
ARQ_HIGIENIZACAO = os.path.join(INDICES, "relatorio_higienizacao.csv")
ARQ_QUALIDADE = os.path.join(INDICES, "relatorio_qualidade.csv")
ARQ_MEMORIA_ESTATISTICA = os.path.join(INDICES, "relatorio_memoria_estatistica.csv")
ARQ_CURADORIA = os.path.join(INDICES, "relatorio_curadoria.csv")
ARQ_CONSULTA = os.path.join(INDICES, "relatorio_consulta.csv")
ARQ_INCREMENTAL = os.path.join(INDICES, "relatorio_atualizacao_incremental.csv")
ARQ_BANCO_REVERSOES = os.path.join(INDICES, "banco_reversoes.csv")
ARQ_RANKING_HISTORICO = os.path.join(INDICES, "ranking_historico.csv")
ARQ_FRAGMENTACAO_CONTEXTO = os.path.join(INDICES, "fragmentacao_contexto.csv")
ARQ_MEMORIA_CONTEXTO = os.path.join(INDICES, "memoria_contexto.csv")
ARQ_CATALOGO_PADROES = os.path.join(INDICES, "catalogo_padroes.csv")
ARQ_GRAFO_CONHECIMENTO = os.path.join(INDICES, "grafo_conhecimento.csv")
ARQ_IMPORTANCIA_ARQUIVOS = os.path.join(INDICES, "indice_importancia_arquivos.csv")
ARQ_CONFIANCA_MEMORIA = os.path.join(INDICES, "indice_confianca_memoria.csv")
ARQ_MEMORIA_HIERARQUICA = os.path.join(INDICES, "memoria_hierarquica.csv")
ARQ_RELACOES_FRACTAIS = os.path.join(INDICES, "relacoes_fractais.csv")
ARQ_DIAGNOSTICO_COGNITIVO = os.path.join(INDICES, "diagnostico_cognitivo.csv")
ARQ_GRAFO_ESTATISTICO = os.path.join(INDICES, "grafo_estatistico.csv")
ARQ_MEMORIA_ASSUNTO = os.path.join(INDICES, "memoria_por_assunto.csv")
ARQ_MEMORIA_EVENTO = os.path.join(INDICES, "memoria_por_evento.csv")
ARQ_REDE_SEMANTICA = os.path.join(INDICES, "rede_semantica.csv")
ARQ_BIBLIOTECA_CONCEITUAL = os.path.join(INDICES, "biblioteca_conceitual.csv")
ARQ_AUTOINSPECAO = os.path.join(INDICES, "autoinspecao_bernardo.csv")
ARQ_PACOTE_HISTORIADOR = os.path.join(INDICES, "pacote_historiador.csv")
ARQ_PACOTE_ZE_EUCRAZIO = os.path.join(INDICES, "pacote_ze_eucrazio.csv")
ARQ_MANIFESTO_PACOTE_ZE = os.path.join(
    INDICES,
    "manifesto_pacote_ze_bernardo.json",
)
ARQ_PACOTE_MOTOR_CONFLUENCIA = os.path.join(INDICES, "pacote_motor_confluencia.csv")

def md5_arquivo(caminho):
    h = hashlib.md5()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def sha256_arquivo(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def status_autoinspecao_pacote_ze():
    if not os.path.exists(ARQ_AUTOINSPECAO):
        return "NAO_AVALIADA"

    try:
        autoinspecao = pd.read_csv(
            ARQ_AUTOINSPECAO,
            sep=";",
            encoding="utf-8-sig",
            dtype=str,
            keep_default_na=False,
        )
    except Exception:
        return "ERRO_LEITURA_AUTOINSPECAO"

    if len(autoinspecao) == 0:
        return "NAO_AVALIADA"

    status = autoinspecao.get("status", pd.Series(dtype=str)).astype(str).str.upper()
    gravidade = autoinspecao.get("gravidade", pd.Series(dtype=str)).astype(str).str.upper()

    if status.isin({"ERRO", "REPROVADO", "BLOQUEADO"}).any():
        return "COM_PENDENCIAS"

    if gravidade.isin({"CRITICA", "ALTA"}).any():
        return "COM_PENDENCIAS"

    return "APROVADA"


def identificar_ativo(valor, arquivo):
    texto = f"{valor} {arquivo}".upper()
    if "WIN" in texto:
        return "WIN"
    if "WDO" in texto:
        return "WDO"
    return "DESCONHECIDO"


def identificar_fractal(pasta, arquivo):
    """
    Identifica o fractal dando prioridade ao nome do arquivo.

    Motivo:
    Um arquivo WIN_15min dentro de uma pasta 5_MIN não pode ser classificado
    como 5_MIN. Primeiro analisamos o arquivo; só depois usamos a pasta
    como fallback.

    Reconhece padrões:
    15min, 15_min, 15-min, 15 min, 15MIN, 15_MIN
    Diário, DIARIO, Semanal, SEMANAL, Mensal, MENSAL.
    """

    def normalizar(texto):
        texto = str(texto).upper()
        texto = texto.replace("Á", "A").replace("À", "A").replace("Â", "A").replace("Ã", "A")
        texto = texto.replace("É", "E").replace("Ê", "E")
        texto = texto.replace("Í", "I")
        texto = texto.replace("Ó", "O").replace("Ô", "O").replace("Õ", "O")
        texto = texto.replace("Ú", "U")
        texto = texto.replace("Ç", "C")
        return texto

    def detectar(texto):
        texto = normalizar(texto)

        if re.search(r"(?<![A-Z0-9])DIARI[O0](?![A-Z0-9])", texto):
            return "DIARIO"

        if re.search(r"(?<![A-Z0-9])SEMANAL(?![A-Z0-9])", texto):
            return "SEMANAL"

        if re.search(r"(?<![A-Z0-9])MENSAL(?![A-Z0-9])", texto):
            return "MENSAL"

        # Ordem decrescente evita confundir 15min com 5min.
        minutos_suportados = [
            240, 180, 120, 90, 60, 45, 30, 20, 15, 12,
            10, 9, 8, 7, 6, 5, 4, 3, 2, 1
        ]

        for minuto in minutos_suportados:
            padroes = [
                rf"(?<!\d){minuto}\s*_?\s*MIN(?!\d)",
                rf"(?<!\d){minuto}\s*-\s*MIN(?!\d)",
                rf"(?<!\d){minuto}\s*MINUTO[S]?(?!\d)",
            ]

            for padrao in padroes:
                if re.search(padrao, texto):
                    return f"{minuto}_MIN"

        return None

    fractal_arquivo = detectar(arquivo)
    if fractal_arquivo:
        return fractal_arquivo

    fractal_pasta = detectar(pasta)
    if fractal_pasta:
        return fractal_pasta

    return "DESCONHECIDO"


def origem_arquivo(caminho, arquivo):
    texto = f"{caminho} {arquivo}".upper()
    texto_normalizado = (
        texto.replace("_", "")
             .replace("-", "")
             .replace(" ", "")
             .replace("É", "E")
             .replace("Á", "A")
             .replace("Ç", "C")
    )

    if (
        "ZEDOEUCRAZIO" in texto_normalizado
        or "ZEDOEUCrazio".upper() in texto_normalizado
        or "ZE_DO_EUCRAZIO" in texto
        or re.search(r"(?<!\d)(2|3|4|6|7|8|9|12|20|45|90|120|180|240)\s*_?\s*MIN", texto)
    ):
        return "ZE_DO_EUCRAZIO"

    if "TRIN_MEMORIA" in texto or "MEMORIA" in texto:
        return "MEMORIA_VIVA"

    return "PROFIT"


def confiabilidade(origem, status):
    if status == "ERRO":
        return 0
    if status == "ALERTA":
        return 70
    if origem == "PROFIT":
        return 100
    if origem == "ZE_DO_EUCRAZIO":
        return 98
    if origem == "MEMORIA_VIVA":
        return 95
    return 80


def limpar_numero(valor):
    if pd.isna(valor):
        return None

    texto = str(valor).strip()
    texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except Exception:
        return None


def ler_datas(df):
    # ISO YYYY-MM-DD usa ano-mês-dia.
    # Formatos brasileiros permanecem day-first.
    # Datas anteriores a 2000 ou posteriores ao dia atual são rejeitadas.
    if df.shape[1] < 2:
        return "N/D", "N/D", "DATA_INVALIDA"

    valores = df.iloc[:, 1].astype(str).str.strip()
    mascara_iso = valores.str.match(
        r"^\d{4}-\d{2}-\d{2}(?:[ T]|$)",
        na=False,
    )

    datas_iso = pd.to_datetime(
        valores.where(mascara_iso),
        errors="coerce",
        yearfirst=True,
        format="mixed",
    )

    datas_br = pd.to_datetime(
        valores.where(~mascara_iso),
        errors="coerce",
        dayfirst=True,
        format="mixed",
    )

    datas = datas_iso.combine_first(datas_br).dropna()

    if len(datas) == 0:
        return "N/D", "N/D", "DATA_INVALIDA"

    limite_inferior = pd.Timestamp("2000-01-01")
    limite_superior = (
        pd.Timestamp(datetime.now().date())
        + pd.Timedelta(days=1)
        - pd.Timedelta(microseconds=1)
    )

    fora_da_janela = (
        (datas < limite_inferior)
        | (datas > limite_superior)
    )

    datas_validas = datas[~fora_da_janela]

    if len(datas_validas) == 0:
        return "N/D", "N/D", "DATA_INVALIDA"

    status = (
        "DATA_FORA_JANELA"
        if bool(fora_da_janela.any())
        else "OK"
    )

    return (
        datas_validas.min().strftime("%d/%m/%Y"),
        datas_validas.max().strftime("%d/%m/%Y"),
        status,
    )


def gerar_tags(ativo, fractal, origem, status, linhas):
    tags = [ativo, fractal, origem]

    if status != "OK":
        tags.append("ALERTA")

    if linhas > 100000:
        tags.append("ARQUIVO_GRANDE")

    if fractal in ["1_MIN", "2_MIN", "3_MIN"]:
        tags.append("MICRO_FRACTAL")

    if fractal in ["DIARIO", "SEMANAL", "MENSAL"]:
        tags.append("MACRO_FRACTAL")

    return ",".join([t for t in tags if t and t != "DESCONHECIDO"])


def estatisticas_basicas(df):
    resultado = {
        "volume_medio": "N/D",
        "range_medio": "N/D",
        "preco_medio": "N/D",
    }

    try:
        if df.shape[1] >= 8:
            maxima = df.iloc[:, 4].apply(limpar_numero)
            minima = df.iloc[:, 5].apply(limpar_numero)
            ultimo = df.iloc[:, 6].apply(limpar_numero)
            volume = df.iloc[:, 7].apply(limpar_numero)

            resultado["volume_medio"] = round(volume.dropna().mean(), 2)
            resultado["range_medio"] = round((maxima - minima).dropna().mean(), 2)
            resultado["preco_medio"] = round(ultimo.dropna().mean(), 2)

    except Exception:
        pass

    return resultado


def backup_indice():
    if os.path.exists(ARQ_INDICE):
        agora = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = os.path.join(VERSOES, f"indice_geral_{agora}.csv")
        shutil.copy2(ARQ_INDICE, destino)


def backup_recuperacao():
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    pasta_backup = os.path.join(RECUPERACAO, f"backup_{agora}")

    os.makedirs(pasta_backup, exist_ok=True)

    arquivos_protegidos = [
        ARQ_INDICE,
        ARQ_WIN,
        ARQ_WDO,
        ARQ_INTEGRIDADE,
        ARQ_STATUS,
        ARQ_DIAGNOSTICO,
        ARQ_ALERTAS,
        ARQ_DUPLICADOS,
        ARQ_USO,
        ARQ_TIMELINE,
        ARQ_ESTATISTICAS,
        ARQ_HIGIENIZACAO,
        ARQ_QUALIDADE,
        ARQ_MEMORIA_ESTATISTICA,
        ARQ_CURADORIA,
        ARQ_CONSULTA,
        ARQ_INCREMENTAL,
        ARQ_BANCO_REVERSOES,
        ARQ_RANKING_HISTORICO,
        ARQ_FRAGMENTACAO_CONTEXTO,
        ARQ_MEMORIA_CONTEXTO,
        ARQ_CATALOGO_PADROES,
        ARQ_GRAFO_CONHECIMENTO,
        ARQ_IMPORTANCIA_ARQUIVOS,
        ARQ_CONFIANCA_MEMORIA,
        ARQ_MEMORIA_HIERARQUICA,
        ARQ_RELACOES_FRACTAIS,
        ARQ_DIAGNOSTICO_COGNITIVO,
        ARQ_GRAFO_ESTATISTICO,
        ARQ_MEMORIA_ASSUNTO,
        ARQ_MEMORIA_EVENTO,
        ARQ_REDE_SEMANTICA,
        ARQ_BIBLIOTECA_CONCEITUAL,
        ARQ_AUTOINSPECAO,
        ARQ_PACOTE_HISTORIADOR,
        ARQ_PACOTE_ZE_EUCRAZIO,
        ARQ_PACOTE_MOTOR_CONFLUENCIA,
        ARQ_LOG,
    ]

    copiados = 0

    for arquivo in arquivos_protegidos:
        if os.path.exists(arquivo):
            destino = os.path.join(pasta_backup, os.path.basename(arquivo))
            shutil.copy2(arquivo, destino)
            copiados += 1

    return pasta_backup, copiados


def carregar_indice_anterior():
    if not os.path.exists(ARQ_INDICE):
        return pd.DataFrame()

    try:
        return pd.read_csv(ARQ_INDICE, sep=";", encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame()

def registrar_timeline(eventos):
    if not eventos:
        return

    df = pd.DataFrame(eventos)

    if os.path.exists(ARQ_TIMELINE):
        df.to_csv(ARQ_TIMELINE, sep=";", index=False, header=False, mode="a", encoding="utf-8-sig")
    else:
        df.to_csv(ARQ_TIMELINE, sep=";", index=False, encoding="utf-8-sig")


def registrar_log(arquivos, alertas, erros):
    linha = pd.DataFrame([{
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "acao": "ATUALIZAR_BIBLIOTECA",
        "arquivos": arquivos,
        "alertas": alertas,
        "erros": erros,
        "resultado": "OK" if erros == 0 else "ERRO"
    }])

    if os.path.exists(ARQ_LOG):
        linha.to_csv(ARQ_LOG, sep=";", index=False, header=False, mode="a", encoding="utf-8-sig")
    else:
        linha.to_csv(ARQ_LOG, sep=";", index=False, encoding="utf-8-sig")


def processar_arquivo(pasta, raiz, arquivo):
    caminho = os.path.join(raiz, arquivo)
    stat = os.stat(caminho)

    registro = {
        "id": "",
        "ativo": "DESCONHECIDO",
        "ativo_original": "N/D",
        "fractal": identificar_fractal(pasta, arquivo),
        "pasta": pasta,
        "arquivo": arquivo,
        "caminho": caminho,
        "linhas": 0,
        "colunas": 0,
        "data_inicio": "N/D",
        "data_fim": "N/D",
        "tamanho_mb": round(stat.st_size / (1024 * 1024), 3),
        "ultima_modificacao": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S"),
        "hash_md5": "",
        "origem": origem_arquivo(caminho, arquivo),
        "confiabilidade": 0,
        "tags": "",
        "volume_medio": "N/D",
        "range_medio": "N/D",
        "preco_medio": "N/D",
        "status": "OK",
        "observacao": "",
    }

    observacoes = []

    try:
        registro["hash_md5"] = md5_arquivo(caminho)

        df = pd.read_csv(caminho, sep=";", header=None, engine="python")

        registro["linhas"] = len(df)
        registro["colunas"] = df.shape[1]

        if len(df) == 0:
            observacoes.append("ARQUIVO_VAZIO")

        if df.shape[1] < 3:
            observacoes.append("COLUNA_INSUFICIENTE")

        if len(df) > 0 and df.shape[1] >= 1:
            registro["ativo_original"] = str(df.iloc[0, 0])
            registro["ativo"] = identificar_ativo(registro["ativo_original"], arquivo)

        data_inicio, data_fim, status_data = ler_datas(df)
        registro["data_inicio"] = data_inicio
        registro["data_fim"] = data_fim

        if status_data != "OK":
            observacoes.append(status_data)

        if registro["ativo"] == "DESCONHECIDO":
            observacoes.append("ATIVO_DESCONHECIDO")

        if registro["fractal"] == "DESCONHECIDO":
            observacoes.append("FRACTAL_DESCONHECIDO")

        est = estatisticas_basicas(df)
        registro.update(est)

        if observacoes:
            registro["status"] = "ALERTA"
            registro["observacao"] = " | ".join(observacoes)

        registro["confiabilidade"] = confiabilidade(registro["origem"], registro["status"])
        registro["tags"] = gerar_tags(
            registro["ativo"],
            registro["fractal"],
            registro["origem"],
            registro["status"],
            registro["linhas"]
        )

        registro["id"] = f"{registro['ativo']}_{registro['fractal']}_{arquivo}"

        return registro

    except Exception as erro:
        registro["status"] = "ERRO"
        registro["observacao"] = str(erro)
        registro["confiabilidade"] = 0
        registro["id"] = f"ERRO_{arquivo}"
        return registro


def atualizar_memoria_uso(indice):
    if os.path.exists(ARQ_USO):
        uso = pd.read_csv(ARQ_USO, sep=";", encoding="utf-8-sig")
    else:
        uso = pd.DataFrame(columns=[
            "arquivo",
            "consultas",
            "ultimo_acesso"
        ])

    arquivos_existentes = set(uso["arquivo"].astype(str))
    novos = []

    for arquivo in indice["arquivo"]:
        if arquivo not in arquivos_existentes:
            novos.append({
                "arquivo": arquivo,
                "consultas": 0,
                "ultimo_acesso": "N/D"
            })

    if novos:
        uso = pd.concat([uso, pd.DataFrame(novos)], ignore_index=True)

    uso.to_csv(ARQ_USO, sep=";", index=False, encoding="utf-8-sig")


def gerar_status(indice):
    total = len(indice)
    linhas = int(indice["linhas"].sum()) if total else 0
    win = len(indice[indice["ativo"] == "WIN"])
    wdo = len(indice[indice["ativo"] == "WDO"])
    alertas = len(indice[indice["status"] == "ALERTA"])
    erros = len(indice[indice["status"] == "ERRO"])

    datas_i = pd.to_datetime(indice["data_inicio"], dayfirst=True, errors="coerce").dropna()
    datas_f = pd.to_datetime(indice["data_fim"], dayfirst=True, errors="coerce").dropna()

    data_inicio = datas_i.min().strftime("%d/%m/%Y") if len(datas_i) else "N/D"
    data_fim = datas_f.max().strftime("%d/%m/%Y") if len(datas_f) else "N/D"

    fractais = ", ".join(sorted(indice["fractal"].dropna().unique()))

    integridade = 0
    if total:
        integridade = round(((total - alertas - erros) / total) * 100, 2)

    maior = indice.sort_values("tamanho_mb", ascending=False).head(1)
    menor = indice.sort_values("tamanho_mb", ascending=True).head(1)

    maior_txt = maior["arquivo"].iloc[0] if len(maior) else "N/D"
    menor_txt = menor["arquivo"].iloc[0] if len(menor) else "N/D"

    texto = f"""
============================================================
BIBLIOTECA HISTORICA TRIN - BERNARDO v4.0
============================================================
Arquivos ............... {total}
Registros .............. {linhas}
WIN .................... {win}
WDO .................... {wdo}
Fractais ............... {fractais}
Data inicial ........... {data_inicio}
Data final ............. {data_fim}
Maior arquivo .......... {maior_txt}
Menor arquivo .......... {menor_txt}
Alertas ................ {alertas}
Erros .................. {erros}
Integridade ............ {integridade}%
Ultima atualizacao ..... {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
============================================================
"""

    with open(ARQ_STATUS, "w", encoding="utf-8") as f:
        f.write(texto)

    with open(ARQ_DIAGNOSTICO, "w", encoding="utf-8") as f:
        f.write(texto)
        f.write("\nBiblioteca pronta para IA: ")
        f.write("SIM" if erros == 0 else "NAO")

    return texto


def detectar_duplicados(indice):
    duplicados = indice[indice.duplicated("hash_md5", keep=False)]
    duplicados.to_csv(ARQ_DUPLICADOS, sep=";", index=False, encoding="utf-8-sig")

def detectar_eventos(indice_anterior, indice_novo):
    eventos = []
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    colunas_necessarias = ["arquivo", "hash_md5"]
 
    if (
        len(indice_anterior) == 0
        or any(coluna not in indice_anterior.columns for coluna in colunas_necessarias)
    ):
        for _, linha in indice_novo.iterrows():
            eventos.append({
                "data_hora": agora,
                "evento": "ARQUIVO_INDEXADO",
                "arquivo": linha["arquivo"],
                "detalhe": "Primeira indexacao ou indice anterior incompativel"
            })
        return eventos

    antigo = dict(zip(indice_anterior["arquivo"], indice_anterior["hash_md5"]))
    novo = dict(zip(indice_novo["arquivo"], indice_novo["hash_md5"]))

    for arquivo, h in novo.items():
        if arquivo not in antigo:
            eventos.append({
                "data_hora": agora,
                "evento": "NOVO_ARQUIVO",
                "arquivo": arquivo,
                "detalhe": "Arquivo novo detectado"
            })
        elif antigo[arquivo] != h:
            eventos.append({
                "data_hora": agora,
                "evento": "ARQUIVO_ALTERADO",
                "arquivo": arquivo,
                "detalhe": "Hash alterado"
            })

    for arquivo in antigo:
        if arquivo not in novo:
            eventos.append({
                "data_hora": agora,
                "evento": "ARQUIVO_REMOVIDO",
                "arquivo": arquivo,
                "detalhe": "Arquivo nao encontrado nesta execucao"
            })

    return eventos


def gerar_relatorio_higienizacao(indice):
    problemas = []

    for _, linha in indice.iterrows():
        arquivo = str(linha.get("arquivo", ""))
        ativo = str(linha.get("ativo", ""))
        fractal = str(linha.get("fractal", ""))
        status = str(linha.get("status", ""))
        observacao = str(linha.get("observacao", ""))
        linhas = int(linha.get("linhas", 0))
        colunas = int(linha.get("colunas", 0))
        hash_md5 = str(linha.get("hash_md5", ""))

        if ativo == "DESCONHECIDO":
            problemas.append({
                "arquivo": arquivo,
                "tipo_problema": "ATIVO_DESCONHECIDO",
                "gravidade": "MEDIA",
                "detalhe": observacao
            })

        if fractal == "DESCONHECIDO":
            problemas.append({
                "arquivo": arquivo,
                "tipo_problema": "FRACTAL_DESCONHECIDO",
                "gravidade": "MEDIA",
                "detalhe": observacao
            })

        if linhas == 0:
            problemas.append({
                "arquivo": arquivo,
                "tipo_problema": "ARQUIVO_VAZIO",
                "gravidade": "ALTA",
                "detalhe": "Arquivo sem registros"
            })

        if colunas < 3:
            problemas.append({
                "arquivo": arquivo,
                "tipo_problema": "COLUNAS_INSUFICIENTES",
                "gravidade": "ALTA",
                "detalhe": f"Arquivo possui apenas {colunas} colunas"
            })

        if status != "OK":
            problemas.append({
                "arquivo": arquivo,
                "tipo_problema": "STATUS_NAO_OK",
                "gravidade": "MEDIA",
                "detalhe": observacao
            })

        nome_upper = arquivo.upper()

        if not ("WIN" in nome_upper or "WDO" in nome_upper):
            problemas.append({
                "arquivo": arquivo,
                "tipo_problema": "NOME_FORA_PADRAO_ATIVO",
                "gravidade": "BAIXA",
                "detalhe": "Nome nao contem WIN ou WDO"
            })

        if hash_md5 in ["", "N/D", "nan"]:
            problemas.append({
                "arquivo": arquivo,
                "tipo_problema": "HASH_AUSENTE",
                "gravidade": "ALTA",
                "detalhe": "Arquivo sem hash valido"
            })

    duplicados = indice[
        indice["hash_md5"].astype(str).ne("") &
        indice.duplicated("hash_md5", keep=False)
    ]

    for _, linha in duplicados.iterrows():
        problemas.append({
            "arquivo": linha["arquivo"],
            "tipo_problema": "HASH_DUPLICADO",
            "gravidade": "MEDIA",
            "detalhe": f"Hash duplicado: {linha['hash_md5']}"
        })

    df = pd.DataFrame(problemas)

    if len(df) == 0:
        df = pd.DataFrame([{
            "arquivo": "N/D",
            "tipo_problema": "NENHUM_PROBLEMA_ENCONTRADO",
            "gravidade": "OK",
            "detalhe": "Biblioteca higienizada sem ocorrencias"
        }])

    df.to_csv(ARQ_HIGIENIZACAO, sep=";", index=False, encoding="utf-8-sig")

    return df


def gerar_metricas_qualidade(indice):
    metricas = []

    for _, linha in indice.iterrows():
        arquivo = str(linha.get("arquivo", ""))
        ativo = str(linha.get("ativo", ""))
        fractal = str(linha.get("fractal", ""))
        status = str(linha.get("status", ""))
        linhas = int(linha.get("linhas", 0))
        colunas = int(linha.get("colunas", 0))
        hash_md5 = str(linha.get("hash_md5", ""))
        data_inicio = str(linha.get("data_inicio", "N/D"))
        data_fim = str(linha.get("data_fim", "N/D"))

        nota = 100
        motivos = []

        if status == "ERRO":
            nota -= 100
            motivos.append("ERRO_NO_ARQUIVO")

        if status == "ALERTA":
            nota -= 25
            motivos.append("STATUS_ALERTA")

        if ativo == "DESCONHECIDO":
            nota -= 20
            motivos.append("ATIVO_DESCONHECIDO")

        if fractal == "DESCONHECIDO":
            nota -= 20
            motivos.append("FRACTAL_DESCONHECIDO")

        if linhas == 0:
            nota -= 40
            motivos.append("ARQUIVO_VAZIO")

        if colunas < 3:
            nota -= 30
            motivos.append("COLUNAS_INSUFICIENTES")

        if hash_md5 in ["", "N/D", "nan"]:
            nota -= 25
            motivos.append("HASH_AUSENTE")

        if data_inicio == "N/D" or data_fim == "N/D":
            nota -= 15
            motivos.append("DATA_INVALIDA")

        if nota < 0:
            nota = 0

        if nota >= 95:
            classificacao = "EXCELENTE"
        elif nota >= 85:
            classificacao = "BOA"
        elif nota >= 70:
            classificacao = "REGULAR"
        elif nota >= 50:
            classificacao = "FRACA"
        else:
            classificacao = "CRITICA"

        metricas.append({
            "arquivo": arquivo,
            "ativo": ativo,
            "fractal": fractal,
            "nota_qualidade": nota,
            "classificacao": classificacao,
            "linhas": linhas,
            "colunas": colunas,
            "status": status,
            "motivos": " | ".join(motivos) if motivos else "OK"
        })

    df = pd.DataFrame(metricas)
    df.to_csv(ARQ_QUALIDADE, sep=";", index=False, encoding="utf-8-sig")

    return df

def gerar_memoria_estatistica(indice):
    estatisticas = []

    grupos = indice.groupby(["ativo", "fractal"])

    for (ativo, fractal), grupo in grupos:
        total_arquivos = len(grupo)
        total_linhas = int(grupo["linhas"].sum())
        tamanho_total_mb = round(grupo["tamanho_mb"].sum(), 3)

        qualidade_media = "N/D"
        if "nota_qualidade" in grupo.columns:
            qualidade_media = round(grupo["nota_qualidade"].mean(), 2)

        data_inicio = pd.to_datetime(
            grupo["data_inicio"],
            dayfirst=True,
            errors="coerce"
        ).dropna()

        data_fim = pd.to_datetime(
            grupo["data_fim"],
            dayfirst=True,
            errors="coerce"
        ).dropna()

        menor_data = data_inicio.min().strftime("%d/%m/%Y") if len(data_inicio) else "N/D"
        maior_data = data_fim.max().strftime("%d/%m/%Y") if len(data_fim) else "N/D"

        volume_medio = pd.to_numeric(
            grupo["volume_medio"],
            errors="coerce"
        ).dropna()

        range_medio = pd.to_numeric(
            grupo["range_medio"],
            errors="coerce"
        ).dropna()

        preco_medio = pd.to_numeric(
            grupo["preco_medio"],
            errors="coerce"
        ).dropna()

        estatisticas.append({
            "ativo": ativo,
            "fractal": fractal,
            "total_arquivos": total_arquivos,
            "total_linhas": total_linhas,
            "tamanho_total_mb": tamanho_total_mb,
            "menor_data": menor_data,
            "maior_data": maior_data,
            "volume_medio_geral": round(volume_medio.mean(), 2) if len(volume_medio) else "N/D",
            "range_medio_geral": round(range_medio.mean(), 2) if len(range_medio) else "N/D",
            "preco_medio_geral": round(preco_medio.mean(), 2) if len(preco_medio) else "N/D",
            "qualidade_media": qualidade_media
        })

    df = pd.DataFrame(estatisticas)
    df.to_csv(ARQ_MEMORIA_ESTATISTICA, sep=";", index=False, encoding="utf-8-sig")

    return df
def gerar_curadoria_automatica(indice, relatorio_higienizacao, relatorio_qualidade, relatorio_memoria_estatistica):
    pareceres = []

    total_arquivos = len(indice)
    total_alertas = len(indice[indice["status"] == "ALERTA"])
    total_erros = len(indice[indice["status"] == "ERRO"])

    qualidade_excelente = 0
    if "classificacao" in relatorio_qualidade.columns:
        qualidade_excelente = len(relatorio_qualidade[relatorio_qualidade["classificacao"] == "EXCELENTE"])

    problemas_higienizacao = 0
    if "gravidade" in relatorio_higienizacao.columns:
        problemas_higienizacao = len(relatorio_higienizacao[relatorio_higienizacao["gravidade"] != "OK"])

    fractais_esperados = {
        "1_MIN", "2_MIN", "3_MIN", "5_MIN", "10_MIN", "15_MIN",
        "30_MIN", "60_MIN", "DIARIO", "SEMANAL"
    }

    fractais_existentes = set(indice["fractal"].dropna().unique())
    fractais_ausentes = sorted(fractais_esperados - fractais_existentes)

    ativos_existentes = set(indice["ativo"].dropna().unique())
    ativos_ausentes = []

    for ativo in ["WIN", "WDO"]:
        if ativo not in ativos_existentes:
            ativos_ausentes.append(ativo)

    if total_erros == 0 and total_alertas == 0:
        status_biblioteca = "SAUDAVEL"
        recomendacao_geral = "Nenhuma acao critica necessaria"
    elif total_erros == 0:
        status_biblioteca = "ATENCAO"
        recomendacao_geral = "Revisar alertas e higienizacao"
    else:
        status_biblioteca = "CRITICA"
        recomendacao_geral = "Corrigir erros antes de usar para inteligencia"

    pareceres.append({
        "item": "STATUS_BIBLIOTECA",
        "situacao": status_biblioteca,
        "detalhe": recomendacao_geral
    })

    pareceres.append({
        "item": "TOTAL_ARQUIVOS",
        "situacao": total_arquivos,
        "detalhe": "Total de arquivos catalogados"
    })

    pareceres.append({
        "item": "ALERTAS",
        "situacao": total_alertas,
        "detalhe": "Quantidade de arquivos em alerta"
    })

    pareceres.append({
        "item": "ERROS",
        "situacao": total_erros,
        "detalhe": "Quantidade de arquivos com erro"
    })

    pareceres.append({
        "item": "QUALIDADE_EXCELENTE",
        "situacao": qualidade_excelente,
        "detalhe": "Arquivos classificados como EXCELENTE"
    })

    pareceres.append({
        "item": "PROBLEMAS_HIGIENIZACAO",
        "situacao": problemas_higienizacao,
        "detalhe": "Ocorrencias encontradas na higienizacao"
    })

    pareceres.append({
        "item": "FRACTAIS_AUSENTES",
        "situacao": ", ".join(fractais_ausentes) if fractais_ausentes else "NENHUM",
        "detalhe": "Fractais esperados ainda nao encontrados"
    })

    pareceres.append({
        "item": "ATIVOS_AUSENTES",
        "situacao": ", ".join(ativos_ausentes) if ativos_ausentes else "NENHUM",
        "detalhe": "Ativos esperados ainda nao encontrados"
    })

    for _, linha in relatorio_memoria_estatistica.iterrows():
        pareceres.append({
            "item": f"COBERTURA_{linha['ativo']}_{linha['fractal']}",
            "situacao": f"{linha['total_arquivos']} arquivos / {linha['total_linhas']} linhas",
            "detalhe": "Cobertura estatistica por ativo e fractal"
        })

    df = pd.DataFrame(pareceres)
    df.to_csv(ARQ_CURADORIA, sep=";", index=False, encoding="utf-8-sig")

    return df


def montar_tabela_consulta(indice, relatorio_qualidade):
    tabela = indice.copy()

    colunas_qualidade = [
        "arquivo",
        "nota_qualidade",
        "classificacao",
        "motivos"
    ]

    if all(coluna in relatorio_qualidade.columns for coluna in colunas_qualidade):
        tabela = tabela.merge(
            relatorio_qualidade[colunas_qualidade],
            on="arquivo",
            how="left"
        )

    colunas_base = [
        "arquivo",
        "ativo",
        "fractal",
        "data_inicio",
        "data_fim",
        "linhas",
        "colunas",
        "status",
        "confiabilidade",
        "nota_qualidade",
        "classificacao",
        "tags",
        "origem",
        "caminho",
    ]

    colunas_existentes = [coluna for coluna in colunas_base if coluna in tabela.columns]
    tabela = tabela[colunas_existentes]

    tabela.to_csv(ARQ_CONSULTA, sep=";", index=False, encoding="utf-8-sig")

    return tabela


def consultar_biblioteca(
    tabela_consulta,
    ativo=None,
    fractal=None,
    status=None,
    classificacao=None,
    texto=None,
    minimo_linhas=None
):
    resultado = tabela_consulta.copy()

    if ativo:
        resultado = resultado[resultado["ativo"].astype(str).str.upper() == str(ativo).upper()]

    if fractal:
        resultado = resultado[resultado["fractal"].astype(str).str.upper() == str(fractal).upper()]

    if status:
        resultado = resultado[resultado["status"].astype(str).str.upper() == str(status).upper()]

    if classificacao and "classificacao" in resultado.columns:
        resultado = resultado[resultado["classificacao"].astype(str).str.upper() == str(classificacao).upper()]

    if texto:
        termo = str(texto).upper()
        mascara = resultado.apply(
            lambda linha: termo in " ".join(linha.astype(str)).upper(),
            axis=1
        )
        resultado = resultado[mascara]

    if minimo_linhas is not None and "linhas" in resultado.columns:
        resultado = resultado[pd.to_numeric(resultado["linhas"], errors="coerce") >= minimo_linhas]

    return resultado



# ============================================================
# MODULO 10 - ATUALIZACAO INCREMENTAL
# ============================================================

def gerar_atualizacao_incremental(indice_anterior, indice_novo):
    eventos = []
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if indice_novo is None or len(indice_novo) == 0:
        df = pd.DataFrame([{
            "data_hora": agora,
            "evento": "SEM_INDICE_NOVO",
            "arquivo": "N/D",
            "detalhe": "Nenhum arquivo novo foi catalogado nesta execucao",
            "acao_recomendada": "Verificar caminho da biblioteca"
        }])
        df.to_csv(ARQ_INCREMENTAL, sep=";", index=False, encoding="utf-8-sig")
        return df

    colunas_necessarias = {"arquivo", "hash_md5"}

    if (
        indice_anterior is None
        or len(indice_anterior) == 0
        or not colunas_necessarias.issubset(set(indice_anterior.columns))
    ):
        for _, linha in indice_novo.iterrows():
            eventos.append({
                "data_hora": agora,
                "evento": "INDEXACAO_INICIAL",
                "arquivo": linha.get("arquivo", "N/D"),
                "detalhe": "Indice anterior ausente ou incompativel",
                "acao_recomendada": "Manter arquivo no indice oficial"
            })
    else:
        antigo = dict(zip(indice_anterior["arquivo"].astype(str), indice_anterior["hash_md5"].astype(str)))
        novo = dict(zip(indice_novo["arquivo"].astype(str), indice_novo["hash_md5"].astype(str)))

        for arquivo, hash_atual in novo.items():
            if arquivo not in antigo:
                eventos.append({
                    "data_hora": agora,
                    "evento": "NOVO_ARQUIVO",
                    "arquivo": arquivo,
                    "detalhe": "Arquivo novo encontrado na biblioteca",
                    "acao_recomendada": "Indexar e incluir na memoria estatistica"
                })
            elif antigo[arquivo] != hash_atual:
                eventos.append({
                    "data_hora": agora,
                    "evento": "ARQUIVO_ALTERADO",
                    "arquivo": arquivo,
                    "detalhe": "Hash diferente do indice anterior",
                    "acao_recomendada": "Revalidar integridade e qualidade"
                })
            else:
                eventos.append({
                    "data_hora": agora,
                    "evento": "INALTERADO",
                    "arquivo": arquivo,
                    "detalhe": "Arquivo sem alteracao detectada",
                    "acao_recomendada": "Nenhuma acao necessaria"
                })

        for arquivo in antigo:
            if arquivo not in novo:
                eventos.append({
                    "data_hora": agora,
                    "evento": "ARQUIVO_REMOVIDO",
                    "arquivo": arquivo,
                    "detalhe": "Arquivo existia no indice anterior e nao foi encontrado agora",
                    "acao_recomendada": "Conferir se foi movido, renomeado ou apagado"
                })

    df = pd.DataFrame(eventos)
    df.to_csv(ARQ_INCREMENTAL, sep=";", index=False, encoding="utf-8-sig")
    return df


# ============================================================
# MODULO 23 - BANCO DE REVERSOES
# ============================================================

def gerar_banco_reversoes(indice, relatorio_qualidade):
    base = indice.copy()

    if "classificacao" not in base.columns and "arquivo" in relatorio_qualidade.columns:
        base = base.merge(
            relatorio_qualidade[["arquivo", "nota_qualidade", "classificacao"]],
            on="arquivo",
            how="left"
        )

    registros = []

    prioridade_por_fractal = {
        "1_MIN": 5,
        "2_MIN": 5,
        "3_MIN": 5,
        "5_MIN": 4,
        "10_MIN": 4,
        "15_MIN": 3,
        "30_MIN": 3,
        "60_MIN": 2,
        "DIARIO": 1,
        "SEMANAL": 1,
        "MENSAL": 1,
    }

    for _, linha in base.iterrows():
        fractal = str(linha.get("fractal", "DESCONHECIDO"))
        linhas = int(linha.get("linhas", 0))
        qualidade = str(linha.get("classificacao", "N/D"))
        prioridade = prioridade_por_fractal.get(fractal, 0)

        if linhas >= 1000 and linha.get("status", "") == "OK":
            elegivel = "SIM"
        else:
            elegivel = "NAO"

        registros.append({
            "codigo_fonte": f"REV_SRC_{len(registros)+1:05d}",
            "arquivo": linha.get("arquivo", "N/D"),
            "ativo": linha.get("ativo", "N/D"),
            "fractal": fractal,
            "data_inicio": linha.get("data_inicio", "N/D"),
            "data_fim": linha.get("data_fim", "N/D"),
            "linhas": linhas,
            "qualidade": qualidade,
            "prioridade_mineracao": prioridade,
            "elegivel_para_historiador": elegivel,
            "observacao": "Fonte catalogada para futura mineracao de reversoes"
        })

    df = pd.DataFrame(registros)
    df.to_csv(ARQ_BANCO_REVERSOES, sep=";", index=False, encoding="utf-8-sig")
    return df


# ============================================================
# MODULO 24 - RANKING HISTORICO
# ============================================================

def gerar_ranking_historico(indice, relatorio_qualidade, relatorio_memoria_estatistica):
    base = relatorio_memoria_estatistica.copy()

    qualidade_por_grupo = relatorio_qualidade.groupby(["ativo", "fractal"]).agg({
        "nota_qualidade": "mean",
        "arquivo": "count"
    }).reset_index() if len(relatorio_qualidade) else pd.DataFrame()

    if len(qualidade_por_grupo):
        qualidade_por_grupo = qualidade_por_grupo.rename(columns={
            "nota_qualidade": "nota_qualidade_media",
            "arquivo": "arquivos_com_qualidade"
        })
        base = base.merge(qualidade_por_grupo, on=["ativo", "fractal"], how="left")

    if "nota_qualidade_media" not in base.columns:
        base["nota_qualidade_media"] = 0

    base["score_historico"] = (
        pd.to_numeric(base["total_arquivos"], errors="coerce").fillna(0) * 2
        + pd.to_numeric(base["total_linhas"], errors="coerce").fillna(0).apply(lambda v: min(v / 10000, 50))
        + pd.to_numeric(base["nota_qualidade_media"], errors="coerce").fillna(0)
    ).round(2)

    base = base.sort_values("score_historico", ascending=False).reset_index(drop=True)
    base.insert(0, "ranking", range(1, len(base) + 1))
    base.to_csv(ARQ_RANKING_HISTORICO, sep=";", index=False, encoding="utf-8-sig")
    return base


# ============================================================
# MODULO 25 - FRAGMENTACAO DE CONTEXTO
# ============================================================

def gerar_fragmentacao_contexto(indice):
    contextos = []
    mapa_contexto = [
        ("ABERTURA", "09:00", "10:30", "Inicio do pregao e maior disputa de fluxo"),
        ("MEIO_PREGAO", "10:31", "15:30", "Periodo de desenvolvimento do movimento"),
        ("FECHAMENTO", "15:31", "18:00", "Ajustes finais e zeragens"),
        ("ALTA_VOLATILIDADE", "N/D", "N/D", "Contexto marcado por range e volume acima da media"),
        ("BAIXA_VOLATILIDADE", "N/D", "N/D", "Contexto marcado por compressao e baixa amplitude"),
    ]

    grupos = indice.groupby(["ativo", "fractal"]).agg({
        "arquivo": "count",
        "linhas": "sum"
    }).reset_index()

    for _, grupo in grupos.iterrows():
        for nome, inicio, fim, detalhe in mapa_contexto:
            contextos.append({
                "ativo": grupo["ativo"],
                "fractal": grupo["fractal"],
                "contexto": nome,
                "hora_inicio": inicio,
                "hora_fim": fim,
                "arquivos_base": int(grupo["arquivo"]),
                "linhas_base": int(grupo["linhas"]),
                "detalhe": detalhe,
                "status": "PREPARADO_PARA_HISTORIADOR"
            })

    df = pd.DataFrame(contextos)
    df.to_csv(ARQ_FRAGMENTACAO_CONTEXTO, sep=";", index=False, encoding="utf-8-sig")
    return df


# ============================================================
# MODULO 27 - MEMORIA DE CONTEXTO
# ============================================================

def gerar_memoria_contexto(indice):
    eventos = [
        ("COPOM", "Evento de politica monetaria; pode alterar volatilidade e direcao"),
        ("PAYROLL", "Dado de emprego americano; pode afetar dolar, indice e fluxo externo"),
        ("VENCIMENTO", "Vencimento de contrato; pode distorcer volume e rolagem"),
        ("ROLAGEM", "Periodo de transicao de contrato; exige cuidado com historico"),
        ("FERIADO", "Liquidez atipica e menor confiabilidade estatistica"),
        ("ABERTURA_EUA", "Abertura do mercado americano; pode mudar regime de fluxo"),
        ("NOTICIA_RELEVANTE", "Evento extraordinario; contexto deve ser marcado manualmente"),
    ]

    ativos = sorted([a for a in indice["ativo"].dropna().unique() if a != "DESCONHECIDO"])
    registros = []

    for ativo in ativos:
        for evento, detalhe in eventos:
            registros.append({
                "ativo": ativo,
                "contexto": evento,
                "tipo": "MACRO_EVENTO",
                "impacto_esperado": "ALTO" if evento in ["COPOM", "PAYROLL", "VENCIMENTO"] else "MEDIO",
                "detalhe": detalhe,
                "acao": "Marcar no calendario operacional quando ocorrer",
                "status": "CATALOGADO"
            })

    df = pd.DataFrame(registros)
    df.to_csv(ARQ_MEMORIA_CONTEXTO, sep=";", index=False, encoding="utf-8-sig")
    return df


# ============================================================
# MODULO 35 - CATALOGO OFICIAL DE PADROES
# ============================================================

def gerar_catalogo_padroes():
    padroes = [
        ("R001", "REVERSAO_VWAP", "Reversao proxima da VWAP com perda de agressao contraria"),
        ("R002", "REVERSAO_EXTREMO", "Reversao apos afastamento excessivo da media"),
        ("R003", "FALSO_ROMPIMENTO", "Rompimento sem sustentacao e retorno para dentro da regiao"),
        ("R004", "ABSORCAO_COMPRADORA", "Agressao vendedora absorvida sem continuidade de queda"),
        ("R005", "ABSORCAO_VENDEDORA", "Agressao compradora absorvida sem continuidade de alta"),
        ("R006", "EXAUSTAO_COMPRA", "Compra agressiva perde eficiencia perto de resistencia"),
        ("R007", "EXAUSTAO_VENDA", "Venda agressiva perde eficiencia perto de suporte"),
        ("R008", "ROMPIMENTO_COM_FLUXO", "Rompimento acompanhado por delta, volume e saldo favoraveis"),
        ("R009", "COMPRESSAO_PRE_EXPLOSAO", "Reducao de range antes de expansao direcional"),
        ("R010", "PULLBACK_INSTITUCIONAL", "Reteste de regiao rompida com defesa de fluxo"),
        ("S001", "SCALPING_EXPLOSAO", "Movimento curto de forte aceleracao e alta frequencia"),
        ("S002", "SCALPING_REJEICAO", "Rejeicao rapida em nivel historico ou VWAP"),
        ("C001", "CONTEXTO_ABERTURA", "Padrao exclusivo de abertura do pregao"),
        ("C002", "CONTEXTO_FECHAMENTO", "Padrao exclusivo de fechamento ou zeragem"),
    ]

    df = pd.DataFrame([
        {
            "codigo": codigo,
            "nome": nome,
            "descricao": descricao,
            "familia": codigo[0],
            "categoria": (
                "REVERSAO" if codigo.startswith("R")
                else "SCALPING" if codigo.startswith("S")
                else "CONTEXTO"
            ),
            "status": "CATALOGADO",
            "origem": "BERNARDO_v4_0"
        }
        for codigo, nome, descricao in padroes
    ])

    df.to_csv(ARQ_CATALOGO_PADROES, sep=";", index=False, encoding="utf-8-sig")
    return df



# ============================================================
# MODULO 41 - GRAFO DE CONHECIMENTO
# MODULO 42 - INDICE DE IMPORTANCIA DOS ARQUIVOS
# MODULO 43 - INDICE DE CONFIANCA DA MEMORIA
# MODULO 44 - MEMORIA HIERARQUICA
# MODULO 45 - RELACOES ENTRE FRACTAIS
# MODULO 46 - DIAGNOSTICO COGNITIVO PREPARATORIO
# ============================================================

def escalar_valor(valor, minimo, maximo):
    try:
        valor = float(valor)
        minimo = float(minimo)
        maximo = float(maximo)
        if maximo == minimo:
            return 100
        return round(((valor - minimo) / (maximo - minimo)) * 100, 2)
    except Exception:
        return 0


def gerar_indice_importancia_arquivos(indice, relatorio_qualidade):
    tabela = indice.copy()

    if "nota_qualidade" not in tabela.columns and "arquivo" in relatorio_qualidade.columns:
        tabela = tabela.merge(
            relatorio_qualidade[["arquivo", "nota_qualidade", "classificacao"]],
            on="arquivo",
            how="left"
        )

    linhas_max = pd.to_numeric(tabela["linhas"], errors="coerce").max()
    tamanho_max = pd.to_numeric(tabela["tamanho_mb"], errors="coerce").max()

    registros = []

    for _, linha in tabela.iterrows():
        arquivo = str(linha.get("arquivo", ""))
        ativo = str(linha.get("ativo", ""))
        fractal = str(linha.get("fractal", ""))
        origem = str(linha.get("origem", ""))
        status = str(linha.get("status", ""))
        linhas = float(linha.get("linhas", 0) or 0)
        tamanho = float(linha.get("tamanho_mb", 0) or 0)
        confiab = float(linha.get("confiabilidade", 0) or 0)
        qualidade = float(linha.get("nota_qualidade", 100) or 100)

        peso_linhas = escalar_valor(linhas, 0, linhas_max)
        peso_tamanho = escalar_valor(tamanho, 0, tamanho_max)

        bonus_fractal = 0
        if fractal in ["1_MIN", "2_MIN", "3_MIN", "5_MIN"]:
            bonus_fractal += 8
        if fractal in ["DIARIO", "SEMANAL", "MENSAL"]:
            bonus_fractal += 5

        bonus_origem = 0
        if origem == "PROFIT":
            bonus_origem = 5
        elif origem == "ZE_DO_EUCRAZIO":
            bonus_origem = 4
        elif origem == "MEMORIA_VIVA":
            bonus_origem = 3

        penalidade = 0
        if status == "ALERTA":
            penalidade += 15
        if status == "ERRO":
            penalidade += 80

        score = (
            qualidade * 0.35
            + confiab * 0.25
            + peso_linhas * 0.20
            + peso_tamanho * 0.10
            + bonus_fractal
            + bonus_origem
            - penalidade
        )

        score = max(0, min(100, round(score, 2)))

        if score >= 90:
            classe = "ESSENCIAL"
        elif score >= 75:
            classe = "ALTA"
        elif score >= 60:
            classe = "MEDIA"
        elif score >= 40:
            classe = "BAIXA"
        else:
            classe = "CRITICA"

        registros.append({
            "arquivo": arquivo,
            "ativo": ativo,
            "fractal": fractal,
            "origem": origem,
            "linhas": int(linhas),
            "tamanho_mb": tamanho,
            "qualidade": qualidade,
            "confiabilidade": confiab,
            "score_importancia": score,
            "classe_importancia": classe,
            "status": status
        })

    df = pd.DataFrame(registros)
    df = df.sort_values("score_importancia", ascending=False)
    df.to_csv(ARQ_IMPORTANCIA_ARQUIVOS, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_indice_confianca_memoria(indice, relatorio_qualidade, relatorio_higienizacao):
    registros = []

    problemas_por_arquivo = {}
    if "arquivo" in relatorio_higienizacao.columns:
        problemas_por_arquivo = relatorio_higienizacao.groupby("arquivo").size().to_dict()

    qualidade_por_arquivo = {}
    if "arquivo" in relatorio_qualidade.columns and "nota_qualidade" in relatorio_qualidade.columns:
        qualidade_por_arquivo = dict(zip(relatorio_qualidade["arquivo"], relatorio_qualidade["nota_qualidade"]))

    for _, linha in indice.iterrows():
        arquivo = str(linha.get("arquivo", ""))
        status = str(linha.get("status", ""))
        hash_md5 = str(linha.get("hash_md5", ""))
        linhas = int(linha.get("linhas", 0) or 0)
        colunas = int(linha.get("colunas", 0) or 0)
        data_inicio = str(linha.get("data_inicio", "N/D"))
        data_fim = str(linha.get("data_fim", "N/D"))
        confiab = float(linha.get("confiabilidade", 0) or 0)
        qualidade = float(qualidade_por_arquivo.get(arquivo, 100) or 100)

        score = 100
        motivos = []

        if status != "OK":
            score -= 20
            motivos.append("STATUS_NAO_OK")

        if hash_md5 in ["", "N/D", "nan"]:
            score -= 20
            motivos.append("HASH_AUSENTE")

        if linhas <= 0:
            score -= 30
            motivos.append("SEM_LINHAS_VALIDAS")

        if colunas < 3:
            score -= 20
            motivos.append("COLUNAS_INSUFICIENTES")

        if data_inicio == "N/D" or data_fim == "N/D":
            score -= 15
            motivos.append("DATAS_INCOMPLETAS")

        qtd_problemas = problemas_por_arquivo.get(arquivo, 0)
        if qtd_problemas:
            score -= min(25, qtd_problemas * 5)
            motivos.append(f"HIGIENIZACAO_{qtd_problemas}_OCORRENCIAS")

        score = (score * 0.55) + (qualidade * 0.25) + (confiab * 0.20)
        score = max(0, min(100, round(score, 2)))

        if score >= 95:
            selo = "CONFIANCA_MAXIMA"
        elif score >= 85:
            selo = "CONFIAVEL"
        elif score >= 70:
            selo = "UTIL_COM_RESSALVA"
        elif score >= 50:
            selo = "BAIXA_CONFIANCA"
        else:
            selo = "NAO_RECOMENDADO"

        registros.append({
            "arquivo": arquivo,
            "ativo": linha.get("ativo", ""),
            "fractal": linha.get("fractal", ""),
            "score_confianca_memoria": score,
            "selo_confianca": selo,
            "motivos": " | ".join(motivos) if motivos else "OK"
        })

    df = pd.DataFrame(registros)
    df.to_csv(ARQ_CONFIANCA_MEMORIA, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_memoria_hierarquica(indice, catalogo_padroes):
    linhas = []

    ativos = sorted(indice["ativo"].dropna().unique())
    fractais = sorted(indice["fractal"].dropna().unique())
    origens = sorted(indice["origem"].dropna().unique()) if "origem" in indice.columns else []

    for ativo in ativos:
        if ativo == "DESCONHECIDO":
            continue
        linhas.append({
            "nivel_1": "MERCADO",
            "nivel_2": "ATIVO",
            "nivel_3": ativo,
            "item": ativo,
            "tipo": "ATIVO",
            "detalhe": "Ativo catalogado na Biblioteca Historica"
        })

    for fractal in fractais:
        if fractal == "DESCONHECIDO":
            continue
        tipo_fractal = "MICRO" if fractal in ["1_MIN", "2_MIN", "3_MIN", "5_MIN"] else "MACRO"
        linhas.append({
            "nivel_1": "TEMPO",
            "nivel_2": tipo_fractal,
            "nivel_3": fractal,
            "item": fractal,
            "tipo": "FRACTAL",
            "detalhe": "Escala temporal disponivel para consulta"
        })

    for origem in origens:
        linhas.append({
            "nivel_1": "ORIGEM",
            "nivel_2": origem,
            "nivel_3": "DADOS",
            "item": origem,
            "tipo": "ORIGEM_DADOS",
            "detalhe": "Fonte produtora ou organizadora do arquivo"
        })

    for _, padrao in catalogo_padroes.iterrows():
        codigo = str(padrao.get("codigo", ""))
        categoria = str(padrao.get("categoria", "PADRAO"))
        nome = str(padrao.get("nome", ""))
        linhas.append({
            "nivel_1": "PADROES",
            "nivel_2": categoria,
            "nivel_3": codigo,
            "item": nome,
            "tipo": "PADRAO_OFICIAL",
            "detalhe": str(padrao.get("descricao", ""))
        })

    df = pd.DataFrame(linhas)
    df.to_csv(ARQ_MEMORIA_HIERARQUICA, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_relacoes_fractais(indice, relatorio_memoria_estatistica):
    mapa_minutos = {
        "1_MIN": 1,
        "2_MIN": 2,
        "3_MIN": 3,
        "4_MIN": 4,
        "5_MIN": 5,
        "6_MIN": 6,
        "7_MIN": 7,
        "8_MIN": 8,
        "9_MIN": 9,
        "10_MIN": 10,
        "12_MIN": 12,
        "15_MIN": 15,
        "20_MIN": 20,
        "30_MIN": 30,
        "45_MIN": 45,
        "60_MIN": 60,
        "90_MIN": 90,
        "120_MIN": 120,
        "180_MIN": 180,
        "240_MIN": 240,
        "DIARIO": 1440,
        "SEMANAL": 10080,
        "MENSAL": 43200
    }

    linhas = []

    for ativo in sorted(indice["ativo"].dropna().unique()):
        if ativo == "DESCONHECIDO":
            continue

        fractais = sorted(set(indice[indice["ativo"] == ativo]["fractal"].dropna()))

        for origem_fractal in fractais:
            for destino_fractal in fractais:
                if origem_fractal == destino_fractal:
                    continue

                min_origem = mapa_minutos.get(origem_fractal)
                min_destino = mapa_minutos.get(destino_fractal)

                if not min_origem or not min_destino:
                    continue

                if min_origem < min_destino:
                    relacao = "AGREGA_PARA"
                    razao = round(min_destino / min_origem, 2)
                else:
                    relacao = "DETALHA_DE"
                    razao = round(min_origem / min_destino, 2)

                if razao <= 3:
                    forca = "FORTE"
                    peso = 0.90
                elif razao <= 12:
                    forca = "MEDIA"
                    peso = 0.70
                else:
                    forca = "FRACA"
                    peso = 0.45

                linhas.append({
                    "ativo": ativo,
                    "fractal_origem": origem_fractal,
                    "fractal_destino": destino_fractal,
                    "relacao": relacao,
                    "razao_temporal": razao,
                    "forca_relacao": forca,
                    "peso_relacao": peso
                })

    df = pd.DataFrame(linhas)
    df.to_csv(ARQ_RELACOES_FRACTAIS, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_grafo_conhecimento(indice, catalogo_padroes, memoria_hierarquica, relacoes_fractais):
    arestas = []

    for _, linha in indice.iterrows():
        arquivo = str(linha.get("arquivo", ""))
        ativo = str(linha.get("ativo", ""))
        fractal = str(linha.get("fractal", ""))
        origem = str(linha.get("origem", ""))

        if ativo and ativo != "DESCONHECIDO":
            arestas.append({
                "origem": arquivo,
                "tipo_origem": "ARQUIVO",
                "destino": ativo,
                "tipo_destino": "ATIVO",
                "relacao": "PERTENCE_A",
                "peso": 0.90,
                "detalhe": "Arquivo pertence ao ativo"
            })

        if fractal and fractal != "DESCONHECIDO":
            arestas.append({
                "origem": arquivo,
                "tipo_origem": "ARQUIVO",
                "destino": fractal,
                "tipo_destino": "FRACTAL",
                "relacao": "USA_ESCALA_TEMPORAL",
                "peso": 0.85,
                "detalhe": "Arquivo pertence ao fractal"
            })

        if origem:
            arestas.append({
                "origem": arquivo,
                "tipo_origem": "ARQUIVO",
                "destino": origem,
                "tipo_destino": "ORIGEM",
                "relacao": "GERADO_POR",
                "peso": 0.75,
                "detalhe": "Arquivo possui origem catalogada"
            })

    for _, padrao in catalogo_padroes.iterrows():
        codigo = str(padrao.get("codigo", ""))
        nome = str(padrao.get("nome", ""))
        categoria = str(padrao.get("categoria", ""))

        arestas.append({
            "origem": codigo,
            "tipo_origem": "CODIGO_PADRAO",
            "destino": nome,
            "tipo_destino": "PADRAO",
            "relacao": "DEFINE",
            "peso": 1.00,
            "detalhe": categoria
        })

    for _, rel in relacoes_fractais.iterrows():
        arestas.append({
            "origem": f"{rel['ativo']}_{rel['fractal_origem']}",
            "tipo_origem": "ATIVO_FRACTAL",
            "destino": f"{rel['ativo']}_{rel['fractal_destino']}",
            "tipo_destino": "ATIVO_FRACTAL",
            "relacao": rel["relacao"],
            "peso": rel["peso_relacao"],
            "detalhe": f"Razao temporal {rel['razao_temporal']} - forca {rel['forca_relacao']}"
        })

    df = pd.DataFrame(arestas)
    df.to_csv(ARQ_GRAFO_CONHECIMENTO, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_diagnostico_cognitivo(
    indice,
    importancia_arquivos,
    confianca_memoria,
    memoria_hierarquica,
    relacoes_fractais,
    grafo_conhecimento
):
    itens = []

    total_arquivos = len(indice)
    total_relacoes = len(grafo_conhecimento)
    total_hierarquia = len(memoria_hierarquica)

    confianca_media = 0
    if "score_confianca_memoria" in confianca_memoria.columns and len(confianca_memoria):
        confianca_media = round(confianca_memoria["score_confianca_memoria"].mean(), 2)

    importancia_media = 0
    if "score_importancia" in importancia_arquivos.columns and len(importancia_arquivos):
        importancia_media = round(importancia_arquivos["score_importancia"].mean(), 2)

    itens.append({
        "item": "ARQUIVOS_CATALOGADOS",
        "valor": total_arquivos,
        "parecer": "Base documental disponivel para memoria cognitiva"
    })

    itens.append({
        "item": "RELACOES_NO_GRAFO",
        "valor": total_relacoes,
        "parecer": "Arestas criadas entre arquivos, ativos, fractais, origens e padroes"
    })

    itens.append({
        "item": "ITENS_HIERARQUICOS",
        "valor": total_hierarquia,
        "parecer": "Estrutura inicial de memoria hierarquica criada"
    })

    itens.append({
        "item": "CONFIANCA_MEDIA",
        "valor": confianca_media,
        "parecer": "Confianca media da memoria calculada automaticamente"
    })

    itens.append({
        "item": "IMPORTANCIA_MEDIA",
        "valor": importancia_media,
        "parecer": "Importancia media dos arquivos calculada automaticamente"
    })

    if total_relacoes >= total_arquivos * 2 and confianca_media >= 85:
        status = "PRONTA_PARA_ZE_DO_EUCRAZIO"
        recomendacao = "Bernardo preparado para receber fractais universais e novos indicadores"
    else:
        status = "PREPARATORIA"
        recomendacao = "Continuar enriquecendo relacoes, indicadores e fractais antes da fase cognitiva completa"

    itens.append({
        "item": "STATUS_COGNITIVO",
        "valor": status,
        "parecer": recomendacao
    })

    df = pd.DataFrame(itens)
    df.to_csv(ARQ_DIAGNOSTICO_COGNITIVO, sep=";", index=False, encoding="utf-8-sig")
    return df



# ============================================================
# BERNARDO v4.0 - ARQUITETURA CONGELADA
# MODULO 47 - GRAFO ESTATISTICO
# MODULO 48 - MEMORIA POR ASSUNTO
# MODULO 49 - MEMORIA POR EVENTO
# MODULO 50 - REDE SEMANTICA
# MODULO 51 - BIBLIOTECA CONCEITUAL
# MODULO 52 - AUTOINSPECAO DO BERNARDO
# MODULO 53 - PACOTES DE ENTREGA PARA MODULOS FUTUROS
# ============================================================

def gerar_grafo_estatistico(grafo_conhecimento, relatorio_memoria_estatistica, importancia_arquivos, confianca_memoria):
    estatisticas = []

    if len(grafo_conhecimento) == 0:
        df = pd.DataFrame()
        df.to_csv(ARQ_GRAFO_ESTATISTICO, sep=";", index=False, encoding="utf-8-sig")
        return df

    confianca_media = 0
    if "score_confianca_memoria" in confianca_memoria.columns and len(confianca_memoria):
        confianca_media = round(confianca_memoria["score_confianca_memoria"].mean(), 2)

    importancia_media = 0
    if "score_importancia" in importancia_arquivos.columns and len(importancia_arquivos):
        importancia_media = round(importancia_arquivos["score_importancia"].mean(), 2)

    agrupado = grafo_conhecimento.groupby(["relacao", "tipo_origem", "tipo_destino"]).agg({
        "origem": "count",
        "peso": "mean"
    }).reset_index()

    for _, linha in agrupado.iterrows():
        ocorrencias = int(linha["origem"])
        peso_medio = round(float(linha["peso"]), 4)

        score_estatistico = round(
            min(100, (ocorrencias * 0.8) + (peso_medio * 40) + (confianca_media * 0.3) + (importancia_media * 0.2)),
            2
        )

        if score_estatistico >= 90:
            forca = "MUITO_FORTE"
        elif score_estatistico >= 75:
            forca = "FORTE"
        elif score_estatistico >= 55:
            forca = "MEDIA"
        else:
            forca = "FRACA"

        estatisticas.append({
            "relacao": linha["relacao"],
            "tipo_origem": linha["tipo_origem"],
            "tipo_destino": linha["tipo_destino"],
            "ocorrencias": ocorrencias,
            "peso_medio": peso_medio,
            "confianca_media_global": confianca_media,
            "importancia_media_global": importancia_media,
            "score_estatistico": score_estatistico,
            "forca_estatistica": forca
        })

    df = pd.DataFrame(estatisticas)
    df = df.sort_values("score_estatistico", ascending=False)
    df.to_csv(ARQ_GRAFO_ESTATISTICO, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_memoria_por_assunto(indice, catalogo_padroes, grafo_conhecimento):
    assuntos_base = [
        {"assunto": "VWAP", "categoria": "PRECO_VALOR", "descricao": "Memoria relacionada a preco medio institucional, bandas e retorno a valor", "termos": "VWAP,MEDIA,VALOR,PRECO"},
        {"assunto": "DELTA", "categoria": "FLUXO", "descricao": "Memoria relacionada a diferenca entre agressao compradora e vendedora", "termos": "DELTA,AGRESSAO,FLUXO"},
        {"assunto": "SALDO", "categoria": "FLUXO", "descricao": "Memoria relacionada ao saldo acumulado de agressao", "termos": "SALDO,ACUMULADO,AGRESSAO"},
        {"assunto": "REVERSAO", "categoria": "PADRAO", "descricao": "Memoria relacionada a mudanca de direcao e rejeicao de preco", "termos": "REVERSAO,REJEICAO,EXTREMO,VWAP"},
        {"assunto": "ROMPIMENTO", "categoria": "PADRAO", "descricao": "Memoria relacionada a rompimentos com ou sem confirmacao de fluxo", "termos": "ROMPIMENTO,EXPLOSAO,FLUXO"},
        {"assunto": "ABSORCAO", "categoria": "PADRAO", "descricao": "Memoria relacionada a absorcao institucional compradora ou vendedora", "termos": "ABSORCAO,DEFESA,INSTITUCIONAL"},
        {"assunto": "SCALPING", "categoria": "PERFIL_OPERACIONAL", "descricao": "Memoria relacionada a oportunidades rapidas e explosoes de fluxo", "termos": "SCALPING,EXPLOSAO,REJEICAO"},
        {"assunto": "CONTEXTO", "categoria": "AMBIENTE", "descricao": "Memoria relacionada a abertura, fechamento, volatilidade e eventos externos", "termos": "ABERTURA,FECHAMENTO,COPOM,PAYROLL,FOMC"}
    ]

    registros = []

    for assunto in assuntos_base:
        termos = [t.strip().upper() for t in assunto["termos"].split(",")]
        arquivos_relacionados = 0
        padroes_relacionados = 0
        relacoes_grafo = 0

        for _, linha in indice.iterrows():
            texto = " ".join([
                str(linha.get("arquivo", "")),
                str(linha.get("tags", "")),
                str(linha.get("origem", "")),
                str(linha.get("fractal", "")),
            ]).upper()
            if any(t in texto for t in termos):
                arquivos_relacionados += 1

        for _, padrao in catalogo_padroes.iterrows():
            texto = " ".join([
                str(padrao.get("codigo", "")),
                str(padrao.get("nome", "")),
                str(padrao.get("categoria", "")),
                str(padrao.get("descricao", "")),
            ]).upper()
            if any(t in texto for t in termos):
                padroes_relacionados += 1

        for _, rel in grafo_conhecimento.iterrows():
            texto = " ".join(rel.astype(str)).upper()
            if any(t in texto for t in termos):
                relacoes_grafo += 1

        densidade = arquivos_relacionados + padroes_relacionados + relacoes_grafo

        if densidade >= 30:
            maturidade = "ALTA"
        elif densidade >= 10:
            maturidade = "MEDIA"
        elif densidade >= 1:
            maturidade = "BAIXA"
        else:
            maturidade = "A_DESENVOLVER"

        registros.append({
            "assunto": assunto["assunto"],
            "categoria": assunto["categoria"],
            "descricao": assunto["descricao"],
            "termos_chave": assunto["termos"],
            "arquivos_relacionados": arquivos_relacionados,
            "padroes_relacionados": padroes_relacionados,
            "relacoes_grafo": relacoes_grafo,
            "densidade_conhecimento": densidade,
            "maturidade_assunto": maturidade
        })

    df = pd.DataFrame(registros)
    df.to_csv(ARQ_MEMORIA_ASSUNTO, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_memoria_por_evento(memoria_contexto, indice):
    eventos_base = [
        ("COPOM", "Politica monetaria Brasil"),
        ("PAYROLL", "Emprego Estados Unidos"),
        ("FOMC", "Politica monetaria Estados Unidos"),
        ("VENCIMENTO", "Vencimento de contratos"),
        ("ROLAGEM", "Rolagem de contratos futuros"),
        ("FERIADO", "Reducao ou distorcao de liquidez"),
        ("ABERTURA", "Inicio do pregao"),
        ("FECHAMENTO", "Encerramento do pregao"),
        ("ALTA_VOLATILIDADE", "Ambiente de grande amplitude"),
        ("BAIXA_VOLATILIDADE", "Ambiente de compressao")
    ]

    data_min = "N/D"
    data_max = "N/D"
    try:
        datas_i = pd.to_datetime(indice["data_inicio"], dayfirst=True, errors="coerce").dropna()
        datas_f = pd.to_datetime(indice["data_fim"], dayfirst=True, errors="coerce").dropna()
        if len(datas_i):
            data_min = datas_i.min().strftime("%d/%m/%Y")
        if len(datas_f):
            data_max = datas_f.max().strftime("%d/%m/%Y")
    except Exception:
        pass

    texto_contexto = ""
    if len(memoria_contexto):
        texto_contexto = " ".join(memoria_contexto.astype(str).fillna("").values.flatten()).upper()

    registros = []
    for evento, descricao in eventos_base:
        ja_catalogado = "SIM" if evento in texto_contexto else "NAO"
        prioridade = "ALTA" if evento in ["COPOM", "PAYROLL", "FOMC", "VENCIMENTO", "ROLAGEM"] else "MEDIA"
        registros.append({
            "evento": evento,
            "descricao": descricao,
            "ja_catalogado": ja_catalogado,
            "prioridade": prioridade,
            "data_minima_biblioteca": data_min,
            "data_maxima_biblioteca": data_max,
            "uso_futuro": "Historiador, Motor de Confluencia, Memoria de Contexto"
        })

    df = pd.DataFrame(registros)
    df.to_csv(ARQ_MEMORIA_EVENTO, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_rede_semantica(memoria_por_assunto, catalogo_padroes):
    relacoes = []
    mapa_relacoes = [
        ("VWAP", "REVERSAO", "SUPORTA_ANALISE_DE", 0.90),
        ("VWAP", "ABSORCAO", "CONTEXTO_DE_VALOR_PARA", 0.82),
        ("DELTA", "ROMPIMENTO", "CONFIRMA_OU_NEGA", 0.88),
        ("DELTA", "SCALPING", "SINALIZA_EXPLOSAO_PARA", 0.86),
        ("SALDO", "CONTEXTO", "INDICA_DOMINIO_DE", 0.76),
        ("ABSORCAO", "REVERSAO", "PODE_ANTECEDER", 0.84),
        ("EXAUSTAO", "REVERSAO", "PODE_GERAR", 0.83),
        ("ROMPIMENTO", "SCALPING", "PODE_OFERECER", 0.78),
        ("CONTEXTO", "SCALPING", "MODULA_RISCO_DE", 0.74),
        ("CONTEXTO", "ROMPIMENTO", "ALTERA_PROBABILIDADE_DE", 0.72)
    ]

    assuntos_existentes = set(memoria_por_assunto["assunto"].astype(str)) if len(memoria_por_assunto) else set()

    for origem, destino, relacao, peso in mapa_relacoes:
        if origem in assuntos_existentes and destino in assuntos_existentes:
            relacoes.append({
                "origem": origem,
                "destino": destino,
                "relacao_semantica": relacao,
                "peso_semantico": peso,
                "status": "ATIVA"
            })

    for _, padrao in catalogo_padroes.iterrows():
        codigo = str(padrao.get("codigo", ""))
        nome = str(padrao.get("nome", ""))
        categoria = str(padrao.get("categoria", ""))
        nome_upper = nome.upper()

        assunto_destino = "CONTEXTO"
        if "REVERSAO" in nome_upper:
            assunto_destino = "REVERSAO"
        elif "ROMPIMENTO" in nome_upper:
            assunto_destino = "ROMPIMENTO"
        elif "ABSORCAO" in nome_upper:
            assunto_destino = "ABSORCAO"
        elif "SCALPING" in nome_upper:
            assunto_destino = "SCALPING"
        elif "EXAUSTAO" in nome_upper:
            assunto_destino = "REVERSAO"

        relacoes.append({
            "origem": codigo,
            "destino": assunto_destino,
            "relacao_semantica": "PERTENCE_A_ASSUNTO",
            "peso_semantico": 0.80,
            "status": f"PADRAO_{categoria}"
        })

    df = pd.DataFrame(relacoes)
    df.to_csv(ARQ_REDE_SEMANTICA, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_biblioteca_conceitual(catalogo_padroes, memoria_por_assunto, rede_semantica):
    fichas = []

    for _, padrao in catalogo_padroes.iterrows():
        codigo = str(padrao.get("codigo", ""))
        nome = str(padrao.get("nome", ""))
        categoria = str(padrao.get("categoria", ""))
        descricao = str(padrao.get("descricao", ""))

        relacoes = rede_semantica[
            (rede_semantica["origem"].astype(str) == codigo) |
            (rede_semantica["destino"].astype(str) == nome)
        ] if len(rede_semantica) else pd.DataFrame()

        fichas.append({
            "codigo": codigo,
            "nome": nome,
            "tipo": "PADRAO",
            "categoria": categoria,
            "descricao": descricao,
            "relacoes_semanticas": len(relacoes),
            "maturidade": "CATALOGADO",
            "uso_futuro": "Historiador, Motor de Confluencia, Score de Qualidade"
        })

    for _, assunto in memoria_por_assunto.iterrows():
        fichas.append({
            "codigo": f"ASSUNTO_{assunto['assunto']}",
            "nome": assunto["assunto"],
            "tipo": "ASSUNTO",
            "categoria": assunto["categoria"],
            "descricao": assunto["descricao"],
            "relacoes_semanticas": int(assunto["relacoes_grafo"]),
            "maturidade": assunto["maturidade_assunto"],
            "uso_futuro": "Busca semantica, IA, Pacote de contexto"
        })

    df = pd.DataFrame(fichas)
    df.to_csv(ARQ_BIBLIOTECA_CONCEITUAL, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_autoinspecao_bernardo(indice, relatorio_curadoria, memoria_por_assunto, memoria_por_evento, rede_semantica, biblioteca_conceitual, diagnostico_cognitivo):
    achados = []

    def adicionar(item, status, gravidade, recomendacao):
        achados.append({
            "item": item,
            "status": status,
            "gravidade": gravidade,
            "recomendacao": recomendacao
        })

    total = len(indice)
    adicionar(
        "BASE_DOCUMENTAL",
        "FORTE" if total >= 100 else "LIMITADA",
        "OK" if total >= 100 else "MEDIA",
        "Biblioteca possui volume suficiente para evolucao cognitiva" if total >= 100 else "Aumentar quantidade de arquivos historicos"
    )

    if "item" in relatorio_curadoria.columns:
        ausentes = relatorio_curadoria[relatorio_curadoria["item"].astype(str) == "FRACTAIS_AUSENTES"]
        if len(ausentes):
            valor = str(ausentes["situacao"].iloc[0])
            adicionar(
                "FRACTAIS_AUSENTES",
                valor,
                "MEDIA" if valor != "NENHUM" else "OK",
                "Zé do Eucrázio deve gerar fractais faltantes" if valor != "NENHUM" else "Cobertura temporal basica completa"
            )

    baixa_maturidade = memoria_por_assunto[
        memoria_por_assunto["maturidade_assunto"].isin(["BAIXA", "A_DESENVOLVER"])
    ] if len(memoria_por_assunto) else pd.DataFrame()

    adicionar(
        "ASSUNTOS_COM_BAIXA_MATURIDADE",
        len(baixa_maturidade) if len(baixa_maturidade) else "NENHUM",
        "MEDIA" if len(baixa_maturidade) else "OK",
        "Enriquecer memoria conceitual apos novos indicadores e fractais" if len(baixa_maturidade) else "Memoria por assunto esta equilibrada"
    )

    eventos_nao = memoria_por_evento[memoria_por_evento["ja_catalogado"] == "NAO"] if len(memoria_por_evento) else pd.DataFrame()
    if len(eventos_nao):
        adicionar("EVENTOS_A_CATALOGAR", len(eventos_nao), "MEDIA", "Criar calendario historico de eventos macro e vencimentos")

    adicionar(
        "REDE_SEMANTICA",
        "ATIVA" if len(rede_semantica) >= 20 else "PEQUENA",
        "OK" if len(rede_semantica) >= 20 else "BAIXA",
        "Rede semantica pronta para consultas conceituais" if len(rede_semantica) >= 20 else "Expandir relacoes semanticas com dados do Historiador"
    )

    adicionar(
        "BIBLIOTECA_CONCEITUAL",
        "ATIVA" if len(biblioteca_conceitual) >= 20 else "INICIAL",
        "OK" if len(biblioteca_conceitual) >= 20 else "BAIXA",
        "Fichas conceituais prontas para IA e Historiador" if len(biblioteca_conceitual) >= 20 else "Expandir fichas conceituais conforme novos padroes surgirem"
    )

    status_cog = ""
    if "item" in diagnostico_cognitivo.columns:
        linha = diagnostico_cognitivo[diagnostico_cognitivo["item"] == "STATUS_COGNITIVO"]
        if len(linha):
            status_cog = str(linha["valor"].iloc[0])

    adicionar(
        "STATUS_FINAL_BERNARDO",
        "PRONTO_PARA_ZE" if status_cog == "PRONTA_PARA_ZE_DO_EUCRAZIO" else "PREPARATORIO",
        "OK" if status_cog == "PRONTA_PARA_ZE_DO_EUCRAZIO" else "MEDIA",
        "Bernardo pode ser congelado como base para engenharia temporal" if status_cog == "PRONTA_PARA_ZE_DO_EUCRAZIO" else "Refinar memoria antes da proxima fase"
    )

    df = pd.DataFrame(achados)
    df.to_csv(ARQ_AUTOINSPECAO, sep=";", index=False, encoding="utf-8-sig")
    return df


def gerar_pacotes_modulos_futuros(indice, relatorio_memoria_estatistica, ranking_historico, banco_reversoes, memoria_por_assunto, rede_semantica, biblioteca_conceitual):
    id_execucao_bernardo = datetime.now().strftime("BERNARDO-%Y%m%d-%H%M%S")
    status_autoinspecao = status_autoinspecao_pacote_ze()
    hash_indice = (
        sha256_arquivo(ARQ_INDICE)
        if os.path.exists(ARQ_INDICE)
        else "INDICE_INDISPONIVEL"
    )

    pacote_historiador = []

    for _, linha in banco_reversoes.iterrows():
        if str(linha.get("elegivel_para_historiador", "")) == "SIM":
            pacote_historiador.append({
                "tipo_pacote": "REVERSAO",
                "ativo": linha.get("ativo", ""),
                "fractal": linha.get("fractal", ""),
                "arquivo": linha.get("arquivo", ""),
                "prioridade": "ALTA",
                "uso": "Historiador deve estudar reversoes recorrentes"
            })

    df_hist = pd.DataFrame(pacote_historiador)
    df_hist.to_csv(ARQ_PACOTE_HISTORIADOR, sep=";", index=False, encoding="utf-8-sig")

    pacote_ze = []
    fractais_atuais = set(indice["fractal"].dropna().unique())
    fractais_desejados = [
        "1_MIN", "2_MIN", "3_MIN", "4_MIN", "5_MIN", "6_MIN", "7_MIN", "8_MIN",
        "9_MIN", "10_MIN", "12_MIN", "15_MIN", "20_MIN", "30_MIN", "45_MIN",
        "60_MIN", "90_MIN", "120_MIN", "180_MIN", "240_MIN", "DIARIO", "SEMANAL", "MENSAL"
    ]

    for fractal in fractais_desejados:
        pacote_ze.append({
            "fractal": fractal,
            "existe_na_biblioteca": "SIM" if fractal in fractais_atuais else "NAO",
            "acao_recomendada": "MANTER_INDEXADO" if fractal in fractais_atuais else "GERAR_COM_ZE_DO_EUCRAZIO",
            "base_recomendada": "1_MIN",
            "versao_bernardo": "4.0",
            "id_execucao_bernardo": id_execucao_bernardo,
            "hash_indice_bernardo": hash_indice,
            "status_autoinspecao_bernardo": status_autoinspecao,
            "manifesto_rastreabilidade": os.path.basename(
                ARQ_MANIFESTO_PACOTE_ZE
            ),
        })

    df_ze = pd.DataFrame(pacote_ze)
    df_ze.to_csv(
        ARQ_PACOTE_ZE_EUCRAZIO,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    manifesto_ze = {
        "tipo_manifesto": "PACOTE_BERNARDO_PARA_ZE",
        "versao_bernardo": "4.0",
        "id_execucao_bernardo": id_execucao_bernardo,
        "data_geracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "arquivo_indice": os.path.basename(ARQ_INDICE),
        "hash_sha256_indice_bernardo": hash_indice,
        "arquivo_pacote_ze": os.path.basename(ARQ_PACOTE_ZE_EUCRAZIO),
        "hash_sha256_pacote_ze_bernardo": sha256_arquivo(
            ARQ_PACOTE_ZE_EUCRAZIO
        ),
        "quantidade_itens": int(len(df_ze)),
        "status_autoinspecao_bernardo": status_autoinspecao,
        "observacao_hash": (
            "O hash do pacote fica no manifesto externo para evitar "
            "autorreferencia circular dentro do proprio CSV."
        ),
    }

    with open(ARQ_MANIFESTO_PACOTE_ZE, "w", encoding="utf-8") as f:
        json.dump(
            manifesto_ze,
            f,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

    pacote_motor = []

    for _, assunto in memoria_por_assunto.iterrows():
        pacote_motor.append({
            "tipo": "ASSUNTO",
            "nome": assunto["assunto"],
            "categoria": assunto["categoria"],
            "maturidade": assunto["maturidade_assunto"],
            "peso_inicial_sugerido": 3 if assunto["maturidade_assunto"] == "ALTA" else 2,
            "uso": "Motor de Confluencia pode usar como eixo de evidencia"
        })

    for _, conceito in biblioteca_conceitual.iterrows():
        pacote_motor.append({
            "tipo": conceito["tipo"],
            "nome": conceito["nome"],
            "categoria": conceito["categoria"],
            "maturidade": conceito["maturidade"],
            "peso_inicial_sugerido": 2,
            "uso": conceito["uso_futuro"]
        })

    df_motor = pd.DataFrame(pacote_motor)
    df_motor.to_csv(ARQ_PACOTE_MOTOR_CONFLUENCIA, sep=";", index=False, encoding="utf-8-sig")

    return df_hist, df_ze, df_motor


def main():
    print("\n" + "=" * 60)
    print("BERNARDO BIBLIOTECARIO v4.0 - BERNARDO 100%")
    print("=" * 60)

    backup_indice()

    pasta_recuperacao, arquivos_recuperados = backup_recuperacao()
    print(f"Backup de recuperacao criado: {pasta_recuperacao}")
    print(f"Arquivos protegidos: {arquivos_recuperados}")

    indice_anterior = carregar_indice_anterior()
    registros = []

    for pasta in sorted(os.listdir(BASE)):
        if pasta not in PASTAS_BIBLIOTECA_OFICIAL:
            continue

        caminho_pasta = os.path.join(BASE, pasta)

        if not os.path.isdir(caminho_pasta):
            continue

        for raiz, _, arquivos in os.walk(caminho_pasta):
            for arquivo in arquivos:
                if not arquivo.lower().endswith(".csv"):
                    continue

                registro = processar_arquivo(pasta, raiz, arquivo)
                registros.append(registro)

                print(
                    f"{registro['status']} | "
                    f"{registro['ativo']} | "
                    f"{registro['fractal']} | "
                    f"{registro['arquivo']} | "
                    f"{registro['linhas']} linhas"
                )

    indice = pd.DataFrame(registros)

    if indice.empty:
        print("ATENCAO: nenhum arquivo foi indexado.")
        indice = pd.DataFrame(columns=[
            "id", "ativo", "ativo_original", "fractal", "pasta",
            "arquivo", "caminho", "linhas", "colunas",
            "data_inicio", "data_fim", "tamanho_mb",
            "ultima_modificacao", "hash_md5", "origem",
            "confiabilidade", "tags", "volume_medio",
            "range_medio", "preco_medio", "status", "observacao"
        ])

    indice.to_csv(ARQ_INDICE, sep=";", index=False, encoding="utf-8-sig")

    indice[indice["ativo"] == "WIN"].to_csv(
        ARQ_WIN, sep=";", index=False, encoding="utf-8-sig"
    )

    indice[indice["ativo"] == "WDO"].to_csv(
        ARQ_WDO, sep=";", index=False, encoding="utf-8-sig"
    )

    indice[[
        "arquivo",
        "ativo",
        "fractal",
        "linhas",
        "colunas",
        "status",
        "observacao",
        "confiabilidade",
        "tags"
    ]].to_csv(ARQ_INTEGRIDADE, sep=";", index=False, encoding="utf-8-sig")

    alertas = indice[indice["status"] != "OK"]
    alertas.to_csv(ARQ_ALERTAS, sep=";", index=False, encoding="utf-8-sig")

    estatisticas = indice.groupby(["ativo", "fractal"]).agg({
        "arquivo": "count",
        "linhas": "sum",
        "tamanho_mb": "sum"
    }).reset_index()

    estatisticas.to_csv(ARQ_ESTATISTICAS, sep=";", index=False, encoding="utf-8-sig")

    detectar_duplicados(indice)

    relatorio_higienizacao = gerar_relatorio_higienizacao(indice)
    relatorio_qualidade = gerar_metricas_qualidade(indice)
    relatorio_memoria_estatistica = gerar_memoria_estatistica(indice)
    relatorio_curadoria = gerar_curadoria_automatica(
        indice,
        relatorio_higienizacao,
        relatorio_qualidade,
        relatorio_memoria_estatistica
    )
    tabela_consulta = montar_tabela_consulta(indice, relatorio_qualidade)
    relatorio_incremental = gerar_atualizacao_incremental(indice_anterior, indice)
    banco_reversoes = gerar_banco_reversoes(indice, relatorio_qualidade)
    ranking_historico = gerar_ranking_historico(indice, relatorio_qualidade, relatorio_memoria_estatistica)
    fragmentacao_contexto = gerar_fragmentacao_contexto(indice)
    memoria_contexto = gerar_memoria_contexto(indice)
    catalogo_padroes = gerar_catalogo_padroes()

    importancia_arquivos = gerar_indice_importancia_arquivos(indice, relatorio_qualidade)
    confianca_memoria = gerar_indice_confianca_memoria(indice, relatorio_qualidade, relatorio_higienizacao)
    memoria_hierarquica = gerar_memoria_hierarquica(indice, catalogo_padroes)
    relacoes_fractais = gerar_relacoes_fractais(indice, relatorio_memoria_estatistica)
    grafo_conhecimento = gerar_grafo_conhecimento(
        indice,
        catalogo_padroes,
        memoria_hierarquica,
        relacoes_fractais
    )
    diagnostico_cognitivo = gerar_diagnostico_cognitivo(
        indice,
        importancia_arquivos,
        confianca_memoria,
        memoria_hierarquica,
        relacoes_fractais,
        grafo_conhecimento
    )

    grafo_estatistico = gerar_grafo_estatistico(
        grafo_conhecimento,
        relatorio_memoria_estatistica,
        importancia_arquivos,
        confianca_memoria
    )
    memoria_por_assunto = gerar_memoria_por_assunto(
        indice,
        catalogo_padroes,
        grafo_conhecimento
    )
    memoria_por_evento = gerar_memoria_por_evento(memoria_contexto, indice)
    rede_semantica = gerar_rede_semantica(memoria_por_assunto, catalogo_padroes)
    biblioteca_conceitual = gerar_biblioteca_conceitual(
        catalogo_padroes,
        memoria_por_assunto,
        rede_semantica
    )
    autoinspecao_bernardo = gerar_autoinspecao_bernardo(
        indice,
        relatorio_curadoria,
        memoria_por_assunto,
        memoria_por_evento,
        rede_semantica,
        biblioteca_conceitual,
        diagnostico_cognitivo
    )
    pacote_historiador, pacote_ze, pacote_motor = gerar_pacotes_modulos_futuros(
        indice,
        relatorio_memoria_estatistica,
        ranking_historico,
        banco_reversoes,
        memoria_por_assunto,
        rede_semantica,
        biblioteca_conceitual
    )

    try:
        from intelligence.bernardo_ordens_fiscal import (
            BernardoOrdensFiscal,
        )
    except ModuleNotFoundError:
        from bernardo_ordens_fiscal import BernardoOrdensFiscal

    resultado_ordens_fiscal = BernardoOrdensFiscal().processar(
        gravar=True
    )

    eventos = detectar_eventos(indice_anterior, indice)
    registrar_timeline(eventos)

    atualizar_memoria_uso(indice)

    qtd_alertas = len(alertas)
    qtd_erros = len(indice[indice["status"] == "ERRO"])

    registrar_log(len(indice), qtd_alertas, qtd_erros)

    status = gerar_status(indice)

    print(status)

    print("Arquivos gerados:")
    print(ARQ_INDICE)
    print(ARQ_WIN)
    print(ARQ_WDO)
    print(ARQ_INTEGRIDADE)
    print(ARQ_STATUS)
    print(ARQ_DIAGNOSTICO)
    print(ARQ_ALERTAS)
    print(ARQ_DUPLICADOS)
    print(ARQ_USO)
    print(ARQ_TIMELINE)
    print(ARQ_ESTATISTICAS)
    print(ARQ_HIGIENIZACAO)
    print(ARQ_QUALIDADE)
    print(ARQ_MEMORIA_ESTATISTICA)
    print(ARQ_CURADORIA)
    print(ARQ_CONSULTA)
    print(ARQ_INCREMENTAL)
    print(ARQ_BANCO_REVERSOES)
    print(ARQ_RANKING_HISTORICO)
    print(ARQ_FRAGMENTACAO_CONTEXTO)
    print(ARQ_MEMORIA_CONTEXTO)
    print(ARQ_CATALOGO_PADROES)
    print(ARQ_GRAFO_CONHECIMENTO)
    print(ARQ_IMPORTANCIA_ARQUIVOS)
    print(ARQ_CONFIANCA_MEMORIA)
    print(ARQ_MEMORIA_HIERARQUICA)
    print(ARQ_RELACOES_FRACTAIS)
    print(ARQ_DIAGNOSTICO_COGNITIVO)
    print(ARQ_GRAFO_ESTATISTICO)
    print(ARQ_MEMORIA_ASSUNTO)
    print(ARQ_MEMORIA_EVENTO)
    print(ARQ_REDE_SEMANTICA)
    print(ARQ_BIBLIOTECA_CONCEITUAL)
    print(ARQ_AUTOINSPECAO)
    print(ARQ_PACOTE_HISTORIADOR)
    print(ARQ_PACOTE_ZE_EUCRAZIO)
    print(ARQ_PACOTE_MOTOR_CONFLUENCIA)
    print("=" * 60)

    print("Resumo higienizacao:")
    print(relatorio_higienizacao["gravidade"].value_counts().to_string())
    print("=" * 60)

    print("Resumo qualidade:")
    print(relatorio_qualidade["classificacao"].value_counts().to_string())
    print("=" * 60)
   
    print("Resumo memoria estatistica:")
    print(
        relatorio_memoria_estatistica[
            ["ativo", "fractal", "total_arquivos", "total_linhas"]
        ].to_string(index=False)
    )
    print("=" * 60)

    print("Resumo curadoria:")
    print(
        relatorio_curadoria[
            ["item", "situacao"]
        ].to_string(index=False)
    )
    print("=" * 60)

    print("Resumo consulta:")
    print(f"Tabela de consulta gerada com {len(tabela_consulta)} registros")
    print("Exemplo WIN 5_MIN:")
    exemplo = consultar_biblioteca(tabela_consulta, ativo="WIN", fractal="5_MIN")
    if len(exemplo):
        colunas_exemplo = [
            coluna for coluna in ["arquivo", "ativo", "fractal", "linhas", "classificacao"]
            if coluna in exemplo.columns
        ]
        print(exemplo[colunas_exemplo].head(10).to_string(index=False))
    else:
        print("Nenhum registro encontrado")
    print("=" * 60)

    print("Resumo atualizacao incremental:")
    if "evento" in relatorio_incremental.columns:
        print(relatorio_incremental["evento"].value_counts().to_string())
    else:
        print("Sem eventos incrementais")
    print("=" * 60)

    print("Resumo banco de reversoes:")
    if "elegivel_para_historiador" in banco_reversoes.columns:
        print(banco_reversoes["elegivel_para_historiador"].value_counts().to_string())
    else:
        print("Banco de reversoes sem registros")
    print("=" * 60)

    print("Top 10 ranking historico:")
    colunas_ranking = [
        coluna for coluna in ["ranking", "ativo", "fractal", "total_arquivos", "total_linhas", "score_historico"]
        if coluna in ranking_historico.columns
    ]
    print(ranking_historico[colunas_ranking].head(10).to_string(index=False))
    print("=" * 60)

    print("Resumo fragmentacao de contexto:")
    print(f"Contextos preparados: {len(fragmentacao_contexto)}")
    print("=" * 60)

    print("Resumo memoria de contexto:")
    print(f"Eventos de contexto catalogados: {len(memoria_contexto)}")
    print("=" * 60)

    print("Catalogo oficial de padroes:")
    print(catalogo_padroes[["codigo", "nome", "status"]].to_string(index=False))
    print("=" * 60)

    print("Resumo importancia dos arquivos:")
    colunas_importancia = [
        coluna for coluna in ["arquivo", "ativo", "fractal", "score_importancia", "classe_importancia"]
        if coluna in importancia_arquivos.columns
    ]
    print(importancia_arquivos[colunas_importancia].head(10).to_string(index=False))
    print("=" * 60)

    print("Resumo confianca da memoria:")
    if "selo_confianca" in confianca_memoria.columns:
        print(confianca_memoria["selo_confianca"].value_counts().to_string())
    else:
        print("Sem dados de confianca")
    print("=" * 60)

    print("Resumo memoria hierarquica:")
    print(f"Itens hierarquicos: {len(memoria_hierarquica)}")
    print("=" * 60)

    print("Resumo relacoes entre fractais:")
    print(f"Relacoes criadas: {len(relacoes_fractais)}")
    print("=" * 60)

    print("Resumo grafo de conhecimento:")
    print(f"Arestas criadas: {len(grafo_conhecimento)}")
    print("=" * 60)

    print("Diagnostico cognitivo:")
    print(diagnostico_cognitivo.to_string(index=False))
    print("=" * 60)

    print("Resumo grafo estatistico:")
    if len(grafo_estatistico):
        print(grafo_estatistico[["relacao", "ocorrencias", "score_estatistico", "forca_estatistica"]].head(10).to_string(index=False))
    else:
        print("Sem grafo estatistico")
    print("=" * 60)

    print("Resumo memoria por assunto:")
    print(memoria_por_assunto[["assunto", "categoria", "densidade_conhecimento", "maturidade_assunto"]].to_string(index=False))
    print("=" * 60)

    print("Resumo memoria por evento:")
    print(memoria_por_evento[["evento", "ja_catalogado", "prioridade"]].to_string(index=False))
    print("=" * 60)

    print("Resumo rede semantica:")
    print(f"Relacoes semanticas: {len(rede_semantica)}")
    print("=" * 60)

    print("Resumo biblioteca conceitual:")
    print(f"Fichas conceituais: {len(biblioteca_conceitual)}")
    print("=" * 60)

    print("Autoinspecao Bernardo:")
    print(autoinspecao_bernardo.to_string(index=False))
    print("=" * 60)

    print("Ordens do Fiscal para Bernardo:")
    print(
        f"Status: {resultado_ordens_fiscal.get('status')} | "
        f"Quantidade: {resultado_ordens_fiscal.get('quantidade')}"
    )
    print("=" * 60)

    print("Pacotes para modulos futuros:")
    print(f"Historiador: {len(pacote_historiador)} itens")
    print(f"Ze do Eucrazio: {len(pacote_ze)} itens")
    print(f"Motor de Confluencia: {len(pacote_motor)} itens")
    print("=" * 60)


if __name__ == "__main__":
    main()
