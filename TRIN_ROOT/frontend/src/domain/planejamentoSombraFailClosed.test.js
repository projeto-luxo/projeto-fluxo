import {
  criarEstadoPlanejamentoSombraInicial,
  normalizarPlanejamentoSombraFailClosed,
} from "./planejamentoSombraFailClosed";

function sombraValida(overrides = {}) {
  return {
    schema_version: "PlanejamentoOperacionalSombraV1",
    id_plano: "PO-TESTE-001",
    modo: "SOMBRA",
    origem_contexto: "AO_VIVO",
    estado: "BLOQUEADO",
    autorizacao: "BLOQUEADA",
    uso_operacional: "BLOQUEADO",
    motivo_bloqueio: "PERIODO_PARCIAL",
    direcao: null,
    entrada_inferior: null,
    entrada_superior: null,
    invalidacao: null,
    stop: null,
    parcial: null,
    alvo: null,
    ordem_corretora: null,
    gates: [],
    evidencias: {},
    hipotese_plano: null,
    rastreabilidade: {
      identidade_snapshot: { timestamp: "2026-07-23T09:00:00-03:00" },
      hash_entrada: null,
      versao_regra: "R1",
      look_ahead: false,
    },
    ...overrides,
  };
}

function payloadValido(sombra = sombraValida(), overrides = {}) {
  return {
    planejamento_operacional_sombra: sombra,
    planejamento_operacional_sombra_status: "SOMBRA_VERSIONADA_BLOQUEADA",
    planejamento_operacional_sombra_erro: null,
    ...overrides,
  };
}

function normalizar(payload, extras = {}) {
  return normalizarPlanejamentoSombraFailClosed({
    payload,
    statusConexao: "ONLINE",
    ...extras,
  });
}

function bloqueado(resultado) {
  expect(resultado.modo).toBe("SOMBRA");
  expect(resultado.autorizacao).toBe("BLOQUEADA");
  expect(resultado.usoOperacional).toBe("BLOQUEADO");
  expect(resultado.entrada).toBeNull();
  expect(resultado.stop).toBeNull();
  expect(resultado.parcial).toBeNull();
  expect(resultado.alvo).toBeNull();
  expect(resultado.ordem).toBeNull();
}

function possui(resultado, prefixo) {
  expect(resultado.motivosBloqueio.some((m) => m === prefixo || m.startsWith(`${prefixo}:`))).toBe(true);
}

test("T01_CAMPOS_OFICIAIS_VALIDOS_EXIBEM_DIAGNOSTICO_BLOQUEADO", () => {
  const r = normalizar(payloadValido());
  expect(r.estado).toBe("PLANO_SOMBRA_INFORMATIVO");
  bloqueado(r);
});

test("T02_CONTRATO_AUSENTE_BLOQUEIA", () => {
  const r = normalizar(null);
  possui(r, "CONTRATO_AUSENTE");
  bloqueado(r);
});

test("T03_CONTRATO_INVALIDO_BLOQUEIA", () => {
  const r = normalizar(payloadValido(sombraValida({ modo: "REAL" })));
  possui(r, "CONTRATO_INVALIDO");
  bloqueado(r);
});

test("T04_CADA_CAMPO_AUSENTE_ISOLADAMENTE_BLOQUEIA", () => {
  for (const campo of [
    "planejamento_operacional_sombra",
    "planejamento_operacional_sombra_status",
    "planejamento_operacional_sombra_erro",
  ]) {
    const payload = payloadValido();
    delete payload[campo];
    possui(normalizar(payload), "CAMPO_AUSENTE");
  }
});

test("T05_TIPOS_INVALIDOS_BLOQUEIAM", () => {
  const r = normalizar(payloadValido([], { planejamento_operacional_sombra_status: 1 }));
  possui(r, "TIPO_INVALIDO");
  bloqueado(r);
});

test("T06_STATUS_AUSENTE_BLOQUEIA", () => {
  const r = normalizar(payloadValido(undefined, { planejamento_operacional_sombra_status: "" }));
  possui(r, "STATUS_AUSENTE");
  bloqueado(r);
});

test("T07_STATUS_DESCONHECIDO_BLOQUEIA", () => {
  const r = normalizar(payloadValido(undefined, { planejamento_operacional_sombra_status: "LIBERADO" }));
  possui(r, "STATUS_DESCONHECIDO");
  bloqueado(r);
});

test("T08_ERRO_PRESENTE_PREVALECE_E_BLOQUEIA", () => {
  const r = normalizar(payloadValido(undefined, { planejamento_operacional_sombra_erro: "falha" }));
  possui(r, "ERRO_PRESENTE");
  expect(r.estado).toBe("ERRO_BLOQUEADO");
  bloqueado(r);
});

test("T09_PAYLOAD_PARCIAL_BLOQUEIA", () => {
  const sombra = sombraValida();
  delete sombra.evidencias;
  const r = normalizar(payloadValido(sombra));
  possui(r, "PAYLOAD_PARCIAL");
  bloqueado(r);
});

test("T10_DADO_DESCONHECIDO_BLOQUEIA", () => {
  const r = normalizar(payloadValido(sombraValida({ estado: "NOVO_ESTADO_NAO_CONTRATADO" })));
  possui(r, "DADO_DESCONHECIDO");
  bloqueado(r);
});

test("T11_WEBSOCKET_DESCONECTADO_BLOQUEIA", () => {
  const r = normalizarPlanejamentoSombraFailClosed({ payload: payloadValido(), statusConexao: "DESCONECTADO" });
  possui(r, "WEBSOCKET_DESCONECTADO");
  expect(r.estado).toBe("DESCONECTADO");
  bloqueado(r);
});

test("T12_STATUS_CONEXAO_DESCONHECIDO_BLOQUEIA", () => {
  const r = normalizarPlanejamentoSombraFailClosed({ payload: payloadValido(), statusConexao: "MISTERIOSO" });
  possui(r, "STATUS_CONEXAO_DESCONHECIDO");
  bloqueado(r);
});

test("T13_ULTIMO_PAYLOAD_OBSOLETO_BLOQUEIA", () => {
  const r = normalizar(payloadValido(sombraValida({ motivo_bloqueio: "ULTIMO_PAYLOAD_OBSOLETO" })));
  possui(r, "ULTIMO_PAYLOAD_OBSOLETO");
  expect(r.estado).toBe("DADO_DESATUALIZADO");
  bloqueado(r);
});

test("T14_FONTE_ESTAGNADA_BLOQUEIA", () => {
  const r = normalizar(payloadValido(sombraValida({ gates: ["RTD_ESTAGNADO"] })));
  possui(r, "FONTE_ESTAGNADA");
  expect(r.estado).toBe("DADO_DESATUALIZADO");
  bloqueado(r);
});

test("T15_TIMESTAMP_AUSENTE_BLOQUEIA", () => {
  const r = normalizar(payloadValido(sombraValida({ rastreabilidade: { identidade_snapshot: {} } })));
  possui(r, "TIMESTAMP_AUSENTE");
  bloqueado(r);
});

test("T16_TIMESTAMP_INVALIDO_BLOQUEIA", () => {
  const r = normalizar(payloadValido(sombraValida({ rastreabilidade: { identidade_snapshot: { timestamp: "nao-data" } } })));
  possui(r, "TIMESTAMP_INVALIDO");
  bloqueado(r);
});

test("T17_TIMESTAMP_NAO_MONOTONICO_BLOQUEIA", () => {
  const r = normalizar(payloadValido(), { ultimoTimestampAceito: "2026-07-23T09:00:00-03:00" });
  possui(r, "TIMESTAMP_NAO_MONOTONICO");
  bloqueado(r);
});

test("T18_LIMIAR_OFICIAL_AUSENTE_BLOQUEIA", () => {
  const r = normalizar(payloadValido());
  possui(r, "LIMIAR_OFICIAL_AUSENTE");
  bloqueado(r);
});

test("T19_NENHUM_FALLBACK_LEGADO_AUTORIZA_OPERACAO", () => {
  const r = normalizar({
    ...payloadValido(),
    planejamentoOperacional: { autorizacao: "LIBERADA", stop: 1, alvo: 2 },
    planejamentoStatus: "LIBERADO",
    entrada: "COMPRA",
  });
  bloqueado(r);
});

test("T20_NENHUM_ESTADO_PRODUZ_ENTRADA_STOP_PARCIAL_ALVO_OU_ORDEM", () => {
  const resultados = [
    criarEstadoPlanejamentoSombraInicial(),
    normalizar(null),
    normalizar(payloadValido()),
    normalizar(payloadValido(sombraValida({ stop: 100, alvo: 200 }))),
  ];
  resultados.forEach(bloqueado);
});
