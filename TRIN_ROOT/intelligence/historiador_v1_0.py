from pathlib import Path
from datetime import datetime
import hashlib
import json

from historiador_estatistico import gerar_estatistica_biblioteca
from historiador_temporal import gerar_cobertura_temporal, gerar_distribuicao_fractais
from historiador_delta import gerar_estatistica_delta
from historiador_volume import gerar_estatistica_volume
from historiador_padroes import gerar_padroes_iniciais
from historiador_contextual import gerar_contexto_inicial, CONHECIMENTO


# ============================================================
# HISTORIADOR v1.0.1 - ORQUESTRADOR CONTROLADO
# Missao: gerar conhecimento inicial a partir do indice oficial
# do Bernardo, com validacao minima e manifesto cartorial.
#
# Nao altera biblioteca historica.
# Nao minera padroes reais.
# Nao gera sinal operacional.
# ============================================================

TRIN_ROOT = Path(__file__).resolve().parents[1]
HISTORICO = TRIN_ROOT / "TRIN_HISTORICO"
INDICE_GERAL = HISTORICO / "00_INDICES" / "indice_geral.csv"
MANIFESTO = CONHECIMENTO / "manifesto_historiador.json"

CONTRATOS_OBRIGATORIOS = [
    TRIN_ROOT / "governance" / "08_CONTRATOS" / "contrato_historiador.md",
    TRIN_ROOT / "governance" / "08_CONTRATOS" / "CONTRATO_ENTRADAS_SAIDAS_HISTORIADOR.md",
    TRIN_ROOT / "governance" / "08_CONTRATOS" / "CONTRATO_INDICE_GERAL_BERNARDO.md",
    TRIN_ROOT / "governance" / "08_CONTRATOS" / "CONTRATO_SCHEMA_INDICE_GERAL_BERNARDO.md",
    TRIN_ROOT / "governance" / "08_CONTRATOS" / "CONTRATO_SCHEMA_CONHECIMENTO_HISTORIADOR.md",
    TRIN_ROOT / "governance" / "08_CONTRATOS" / "CONTRATO_MANIFESTO_HISTORIADOR.md",
]


def sha256_arquivo(caminho):
    caminho = Path(caminho)
    if not caminho.exists() or not caminho.is_file():
        return None

    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1024 * 1024), b""):
            h.update(bloco)

    return h.hexdigest()


def contar_linhas_csv(caminho):
    caminho = Path(caminho)
    if not caminho.exists() or not caminho.is_file():
        return 0

    try:
        with caminho.open("r", encoding="utf-8-sig", errors="ignore") as f:
            total = sum(1 for _ in f)

        return max(total - 1, 0)
    except Exception:
        return 0


def validar_entrada_historiador():
    erros = []
    ressalvas = []

    if not INDICE_GERAL.exists():
        erros.append(f"indice_geral.csv nao encontrado: {INDICE_GERAL}")

    faltantes = [str(c) for c in CONTRATOS_OBRIGATORIOS if not c.exists()]
    if faltantes:
        erros.append("Contratos obrigatorios ausentes: " + " | ".join(faltantes))

    # O Historiador ainda nao esta homologado.
    ressalvas.append("Historiador em TESTE_CONTROLADO, nao homologado.")
    ressalvas.append("Conhecimento gerado como CONHECIMENTO_INICIAL_COM_RESSALVAS.")
    ressalvas.append("HistoriadorAdapter deve ser tratado como evidencia fraca.")
    ressalvas.append("Padrao catalogado nao significa padrao historico comprovado.")
    ressalvas.append("Cobertura temporal nao substitui Fiscal Temporal.")

    return erros, ressalvas


def registrar_saida(caminho):
    caminho = Path(caminho)
    return {
        "caminho": str(caminho),
        "existe": caminho.exists(),
        "linhas": contar_linhas_csv(caminho) if caminho.suffix.lower() == ".csv" else None,
        "hash_sha256": sha256_arquivo(caminho),
        "status": "GERADO" if caminho.exists() else "AUSENTE",
    }


def gerar_manifesto(saidas, erros, ressalvas):
    CONHECIMENTO.mkdir(parents=True, exist_ok=True)

    status_execucao = "FALHOU" if erros else "CONCLUIDO_COM_RESSALVAS"

    manifesto = {
        "modulo": "HISTORIADOR",
        "versao_historiador": "v1.0.1",
        "data_execucao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status_execucao": status_execucao,
        "modo_execucao": "TESTE_CONTROLADO",
        "classificacao_conhecimento": "CONHECIMENTO_INICIAL_COM_RESSALVAS",
        "entradas": {
            "indice_bernardo": {
                "caminho": str(INDICE_GERAL),
                "existe": INDICE_GERAL.exists(),
                "hash_sha256": sha256_arquivo(INDICE_GERAL),
                "linhas": contar_linhas_csv(INDICE_GERAL),
                "status_schema": "PENDENTE_VALIDACAO_ESTRITA",
                "contrato_schema": "CONTRATO_SCHEMA_INDICE_GERAL_BERNARDO.md",
            },
            "contratos_governanca": [
                {
                    "caminho": str(c),
                    "existe": c.exists(),
                    "hash_sha256": sha256_arquivo(c),
                }
                for c in CONTRATOS_OBRIGATORIOS
            ],
            "fiscal_temporal": {
                "status_base": "PENDENTE_INTEGRACAO_FORMAL",
                "ressalvas": [
                    "Manifesto v1.0.1 ainda nao valida automaticamente o ultimo laudo do Fiscal Temporal."
                ],
            },
        },
        "saidas": [registrar_saida(s) for s in saidas],
        "erros": erros,
        "ressalvas": ressalvas,
        "status_final": "AGUARDANDO_AUDITORIA_HARD",
    }

    MANIFESTO.write_text(
        json.dumps(manifesto, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return MANIFESTO


def main():
    print("\n" + "=" * 60)
    print("HISTORIADOR v1.0.1 - TESTE CONTROLADO")
    print("=" * 60)

    erros, ressalvas = validar_entrada_historiador()

    if erros:
        manifesto = gerar_manifesto([], erros, ressalvas)
        print("EXECUCAO BLOQUEADA")
        for erro in erros:
            print("ERRO:", erro)
        print("Manifesto:", manifesto)
        raise SystemExit(1)

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
        "HISTORIADOR v1.0.1 - RELATORIO OFICIAL",
        "=" * 60,
        f"Data/hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "Status: CONCLUIDO_COM_RESSALVAS",
        "Modo: TESTE_CONTROLADO",
        "Missao: transformar indice oficial do Bernardo em conhecimento inicial.",
        "Ressalvas:",
        "- Historiador ainda nao homologado.",
        "- Conhecimento inicial com ressalvas.",
        "- Adapter deve ser tratado como evidencia fraca.",
        "Arquivos gerados:",
    ]

    for caminho in saidas:
        texto.append(f"- {caminho}")

    texto.append(f"- {MANIFESTO}")
    texto.append("=" * 60)
    relatorio.write_text("\n".join(texto), encoding="utf-8")

    saidas.append(relatorio)

    manifesto = gerar_manifesto(saidas, erros, ressalvas)

    print("Arquivos gerados:")
    for caminho in saidas:
        print(caminho)

    print("Manifesto:", manifesto)
    print("=" * 60)


if __name__ == "__main__":
    main()
