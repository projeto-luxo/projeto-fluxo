// frontend/src/App.js
import React, { useEffect, useRef, useState } from "react";
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

  const vwapLineRef = useRef(null);
  const vwapSuperiorRef = useRef(null);
  const vwapInferiorRef = useRef(null);

  const socketRef = useRef(null);
  const carregouHistoricoRef = useRef(false);

  const [dataInfo, setDataInfo] = useState({});
  const [wsStatus, setWsStatus] = useState("DESCONECTADO");

  const ordenarPorTempo = (lista) => {
    if (!Array.isArray(lista)) return [];
    return [...lista].sort((a, b) => a.time - b.time);
  };

  const formatar = (valor) => {
    if (valor === null || valor === undefined) return "-";
    const n = Number(valor);
    if (!Number.isFinite(n)) return valor;
    return n.toFixed(2);
  };

  const setLinhaHorizontal = (seriesRef, primeiroTime, ultimoTime, valor) => {
    if (!seriesRef.current) return;

    if (valor === null || valor === undefined || Number.isNaN(Number(valor))) {
      seriesRef.current.setData([]);
      return;
    }

    seriesRef.current.setData([
      { time: primeiroTime, value: Number(valor) },
      { time: ultimoTime, value: Number(valor) },
    ]);
  };

  const gerarMarkersInstitucionais = (historico) => {
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
  };

  const processarDados = (data) => {
    setWsStatus("ONLINE");

    const historico = ordenarPorTempo(data.historico || []);
    const vwap = ordenarPorTempo(data.vwap || []);
    const vwapSuperior = ordenarPorTempo(data.vwap_superior || []);
    const vwapInferior = ordenarPorTempo(data.vwap_inferior || []);

    if (!historico.length || !candleSeriesRef.current) return;

    const ultimoCandle = historico[historico.length - 1];
    const primeiroTime = historico[0].time;
    const ultimoTime = ultimoCandle.time;

    const engine = data.engine || {};
    const agressao = data.agressao || {};

    setDataInfo({
      score: data.forca ?? data.score ?? data.sinal?.forca ?? engine.engine_score,
      sinal: data.sinal?.sinal ?? data.sinal ?? "SEM ENTRADA",
      entrada: data.entrada ?? data.sinal?.entrada ?? "AGUARDAR",
      tendencia: data.tendencia ?? data.sinal?.tendencia ?? "NEUTRO",

      frequencia: data.frequencia_mercado ?? agressao.frequencia_mercado,
      intensidade: data.intensidade_fluxo ?? agressao.intensidade_fluxo,
      scoreAgressao: data.score_agressao ?? agressao.score_agressao,
      leituraAgressao: data.leitura_agressao ?? agressao.leitura_agressao,

      saldo: data.saldo_agressor ?? ultimoCandle.saldo,
      delta: data.delta ?? ultimoCandle.delta,
      volume: data.volume ?? ultimoCandle.volume,

      compra: data.pressao_compra ?? agressao.persistencia_compra ?? 0,
      venda: data.pressao_venda ?? agressao.persistencia_venda ?? 0,

      explosao: data.tipo_explosao ?? agressao.tipo_explosao ?? agressao.explosao ?? "SEM EXPLOSÃO",
      explosaoDetectada: data.explosao_detectada ?? agressao.explosao_detectada,

      reversao: data.reversao,

      engineScore: data.engine_score ?? engine.engine_score,
      engineFase: data.engine_fase ?? engine.engine_fase,
      engineDirecao: data.engine_direcao ?? engine.engine_direcao,
      engineTrap: data.engine_trap ?? engine.engine_trap,
      engineAbsorcao: data.engine_absorcao ?? engine.engine_absorcao,
      engineSeqDelta: data.engine_seq_delta ?? engine.engine_seq_delta,

      stop: data.stop,
      parcial: data.parcial,
      alvo: data.alvo,
    });

    if (!carregouHistoricoRef.current) {
      candleSeriesRef.current.setData(historico);
      vwapLineRef.current.setData(vwap);
      vwapSuperiorRef.current.setData(vwapSuperior);
      vwapInferiorRef.current.setData(vwapInferior);

      if (typeof candleSeriesRef.current.setMarkers === "function") {
        candleSeriesRef.current.setMarkers(gerarMarkersInstitucionais(historico));
      }

      carregouHistoricoRef.current = true;
    } else {
      candleSeriesRef.current.update(ultimoCandle);

      if (vwap.length) vwapLineRef.current.update(vwap[vwap.length - 1]);
      if (vwapSuperior.length) vwapSuperiorRef.current.update(vwapSuperior[vwapSuperior.length - 1]);
      if (vwapInferior.length) vwapInferiorRef.current.update(vwapInferior[vwapInferior.length - 1]);

      if (typeof candleSeriesRef.current.setMarkers === "function") {
        candleSeriesRef.current.setMarkers(gerarMarkersInstitucionais(historico));
      }
    }

    setLinhaHorizontal(stopLineRef, primeiroTime, ultimoTime, data.stop);
    setLinhaHorizontal(parcialLineRef, primeiroTime, ultimoTime, data.parcial);
    setLinhaHorizontal(alvoLineRef, primeiroTime, ultimoTime, data.alvo);
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: window.innerHeight - 20,
      layout: {
        background: {
          type: "solid",
          color: "#020816",
        },
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
        fixLeftEdge: true,
        fixRightEdge: false,
        lockVisibleTimeRangeOnResize: false,
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
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);

      if (socketRef.current) {
        disconnectTrinWebSocket();
      }

      chart.remove();
    };
  }, []);

  const scoreAgressao = Number(dataInfo.scoreAgressao || 0);
  const compra = Number(dataInfo.compra || 0);
  const venda = Number(dataInfo.venda || 0);

  const glowRadar =
    wsStatus === "ONLINE"
      ? dataInfo.explosao && dataInfo.explosao !== "SEM EXPLOSÃO"
        ? "#ffaa00"
        : scoreAgressao > 15
        ? "#00ff99"
        : scoreAgressao < -15
        ? "#ff3333"
        : compra > venda
        ? "#00ffc8"
        : venda > compra
        ? "#ff4444"
        : "#00d4ff"
      : "#ff4444";

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        padding: 10,
        background:
          "radial-gradient(circle at top, #071120 0%, #020816 70%)",
        boxSizing: "border-box",
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

          @keyframes livePulse {
            0% { opacity: .45; }
            50% { opacity: 1; }
            100% { opacity: .45; }
          }
        `}
      </style>

      <div
        style={{
          flex: 1,
          minWidth: 0,
          border: `2px solid ${glowRadar}`,
          borderRadius: 8,
          overflow: "hidden",
          boxShadow: `0 0 35px ${glowRadar}`,
          position: "relative",
        }}
      >
        <TopBar dataInfo={dataInfo} cor={glowRadar} wsStatus={wsStatus} />
        <div ref={chartContainerRef} style={{ height: "100%" }} />
      </div>

      <div style={{ width: 340, marginLeft: 10 }}>
        <Titulo>TRIN FLOW PRO 5.8.1 WS</Titulo>

        <Radar cor={glowRadar} intensidade={dataInfo.intensidade} wsStatus={wsStatus} />

        <Box color="#0b5d1e">SCORE: {dataInfo.score ?? "-"}</Box>
        <Box color="#004d40">FREQUÊNCIA: {dataInfo.frequencia || "-"}</Box>
        <Box color="#4a148c">INTENSIDADE: {formatar(dataInfo.intensidade)}</Box>
        <Box color="#263238">SCORE AGRESSÃO: {formatar(dataInfo.scoreAgressao)}</Box>
        <Box color="#311b92">{dataInfo.leituraAgressao || "AGUARDANDO LEITURA"}</Box>

        <Box color="#102027">SINAL: {dataInfo.sinal || "SEM ENTRADA"}</Box>
        <Box color="#1b2631">ENTRADA: {dataInfo.entrada || "AGUARDAR"}</Box>
        <Box color="#263238">TENDÊNCIA: {dataInfo.tendencia || "NEUTRO"}</Box>

        <Box color="#424242">SALDO: {dataInfo.saldo ?? "-"}</Box>
        <Box color="#424242">DELTA: {dataInfo.delta ?? "-"}</Box>
        <Box color="#424242">VOLUME: {dataInfo.volume ?? "-"}</Box>
        <Box color="#263238">EXPLOSÃO: {dataInfo.explosao || "SEM EXPLOSÃO"}</Box>

        <Box color="#0d2538">FASE: {dataInfo.engineFase || "AGUARDANDO"}</Box>
        <Box color="#0d2538">DIREÇÃO: {dataInfo.engineDirecao || "NEUTRO"}</Box>
        <Box color="#0d2538">TRAP: {dataInfo.engineTrap || "SEM TRAP"}</Box>
        <Box color="#0d2538">SEQ DELTA: {dataInfo.engineSeqDelta ?? "-"}</Box>

        <PressaoBar compra={dataInfo.compra} venda={dataInfo.venda} />
      </div>
    </div>
  );
}

function TopBar({ dataInfo, cor, wsStatus }) {
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
      <MiniBadge cor={cor}>FASE: {dataInfo.engineFase || "AGUARDANDO"}</MiniBadge>
      <MiniBadge cor={cor}>DIREÇÃO: {dataInfo.engineDirecao || "NEUTRO"}</MiniBadge>
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
        height: 170,
        background: "#05101d",
        border: `1px solid ${cor}`,
        borderRadius: 12,
        marginBottom: 10,
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
        PRESSÃO INSTITUCIONAL
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
        padding: 10,
        marginBottom: 8,
        borderRadius: 6,
        fontWeight: "900",
        textAlign: "center",
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
        padding: 8,
        marginBottom: 5,
        borderRadius: 5,
        fontWeight: "bold",
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