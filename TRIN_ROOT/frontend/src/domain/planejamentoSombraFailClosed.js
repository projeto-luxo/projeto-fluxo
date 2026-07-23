const STATUS_BACKEND_PERMITIDOS = new Set([
  "SOMBRA_VERSIONADA_BLOQUEADA",
  "ERRO_BLOQUEADO",
]);

const ESTADOS_BACKEND_CONHECIDOS = new Set([
  "BLOQUEADO",
  "ERRO_BLOQUEADO",
  "PLANO_SOMBRA",
  "SEM_OPERACAO",
  "SEM_PLANO",
  "AGUARDANDO",
]);

const STATUS_CONEXAO_CONHECIDOS = new Set([
  "ONLINE",
  "DESCONECTADO",
  "RECONECTANDO",
  "ERRO_JSON",
  "ERRO_PROCESSAMENTO",
]);

const CAMPOS_OFICIAIS = [
  "planejamento_operacional_sombra",
  "planejamento_operacional_sombra_status",
  "planejamento_operacional_sombra_erro",
];

const CAMPOS_DIAGNOSTICOS_OBRIGATORIOS = [
  "schema_version",
  "id_plano",
  "modo",
  "origem_contexto",
  "estado",
  "autorizacao",
  "uso_operacional",
  "motivo_bloqueio",
  "gates",
  "evidencias",
  "rastreabilidade",
];

const CAMPOS_OPERACIONAIS_NULOS = [
  "entrada_inferior",
  "entrada_superior",
  "invalidacao",
  "stop",
  "parcial",
  "alvo",
  "ordem_corretora",
];

function objetoSimples(valor) {
  return Boolean(valor) && typeof valor === "object" && !Array.isArray(valor);
}

function unico(valores) {
  return Array.from(new Set(valores.filter(Boolean)));
}

function contemMarcador(valor, marcador) {
  try {
    return JSON.stringify(valor || "").toUpperCase().includes(marcador);
  } catch (_erro) {
    return false;
  }
}

function estadoSeguro({
  estado = "BLOQUEADO",
  estadoBackend = "DESCONHECIDO",
  statusBackend = "AUSENTE",
  origem = "DESCONHECIDA",
  idPlano = "NAO_INFORMADO",
  motivos = [],
  erro = "",
  timestamp = null,
  timestampMonotonicoAceito = false,
  gates = [],
  evidencias = {},
  rastreabilidade = {},
} = {}) {
  return {
    modo: "SOMBRA",
    estado,
    estadoBackend,
    statusBackend,
    autorizacao: "BLOQUEADA",
    usoOperacional: "BLOQUEADO",
    origem,
    idPlano,
    motivosBloqueio: unico(motivos),
    erro,
    timestamp,
    timestampMonotonicoAceito,
    gates: Array.isArray(gates) ? gates : [],
    evidencias: objetoSimples(evidencias) ? evidencias : {},
    rastreabilidade: objetoSimples(rastreabilidade) ? rastreabilidade : {},
    entrada: null,
    stop: null,
    parcial: null,
    alvo: null,
    ordem: null,
  };
}

export function criarEstadoPlanejamentoSombraInicial() {
  return estadoSeguro({
    estado: "AUSENTE",
    motivos: ["CONTRATO_AUSENTE", "LIMIAR_OFICIAL_AUSENTE"],
  });
}

export function normalizarPlanejamentoSombraFailClosed({
  payload,
  statusConexao,
  ultimoTimestampAceito = null,
} = {}) {
  const motivos = [];
  const statusConexaoTexto = String(statusConexao || "").toUpperCase();

  if (!STATUS_CONEXAO_CONHECIDOS.has(statusConexaoTexto)) {
    motivos.push("STATUS_CONEXAO_DESCONHECIDO");
  } else if (statusConexaoTexto !== "ONLINE") {
    motivos.push("WEBSOCKET_DESCONECTADO");
  }

  if (payload === null || payload === undefined) {
    return estadoSeguro({
      estado: statusConexaoTexto === "ONLINE" ? "AUSENTE" : "DESCONECTADO",
      motivos: [...motivos, "CONTRATO_AUSENTE", "LIMIAR_OFICIAL_AUSENTE"],
    });
  }

  if (!objetoSimples(payload)) {
    return estadoSeguro({
      estado: "PAYLOAD_INCOMPLETO",
      motivos: [...motivos, "CONTRATO_INVALIDO", "LIMIAR_OFICIAL_AUSENTE"],
    });
  }

  for (const campo of CAMPOS_OFICIAIS) {
    if (!Object.prototype.hasOwnProperty.call(payload, campo)) {
      motivos.push(`CAMPO_AUSENTE:${campo}`);
    }
  }

  const sombra = payload.planejamento_operacional_sombra;
  const statusBackend = payload.planejamento_operacional_sombra_status;
  const erroBackend = payload.planejamento_operacional_sombra_erro;

  if (!objetoSimples(sombra)) motivos.push("TIPO_INVALIDO:planejamento_operacional_sombra");
  if (typeof statusBackend !== "string") motivos.push("TIPO_INVALIDO:planejamento_operacional_sombra_status");
  if (!(erroBackend === null || erroBackend === undefined || typeof erroBackend === "string")) {
    motivos.push("TIPO_INVALIDO:planejamento_operacional_sombra_erro");
  }

  if (typeof statusBackend === "string" && !statusBackend.trim()) {
    motivos.push("STATUS_AUSENTE");
  } else if (typeof statusBackend === "string" && !STATUS_BACKEND_PERMITIDOS.has(statusBackend)) {
    motivos.push("STATUS_DESCONHECIDO");
  }

  const erroTexto = typeof erroBackend === "string" ? erroBackend.trim() : "";
  if (erroTexto || statusBackend === "ERRO_BLOQUEADO") motivos.push("ERRO_PRESENTE");

  if (!objetoSimples(sombra)) {
    return estadoSeguro({
      estado: erroTexto ? "ERRO_BLOQUEADO" : "PAYLOAD_INCOMPLETO",
      statusBackend: typeof statusBackend === "string" ? statusBackend : "AUSENTE",
      motivos: [...motivos, "LIMIAR_OFICIAL_AUSENTE"],
      erro: erroTexto,
    });
  }

  for (const campo of CAMPOS_DIAGNOSTICOS_OBRIGATORIOS) {
    if (!Object.prototype.hasOwnProperty.call(sombra, campo)) {
      motivos.push(`PAYLOAD_PARCIAL:${campo}`);
    }
  }

  if (sombra.schema_version !== "PlanejamentoOperacionalSombraV1") motivos.push("CONTRATO_INVALIDO:SCHEMA");
  if (sombra.modo !== "SOMBRA") motivos.push("CONTRATO_INVALIDO:MODO");
  if (sombra.autorizacao !== "BLOQUEADA") motivos.push("CONTRATO_INVALIDO:AUTORIZACAO");
  if (sombra.uso_operacional !== "BLOQUEADO") motivos.push("CONTRATO_INVALIDO:USO_OPERACIONAL");
  if (!Array.isArray(sombra.gates)) motivos.push("TIPO_INVALIDO:gates");
  if (!objetoSimples(sombra.evidencias)) motivos.push("TIPO_INVALIDO:evidencias");
  if (!objetoSimples(sombra.rastreabilidade)) motivos.push("TIPO_INVALIDO:rastreabilidade");

  for (const campo of CAMPOS_OPERACIONAIS_NULOS) {
    if (sombra[campo] !== null) motivos.push(`CONTRATO_INVALIDO:${campo.toUpperCase()}_NAO_NULO`);
  }

  if (typeof sombra.estado !== "string" || !sombra.estado.trim()) {
    motivos.push("DADO_DESCONHECIDO");
  } else if (!ESTADOS_BACKEND_CONHECIDOS.has(sombra.estado)) {
    motivos.push("DADO_DESCONHECIDO");
  }

  const identidade = objetoSimples(sombra.rastreabilidade?.identidade_snapshot)
    ? sombra.rastreabilidade.identidade_snapshot
    : {};
  const timestampBruto = identidade.timestamp;
  let timestamp = null;
  let timestampMonotonicoAceito = false;

  if (timestampBruto === null || timestampBruto === undefined || timestampBruto === "") {
    motivos.push("TIMESTAMP_AUSENTE");
  } else {
    const timestampNumero = Date.parse(String(timestampBruto));
    if (!Number.isFinite(timestampNumero)) {
      motivos.push("TIMESTAMP_INVALIDO");
    } else {
      timestamp = String(timestampBruto);
      const anteriorNumero = ultimoTimestampAceito ? Date.parse(String(ultimoTimestampAceito)) : null;
      if (Number.isFinite(anteriorNumero) && timestampNumero <= anteriorNumero) {
        motivos.push("TIMESTAMP_NAO_MONOTONICO");
      } else if (statusConexaoTexto === "ONLINE") {
        timestampMonotonicoAceito = true;
      }
    }
  }

  if (
    contemMarcador(sombra.motivo_bloqueio, "ULTIMO_PAYLOAD_OBSOLETO") ||
    contemMarcador(sombra.gates, "ULTIMO_PAYLOAD_OBSOLETO")
  ) {
    motivos.push("ULTIMO_PAYLOAD_OBSOLETO");
  }

  if (
    contemMarcador(sombra.motivo_bloqueio, "FONTE_ESTAGNADA") ||
    contemMarcador(sombra.motivo_bloqueio, "RTD_ESTAGNADO") ||
    contemMarcador(sombra.gates, "FONTE_ESTAGNADA") ||
    contemMarcador(sombra.gates, "RTD_ESTAGNADO")
  ) {
    motivos.push("FONTE_ESTAGNADA");
  }

  // Não existe limiar quantitativo oficial na base auditada. A lacuna bloqueia.
  motivos.push("LIMIAR_OFICIAL_AUSENTE");

  let estado = "PLANO_SOMBRA_INFORMATIVO";
  if (!STATUS_CONEXAO_CONHECIDOS.has(statusConexaoTexto) || statusConexaoTexto !== "ONLINE") {
    estado = "DESCONECTADO";
  } else if (motivos.some((m) => m.startsWith("CAMPO_AUSENTE") || m.startsWith("PAYLOAD_PARCIAL") || m.startsWith("TIPO_INVALIDO"))) {
    estado = "PAYLOAD_INCOMPLETO";
  } else if (motivos.some((m) => m.startsWith("CONTRATO_INVALIDO:SCHEMA"))) {
    estado = "SCHEMA_DESCONHECIDO";
  } else if (motivos.includes("ERRO_PRESENTE")) {
    estado = "ERRO_BLOQUEADO";
  } else if (motivos.some((m) => ["ULTIMO_PAYLOAD_OBSOLETO", "FONTE_ESTAGNADA", "TIMESTAMP_INVALIDO", "TIMESTAMP_NAO_MONOTONICO"].includes(m))) {
    estado = "DADO_DESATUALIZADO";
  } else if (motivos.some((m) => m.startsWith("CONTRATO_INVALIDO") || m === "DADO_DESCONHECIDO")) {
    estado = "BLOQUEADO";
  }

  return estadoSeguro({
    estado,
    estadoBackend: typeof sombra.estado === "string" ? sombra.estado : "DESCONHECIDO",
    statusBackend: typeof statusBackend === "string" && statusBackend ? statusBackend : "AUSENTE",
    origem: typeof sombra.origem_contexto === "string" && sombra.origem_contexto ? sombra.origem_contexto : "DESCONHECIDA",
    idPlano: typeof sombra.id_plano === "string" && sombra.id_plano ? sombra.id_plano : "NAO_INFORMADO",
    motivos,
    erro: erroTexto,
    timestamp,
    timestampMonotonicoAceito,
    gates: sombra.gates,
    evidencias: sombra.evidencias,
    rastreabilidade: sombra.rastreabilidade,
  });
}
