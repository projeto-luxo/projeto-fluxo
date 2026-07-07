// frontend/src/App.js
import React, { useCallback, useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";
import {
  connectTrinWebSocket,
  disconnectTrinWebSocket
} from "./services/trinWebSocket";

export default function App() {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);

  const candleSeriesRef = useRef(null);

  const stopLineRef = useRef(null);
  const parcialLineRef = useRef(null);
  const alvoLineRef = useRef(null);

  const stopPriceLineRef = useRef(null);
  const parcialPriceLineRef = useRef(null);
  const alvoPriceLineRef = useRef(null);

  const vwapLineRef = useRef(null);
  const vwapSuperiorRef = useRef(null);
  const vwapInferiorRef = useRef(null);

  const hotZoneTopRef = useRef(null);
  const hotZoneBottomRef = useRef(null);
  const absorcaoLineRef = useRef(null);

  const heatmap1Ref = useRef(null);
  const heatmap2Ref = useRef(null);
  const heatmap3Ref = useRef(null);
  const heatmap4Ref = useRef(null);
  const heatmap5Ref = useRef(null);

  const socketRef = useRef(null);
  const carregouHistoricoRef = useRef(false);

  const [dataInfo, setDataInfo] = useState({});
  const [wsStatus, setWsStatus] = useState("DESCONECTADO");
  const [ttRawStatus, setTtRawStatus] = useState(null);
  const [ttRawErro, setTtRawErro] = useState("");

  const ordenarPorTempo = useCallback((lista) => {
    if (!Array.isArray(lista)) return [];

    const mapa = new Map();

    lista.forEach((item) => {
      if (!item || item.time === undefined || item.time === null) return;

      mapa.set(Number(item.time), {
        ...item,
        time: Number(item.time),
      });
    });

    return Array.from(mapa.values()).sort((a, b) => a.time - b.time);
  }, []);

  const formatar = (valor) => {
    if (valor === null || valor === undefined) return "-";

    const n = Number(valor);

    if (!Number.isFinite(n)) return valor;

    return n.toFixed(2);
  };

  const setLinhaHorizontal = useCallback((seriesRef, primeiroTime, ultimoTime, valor) => {
    if (!seriesRef.current) return;

    if (
      valor === null ||
      valor === undefined ||
      primeiroTime === undefined ||
      ultimoTime === undefined ||
      Number.isNaN(Number(valor))
    ) {
      seriesRef.current.setData([]);
      return;
    }

    seriesRef.current.setData([
      { time: primeiroTime, value: Number(valor) },
      { time: ultimoTime, value: Number(valor) },
    ]);
  }, []);
const atualizarPriceLineExecucao = useCallback((priceLineRef, titulo, valor, cor, lineStyle = 0) => {
  if (!candleSeriesRef.current) return;

  if (priceLineRef.current) {
    candleSeriesRef.current.removePriceLine(priceLineRef.current);
    priceLineRef.current = null;
  }

  if (
    valor === null ||
    valor === undefined ||
    Number.isNaN(Number(valor))
  ) {
    return;
  }

 priceLineRef.current = candleSeriesRef.current.createPriceLine({
  price: Number(valor),

  color: cor,

  lineWidth:
    titulo === "STOP"
      ? 3
      : titulo === "ALVO"
      ? 3
      : 2,

  lineStyle,

  axisLabelVisible: true,

  axisLabelColor: "#000000",

  axisLabelTextColor:
    titulo === "STOP"
      ? "#ff4d4d"
      : titulo === "PARCIAL"
      ? "#ffd700"
      : "#00ff88",

  title:
    titulo === "STOP"
      ? "ðŸŸ¥ STOP"
      : titulo === "PARCIAL"
      ? "ðŸŸ¨ PARCIAL"
      : "ðŸŸ© ALVO",
  });
}, []);

  const gerarMarkersInstitucionais = useCallback((historico) => {
    if (!Array.isArray(historico)) return [];

    return historico
      .filter((candle) => candle.reversao_detectada || candle.explosao_detectada)
      .slice(-30)
      .map((candle) => {
        if (candle.explosao_detectada) {
          return {
            time: candle.time,
            position: candle.delta >= 0 ? "belowBar" : "aboveBar",
            color: candle.delta >= 0 ? "#00ff99" : "#ff3333",
            shape: candle.delta >= 0 ? "arrowUp" : "arrowDown",
            text: candle.delta >= 0 ? "BUY EXP" : "SELL EXP",
          };
        }

        return {
          time: candle.time,
          position: candle.close >= candle.open ? "belowBar" : "aboveBar",
          color: "#ffaa00",
          shape: "circle",
          text: "REV",
        };
      });
  }, []);

    const calcularContextoInstitucional = useCallback((info) => {
    const compra = Number(info.compra || 0);
    const venda = Number(info.venda || 0);
    const scoreAgressao = Number(info.scoreAgressao || 0);
    const scoreEngine = Number(info.engineScore || info.score || 0);
    const seqDelta = Number(info.engineSeqDelta || 0);

    const fase = info.engineFase || "AGUARDANDO";
    const direcao = info.engineDirecao || "NEUTRO";
    const trap = info.engineTrap || null;
    const absorcao = Boolean(info.engineAbsorcao);

    const temHotZone =
      info.zonaLow !== null &&
      info.zonaLow !== undefined &&
      info.zonaHigh !== null &&
      info.zonaHigh !== undefined;

    if (absorcao) {
      return {
        texto: "ABSORÃ‡ÃƒO ATIVA",
        cor: "#ff00ff",
        detalhe: "Defesa institucional ativa dentro da zona"
      };
    }

    if (fase === "ROMPIMENTO" && direcao === "COMPRA") {
      return {
        texto: "ROMPIMENTO COMPRADOR",
        cor: "#00ffc8",
        detalhe: "Fluxo comprador em expansÃ£o"
      };
    }

    if (fase === "ROMPIMENTO" && direcao === "VENDA") {
      return {
        texto: "ROMPIMENTO VENDEDOR",
        cor: "#ff3333",
        detalhe: "Fluxo vendedor em expansÃ£o"
      };
    }

    if (fase === "EXAUSTAO") {
      return {
        texto: "EXAUSTÃƒO INSTITUCIONAL",
        cor: "#ffaa00",
        detalhe: "Fluxo extremo com risco de reversÃ£o"
      };
    }

    if (fase === "COMPRESSAO") {
      return {
        texto: "COMPRESSÃƒO INSTITUCIONAL",
        cor: "#ffaa00",
        detalhe: "Mercado comprimido dentro da zona institucional"
      };
    }

    if (fase === "ACUMULACAO") {
      if (direcao === "COMPRA" || seqDelta > 0 || trap === "COMPRA") {
        return {
          texto: "ACUMULAÃ‡ÃƒO COMPRADORA",
          cor: "#00d4ff",
          detalhe: "Compradores defendendo regiÃ£o"
        };
      }

      if (direcao === "VENDA" || seqDelta < 0 || trap === "VENDA") {
        return {
          texto: "ACUMULAÃ‡ÃƒO VENDEDORA",
          cor: "#ff6666",
          detalhe: "Vendedores defendendo regiÃ£o"
        };
      }

      return {
        texto: "ACUMULAÃ‡ÃƒO NEUTRA",
        cor: "#ffaa00",
        detalhe: "Zona institucional sem domÃ­nio claro"
      };
    }

    if (fase === "DISTRIBUICAO") {
      return {
        texto: "DISTRIBUIÃ‡ÃƒO VENDEDORA",
        cor: "#ff6666",
        detalhe: "Vendedores defendendo regiÃ£o"
      };
    }

    if (temHotZone) {
      if (compra > venda && scoreAgressao > 0) {
        return {
          texto: "DEFESA COMPRADORA",
          cor: "#00ff99",
          detalhe: "Hot zone com predominÃ¢ncia compradora"
        };
      }

      if (venda > compra && scoreAgressao < 0) {
        return {
          texto: "DEFESA VENDEDORA",
          cor: "#ff3333",
          detalhe: "Hot zone com predominÃ¢ncia vendedora"
        };
      }

      return {
        texto: "HOT ZONE NEUTRA",
        cor: "#ffaa00",
        detalhe: "RegiÃ£o institucional em observaÃ§Ã£o"
      };
    }

    if (scoreEngine >= 7 && direcao === "COMPRA") {
      return {
        texto: "CONTEXTO COMPRADOR",
        cor: "#00ff99",
        detalhe: "Score institucional favorece compra"
      };
    }

    if (scoreEngine >= 7 && direcao === "VENDA") {
      return {
        texto: "CONTEXTO VENDEDOR",
        cor: "#ff3333",
        detalhe: "Score institucional favorece venda"
      };
    }

    return {
      texto: "CONTEXTO NEUTRO",
      cor: "#00d4ff",
      detalhe: "Aguardando confirmaÃ§Ã£o institucional"
    };
  }, []);

 const atualizarHeatmap = useCallback((primeiroTime, ultimoTime, zonaLow, zonaHigh, absorcao, compra, venda) => {
    if (
      zonaLow === null ||
      zonaLow === undefined ||
      zonaHigh === null ||
      zonaHigh === undefined
    ) {
      setLinhaHorizontal(heatmap1Ref, primeiroTime, ultimoTime, null);
      setLinhaHorizontal(heatmap2Ref, primeiroTime, ultimoTime, null);
      setLinhaHorizontal(heatmap3Ref, primeiroTime, ultimoTime, null);
      setLinhaHorizontal(heatmap4Ref, primeiroTime, ultimoTime, null);
      setLinhaHorizontal(heatmap5Ref, primeiroTime, ultimoTime, null);
      return;
    }

    const low = Number(zonaLow);
    const high = Number(zonaHigh);

    if (!Number.isFinite(low) || !Number.isFinite(high) || high <= low) {
      setLinhaHorizontal(heatmap1Ref, primeiroTime, ultimoTime, null);
      setLinhaHorizontal(heatmap2Ref, primeiroTime, ultimoTime, null);
      setLinhaHorizontal(heatmap3Ref, primeiroTime, ultimoTime, null);
      setLinhaHorizontal(heatmap4Ref, primeiroTime, ultimoTime, null);
      setLinhaHorizontal(heatmap5Ref, primeiroTime, ultimoTime, null);
      return;
    }

    const faixa = high - low;

    setLinhaHorizontal(heatmap1Ref, primeiroTime, ultimoTime, low + faixa * 0.16);
    setLinhaHorizontal(heatmap2Ref, primeiroTime, ultimoTime, low + faixa * 0.33);
    setLinhaHorizontal(heatmap3Ref, primeiroTime, ultimoTime, low + faixa * 0.50);
    setLinhaHorizontal(heatmap4Ref, primeiroTime, ultimoTime, low + faixa * 0.66);
    setLinhaHorizontal(heatmap5Ref, primeiroTime, ultimoTime, low + faixa * 0.84);
// ---------- Heatmap visual reforÃ§ado ----------
const compraNum = Number(compra || 0);
const vendaNum = Number(venda || 0);

let corBase = "255, 170, 0"; // neutro laranja
let opacidadeLinha = 0.18;
let espessuraLinha = 2;

if (absorcao) {
  corBase = "255, 0, 255"; // magenta
  opacidadeLinha = 0.9;
  espessuraLinha = 4;
} else if (compraNum > vendaNum) {
  corBase = "0, 255, 153"; // verde
  opacidadeLinha = 0.45;
  espessuraLinha = 3;
} else if (vendaNum > compraNum) {
  corBase = "255, 51, 51"; // vermelho
  opacidadeLinha = 0.45;
  espessuraLinha = 3;
}

// Aplicando cores e opacidade reforÃ§ada nas 5 linhas
[heatmap1Ref, heatmap2Ref, heatmap3Ref, heatmap4Ref, heatmap5Ref].forEach((ref, i) => {
  const fatorOpacidade = i === 2 ? 1.0 : opacidadeLinha; // central mais visÃ­vel
  const fatorEspessura = i === 2 ? espessuraLinha : espessuraLinha - 1;
  ref.current?.applyOptions({
    color: `rgba(${corBase}, ${fatorOpacidade})`,
    lineWidth: fatorEspessura,
  });
});
   
  }, [setLinhaHorizontal]);
  const processarDados = useCallback((data) => {
    setWsStatus("ONLINE");

    let historico = ordenarPorTempo(data.historico || []);

    // Calibracao: remove candle fallback 100 quando ja existe preco real
    const historicoReal = historico.filter((c) => {
      const preco = Number(c?.close ?? c?.ultimo ?? c?.open ?? 0);
      return Number.isFinite(preco) && preco > 1000;
    });

    if (historicoReal.length > 0) {
      historico = historicoReal;
    }

    const vwap = ordenarPorTempo(data.vwap || []);
    const vwapSuperior = ordenarPorTempo(data.vwap_superior || []);
    const vwapInferior = ordenarPorTempo(data.vwap_inferior || []);

    if (!historico.length || !candleSeriesRef.current) return;

    const ultimoCandle = historico[historico.length - 1];
    const primeiroTime = historico[0].time;
    const ultimoTime = ultimoCandle.time;

    const ajustarJanelaGrafico = () => {
      if (!chartRef.current || !historico.length) return;

      const totalCandles = historico.length;

      chartRef.current.timeScale().setVisibleLogicalRange({
        from: Math.max(0, totalCandles - 120),
        to: totalCandles + 8,
      });
    };

    const engine = data.engine || {};
    const agressao = data.agressao || {};

    // IntegraÃ§Ã£o cognitiva TRIN â€” ConfluenceEngine v2.2
    const confluencia = data.confluencia || {};
    const evidenciasConfluencia =
      data.evidencias_confluencia ||
      confluencia.evidencias ||
      [];

    const evidenciaFiscal =
      evidenciasConfluencia.find((e) => e.nome === "FISCAL_TEMPORAL") || {};

    const evidenciaBernardo =
      evidenciasConfluencia.find((e) => e.nome === "BERNARDO") || {};

    const evidenciaHistoriador =
      evidenciasConfluencia.find((e) => e.nome === "HISTORIADOR") || {};

    const zonaLow = data.engine_zona_low ?? engine.engine_zona_low;
    const zonaHigh = data.engine_zona_high ?? engine.engine_zona_high;
    const absorcao = data.engine_absorcao ?? engine.engine_absorcao;

    const entradaBackend = data.entrada ?? data.sinal?.entrada ?? "AGUARDAR";

    // Calibracao do placar:
    // se o candle trouxer volume_compra/volume_venda real, ele manda no placar.
    // Isso evita o erro visual 100% / 0% quando o backend manda campo ja normalizado.
    const compraCandleReal = Number(
      ultimoCandle.volume_compra ??
      ultimoCandle.compra ??
      ultimoCandle.pressao_compra ??
      0
    );

    const vendaCandleReal = Number(
      ultimoCandle.volume_venda ??
      ultimoCandle.venda ??
      ultimoCandle.pressao_venda ??
      0
    );

    const compraTopo = Number(data.pressao_compra ?? agressao.persistencia_compra ?? 0);
    const vendaTopo = Number(data.pressao_venda ?? agressao.persistencia_venda ?? 0);

    const usarPressaoCandleReal =
      Number.isFinite(compraCandleReal) &&
      Number.isFinite(vendaCandleReal) &&
      compraCandleReal + vendaCandleReal > 1000;

    const compraPainelFonte = usarPressaoCandleReal ? compraCandleReal : compraTopo;
    const vendaPainelFonte = usarPressaoCandleReal ? vendaCandleReal : vendaTopo;

    const temEntradaPainel =
     entradaBackend.includes("COMPRA") ||
     entradaBackend.includes("VENDA");
    const baseInfo = {
      score: engine.engine_score ?? data.score ?? data.forca ?? data.sinal?.forca, 
      sinal: data.sinal?.sinal ?? data.sinal ?? "SEM ENTRADA",
      entrada: entradaBackend,
      tendencia: data.tendencia ?? data.sinal?.tendencia ?? "NEUTRO",

      frequencia: data.frequencia_mercado ?? agressao.frequencia_mercado,
      intensidade: data.intensidade_fluxo ?? agressao.intensidade_fluxo,
      scoreAgressao: data.score_agressao ?? agressao.score_agressao,
      leituraAgressao: data.leitura_agressao ?? agressao.leitura_agressao,

      saldo: data.saldo_agressor ?? ultimoCandle.saldo,
      delta: data.delta ?? ultimoCandle.delta,
      volume: data.volume ?? ultimoCandle.volume,

      // Calibracao recuperada: painel usa ultimo candle real como fonte visual
      open: ultimoCandle.open,
      high: ultimoCandle.high,
      low: ultimoCandle.low,
      close: ultimoCandle.close,
      ultimo: ultimoCandle.ultimo ?? ultimoCandle.close,
      maximo: ultimoCandle.high,
      minimo: ultimoCandle.low,
      vwap: data.vwap_atual ?? data.vwap_real ?? ultimoCandle.vwap ?? ultimoCandle.vwap_real,
      fonteDados: ultimoCandle.fonte_dados,
      abaOrigem: ultimoCandle.aba_origem,

      compra: compraPainelFonte,
      venda: vendaPainelFonte,

      explosao:
        data.tipo_explosao ??
        agressao.tipo_explosao ??
        (data.explosao_detectada ? "EXPLOSÃƒO DETECTADA" : "SEM EXPLOSÃƒO"),

      explosaoDetectada:
        data.explosao_detectada ??
        agressao.explosao_detectada ??
        false,

      engineScore: data.engine_score ?? engine.engine_score,
      engineFase: data.engine_fase ?? engine.engine_fase,
      engineDirecao: data.engine_direcao ?? engine.engine_direcao,
      engineTrap: data.engine_trap ?? engine.engine_trap,
      engineAbsorcao: absorcao,
      engineSeqDelta: data.engine_seq_delta ?? engine.engine_seq_delta,

      // Campos cognitivos oficiais do TRIN
      scoreConfluencia:
        data.score_confluencia ??
        confluencia.score_confluencia,

      direcaoConfluencia:
        data.direcao_confluencia ??
        confluencia.direcao ??
        "NEUTRO",

      qualidadeConfluencia:
        data.qualidade_confluencia ??
        confluencia.qualidade ??
        "DESCONHECIDO",

      alertaConfluencia:
        data.alerta_confluencia ??
        confluencia.alerta ??
        "SEM ALERTA",

      bloqueioCognitivo:
        data.bloqueio_cognitivo === true ||
        data.qualidade_confluencia === "BLOQUEADO_POR_CERTIFICACAO" ||
        confluencia.qualidade === "BLOQUEADO_POR_CERTIFICACAO",

      fiscalStatus:
        data.status_certificacao ??
        evidenciaFiscal?.valor?.status ??
        "DESCONHECIDO",

      bernardoStatus:
        evidenciaBernardo?.valor?.status ??
        "SEM BERNARDO",

      bernardoSimilaridade:
        evidenciaBernardo?.valor?.similaridade ??
        "-",

      historiadorPadrao:
        evidenciaHistoriador?.valor?.padrao ??
        "SEM PADRAO",

      historiadorScore:
        evidenciaHistoriador?.valor?.score_historico ??
        "-",

      qtdEvidenciasConfluencia:
        evidenciasConfluencia.length,

      contratoAtivo:
        data.contrato_ativo || {},

      contratoAtivoStatus:
        data.contrato_ativo_status ||
        data.contrato_ativo?.status_validacao ||
        "SEM STATUS",

      contratoAtivoMotivo:
        data.contrato_ativo_motivo ||
        data.contrato_ativo?.motivo ||
        "",

      contratoAtivoBloqueio:
        Boolean(
          data.contrato_ativo_bloqueio ||
          data.contrato_ativo?.bloqueio_operacional
        ),

      painelTemporal: data.painel_temporal || {},
      painelRegua:
        data.painel_temporal?.regua_painel ||
        data.painel_temporal?.tipo_candle ||
        "DESCONHECIDA",
      painelTimeframe:
        data.painel_temporal?.timeframe_painel ||
        "DESCONHECIDO",
      painelOrigemTemporal:
        data.painel_temporal?.origem ||
        "DESCONHECIDA",
      painelFractalOficial:
        data.painel_temporal?.fractal_oficial ||
        "NAO_INFORMADO",
      painelStatus:
        data.painel_temporal?.status_painel ||
        "DESCONHECIDO",
      painelTimeframesDisponiveis:
        data.painel_temporal?.timeframes_disponiveis ||
        ["15s", "30s", "1_MIN", "2_MIN", "5_MIN", "10_MIN", "15_MIN", "30_MIN", "60_MIN", "DIARIO", "SEMANAL"],
      painelTimeframesReservados:
        data.painel_temporal?.timeframes_reservados ||
        ["DIARIO", "SEMANAL"],

      contratoExcelRtd:
        data.contrato_ativo?.contrato_excel_rtd || "-",

      contratoEsperadoRtd:
        data.contrato_ativo?.contrato_esperado_rtd || "-",

      contratoResolverStatus:
        data.contrato_ativo?.resolver_status || "-",

      justificativaConfluencia:
        data.justificativa_confluencia ??
        confluencia.justificativa ??
        "",

      zonaLow,
      zonaHigh,

     stop: temEntradaPainel ? data.stop : null,
parcial: temEntradaPainel ? data.parcial : null,
alvo: temEntradaPainel ? data.alvo : null,
    };

    const contexto = calcularContextoInstitucional(baseInfo);

    const fiscalBloqueandoConfluencia =
      data.qualidade_confluencia === "BLOQUEADO_POR_CERTIFICACAO" ||
      String(data.alerta_confluencia || "").includes("FISCAL");

    const direcaoContexto = baseInfo.engineDirecao || "NEUTRO";

    const contextoTextoFinal =
      fiscalBloqueandoConfluencia && direcaoContexto !== "NEUTRO"
        ? `${direcaoContexto} BLOQUEADA PELO FISCAL`
        : fiscalBloqueandoConfluencia
          ? "CONFLUENCIA BLOQUEADA PELO FISCAL"
          : contexto.texto;

    const contextoDetalheFinal =
      fiscalBloqueandoConfluencia
        ? "Contrato aprovado, mas confluencia operacional aguardando certificacao fiscal"
        : contexto.detalhe;

    const contextoCorFinal =
      fiscalBloqueandoConfluencia
        ? "#ff3333"
        : contexto.cor;

    const fiscalStatusFinal =
      fiscalBloqueandoConfluencia
        ? "BLOQUEANDO CONFLUENCIA"
        : (
            data.fiscal_status ||
            data.status_certificacao ||
            baseInfo.fiscalStatus ||
            "DESCONHECIDO"
          );

    setDataInfo({
      ...baseInfo,

      qualidadeConfluencia: data.qualidade_confluencia,
      alertaConfluencia: data.alerta_confluencia,
      fiscalStatus: fiscalStatusFinal,
      contratoAtivoStatus: data.contrato_ativo_status,
      contratoAtivoBloqueio: data.contrato_ativo_bloqueio,

      contextoInstitucional: contextoTextoFinal,
      contextoTexto: contextoTextoFinal,
      contextoCor: contextoCorFinal,
      contextoDetalhe: contextoDetalheFinal,
    });

    if (!carregouHistoricoRef.current) {
      candleSeriesRef.current.setData(historico);
      vwapLineRef.current.setData(vwap);
      vwapSuperiorRef.current.setData(vwapSuperior);
      vwapInferiorRef.current.setData(vwapInferior);

      if (typeof candleSeriesRef.current.setMarkers === "function") {
        candleSeriesRef.current.setMarkers(gerarMarkersInstitucionais(historico));
      }

      if (chartRef.current) {
        chartRef.current.timeScale().fitContent();
      }

      carregouHistoricoRef.current = true;
    } else {
      const precoValidoPainel =
        Number(ultimoCandle.close) > 1000 &&
        Number.isFinite(Number(ultimoCandle.close));

      if (precoValidoPainel) {
        candleSeriesRef.current.update(ultimoCandle);
      }

      if (vwap.length) {
        vwapLineRef.current.update(vwap[vwap.length - 1]);
      }

      if (vwapSuperior.length) {
        vwapSuperiorRef.current.update(vwapSuperior[vwapSuperior.length - 1]);
      }

      if (vwapInferior.length) {
        vwapInferiorRef.current.update(vwapInferior[vwapInferior.length - 1]);
      }

      if (typeof candleSeriesRef.current.setMarkers === "function") {
        candleSeriesRef.current.setMarkers(gerarMarkersInstitucionais(historico));
      }
    }

    ajustarJanelaGrafico();

const entradaAtual = baseInfo.entrada || "";
const scoreAtual = Number(baseInfo.score || 0);
const faseAtual = baseInfo.engineFase || "AGUARDANDO";
const contextoAtual = baseInfo.contextoInstitucional || "";
const direcaoAtual = baseInfo.engineDirecao || "NEUTRO";

const ehScalping =
  entradaAtual.includes("SCALPING");

const temEntradaReal =
  ehScalping
    ? (
        entradaAtual.includes("COMPRA") ||
        entradaAtual.includes("VENDA")
      )
    : (
        (
          entradaAtual.includes("COMPRA") ||
          entradaAtual.includes("VENDA")
        ) &&
        scoreAtual >= 5 &&
        faseAtual !== "AGUARDANDO" &&
        !contextoAtual.includes("NEUTRO") &&
        direcaoAtual !== "NEUTRO"
      );

if (temEntradaReal) {
  setLinhaHorizontal(stopLineRef, primeiroTime, ultimoTime, data.stop);
  setLinhaHorizontal(parcialLineRef, primeiroTime, ultimoTime, data.parcial);
  setLinhaHorizontal(alvoLineRef, primeiroTime, ultimoTime, data.alvo);

  atualizarPriceLineExecucao(stopPriceLineRef, "STOP", data.stop, "#ff1f1f", 0);
  atualizarPriceLineExecucao(parcialPriceLineRef, "PARCIAL", data.parcial, "#ffd700", 2);
  atualizarPriceLineExecucao(alvoPriceLineRef, "ALVO", data.alvo, "#00ff88", 0);

} else {
  setLinhaHorizontal(stopLineRef, primeiroTime, ultimoTime, null);
  setLinhaHorizontal(parcialLineRef, primeiroTime, ultimoTime, null);
  setLinhaHorizontal(alvoLineRef, primeiroTime, ultimoTime, null);

  atualizarPriceLineExecucao(stopPriceLineRef, "STOP", null, "#ff1f1f", 0);
  atualizarPriceLineExecucao(parcialPriceLineRef, "PARCIAL", null, "#ffd700", 2);
  atualizarPriceLineExecucao(alvoPriceLineRef, "ALVO", null, "#00ff88", 0);
}
    setLinhaHorizontal(hotZoneTopRef, primeiroTime, ultimoTime, zonaHigh);
    setLinhaHorizontal(hotZoneBottomRef, primeiroTime, ultimoTime, zonaLow);

    atualizarHeatmap(
      primeiroTime,
      ultimoTime,
      zonaLow,
      zonaHigh,
      absorcao,
      baseInfo.compra,
      baseInfo.venda
    );

    if (
      absorcao &&
      zonaLow !== null &&
      zonaLow !== undefined &&
      zonaHigh !== null &&
      zonaHigh !== undefined
    ) {
      const meioZona = (Number(zonaLow) + Number(zonaHigh)) / 2;
      setLinhaHorizontal(absorcaoLineRef, primeiroTime, ultimoTime, meioZona);
    } else {
      setLinhaHorizontal(absorcaoLineRef, primeiroTime, ultimoTime, null);
    }
  }, [
    atualizarPriceLineExecucao,
    ordenarPorTempo,
    gerarMarkersInstitucionais,
    setLinhaHorizontal,
    atualizarHeatmap,
    calcularContextoInstitucional,
  ]);
 

  useEffect(() => {
    if (!chartContainerRef.current) return;

    carregouHistoricoRef.current = false;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: window.innerHeight - 20,
      layout: {
        background: { type: "solid", color: "#020816" },
        textColor: "#ffffff",
      },
      grid: {
        vertLines: { color: "#1c2f4a" },
        horzLines: { color: "#1c2f4a" },
      },
      rightPriceScale: {
        borderColor: "#334158",
      },
      timeScale: {
        borderColor: "#334158",
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 8,
        barSpacing: 4,
        minBarSpacing: 3,
        fixLeftEdge: false,
        fixRightEdge: false,
      },
    });

    chartRef.current = chart;

    candleSeriesRef.current = chart.addCandlestickSeries({
      upColor: "#00ffc8",
      downColor: "#ff4444",
      borderUpColor: "#00ffc8",
      borderDownColor: "#ff4444",
      wickUpColor: "#00ffc8",
      wickDownColor: "#ff4444",
    });

    stopLineRef.current = chart.addLineSeries({
      color: "#ff0000",
      lineWidth: 1,
      lineStyle: 2,
    });

    parcialLineRef.current = chart.addLineSeries({
      color: "#ffff00",
      lineWidth: 1,
      lineStyle: 2,
    });

    alvoLineRef.current = chart.addLineSeries({
      color: "#00ff66",
      lineWidth: 1,
      lineStyle: 2,
    });

    vwapLineRef.current = chart.addLineSeries({
      color: "#0066ff",
      lineWidth: 3,
    });

    vwapSuperiorRef.current = chart.addLineSeries({
      color: "#00ffff",
      lineWidth: 1,
      lineStyle: 2,
    });

    vwapInferiorRef.current = chart.addLineSeries({
      color: "#00ffff",
      lineWidth: 1,
      lineStyle: 2,
    });

    hotZoneTopRef.current = chart.addLineSeries({
      color: "#ffaa00",
      lineWidth: 4,
      lineStyle: 2,
    });

    hotZoneBottomRef.current = chart.addLineSeries({
      color: "#ffaa00",
      lineWidth: 4,
      lineStyle: 2,
    });

    heatmap1Ref.current = chart.addLineSeries({
      color: "rgba(255, 170, 0, 0.18)",
      lineWidth: 2,
      lineStyle: 0,
    });

    heatmap2Ref.current = chart.addLineSeries({
      color: "rgba(255, 170, 0, 0.30)",
      lineWidth: 2,
      lineStyle: 0,
    });

    heatmap3Ref.current = chart.addLineSeries({
      color: "rgba(255, 170, 0, 0.60)",
      lineWidth: 3,
      lineStyle: 0,
    });

    heatmap4Ref.current = chart.addLineSeries({
      color: "rgba(255, 170, 0, 0.30)",
      lineWidth: 2,
      lineStyle: 0,
    });

    heatmap5Ref.current = chart.addLineSeries({
      color: "rgba(255, 170, 0, 0.18)",
      lineWidth: 2,
      lineStyle: 0,
    });

    absorcaoLineRef.current = chart.addLineSeries({
      color: "#ff00ff",
      lineWidth: 3,
      lineStyle: 1,
    });

    socketRef.current = connectTrinWebSocket(
      (data) => {
        setWsStatus("ONLINE");
        processarDados(data);
      },
      setWsStatus
    );

    const handleResize = () => {
      if (!chartContainerRef.current || !chartRef.current) return;

      chartRef.current.applyOptions({
        width: chartContainerRef.current.clientWidth,
        height: window.innerHeight - 20,
      });

      chartRef.current.timeScale().fitContent();
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);

      if (socketRef.current) {
        disconnectTrinWebSocket();
      }

      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }

      candleSeriesRef.current = null;

      stopLineRef.current = null;
      parcialLineRef.current = null;
      alvoLineRef.current = null;

      vwapLineRef.current = null;
      vwapSuperiorRef.current = null;
      vwapInferiorRef.current = null;

      hotZoneTopRef.current = null;
      hotZoneBottomRef.current = null;
      absorcaoLineRef.current = null;

      heatmap1Ref.current = null;
      heatmap2Ref.current = null;
      heatmap3Ref.current = null;
      heatmap4Ref.current = null;
      heatmap5Ref.current = null;
    };
  }, [processarDados]);

  async function alterarTimeframePainel(timeframe) {
    try {
      const resposta = await fetch(`http://127.0.0.1:8001/painel/timeframe/${timeframe}`);
      const resultado = await resposta.json();

      if (!resultado.ok) {
        alert(`${resultado.status || "TIMEFRAME_NAO_APLICADO"}: ${resultado.motivo || "Timeframe nao liberado."}`);
        return;
      }

      carregouHistoricoRef.current = false;

      if (candleSeriesRef.current) {
        candleSeriesRef.current.setData([]);
      }

      if (vwapLineRef.current) {
        vwapLineRef.current.setData([]);
      }

      if (vwapSuperiorRef.current) {
        vwapSuperiorRef.current.setData([]);
      }

      if (vwapInferiorRef.current) {
        vwapInferiorRef.current.setData([]);
      }
    } catch (erro) {
      console.error("Erro ao alterar timeframe do painel:", erro);
      alert("Erro ao alterar timeframe do painel.");
    }
  }

  const statusVisual = dataInfo.volume !== undefined ? "ONLINE" : wsStatus;

  const scoreAgressao = Number(dataInfo.scoreAgressao || 0);
  const compra = Number(dataInfo.compra || 0);
  const venda = Number(dataInfo.venda || 0);

  const temHotZone =
    dataInfo.zonaLow !== null &&
    dataInfo.zonaLow !== undefined &&
    dataInfo.zonaHigh !== null &&
    dataInfo.zonaHigh !== undefined;

  const glowRadar =
    statusVisual === "ONLINE"
      ? dataInfo.contextoCor ||
        (dataInfo.engineAbsorcao
          ? "#ff00ff"
          : temHotZone
          ? "#ffaa00"
          : dataInfo.explosao && dataInfo.explosao !== "SEM EXPLOSÃƒO"
          ? "#ffaa00"
          : scoreAgressao > 15
          ? "#00ff99"
          : scoreAgressao < -15
          ? "#ff3333"
          : compra > venda
          ? "#00ffc8"
          : venda > compra
          ? "#ff4444"
          : "#00d4ff")
      : "#ff4444";


  useEffect(() => {
    let ativo = true;

    async function carregarTtRawStatus() {
      try {
        const resposta = await fetch("http://127.0.0.1:8001/tt/raw/status");
        const json = await resposta.json();

        if (!ativo) return;

        setTtRawStatus(json);
        setTtRawErro("");
      } catch (erro) {
        if (!ativo) return;

        setTtRawErro("TT_RAW_STATUS_INDISPONIVEL");
      }
    }

    carregarTtRawStatus();

    const timer = setInterval(carregarTtRawStatus, 15000);

    return () => {
      ativo = false;
      clearInterval(timer);
    };
  }, []);

  const ultimoPainel = dataInfo.ultimo ?? dataInfo.close ?? dataInfo.preco ?? "-";
  const maximaPainel = dataInfo.maximo ?? dataInfo.maxima ?? dataInfo.high ?? "-";
  const minimaPainel = dataInfo.minimo ?? dataInfo.minima ?? dataInfo.low ?? "-";
  const volumePainel = dataInfo.volume ?? "-";
  const deltaPainel = dataInfo.delta ?? "-";
  const saldoPainel = dataInfo.saldo ?? "-";
  const vwapPainel = dataInfo.vwap ?? dataInfo.vwapReal ?? dataInfo.vwap_real ?? "-";
  const distVwapPainel = dataInfo.distanciaVwap ?? dataInfo.distancia_vwap ?? "-";

  const direcaoPainel = dataInfo.direcaoConfluencia || dataInfo.engineDirecao || "NEUTRO";
  const entradaTexto = String(dataInfo.entrada || "AGUARDAR").toUpperCase();

  const bloqueadoPainel =
    Boolean(dataInfo.bloqueioCognitivo) ||
    Boolean(dataInfo.contratoAtivoBloqueio) ||
    dataInfo.qualidadeConfluencia === "BLOQUEADO_POR_CERTIFICACAO";

  const temEntradaValida =
    !bloqueadoPainel &&
    entradaTexto &&
    !["AGUARDAR", "SEM ENTRADA", "SEM SINAL", "-", "NAO", "NÃO"].includes(entradaTexto) &&
    dataInfo.stop != null &&
    dataInfo.parcial != null &&
    dataInfo.alvo != null;

  const alertaPainel = dataInfo.alertaConfluencia || "";
  const temAlerta =
    Boolean(alertaPainel && alertaPainel !== "SEM ALERTA") ||
    Boolean(dataInfo.engineAbsorcao) ||
    Boolean(temHotZone) ||
    Boolean(dataInfo.explosao && dataInfo.explosao !== "SEM EXPLOSÃO");

  const statusFinalPainel = bloqueadoPainel ? "BLOQUEADO" : "MONITORANDO";
  const macroPainel = dataInfo.contextoInstitucional || "AGUARDANDO";
  const microPainel = dataInfo.contextoDetalhe || "Aguardando dados institucionais";
  const topoPainel = dataInfo.ultimoTopo ?? dataInfo.ultimo_topo ?? "-";
  const fundoPainel = dataInfo.ultimoFundo ?? dataInfo.ultimo_fundo ?? "-";

  const corEstadoPainel =
    bloqueadoPainel ? "#ff3333" :
    direcaoPainel === "COMPRA" ? "#00ff77" :
    direcaoPainel === "VENDA" ? "#ff4444" :
    "#00d9ff";

  const bloqueioPorFiscalPainel =
    dataInfo.qualidadeConfluencia === "BLOQUEADO_POR_CERTIFICACAO" ||
    String(dataInfo.alertaConfluencia || "").includes("FISCAL");

  const motivoBloqueioPainel =
    bloqueioPorFiscalPainel
      ? "FISCAL BLOQUEANDO CONFLUENCIA"
      : dataInfo.contratoAtivoBloqueio
        ? "CONTRATO BLOQUEADO"
        : bloqueadoPainel
          ? "BLOQUEIO OPERACIONAL"
          : "SEM BLOQUEIO";

  const estadoCentralPainel =
    bloqueadoPainel
      ? "AGUARDAR"
      : temEntradaValida
        ? "ENTRADA"
        : direcaoPainel;

  const subtituloCentralPainel =
    bloqueadoPainel
      ? "BLOQUEADO"
      : temEntradaValida
        ? "VALIDADA"
        : "MONITORANDO";

  const acaoPrincipalPainel =
    bloqueioPorFiscalPainel ? "AGUARDAR CERTIFICACAO" :
    bloqueadoPainel ? "AGUARDAR CONFIRMACAO" :
    temEntradaValida ? String(dataInfo.entrada || "ENTRADA") :
    direcaoPainel === "COMPRA" ? "MONITORAR COMPRA" :
    direcaoPainel === "VENDA" ? "MONITORAR VENDA" :
    "MONITORAR MERCADO";

  const contextoIndicadorPainel =
    bloqueioPorFiscalPainel
      ? "FISCAL"
      : bloqueadoPainel
        ? "BLOQ"
        : (dataInfo.score ?? 0);

  const statusConfluenciaPainel =
    bloqueioPorFiscalPainel
      ? "BLOQ"
      : bloqueadoPainel
        ? "BLOQ"
        : temEntradaValida
          ? "LIB"
          : "MON";

  const autorizacaoOperacionalPainel =
    bloqueioPorFiscalPainel
      ? "BLOQUEADA PELO FISCAL"
      : bloqueadoPainel
        ? "BLOQUEADA"
        : temEntradaValida
          ? "LIBERADA"
          : "AGUARDANDO";

  const alertaPrincipalPainel =
    alertaPainel && alertaPainel !== "SEM ALERTA"
      ? alertaPainel
      : bloqueadoPainel
        ? "CONFLUENCIA BLOQUEADA"
        : "SEM ALERTA CRITICO";

  const compraBrutaPainel = Math.max(0, Number(dataInfo.compra || 0));
  const vendaBrutaPainel = Math.max(0, Number(dataInfo.venda || 0));
  const totalPressaoPainel = compraBrutaPainel + vendaBrutaPainel;

  const compraPctPainel =
    totalPressaoPainel > 0
      ? Math.round((compraBrutaPainel / totalPressaoPainel) * 100)
      : 0;

  const vendaPctPainel =
    totalPressaoPainel > 0
      ? Math.max(0, 100 - compraPctPainel)
      : 0;

  const forcaPlacarPainel = Math.max(compraPctPainel, vendaPctPainel);
  const barrasPlacarPainel = Math.max(0, Math.round((forcaPlacarPainel / 100) * 14));
  const barrasAlertaPainel = Math.max(0, Math.round((forcaPlacarPainel / 100) * 18));

  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        padding: 18,
        boxSizing: "border-box",
        background: "radial-gradient(circle at center, #172324 0%, #081013 42%, #010409 100%)",
        color: "#ffffff",
        overflow: "hidden",
        display: "grid",
        gridTemplateColumns: "37% 22% 41%",
        gridTemplateRows: "1fr 170px",
        gap: 16,
        fontFamily: "Arial, sans-serif",
      }}
    >
      <style>
        {`
          @keyframes pulseRadar {
            0% { transform: scale(0.92); opacity: 0.5; }
            50% { transform: scale(1.08); opacity: 1; }
            100% { transform: scale(0.92); opacity: 0.5; }
          }

          @keyframes spinScanner {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }

          @keyframes hotPulse {
            0% { opacity: .45; box-shadow: 0 0 18px #ffaa00; }
            50% { opacity: 1; box-shadow: 0 0 35px #ffaa00; }
            100% { opacity: .45; box-shadow: 0 0 18px #ffaa00; }
          }
        `}
      </style>

      <div
        style={{
          gridColumn: "1",
          gridRow: "1",
          padding: "30px 28px",
          borderRadius: 24,
          background: "linear-gradient(180deg, rgba(13,22,24,0.70), rgba(1,5,8,0.94))",
          border: "1px solid rgba(0,217,255,0.14)",
          boxShadow: "inset 0 0 55px rgba(0,255,180,0.04), 0 0 28px rgba(0,217,255,0.08)",
          overflow: "hidden",
        }}
      >
        <div style={{ color: "#00d9ff", fontSize: 13, fontWeight: "900", marginBottom: 30 }}>
          TRIN Updates
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 22 }}>
          <div style={{ height: 1, flex: 1, background: "rgba(255,255,255,0.45)" }} />
          <div style={{ color: "#cfd8dc", fontSize: 16 }}>
            Nova Atualizacao
          </div>
          <div style={{ height: 1, flex: 1, background: "rgba(255,255,255,0.45)" }} />
        </div>

        <div style={{ color: "#d7dde1", fontSize: 15, lineHeight: 1.55, marginBottom: 18 }}>
          CONTEXTO: {macroPainel}
        </div>

        <div style={{ color: corEstadoPainel, fontSize: 15, fontWeight: "900", lineHeight: 1.55, marginBottom: 18 }}>
          CENARIO: {microPainel}
        </div>

        <div style={{ color: "#d7dde1", fontSize: 14, lineHeight: 1.6, marginBottom: 28 }}>
          • Direcao: {direcaoPainel}<br />
          • Entrada: {temEntradaValida ? dataInfo.entrada : "AGUARDAR"}<br />
          • Autorizacao: {autorizacaoOperacionalPainel}<br />
          • Qualidade: {dataInfo.qualidadeConfluencia || "DESCONHECIDA"}<br />
          • Fiscal: {dataInfo.fiscalStatus || "DESCONHECIDO"}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 22, marginBottom: 18 }}>
          <div style={{ color: "#8f9aa3", fontWeight: "900", fontStyle: "italic", fontSize: 20, lineHeight: 1.05 }}>
            SMART<br />MONEY
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8, flex: 1 }}>
            {[
              ["1", formatar(ultimoPainel), "#8b1f1f", "#ff5555"],
              ["2", formatar(minimaPainel), "#006b3c", "#00ff99"],
              ["3", formatar(vwapPainel), "#006b3c", "#00ff99"],
              ["4", formatar(maximaPainel), "#8b1f1f", "#ff5555"],
            ].map(([n, valor, fundo, borda]) => (
              <div key={n} style={{ textAlign: "center" }}>
                <div style={{ fontWeight: "900", marginBottom: 5 }}>{n}</div>
                <div style={{ padding: "8px 4px", borderRadius: 7, background: fundo, border: `1px solid ${borda}`, fontWeight: "900" }}>
                  {valor}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div
          style={{
            marginTop: 26,
            padding: "14px 18px",
            borderRadius: 10,
            border: `1px solid ${corEstadoPainel}`,
            color: corEstadoPainel,
            fontWeight: "900",
            fontSize: 28,
            letterSpacing: 2,
            textAlign: "center",
            boxShadow: `0 0 24px ${corEstadoPainel}55`,
          }}
        >
          {bloqueadoPainel ? motivoBloqueioPainel : acaoPrincipalPainel}
        </div>

        <div style={{ marginTop: 34 }}>
          <div style={{ color: "#cfd8dc", fontSize: 12, fontWeight: "900", marginBottom: 10 }}>
            PLACAR ESTATISTICO
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "110px 110px 1fr", gap: 14, alignItems: "end" }}>
            <div style={{ border: "1px solid rgba(0,255,120,0.45)", borderRadius: 10, padding: 12, textAlign: "center" }}>
              <div style={{ color: "#00ff77", fontSize: 12, fontWeight: "900" }}>COMPRA</div>
              <div style={{ color: "#ffffff", fontSize: 24, fontWeight: "900" }}>{compraPctPainel}%</div>
            </div>

            <div style={{ border: "1px solid rgba(255,60,60,0.45)", borderRadius: 10, padding: 12, textAlign: "center" }}>
              <div style={{ color: "#ff4444", fontSize: 12, fontWeight: "900" }}>VENDA</div>
              <div style={{ color: "#ffffff", fontSize: 24, fontWeight: "900" }}>{vendaPctPainel}%</div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(14, 1fr)", gap: 5 }}>
              {Array.from({ length: 14 }).map((_, i) => (
                <div
                  key={i}
                  style={{
                    height: 42,
                    borderRadius: 3,
                    background: i < barrasPlacarPainel ? corEstadoPainel : "rgba(255,255,255,0.16)",
                    boxShadow: i < barrasPlacarPainel ? `0 0 12px ${corEstadoPainel}` : "none",
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      <div
        style={{
          gridColumn: "2",
          gridRow: "1",
          position: "relative",
          borderRadius: 24,
          background: "linear-gradient(180deg, rgba(11,18,20,0.58), rgba(0,3,8,0.90))",
          border: "1px solid rgba(255,255,255,0.10)",
          boxShadow: "inset 0 0 65px rgba(255,255,255,0.04), 0 0 22px rgba(0,217,255,0.06)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "32px 20px",
          overflow: "hidden",
        }}
      >
        <div style={{ alignSelf: "stretch", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ color: "#8a969e", fontSize: 12, fontWeight: "900" }}>CONTEXTO</div>
            <div style={{ color: corEstadoPainel, fontSize: 34, fontWeight: "900", marginTop: 8 }}>
              {contextoIndicadorPainel}
            </div>
          </div>

          <div style={{ textAlign: "center" }}>
            <div style={{ color: "#8a969e", fontSize: 12, fontWeight: "900" }}>CONFL</div>
            <div style={{ color: corEstadoPainel, fontSize: 34, fontWeight: "900", marginTop: 8 }}>
              {formatar(dataInfo.scoreConfluencia)}
            </div>
            <div style={{ color: corEstadoPainel, fontSize: 11, fontWeight: "900", letterSpacing: 1, marginTop: 3 }}>
              {statusConfluenciaPainel}
            </div>
          </div>
        </div>

        <div
          style={{
            width: 250,
            height: 190,
            border: "1px solid rgba(255,255,255,0.18)",
            borderRadius: 28,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: `0 0 44px ${corEstadoPainel}22, inset 0 0 34px rgba(255,255,255,0.04)`,
          }}
        >
          <div
            style={{
              width: 0,
              height: 0,
              borderLeft: "48px solid transparent",
              borderRight: "48px solid transparent",
              borderBottom: `86px solid ${corEstadoPainel}`,
              filter: `drop-shadow(0 0 22px ${corEstadoPainel})`,
              transform: direcaoPainel === "VENDA" ? "rotate(180deg)" : "none",
            }}
          />
        </div>

        <div style={{ textAlign: "center" }}>
          <div style={{ color: corEstadoPainel, fontSize: 32, fontWeight: "900" }}>
            {estadoCentralPainel}
          </div>
          <div style={{ color: "#b0bec5", fontSize: 13, fontWeight: "bold", marginTop: 6 }}>
            {subtituloCentralPainel}
          </div>
          <div style={{ color: "#8a969e", fontSize: 11, fontWeight: "900", marginTop: 10 }}>
            DIRECAO: {direcaoPainel}
          </div>
        </div>

        <div
          style={{
            width: 4,
            height: 130,
            borderRadius: 999,
            background: corEstadoPainel,
            boxShadow: `0 0 25px ${corEstadoPainel}`,
            opacity: 0.95,
          }}
        />
      </div>

      <div
        style={{
          gridColumn: "3",
          gridRow: "1",
          borderRadius: 18,
          border: `1px solid ${corEstadoPainel}`,
          background: "#020712",
          boxShadow: `0 0 28px ${corEstadoPainel}88, inset 0 0 24px rgba(0,217,255,0.04)`,
          overflow: "hidden",
          position: "relative",
        }}
      >
        <TopBar dataInfo={dataInfo} cor={corEstadoPainel} wsStatus={statusVisual} />

        {temHotZone && (
          <HotZoneOverlay
            low={dataInfo.zonaLow}
            high={dataInfo.zonaHigh}
            absorcao={dataInfo.engineAbsorcao}
            compra={dataInfo.compra}
            venda={dataInfo.venda}
          />
        )}

        <div ref={chartContainerRef} style={{ height: "100%" }} />
      </div>

      <div
        style={{
          gridColumn: "1 / 4",
          gridRow: "2",
          borderRadius: 18,
          background: "linear-gradient(90deg, rgba(4,10,13,0.97), rgba(3,15,12,0.94), rgba(4,10,13,0.97))",
          border: `1px solid ${corEstadoPainel}`,
          boxShadow: `0 0 30px ${corEstadoPainel}66`,
          display: "grid",
          gridTemplateColumns: "240px 1fr 330px",
          gap: 18,
          alignItems: "center",
          padding: "16px 24px",
        }}
      >
        <div>
          <div style={{ color: corEstadoPainel, fontSize: 32, fontWeight: "900", letterSpacing: 2 }}>
            ALERTA
          </div>
          <div style={{ color: "#d0d7dc", fontSize: 12, fontWeight: "bold" }}>
            {motivoBloqueioPainel || alertaPrincipalPainel}
          </div>
        </div>

        <div>
          <div style={{ color: corEstadoPainel, fontSize: 38, fontWeight: "900", textAlign: "center", letterSpacing: 3 }}>
            {acaoPrincipalPainel}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(18, 1fr)", gap: 5, marginTop: 16 }}>
            {Array.from({ length: 18 }).map((_, i) => (
              <div
                key={i}
                style={{
                  height: 34,
                  borderRadius: 3,
                  background: i < barrasAlertaPainel ? corEstadoPainel : "rgba(255,255,255,0.18)",
                  boxShadow: i < barrasAlertaPainel ? `0 0 12px ${corEstadoPainel}` : "none",
                }}
              />
            ))}
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
          <Box color="#12313d">ULTIMO<br />{formatar(ultimoPainel)}</Box>
          <Box color="#263238">VWAP<br />{formatar(vwapPainel)}</Box>
          <Box color={Number(deltaPainel || 0) >= 0 ? "#004d40" : "#4a0000"}>DELTA<br />{deltaPainel}</Box>
          <Box color={Number(saldoPainel || 0) >= 0 ? "#004d40" : "#4a0000"}>SALDO<br />{saldoPainel}</Box>
        </div>
      </div>
    </div>
  );
}

function HotZoneOverlay({ low, high, absorcao, compra, venda }) {
  const compraNum = Number(compra || 0);
  const vendaNum = Number(venda || 0);

  let cor = "#ffaa00";
  let texto = "HOT ZONE NEUTRA";

  if (absorcao) {
    cor = "#ff00ff";
    texto = "HOT ZONE â€¢ ABSORÃ‡ÃƒO";
  } else if (compraNum > vendaNum) {
    cor = "#00ff99";
    texto = "DEFESA COMPRADORA";
  } else if (vendaNum > compraNum) {
    cor = "#ff3333";
    texto = "DEFESA VENDEDORA";
  }

  return (
    <div
      style={{
        position: "absolute",
        zIndex: 8,
        left: 20,
        bottom: 20,
        padding: "8px 12px",
        borderRadius: 8,
        background: `rgba(2, 8, 22, 0.88)`,
        color: cor,
        border: `1px solid ${cor}`,
        fontSize: 12,
        fontWeight: "900",
        animation: "hotPulse 1.6s infinite",
        boxShadow: `0 0 28px ${cor}`,
        pointerEvents: "none",
      }}
    >
      {texto} {Number(low).toFixed(2)} / {Number(high).toFixed(2)}
    </div>
  );
}

function TopBar({ dataInfo, cor, wsStatus }) {
  const direcaoTopo =
    dataInfo.direcaoConfluencia ||
    dataInfo.engineDirecao ||
    "NEUTRO";

  const faseTopoBruta = String(dataInfo.engineFase || "AGUARDANDO").toUpperCase();

  const faseTopo =
    faseTopoBruta === "SIMULADO_TRINENGINE_SEM_PROCESSAR"
      ? "AGUARDANDO MOTOR"
      : faseTopoBruta;

  return (
    <div
      style={{
        position: "absolute",
        zIndex: 10,
        top: 10,
        left: 12,
        display: "flex",
        gap: 8,
        pointerEvents: "none",
      }}
    >
      <MiniBadge cor={wsStatus === "ONLINE" ? "#00ff99" : "#ff4444"}>
        WS {wsStatus}
      </MiniBadge>

      <MiniBadge cor={cor}>
        CONTEXTO: {dataInfo.contextoInstitucional || "AGUARDANDO"}
      </MiniBadge>

      <MiniBadge cor={cor}>FASE: {faseTopo}</MiniBadge>
      <MiniBadge cor={cor}>DIREÃ‡ÃƒO: {direcaoTopo}</MiniBadge>
      <MiniBadge cor={cor}>ENTRADA: {dataInfo.entrada || "AGUARDAR"}</MiniBadge>
    </div>
  );
}

function MiniBadge({ children, cor }) {
  return (
    <div
      style={{
        background: "rgba(2, 8, 22, 0.85)",
        color: cor,
        border: `1px solid ${cor}`,
        borderRadius: 999,
        padding: "5px 9px",
        fontSize: 11,
        fontWeight: "900",
        boxShadow: `0 0 14px ${cor}`,
      }}
    >
      {children}
    </div>
  );
}

function Radar({ cor, intensidade, wsStatus }) {
  return (
    <div
      style={{
        height: 165,
        background: "radial-gradient(circle at center, #061421 0%, #020812 70%)",
        border: `1px solid ${cor}`,
        borderRadius: 14,
        marginBottom: 12,
        position: "relative",
        overflow: "hidden",
        boxShadow: `0 0 30px ${cor}`,
      }}
    >
      <div
        style={{
          width: 120,
          height: 120,
          borderRadius: "50%",
          border: `2px solid ${cor}`,
          position: "absolute",
          left: "50%",
          top: "50%",
          marginLeft: -60,
          marginTop: -60,
          animation: "pulseRadar 1.4s infinite",
          boxShadow: `0 0 35px ${cor}`,
        }}
      />

      <div
        style={{
          width: 2,
          height: 75,
          background: cor,
          position: "absolute",
          left: "50%",
          top: "15%",
          transformOrigin: "bottom center",
          animation: "spinScanner 2s linear infinite",
          boxShadow: `0 0 15px ${cor}`,
        }}
      />

      <div
        style={{
          position: "absolute",
          bottom: 8,
          left: 10,
          right: 10,
          color: cor,
          display: "flex",
          justifyContent: "space-between",
          fontSize: 11,
          fontWeight: "900",
        }}
      >
        <span>RADAR WS {wsStatus}</span>
        <span>{formatarGlobal(intensidade)}</span>
      </div>
    </div>
  );
}

function PressaoBar({ compra, venda }) {
  return (
    <div
      style={{
        background: "#101010",
        padding: 10,
        borderRadius: 8,
        marginTop: 10,
      }}
    >
      <div style={{ fontWeight: "bold", marginBottom: 8, color: "#ffffff" }}>
        PRESSÃƒO INSTITUCIONAL
      </div>

      <div
        style={{
          height: 18,
          background: "#222",
          borderRadius: 10,
          overflow: "hidden",
          marginBottom: 6,
        }}
      >
        <div
          style={{
            width: `${Math.min(Number(compra || 0), 100)}%`,
            height: "100%",
            background: "linear-gradient(90deg,#00ff99,#00ffc8)",
            transition: "all 0.4s ease",
          }}
        />
      </div>

      <div style={{ color: "#00ffc8", marginBottom: 10 }}>
        COMPRA: {compra || 0}%
      </div>

      <div
        style={{
          height: 18,
          background: "#222",
          borderRadius: 10,
          overflow: "hidden",
          marginBottom: 6,
        }}
      >
        <div
          style={{
            width: `${Math.min(Number(venda || 0), 100)}%`,
            height: "100%",
            background: "linear-gradient(90deg,#ff4444,#ff0000)",
            transition: "all 0.4s ease",
          }}
        />
      </div>

      <div style={{ color: "#ff4444" }}>VENDA: {venda || 0}%</div>
    </div>
  );
}

function Titulo({ children }) {
  return (
    <div
      style={{
        background: "linear-gradient(90deg,#00ffc8,#0066ff)",
        color: "#001014",
        padding: 11,
        marginBottom: 10,
        borderRadius: 8,
        fontWeight: "900",
        textAlign: "center",
        letterSpacing: 0.8,
        boxShadow: "0 0 18px rgba(0,217,255,0.35)",
      }}
    >
      {children}
    </div>
  );
}

function Box({ children, color }) {
  return (
    <div
      style={{
        backgroundColor: color,
        color: "white",
        padding: "10px 11px",
        marginBottom: 8,
        borderRadius: 8,
        fontWeight: "bold",
        lineHeight: 1.25,
        boxShadow: "inset 0 0 14px rgba(255,255,255,0.04), 0 0 12px rgba(0,217,255,0.10)",
        border: "1px solid rgba(255,255,255,0.07)",
      }}
    >
      {children}
    </div>
  );
}

function formatarGlobal(valor) {
  if (valor === null || valor === undefined) return "-";

  const n = Number(valor);

  if (!Number.isFinite(n)) return valor;

  return n.toFixed(2);
}

