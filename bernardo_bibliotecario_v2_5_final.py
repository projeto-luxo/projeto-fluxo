import os
import hashlib
import shutil
import pandas as pd
from datetime import datetime


BASE = r"C:\Users\User\projeto_fluxo\TRIN_HISTORICO"
INDICES = os.path.join(BASE, "00_INDICES")
VERSOES = os.path.join(INDICES, "VERSOES")
RECUPERACAO = os.path.join(INDICES, "RECUPERACAO")

os.makedirs(INDICES, exist_ok=True)
os.makedirs(VERSOES, exist_ok=True)
os.makedirs(RECUPERACAO, exist_ok=True)

IGNORAR = {"00_INDICES", "00_MEMORIA_PROCESSADA"}

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

def md5_arquivo(caminho):
    h = hashlib.md5()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)
    return h.hexdigest()


def identificar_ativo(valor, arquivo):
    texto = f"{valor} {arquivo}".upper()
    if "WIN" in texto:
        return "WIN"
    if "WDO" in texto:
        return "WDO"
    return "DESCONHECIDO"


def identificar_fractal(pasta, arquivo):
    texto = f"{pasta} {arquivo}".upper()

    mapa = [
        ("1_MIN", "1_MIN"),
        ("2_MIN", "2_MIN"),
        ("3_MIN", "3_MIN"),
        ("5_MIN", "5_MIN"),
        ("10_MIN", "10_MIN"),
        ("15_MIN", "15_MIN"),
        ("30_MIN", "30_MIN"),
        ("60_MIN", "60_MIN"),
        ("DIARIO", "DIARIO"),
        ("SEMANAL", "SEMANAL"),
        ("MENSAL", "MENSAL"),
    ]

    for chave, fractal in mapa:
        if chave in texto:
            return fractal

    return "DESCONHECIDO"


def origem_arquivo(caminho, arquivo):
    texto = f"{caminho} {arquivo}".upper()

    if "ZEDOEUCRAZIO" in texto or "2MIN" in texto or "3MIN" in texto:
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
    if df.shape[1] < 2:
        return "N/D", "N/D", "DATA_INVALIDA"

    datas = pd.to_datetime(
        df.iloc[:, 1],
        dayfirst=True,
        errors="coerce"
    ).dropna()

    if len(datas) == 0:
        return "N/D", "N/D", "DATA_INVALIDA"

    return (
        datas.min().strftime("%d/%m/%Y"),
        datas.max().strftime("%d/%m/%Y"),
        "OK"
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
BIBLIOTECA HISTORICA TRIN - BERNARDO v2.5
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


def main():
    print("\n" + "=" * 60)
    print("BERNARDO BIBLIOTECARIO v2.5 - MODULOS 09, 15, 16, 17, 19 E 20")
    print("=" * 60)

    backup_indice()

    pasta_recuperacao, arquivos_recuperados = backup_recuperacao()
    print(f"Backup de recuperacao criado: {pasta_recuperacao}")
    print(f"Arquivos protegidos: {arquivos_recuperados}")

    indice_anterior = carregar_indice_anterior()
    registros = []

    for pasta in sorted(os.listdir(BASE)):
        if pasta in IGNORAR:
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

    indice.to_csv(ARQ_INDICE, sep=";", index=False, encoding="utf-8-sig")
    indice[indice["ativo"] == "WIN"].to_csv(ARQ_WIN, sep=";", index=False, encoding="utf-8-sig")
    indice[indice["ativo"] == "WDO"].to_csv(ARQ_WDO, sep=";", index=False, encoding="utf-8-sig")

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


if __name__ == "__main__":
    main()
