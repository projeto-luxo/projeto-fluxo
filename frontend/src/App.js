import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";

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

  const processarDados = (data) => {
    if (!data.historico?.length) return;
    if (!candleSeriesRef.current) return;

    const ultimoCandle = data.historico[data.historico.length - 1];
    const primeiroTime = data.historico[0].time;
    const ultimoTime = ultimoCandle.time;

    setDataInfo({
      score: data.forca,
      frequencia: data.frequencia_mercado,
      intensidade: data.intensidade_fluxo,
      scoreAgressao: data.score_agressao,
      leituraAgressao: data.leitura_agressao,
      saldo: data.saldo_agressor,
      delta: data.delta,
      volume: data.volume,
      compra: data.pressao_compra || 0,
      venda: data.pressao_venda || 0,
      explosao: data.tipo_explosao,
    });

    if (!carregouHistoricoRef.current) {
      candleSeriesRef.current.setData(data.historico);
      vwapLineRef.current.setData(data.vwap || []);
      vwapSuperiorRef.current.setData(data.vwap_superior || []);
      vwapInferiorRef.current.setData(data.vwap_inferior || []);
      carregouHistoricoRef.current = true;
    } else {
      candleSeriesRef.current.update(ultimoCandle);

      if (data.vwap?.length > 0) {
        vwapLineRef.current.update(data.vwap[data.vwap.length - 1]);
      }

      if (data.vwap_superior?.length > 0) {
        vwapSuperiorRef.current.update(
          data.vwap_superior[data.vwap_superior.length - 1]
        );
      }

      if (data.vwap_inferior?.length > 0) {
        vwapInferiorRef.current.update(
          data.vwap_inferior[data.vwap_inferior.length - 1]
        );
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
        secondsVisible: true,
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

    socketRef.current = new WebSocket("ws://127.0.0.1:8000/ws");

    socketRef.current.onopen = () => {
      console.log("TRIN WebSocket conectado.");
    };

    socketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      processarDados(data);
    };

    socketRef.current.onerror = (error) => {
      console.error("Erro no WebSocket:", error);
    };

    socketRef.current.onclose = () => {
      console.log("TRIN WebSocket desconectado.");
    };

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
        socketRef.current.close();
      }

      chart.remove();
    };
  }, []);

  const glowRadar =
    dataInfo.scoreAgressao > 15
      ? "#00ff99"
      : dataInfo.scoreAgressao < -15
      ? "#ff3333"
      : "#00d4ff";

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
        `}
      </style>

      <div
        style={{
          flex: 1,
          minWidth: 0,
          border: "2px solid #18304f",
          borderRadius: 8,
          overflow: "hidden",
          boxShadow: `0 0 35px ${glowRadar}`,
        }}
      >
        <div ref={chartContainerRef} style={{ height: "100%" }} />
      </div>

      <div style={{ width: 340, marginLeft: 10 }}>
        <Titulo>TRIN FLOW PRO 5.5 WS</Titulo>

        <Radar cor={glowRadar} />

        <Box color="#0b5d1e">SCORE: {dataInfo.score}</Box>
        <Box color="#004d40">FREQUÊNCIA: {dataInfo.frequencia}</Box>
        <Box color="#4a148c">INTENSIDADE: {dataInfo.intensidade}</Box>
        <Box color="#263238">
          SCORE AGRESSÃO: {dataInfo.scoreAgressao}
        </Box>
        <Box color="#311b92">{dataInfo.leituraAgressao}</Box>
        <Box color="#424242">SALDO: {dataInfo.saldo}</Box>
        <Box color="#424242">DELTA: {dataInfo.delta}</Box>
        <Box color="#424242">VOLUME: {dataInfo.volume}</Box>
        <Box color="#263238">EXPLOSÃO: {dataInfo.explosao}</Box>

        <PressaoBar compra={dataInfo.compra} venda={dataInfo.venda} />
      </div>
    </div>
  );
}

function Radar({ cor }) {
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
      <div style={{ fontWeight: "bold", marginBottom: 8 }}>
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
            width: `${compra || 0}%`,
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
            width: `${venda || 0}%`,
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