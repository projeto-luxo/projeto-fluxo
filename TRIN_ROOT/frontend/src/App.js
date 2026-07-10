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
  const ultimoTimeframeGraficoRef = useRef(null);
  const ultimoTamanhoHistoricoRef = useRef(0);
  const ultimoPrimeiroTimeGraficoRef = useRef(null);
  const ultimoUltimoTimeGraficoRef = useRef(null);

  const [dataInfo, setDataInfo] = useState({});
  const [wsStatus, setWsStatus] = useState("DESCONECTADO");
  const [ttRawStatus, setTtRawStatus] = useState(null);
  const [ttRawErro, setTtRawErro] = useState("");

  const [replayStatus, setReplayStatus] = useState({
    ativo: false,
    modo_dados: "AO_VIVO",
    csv: "",
    data_pregao: "2026-01-26",
    indice: 0,
    total: 0,
    ultimo_erro: "",
  });
  const [replayDataPregao, setReplayDataPregao] = useState("2026-01-26");


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

  const aplicarEscalaTempoPorTimeframe = useCallback((timeframe) => {
    if (!chartRef.current) return;

    const tf = String(timeframe || "").toUpperCase();
    const mostrarSegundos = tf === "15S" || tf === "30S";

    chartRef.current.applyOptions({
      timeScale: {
        timeVisible: true,
        secondsVisible: mostrarSegundos,
      },
    });
  }, []);

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

    let vwap = ordenarPorTempo(data.vwap || []);
    let vwapSuperior = ordenarPorTempo(data.vwap_superior || []);
    let vwapInferior = ordenarPorTempo(data.vwap_inferior || []);

    if (!historico.length || !candleSeriesRef.current) return;

    let ultimoCandle = historico[historico.length - 1];

    const timeframeAtualGrafico =
      data.painel_temporal?.timeframe_painel ||
      ultimoCandle.timeframe_painel ||
      "DESCONHECIDO";

    // PATCH_GRAFICO_SERIES_TEMPORAIS_03
    // Remove segmentos visuais quebrados por grandes buracos temporais
    // e alinha VWAP/bandas na mesma regua dos candles.
    const segundosPorTimeframeVisual = {
      "15S": 15,
      "30S": 30,
      "1_MIN": 60,
      "2_MIN": 120,
      "5_MIN": 300,
      "10_MIN": 600,
      "15_MIN": 900,
      "30_MIN": 1800,
      "60_MIN": 3600,
    };

    const filtrarHistoricoVisualContinuo = (candles, timeframe) => {
      if (!Array.isArray(candles) || candles.length < 3) return candles;

      const tf = String(timeframe || "").toUpperCase();
      const esperado = segundosPorTimeframeVisual[tf];

      if (!esperado) return candles;

      const limiteGap = Math.max(esperado * 8, 90);

      let inicioSegmentoAtual = 0;

      for (let i = candles.length - 1; i > 0; i -= 1) {
        const atual = Number(candles[i]?.time);
        const anterior = Number(candles[i - 1]?.time);

        if (!Number.isFinite(atual) || !Number.isFinite(anterior)) continue;

        const gap = atual - anterior;

        if (gap > limiteGap) {
          inicioSegmentoAtual = i;
          break;
        }
      }

      if (inicioSegmentoAtual <= 0) return candles;

      const segmentoAtual = candles.slice(inicioSegmentoAtual);

      // Se nasceu apenas 1 ou poucos candles depois de um grande buraco temporal,
      // trata como leitura isolada pos-pausa e preserva o bloco anterior no grafico.
      if (segmentoAtual.length < 8 && candles.length > inicioSegmentoAtual) {
        return candles.slice(Math.max(0, inicioSegmentoAtual - 120), inicioSegmentoAtual);
      }

      return segmentoAtual;
    };

    const alinharSerieAoHistorico = (serie, candles) => {
      if (!Array.isArray(serie) || !serie.length || !Array.isArray(candles) || !candles.length) {
        return [];
      }

      const pontos = ordenarPorTempo(serie)
        .filter((ponto) =>
          ponto &&
          ponto.time !== undefined &&
          ponto.value !== undefined &&
          Number.isFinite(Number(ponto.time)) &&
          Number.isFinite(Number(ponto.value))
        );

      if (!pontos.length) return [];

      const alinhada = [];
      let idx = 0;
      let ultimoValor = null;

      candles.forEach((candle) => {
        const t = Number(candle.time);
        if (!Number.isFinite(t)) return;

        while (idx < pontos.length && Number(pontos[idx].time) <= t) {
          ultimoValor = Number(pontos[idx].value);
          idx += 1;
        }

        if (ultimoValor !== null && Number.isFinite(ultimoValor)) {
          alinhada.push({
            time: candle.time,
            value: ultimoValor,
          });
        }
      });

      return alinhada;
    };

    historico = filtrarHistoricoVisualContinuo(historico, timeframeAtualGrafico);
    ultimoCandle = historico[historico.length - 1] || ultimoCandle;

    vwap = alinharSerieAoHistorico(vwap, historico);
    vwapSuperior = alinharSerieAoHistorico(vwapSuperior, historico);
    vwapInferior = alinharSerieAoHistorico(vwapInferior, historico);

    aplicarEscalaTempoPorTimeframe(timeframeAtualGrafico);

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
    const contratoDeltaSaldo = data.contrato_delta_saldo || {};

    // IntegraÃ§Ã£o cognitiva TRIN â€” ConfluenceEngine v2.2
    const confluencia = data.confluencia || {};
    const evidenciasConfluencia =
      data.evidencias_confluencia ||
      confluencia.evidencias ||
      [];

    const evidenciaFluxo =
      evidenciasConfluencia.find((e) => e.nome === "FLUXO_DELTA_SALDO") || {};

    const evidenciaAgressaoConfluencia =
      evidenciasConfluencia.find((e) => e.nome === "AGRESSAO") || {};

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

      // CR-03D4: proveniencia e contrato semantico Delta / Saldo.
      deltaFonte:
        contratoDeltaSaldo.delta_fonte ??
        ultimoCandle.delta_fonte ??
        "NAO_INFORMADA",

      saldoFonte:
        contratoDeltaSaldo.saldo_fonte ??
        ultimoCandle.saldo_fonte ??
        "NAO_INFORMADA",

      deltaSaldoRelacao:
        contratoDeltaSaldo.delta_saldo_relacao ??
        confluencia.delta_saldo_relacao ??
        ultimoCandle.delta_saldo_relacao ??
        "INDETERMINADO",

      deltaSaldoIndependentes:
        contratoDeltaSaldo.delta_saldo_independentes ??
        confluencia.delta_saldo_independentes ??
        ultimoCandle.delta_saldo_independentes ??
        false,

      saldoFallbackDelta:
        contratoDeltaSaldo.saldo_fallback_delta ??
        ultimoCandle.saldo_fallback_delta ??
        false,

      fluxoAgressorCanonico:
        contratoDeltaSaldo.fluxo_agressor_canonico ??
        confluencia.fluxo_agressor_canonico ??
        ultimoCandle.fluxo_agressor_canonico,

      fluxoAgressorFonte:
        contratoDeltaSaldo.fluxo_agressor_fonte ??
        evidenciaFluxo?.valor?.fluxo_agressor_fonte ??
        ultimoCandle.fluxo_agressor_fonte ??
        "NAO_INFORMADA",

      fluxoAgressorStatus:
        contratoDeltaSaldo.fluxo_agressor_status ??
        evidenciaFluxo?.valor?.fluxo_agressor_status ??
        ultimoCandle.fluxo_agressor_status ??
        "INDETERMINADO",

      modoEvidenciaAgressao:
        data.modo_evidencia_agressao ??
        agressao.modo_evidencia_agressao ??
        evidenciaAgressaoConfluencia?.valor?.modo_evidencia_agressao ??
        "INDETERMINADO",

      modoEvidenciaFluxo:
        data.modo_evidencia_fluxo ??
        confluencia.modo_evidencia_fluxo ??
        evidenciaFluxo?.valor?.modo_evidencia_fluxo ??
        "INDETERMINADO",

      fluxoAgressaoCorrelacionados:
        data.fluxo_agressao_correlacionados ??
        confluencia.fluxo_agressao_correlacionados ??
        evidenciaAgressaoConfluencia?.valor?.correlacionada_fluxo_canonico ??
        false,

      correlacaoFluxoAgressao:
        data.correlacao_fluxo_agressao ??
        confluencia.correlacao_fluxo_agressao ??
        evidenciaAgressaoConfluencia?.valor?.correlacao_fluxo_agressao ??
        "INDETERMINADA",

      agressaoConfirmacaoDirecionalIndependente:
        data.agressao_confirmacao_direcional_independente ??
        confluencia.agressao_confirmacao_direcional_independente ??
        evidenciaAgressaoConfluencia?.valor?.confirmacao_direcional_independente ??
        true,

      saldo: data.saldo_agressor ?? ultimoCandle.saldo,
      delta: data.delta ?? ultimoCandle.delta,
      volume: data.volume ?? ultimoCandle.volume,

      volumeNormalizadoCapado:
        ultimoCandle.volume_normalizado_capado ??
        data.volume_normalizado_capado ??
        data.volume ??
        ultimoCandle.volume,

      volumeReal:
        ultimoCandle.volume_real ??
        data.volume_real,

      volumeDeltaEstimado:
        ultimoCandle.volume_delta_estimado ??
        data.volume_delta_estimado,

      volumeCandleEstimado:
        ultimoCandle.volume_candle_estimado ??
        data.volume_candle_estimado,

      volumeTipo:
        ultimoCandle.volume_tipo ??
        data.volume_tipo ??
        "NAO_INFORMADO",

      // Calibracao recuperada: painel usa ultimo candle real como fonte visual
      open: ultimoCandle.open,
      high: ultimoCandle.high,
      low: ultimoCandle.low,
      close: ultimoCandle.close,
      ultimo: ultimoCandle.ultimo ?? ultimoCandle.close,
      maximo: ultimoCandle.high,
      minimo: ultimoCandle.low,
      vwap: data.vwap_atual ?? data.vwap_real ?? ultimoCandle.vwap ?? ultimoCandle.vwap_real,
      fonteDados:
        ultimoCandle.fonte_dados ||
        data.fonte_dados ||
        data.painel_temporal?.origem ||
        "DESCONHECIDA",
      abaOrigem: ultimoCandle.aba_origem,

      modoOperacional:
        data.modo_replay
          ? "REPLAY"
          : data.painel_temporal?.origem === "RTD_EXCEL_AGREGADO"
            ? "AO_VIVO"
            : data.fonte_dados || "DESCONHECIDO",

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

      statusFonte:
        data.painel_temporal?.status_fonte ||
        ultimoCandle.status_fonte ||
        data.status_fonte ||
        "NAO_INFORMADO",

      fonteEstagnada:
        Boolean(
          data.painel_temporal?.fonte_estagnada ??
          ultimoCandle.fonte_estagnada ??
          data.fonte_estagnada ??
          false
        ),

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

    const precisaReconstruirGrafico =
      !carregouHistoricoRef.current ||
      ultimoTimeframeGraficoRef.current !== timeframeAtualGrafico ||
      ultimoTamanhoHistoricoRef.current !== historico.length ||
      ultimoPrimeiroTimeGraficoRef.current !== primeiroTime ||
      Number(ultimoTime) < Number(ultimoUltimoTimeGraficoRef.current || 0);

    if (precisaReconstruirGrafico) {
      candleSeriesRef.current.setData(historico);
      vwapLineRef.current.setData(vwap);
      vwapSuperiorRef.current.setData(vwapSuperior);
      vwapInferiorRef.current.setData(vwapInferior);

      if (typeof candleSeriesRef.current.setMarkers === "function") {
        candleSeriesRef.current.setMarkers(gerarMarkersInstitucionais(historico));
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

    ultimoTimeframeGraficoRef.current = timeframeAtualGrafico;
    ultimoTamanhoHistoricoRef.current = historico.length;
    ultimoPrimeiroTimeGraficoRef.current = primeiroTime;
    ultimoUltimoTimeGraficoRef.current = ultimoTime;

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
    aplicarEscalaTempoPorTimeframe,
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
      height: Math.max(1, chartContainerRef.current.clientHeight),
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
        height: Math.max(1, chartContainerRef.current.clientHeight),
      });

      chartRef.current.timeScale().fitContent();
    };

    const resizeObserver =
      typeof ResizeObserver !== "undefined"
        ? new ResizeObserver(handleResize)
        : null;

    resizeObserver?.observe(chartContainerRef.current);
    window.addEventListener("resize", handleResize);

    return () => {
      resizeObserver?.disconnect();
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

      aplicarEscalaTempoPorTimeframe(timeframe);

      carregouHistoricoRef.current = false;
      ultimoTimeframeGraficoRef.current = null;
      ultimoTamanhoHistoricoRef.current = 0;
      ultimoPrimeiroTimeGraficoRef.current = null;
      ultimoUltimoTimeGraficoRef.current = null;

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


  const carregarStatusReplay = useCallback(async () => {
    try {
      const resposta = await fetch("http://127.0.0.1:8001/painel/replay/status");
      const json = await resposta.json();

      setReplayStatus({
        ativo: Boolean(json.ativo),
        modo_dados: json.modo_dados || (json.ativo ? "REPLAY" : "AO_VIVO"),
        csv: json.csv || "",
        data_pregao: json.data_pregao || replayDataPregao,
        indice: json.indice || 0,
        total: json.total || 0,
        ultimo_erro: json.ultimo_erro || "",
      });
    } catch (erro) {
      setReplayStatus((atual) => ({
        ...atual,
        ultimo_erro: "Replay indisponivel",
      }));
    }
  }, [replayDataPregao]);

  const alternarModoReplay = useCallback(async () => {
    const ativar = !replayStatus.ativo;

    const url = ativar
      ? `http://127.0.0.1:8001/painel/replay/start?data_pregao=${encodeURIComponent(replayDataPregao || "")}&intervalo_segundos=5.0&intervalo_segundos=5.0`
      : "http://127.0.0.1:8001/painel/replay/stop";

    try {
      await fetch(url);
      await carregarStatusReplay();

      carregouHistoricoRef.current = false;
      ultimoTimeframeGraficoRef.current = null;
      ultimoTamanhoHistoricoRef.current = 0;
      ultimoPrimeiroTimeGraficoRef.current = null;
      ultimoUltimoTimeGraficoRef.current = null;

      if (candleSeriesRef.current) candleSeriesRef.current.setData([]);
      if (vwapLineRef.current) vwapLineRef.current.setData([]);
      if (vwapSuperiorRef.current) vwapSuperiorRef.current.setData([]);
      if (vwapInferiorRef.current) vwapInferiorRef.current.setData([]);

      setTimeout(() => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({
            width: chartContainerRef.current.clientWidth,
            height: Math.max(320, chartContainerRef.current.clientHeight || window.innerHeight - 20),
          });

          chartRef.current.timeScale().fitContent();
        }
      }, 250);
    } catch (erro) {
      alert("Erro ao alternar modo Replay.");
    }
  }, [replayStatus.ativo, replayDataPregao, carregarStatusReplay]);

  const carregarDataReplay = useCallback(async () => {
    try {
      const url = `http://127.0.0.1:8001/painel/replay/start?data_pregao=${encodeURIComponent(replayDataPregao || "")}&intervalo_segundos=5.0&intervalo_segundos=5.0`;

      await fetch(url);
      await carregarStatusReplay();

      carregouHistoricoRef.current = false;
      ultimoTimeframeGraficoRef.current = null;
      ultimoTamanhoHistoricoRef.current = 0;
      ultimoPrimeiroTimeGraficoRef.current = null;
      ultimoUltimoTimeGraficoRef.current = null;

      if (candleSeriesRef.current) candleSeriesRef.current.setData([]);
      if (vwapLineRef.current) vwapLineRef.current.setData([]);
      if (vwapSuperiorRef.current) vwapSuperiorRef.current.setData([]);
      if (vwapInferiorRef.current) vwapInferiorRef.current.setData([]);
    } catch (erro) {
      alert("Erro ao carregar data do Replay.");
    }
  }, [replayDataPregao, carregarStatusReplay]);

  useEffect(() => {
    carregarStatusReplay();

    const id = setInterval(() => {
      carregarStatusReplay();
    }, 4000);

    return () => clearInterval(id);
  }, [carregarStatusReplay]);


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
  const volumeNormalizadoPainel = dataInfo.volumeNormalizadoCapado ?? dataInfo.volume ?? "-";
  const volumeCandleEstimadoPainel = dataInfo.volumeCandleEstimado ?? "-";
  const volumeTipoPainel = dataInfo.volumeTipo ?? "NAO_INFORMADO";
  const deltaPainel = dataInfo.delta ?? "-";
  const saldoPainel = dataInfo.saldo ?? "-";

  // CR-03D4: leitura visual do contrato semantico sem alterar calculos.
  const deltaFontePainel = dataInfo.deltaFonte || "NAO_INFORMADA";
  const saldoFontePainel = dataInfo.saldoFonte || "NAO_INFORMADA";
  const fluxoFontePainel = dataInfo.fluxoAgressorFonte || "NAO_INFORMADA";
  const relacaoDeltaSaldoPainel = String(
    dataInfo.deltaSaldoRelacao || "INDETERMINADO"
  ).toUpperCase();

  const deltaSaldoIndependentesPainel =
    dataInfo.deltaSaldoIndependentes === true;

  const contratoSemDadosPainel =
    relacaoDeltaSaldoPainel === "SEM_DADOS" ||
    relacaoDeltaSaldoPainel === "INDETERMINADO";

  const evidenciasCorrelacionadasPainel =
    Boolean(dataInfo.fluxoAgressaoCorrelacionados) ||
    (
      !deltaSaldoIndependentesPainel &&
      !contratoSemDadosPainel
    );

  const modoEvidenciaFluxoPainel =
    String(dataInfo.modoEvidenciaFluxo || "INDETERMINADO").toUpperCase();

  const modoEvidenciaAgressaoPainel =
    String(dataInfo.modoEvidenciaAgressao || "INDETERMINADO").toUpperCase();

  const modoSemanticoPainel =
    modoEvidenciaFluxoPainel === modoEvidenciaAgressaoPainel
      ? modoEvidenciaFluxoPainel
      : `${modoEvidenciaFluxoPainel} / ${modoEvidenciaAgressaoPainel}`;

  const corContratoSemanticoPainel =
    contratoSemDadosPainel
      ? "#8a969e"
      : deltaSaldoIndependentesPainel
        ? "#00d9ff"
        : "#ffaa00";

  const textoRelacaoDeltaSaldoPainel =
    relacaoDeltaSaldoPainel === "EQUIVALENTES_OBSERVADOS"
      ? "EQUIVALENTES OBSERVADOS"
      : relacaoDeltaSaldoPainel === "SALDO_DERIVADO_DELTA"
        ? "SALDO DERIVADO DO DELTA"
        : relacaoDeltaSaldoPainel === "DELTA_DERIVADO_SALDO"
          ? "DELTA DERIVADO DO SALDO"
          : relacaoDeltaSaldoPainel === "INDEPENDENTES"
            ? "EVIDENCIAS INDEPENDENTES"
            : relacaoDeltaSaldoPainel.replaceAll("_", " ");

  const avisoContratoSemanticoPainel =
    contratoSemDadosPainel
      ? "CONTRATO SEM DADOS SUFICIENTES"
      : evidenciasCorrelacionadasPainel
        ? "EVIDENCIAS CORRELACIONADAS · SEM DUPLA CONTAGEM"
        : "EVIDENCIAS INDEPENDENTES";

  const vwapPainel = dataInfo.vwap ?? dataInfo.vwapReal ?? dataInfo.vwap_real ?? "-";
  const distVwapPainel = dataInfo.distanciaVwap ?? dataInfo.distancia_vwap ?? "-";

  const modoOperacionalPainel =
    dataInfo.modoOperacional ||
    (dataInfo.painelOrigemTemporal === "RTD_EXCEL_AGREGADO" ? "AO_VIVO" : "DESCONHECIDO");

  const fonteOperacionalPainel =
    dataInfo.fonteDados ||
    dataInfo.painelOrigemTemporal ||
    "DESCONHECIDA";

  const timeframeOperacionalPainel =
    dataInfo.painelTimeframe ||
    "DESCONHECIDO";

  const statusOperacionalPainel =
    dataInfo.painelStatus ||
    "DESCONHECIDO";

  const statusFontePainel =
    dataInfo.statusFonte ||
    "NAO_INFORMADO";

  const fonteEstagnadaPainel =
    Boolean(dataInfo.fonteEstagnada) ||
    statusFontePainel === "RTD_ESTAGNADO";

  const textoFonteRtdPainel =
    fonteEstagnadaPainel
      ? "ESTAGNADA"
      : statusFontePainel === "RTD_ATUALIZANDO"
        ? "ATUALIZANDO"
        : statusFontePainel;

  const corFonteRtdPainel =
    fonteEstagnadaPainel
      ? "#ff4444"
      : statusFontePainel === "RTD_ATUALIZANDO"
        ? "#00ff99"
        : "#ffffff";

  const contratoOperacionalPainel =
    dataInfo.contratoExcelRtd ||
    dataInfo.contratoEsperadoRtd ||
    "-";

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

  const chamadaPrincipalPainel =
    bloqueioPorFiscalPainel
      ? "AUTORIZACAO BLOQUEADA"
      : bloqueadoPainel
        ? motivoBloqueioPainel
        : acaoPrincipalPainel;

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

  const estadoQualidadePainel =
    dataInfo.qualidadeConfluencia === "BLOQUEADO_POR_CERTIFICACAO"
      ? "BLOQUEADO POR CERTIFICACAO"
      : dataInfo.qualidadeConfluencia === "FORTE"
        ? "CONFLUENCIA FORTE"
        : dataInfo.qualidadeConfluencia === "MEDIA"
          ? "CONFLUENCIA MEDIA"
          : dataInfo.qualidadeConfluencia === "FRACA"
            ? "CONFLUENCIA FRACA"
            : dataInfo.qualidadeConfluencia === "NEUTRA"
              ? "CONFLUENCIA NEUTRA"
              : (dataInfo.qualidadeConfluencia || "DESCONHECIDO");

  const alertaPrincipalPainel =
    alertaPainel && alertaPainel !== "SEM ALERTA"
      ? alertaPainel
      : bloqueadoPainel
        ? "CONFLUENCIA BLOQUEADA"
        : "SEM ALERTA CRITICO";

  const tituloAlertaRodape =
    bloqueioPorFiscalPainel
      ? "ALERTA FISCAL"
      : temAlerta
        ? "ALERTA"
        : "STATUS";

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
        padding: 10,
        boxSizing: "border-box",
        background: "radial-gradient(circle at center, #172324 0%, #081013 42%, #010409 100%)",
        color: "#ffffff",
        overflow: "hidden",
        display: "grid",
        gridTemplateColumns: "minmax(300px, 18%) minmax(280px, 16%) minmax(0, 1fr)",
        gridTemplateRows: "minmax(0, 1fr) 150px",
        gap: 10,
        minWidth: 0,
        minHeight: 0,
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

          .trin-side-scroll {
            scrollbar-width: thin;
            scrollbar-color: rgba(0, 217, 255, 0.45) rgba(255, 255, 255, 0.04);
          }

          .trin-side-scroll::-webkit-scrollbar {
            width: 7px;
          }

          .trin-side-scroll::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.04);
            border-radius: 999px;
          }

          .trin-side-scroll::-webkit-scrollbar-thumb {
            background: rgba(0, 217, 255, 0.42);
            border-radius: 999px;
            border: 1px solid rgba(0, 217, 255, 0.18);
          }

          .trin-side-scroll::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 217, 255, 0.70);
          }
        `}
      </style>

      <div
        className="trin-side-scroll"
        style={{
          gridColumn: "1",
          gridRow: "1 / 3",
          minWidth: 0,
          minHeight: 0,
          padding: "24px 20px",
          borderRadius: 24,
          background: "linear-gradient(180deg, rgba(13,22,24,0.70), rgba(1,5,8,0.94))",
          border: "1px solid rgba(0,217,255,0.14)",
          boxShadow: "inset 0 0 55px rgba(0,255,180,0.04), 0 0 28px rgba(0,217,255,0.08)",
          overflowX: "hidden",
          overflowY: "auto",
        }}
      >
        <div style={{ color: "#00d9ff", fontSize: 13, fontWeight: "900", marginBottom: 30 }}>
          TRIN COCKPIT
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 22 }}>
          <div style={{ height: 1, flex: 1, background: "rgba(255,255,255,0.45)" }} />
          <div style={{ color: "#cfd8dc", fontSize: 16 }}>
            STATUS OPERACIONAL
          </div>
          <div style={{ height: 1, flex: 1, background: "rgba(255,255,255,0.45)" }} />
        </div>

        <div style={{ color: "#d7dde1", fontSize: 15, lineHeight: 1.55, marginBottom: 18 }}>
          CONTEXTO: {macroPainel}
        </div>

        <div style={{ color: corEstadoPainel, fontSize: 15, fontWeight: "900", lineHeight: 1.55, marginBottom: 18 }}>
          CENARIO: {microPainel}
        </div>

        <div style={{ color: "#d7dde1", fontSize: 14, lineHeight: 1.6, marginBottom: 18 }}>
          • Direcao: {direcaoPainel}<br />
          • Entrada: {temEntradaValida ? dataInfo.entrada : "AGUARDAR"}<br />
          • Autorizacao: {autorizacaoOperacionalPainel}<br />
          • Estado: {estadoQualidadePainel}<br />
          • Fiscal: {dataInfo.fiscalStatus || "DESCONHECIDO"}
        </div>

        <div
          style={{
            border: "1px solid rgba(0,217,255,0.22)",
            background: "rgba(0,217,255,0.055)",
            borderRadius: 12,
            padding: "10px 12px",
            marginBottom: 24,
            color: "#d7dde1",
            fontSize: 12,
            lineHeight: 1.55,
            boxShadow: "inset 0 0 18px rgba(0,217,255,0.05)",
          }}
        >
          <div style={{ color: "#00d9ff", fontWeight: "900", fontSize: 11, letterSpacing: 1, marginBottom: 6 }}>
            FONTE OPERACIONAL
          </div>
          <div>• Modo: <b>{modoOperacionalPainel}</b></div>
          <div>• Fonte: <b>{fonteOperacionalPainel}</b></div>
          <div>• TF: <b>{timeframeOperacionalPainel}</b></div>
          <div>• Status: <b>{statusOperacionalPainel}</b></div>
          <div>
            • Fonte RTD: <b style={{ color: corFonteRtdPainel }}>{textoFonteRtdPainel}</b>
          </div>
          <div>• Contrato: <b>{contratoOperacionalPainel}</b></div>
          <div style={{ marginTop: 6, color: "#00d9ff", fontWeight: "900" }}>
            VOLUME DO CANDLE
          </div>
          <div>• Vol norm: <b>{formatar(volumeNormalizadoPainel)}</b></div>
          <div>• Vol candle: <b>{formatar(volumeCandleEstimadoPainel)}</b></div>
          <div>• Tipo: <b>{volumeTipoPainel}</b></div>
        </div>

        {/* CR-03D4: contrato semantico visivel ao operador. */}
        <div
          title={[
            `Delta: ${deltaFontePainel}`,
            `Saldo: ${saldoFontePainel}`,
            `Fluxo canonico: ${fluxoFontePainel}`,
            `Correlacao: ${dataInfo.correlacaoFluxoAgressao || "INDETERMINADA"}`,
          ].join("\n")}
          style={{
            border: `1px solid ${corContratoSemanticoPainel}88`,
            background: contratoSemDadosPainel
              ? "rgba(55,65,72,0.28)"
              : evidenciasCorrelacionadasPainel
                ? "rgba(61,38,0,0.58)"
                : "rgba(0,38,52,0.52)",
            borderRadius: 12,
            padding: "11px 12px",
            marginBottom: 18,
            color: "#d7dde1",
            fontSize: 11,
            lineHeight: 1.45,
            boxShadow: `inset 0 0 18px ${corContratoSemanticoPainel}10, 0 0 18px ${corContratoSemanticoPainel}12`,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 8,
              marginBottom: 8,
            }}
          >
            <div
              style={{
                color: corContratoSemanticoPainel,
                fontWeight: "900",
                fontSize: 11,
                letterSpacing: 1,
              }}
            >
              CONTRATO DELTA / SALDO
            </div>

            <div
              style={{
                color: corContratoSemanticoPainel,
                border: `1px solid ${corContratoSemanticoPainel}88`,
                borderRadius: 999,
                padding: "2px 7px",
                fontSize: 9,
                fontWeight: "900",
                whiteSpace: "nowrap",
              }}
            >
              {modoSemanticoPainel}
            </div>
          </div>

          <div>
            • Relacao: <b style={{ color: corContratoSemanticoPainel }}>
              {textoRelacaoDeltaSaldoPainel}
            </b>
          </div>
          <div>
            • Independentes: <b>{deltaSaldoIndependentesPainel ? "SIM" : "NAO"}</b>
          </div>
          <div title={deltaFontePainel}>
            • Origem Delta: <b>{resumirFonteSemantica(deltaFontePainel)}</b>
          </div>
          <div title={saldoFontePainel}>
            • Origem Saldo: <b>{resumirFonteSemantica(saldoFontePainel)}</b>
          </div>
          <div title={fluxoFontePainel}>
            • Fluxo canonico: <b>{resumirFonteSemantica(fluxoFontePainel)}</b>
          </div>

          <div
            style={{
              marginTop: 8,
              padding: "6px 8px",
              borderRadius: 7,
              color: corContratoSemanticoPainel,
              background: `${corContratoSemanticoPainel}12`,
              border: `1px solid ${corContratoSemanticoPainel}55`,
              fontSize: 9,
              fontWeight: "900",
              letterSpacing: 0.45,
              textAlign: "center",
            }}
          >
            {avisoContratoSemanticoPainel}
          </div>
        </div>

        {/* CR-03A: Replay movido para a coluna lateral esquerda */}
        <div
          style={{
            border: replayStatus.ativo
              ? "1px solid rgba(255,170,0,0.55)"
              : "1px solid rgba(0,255,153,0.35)",
            background: replayStatus.ativo
              ? "rgba(45,28,0,0.72)"
              : "rgba(0,35,26,0.58)",
            borderRadius: 12,
            padding: "12px",
            marginBottom: 18,
            boxShadow: replayStatus.ativo
              ? "0 0 18px rgba(255,170,0,0.18)"
              : "0 0 18px rgba(0,255,153,0.10)",
          }}
        >
          <div
            style={{
              color: replayStatus.ativo ? "#ffd27a" : "#00ff99",
              fontSize: 11,
              fontWeight: "900",
              letterSpacing: 1,
              marginBottom: 10,
            }}
          >
            REPLAY DIAGNOSTICO
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "minmax(0, 1fr) auto",
              gap: 8,
              marginBottom: 8,
            }}
          >
            <input
              type="date"
              value={replayDataPregao}
              onChange={(e) => setReplayDataPregao(e.target.value)}
              style={{
                minWidth: 0,
                width: "100%",
                boxSizing: "border-box",
                background: "rgba(0,0,0,0.45)",
                color: "#ffffff",
                border: "1px solid rgba(255,255,255,0.18)",
                borderRadius: 8,
                padding: "7px 8px",
                fontSize: 11,
                fontWeight: "900",
              }}
            />

            <button
              onClick={carregarDataReplay}
              title="Carregar o pregao escolhido no Replay"
              style={{
                border: "1px solid rgba(255,255,255,0.18)",
                background: replayStatus.ativo
                  ? "rgba(255,170,0,0.16)"
                  : "rgba(255,255,255,0.08)",
                color: replayStatus.ativo ? "#ffd27a" : "#cfd8dc",
                borderRadius: 8,
                padding: "7px 9px",
                fontSize: 10,
                fontWeight: "900",
                cursor: "pointer",
              }}
            >
              CARREGAR
            </button>
          </div>

          <button
            onClick={alternarModoReplay}
            title="Alternar entre AO_VIVO e REPLAY diagnostico"
            style={{
              width: "100%",
              border: replayStatus.ativo
                ? "1px solid rgba(255,170,0,0.55)"
                : "1px solid rgba(0,255,153,0.35)",
              background: replayStatus.ativo
                ? "rgba(255,170,0,0.12)"
                : "rgba(0,255,153,0.08)",
              color: replayStatus.ativo ? "#ffd27a" : "#00ff99",
              borderRadius: 8,
              padding: "8px 10px",
              fontSize: 11,
              fontWeight: "900",
              letterSpacing: 1,
              cursor: "pointer",
            }}
          >
            {replayStatus.ativo ? "REPLAY ON" : "AO VIVO"}
          </button>

          <div
            style={{
              marginTop: 9,
              color: replayStatus.ativo ? "#ffd27a" : "#9fb8b0",
              fontSize: 10,
              fontWeight: "900",
              lineHeight: 1.4,
            }}
          >
            {replayStatus.ativo ? (
              <>
                NAO OPERACIONAL · NAO CERTIFICADO<br />
                PREGAO: {replayDataPregao || replayStatus.data_pregao}<br />
                POSICAO: {replayStatus.indice}/{replayStatus.total}
              </>
            ) : (
              <>
                MODO OPERACIONAL: AO VIVO<br />
                REPLAY DIAGNOSTICO PARADO
              </>
            )}
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 22, marginBottom: 18 }}>
          <div style={{ color: "#8f9aa3", fontWeight: "900", fontStyle: "italic", fontSize: 20, lineHeight: 1.05 }}>
            SMART<br />MONEY
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8, flex: 1 }}>
            {[
              ["ULT", formatar(ultimoPainel), "#8b1f1f", "#ff5555"],
              ["MIN", formatar(minimaPainel), "#006b3c", "#00ff99"],
              ["VWAP", formatar(vwapPainel), "#006b3c", "#00ff99"],
              ["MAX", formatar(maximaPainel), "#8b1f1f", "#ff5555"],
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
          {chamadaPrincipalPainel}
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
          gridRow: "1 / 3",
          minWidth: 0,
          minHeight: 0,
          position: "relative",
          borderRadius: 24,
          background: "linear-gradient(180deg, rgba(11,18,20,0.58), rgba(0,3,8,0.90))",
          border: "1px solid rgba(255,255,255,0.10)",
          boxShadow: "inset 0 0 65px rgba(255,255,255,0.04), 0 0 22px rgba(0,217,255,0.06)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "26px 14px",
          overflow: "hidden",
        }}
      >
        <div style={{ alignSelf: "stretch", display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)", gap: 8 }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ color: "#8a969e", fontSize: 12, fontWeight: "900" }}>CONTEXTO</div>
            <div style={{ color: corEstadoPainel, fontSize: "clamp(20px, 1.55vw, 28px)", fontWeight: "900", marginTop: 8, whiteSpace: "nowrap", overflowWrap: "normal" }}>
              {contextoIndicadorPainel}
            </div>
          </div>

          <div style={{ textAlign: "center" }}>
            <div style={{ color: "#8a969e", fontSize: 12, fontWeight: "900" }}>CONFL</div>
            <div style={{ color: corEstadoPainel, fontSize: "clamp(20px, 1.55vw, 28px)", fontWeight: "900", marginTop: 8, whiteSpace: "nowrap", overflowWrap: "normal" }}>
              {formatar(dataInfo.scoreConfluencia)}
            </div>
            <div style={{ color: corEstadoPainel, fontSize: 11, fontWeight: "900", letterSpacing: 1, marginTop: 3 }}>
              {statusConfluenciaPainel}
            </div>
          </div>
        </div>

        <div
          style={{
            width: "min(250px, 100%)",
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

        <div style={{ textAlign: "center", width: "100%" }}>
          <div style={{ color: corEstadoPainel, fontSize: "clamp(26px, 1.8vw, 32px)", fontWeight: "900", whiteSpace: "nowrap" }}>
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
          minWidth: 0,
          minHeight: 0,
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

        <div
          ref={chartContainerRef}
          style={{ width: "100%", height: "100%", minWidth: 0, minHeight: 0 }}
        />
      </div>

      <div
        style={{
          gridColumn: "3",
          gridRow: "2",
          minWidth: 0,
          minHeight: 0,
          borderRadius: 18,
          background: "linear-gradient(90deg, rgba(4,10,13,0.97), rgba(3,15,12,0.94), rgba(4,10,13,0.97))",
          border: `1px solid ${corEstadoPainel}`,
          boxShadow: `0 0 30px ${corEstadoPainel}66`,
          display: "grid",
          gridTemplateColumns: "minmax(170px, 0.75fr) minmax(320px, 1.7fr) minmax(240px, 0.9fr)",
          gap: 12,
          alignItems: "center",
          padding: "12px 18px",
          overflow: "hidden",
        }}
      >
        <div>
          <div style={{ color: corEstadoPainel, fontSize: "clamp(22px, 1.5vw, 30px)", fontWeight: "900", letterSpacing: 2 }}>
            {tituloAlertaRodape}
          </div>
          <div style={{ color: "#d0d7dc", fontSize: 12, fontWeight: "bold" }}>
            {motivoBloqueioPainel || alertaPrincipalPainel}
          </div>
        </div>

        <div>
          <div style={{ color: "#d0d7dc", fontSize: 12, fontWeight: "900", textAlign: "center", letterSpacing: 2, marginBottom: 4 }}>
            ACAO
          </div>
          <div style={{ color: corEstadoPainel, fontSize: "clamp(24px, 2vw, 36px)", fontWeight: "900", textAlign: "center", letterSpacing: 3, lineHeight: 1.05 }}>
            {acaoPrincipalPainel}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(18, 1fr)", gap: 4, marginTop: 10 }}>
            {Array.from({ length: 18 }).map((_, i) => (
              <div
                key={i}
                style={{
                  height: 22,
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
          <Box
            color={Number(deltaPainel || 0) >= 0 ? "#004d40" : "#4a0000"}
            title={`DELTA · ${deltaFontePainel} · ${textoRelacaoDeltaSaldoPainel}`}
          >
            DELTA<br />{deltaPainel}
          </Box>
          <Box
            color={Number(saldoPainel || 0) >= 0 ? "#004d40" : "#4a0000"}
            title={`SALDO · ${saldoFontePainel} · ${textoRelacaoDeltaSaldoPainel}`}
          >
            SALDO<br />{saldoPainel}
          </Box>
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

  const contextoTopoBruto = String(dataInfo.contextoInstitucional || "AGUARDANDO");

  const contextoTopo =
    dataInfo.qualidadeConfluencia === "BLOQUEADO_POR_CERTIFICACAO" ||
    contextoTopoBruto.includes("FISCAL")
      ? "BLOQUEIO FISCAL"
      : contextoTopoBruto;

  const entradaTopoBruta = String(dataInfo.entrada || "AGUARDAR").toUpperCase();

  const bloqueioOperacionalTopo =
    dataInfo.qualidadeConfluencia === "BLOQUEADO_POR_CERTIFICACAO" ||
    String(dataInfo.alertaConfluencia || "").includes("FISCAL") ||
    contextoTopoBruto.includes("FISCAL");

  const temEntradaTopo =
    entradaTopoBruta &&
    !["AGUARDAR", "SEM ENTRADA", "SEM SINAL", "-", "NAO", "NÃO"].includes(entradaTopoBruta);

  const acaoTopo =
    bloqueioOperacionalTopo
      ? "AGUARDAR"
      : temEntradaTopo
        ? entradaTopoBruta
        : "AGUARDAR";

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
        CONTEXTO: {contextoTopo}
      </MiniBadge>

      <MiniBadge cor={cor}>FASE: {faseTopo}</MiniBadge>
      <MiniBadge cor={cor}>DIRECAO: {direcaoTopo}</MiniBadge>
      <MiniBadge cor={cor}>ACAO: {acaoTopo}</MiniBadge>
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

function Box({ children, color, title }) {
  return (
    <div
      title={title}
      style={{
        backgroundColor: color,
        color: "white",
        padding: "8px 10px",
        marginBottom: 0,
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

function resumirFonteSemantica(fonte) {
  const texto = String(fonte || "NAO_INFORMADA").toUpperCase();

  const aliases = {
    RTD_EXCEL_I2_DERIVADO_L2: "I2 <- L2 (RTD)",
    RTD_EXCEL_J2_TOPICO_103: "J2 · TOPICO 103",
    RTD_EXCEL_VOLUME_AGRESSAO_SALDO_L2: "L2 · SALDO AGRESSAO",
    REPLAY_CSV_CAMPO_DELTA: "REPLAY · CAMPO DELTA",
    REPLAY_CSV_CAMPO_SALDO: "REPLAY · CAMPO SALDO",
    REPLAY_CSV_CAMPO_AGRESSAO_SALDO: "REPLAY · AGRESSAO SALDO",
    REPLAY_FALLBACK_DELTA: "REPLAY · FALLBACK DELTA",
    REPLAY_CSV_SEM_DELTA: "REPLAY · SEM DELTA",
    REPLAY_CSV_SEM_SALDO: "REPLAY · SEM SALDO",
    SEM_DADOS: "SEM DADOS",
  };

  const semAgregado = texto.replace(/^REPLAY_AGREGADO:/, "");

  if (aliases[semAgregado]) {
    return aliases[semAgregado];
  }

  const legivel = semAgregado
    .replace(/^RTD_EXCEL_/, "")
    .replaceAll("_", " ");

  return legivel.length > 30
    ? `${legivel.slice(0, 27)}...`
    : legivel;
}

function formatarGlobal(valor) {
  if (valor === null || valor === undefined) return "-";

  const n = Number(valor);

  if (!Number.isFinite(n)) return valor;

  return n.toFixed(2);
}

