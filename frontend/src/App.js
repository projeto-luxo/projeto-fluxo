import React, { useCallback, useEffect, useRef, useState } from "react";
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

  const ordenarPorTempo = useCallback((lista) => {
    if (!Array.isArray(lista)) return [];

    const mapa = new Map();

    lista.forEach((item) => {
      if (item && item.time !== undefined) {
        mapa.set(item.time, item);
      }
    });

    return Array.from(mapa.values()).sort((a, b) => a.time - b.time);
  }, []);

  const setLinhaHorizontal = useCallback(
    (seriesRef, primeiroTime, ultimoTime, valor) => {
      if (!seriesRef.current) return;

      if (valor === null || valor === undefined || Number.isNaN(Number(valor))) {
        seriesRef.current.setData([]);
        return;
      }

      seriesRef.current.setData([
        { time: primeiroTime, value: Number(valor) },
        { time: ultimoTime, value: Number(valor) },
      ]);
    },
    []
  );

  const gerarMarkersREV = useCallback((historico) => {
    if (!historico || historico.length === 0) return [];

    return historico
      .filter((candle) => candle.reversao_detectada)
      .slice(-20)
      .map((candle) => ({
        time: candle.time,
        position: candle.close >= candle.open ? "belowBar" : "aboveBar",
        color: "#ffaa00",
        shape: "circle",
        text: "REV",
      }));
  }, []);

  const processarDados = useCallback(
    (data) => {
      const historicoOrdenado = ordenarPorTempo(data.historico);

      if (!historicoOrdenado.length) return;
      if (!candleSeriesRef.current) return;

      const ultimoCandle = historicoOrdenado[historicoOrdenado.length - 1];
      const primeiroTime = historicoOrdenado[0].time;
      const ultimoTime = ultimoCandle.time;

      const vwap = ordenarPorTempo(data.vwap || []);
      const vwapSuperior = ordenarPorTempo(data.vwap_superior || []);
      const vwapInferior = ordenarPorTempo(data.vwap_inferior || []);

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
        reversao: data.reversao,
        entrada: data.entrada,
        tendencia: data.tendencia,
        engineFase: data.engine_fase,
        engineDirecao: data.engine_direcao,
        engineScore: data.engine_score,
        engineTrap: data.engine_trap,
      });

      if (!carregouHistoricoRef.current) {
        candleSeriesRef.current.setData(historicoOrdenado);
        vwapLineRef.current.setData(vwap);
        vwapSuperiorRef.current.setData(vwapSuperior);
        vwapInferiorRef.current.setData(vwapInferior);

        if (typeof candleSeriesRef.current.setMarkers === "function") {
          candleSeriesRef.current.setMarkers(gerarMarkersREV(historicoOrdenado));
        }

        setTimeout(() => {
          if (chartRef.current) {
            chartRef.current.timeScale().setVisibleLogicalRange({
              from: 0,
              to: 120,
            });
          }
        }, 100);

        carregouHistoricoRef.current = true;
      } else {
        candleSeriesRef.current.update(ultimoCandle);

        if (vwap.length > 0) {
          vwapLineRef.current.update(vwap[vwap.length - 1]);
        }

        if (vwapSuperior.length > 0) {
          vwapSuperiorRef.current.update(vwapSuperior[vwapSuperior.length - 1]);
        }

        if (vwapInferior.length > 0) {
          vwapInferiorRef.current.update(vwapInferior[vwapInferior.length - 1]);
        }

        if (typeof candleSeriesRef.current.setMarkers === "function") {
          candleSeriesRef.current.setMarkers(gerarMarkersREV(historicoOrdenado));
        }
      }

      setLinhaHorizontal(stopLineRef, primeiroTime, ultimoTime, data.stop);
      setLinhaHorizontal(parcialLineRef, primeiroTime, ultimoTime, data.parcial);
      setLinhaHorizontal(alvoLineRef, primeiroTime, ultimoTime, data.alvo);
    },
    [ordenarPorTempo, gerarMarkersREV, setLinhaHorizontal]
  );

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

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const scoreAgressao = Number(dataInfo.scoreAgressao || 0);
  const compra = Number(dataInfo.compra || 0);
  const venda = Number(dataInfo.venda || 0);

  const glowRadar =
    dataInfo.explosao && dataInfo.explosao !== "SEM EXPLOSÃO"
      ? "#ffaa00"
      : scoreAgressao > 15
      ? "#00ff99"
      : scoreAgressao < -15
      ? "#ff3333"
      : compra > venda
      ? "#00ffc8"
      : venda > compra
      ? "#ff4444"
      : "#00d4ff";

  const leituraDominante =
    compra > 65
      ? "DOMÍNIO COMPRADOR"
      : venda > 65
      ? "DOMÍNIO VENDEDOR"
      : "FLUXO EQUILIBRADO";

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        padding: 10,
        background:
          "radial-gradient(circle at top, #071120 0%, #020816 72%)",
        boxSizing: "border-box",
      }}
    >
      <style>
        {`
          @keyframes pulseRadar {
            0% { transform: scale(0.92); opacity: 0.50; }
            50% { transform: scale(1.08); opacity: 1; }
            100% { transform: scale(0.92); opacity: 0.50; }
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
          borderRadius: 10,
          overflow: "hidden",
          boxShadow: `0 0 38px ${glowRadar}`,
        }}
      >
        <div ref={chartContainerRef} style={{ height: "100%" }} />
      </div>

      <div
        style={{
          width: 370,
          marginLeft: 10,
          background:
            "linear-gradient(180deg, rgba(3,10,24,0.98), rgba(1,5,12,0.98))",
          borderRadius: 10,
          border: `1px solid ${glowRadar}`,
          padding: 8,
          boxShadow: `0 0 26px ${glowRadar}`,
          boxSizing: "border-box",
        }}
      >
        <Titulo>TRIN FLOW PRO 5.7 WS DESK</Titulo>

        <Radar cor={glowRadar} intensidade={dataInfo.intensidade} />

        <Secao titulo="REGIME INSTITUCIONAL">
          <Linha label="FASE" valor={dataInfo.engineFase || "AGUARDANDO"} cor="#00d4ff" />
          <Linha label="DIREÇÃO" valor={dataInfo.engineDirecao || "NEUTRO"} cor="#00ffc8" />
          <Linha label="ENTRADA" valor={dataInfo.entrada || "AGUARDAR"} cor="#ffaa00" />
          <Linha label="REVERSÃO" valor={dataInfo.reversao || "SEM REVERSÃO"} cor="#ffaa00" />
          <Linha label="TRAP" valor={dataInfo.engineTrap || "SEM TRAP"} cor="#ff66ff" />
        </Secao>

        <Secao titulo="AGRESSÃO E FLUXO">
          <BoxDestaque cor="#0b5d1e">SCORE: {dataInfo.score}</BoxDestaque>
          <BoxDestaque cor="#263238">
            SCORE AGRESSÃO: {formatar(dataInfo.scoreAgressao)}
          </BoxDestaque>
          <BoxDestaque cor="#311b92">
            {dataInfo.leituraAgressao || "AGUARDANDO LEITURA"}
          </BoxDestaque>
          <Linha label="FREQUÊNCIA" valor={dataInfo.frequencia || "-"} cor="#00ffc8" />
          <Linha label="INTENSIDADE" valor={formatar(dataInfo.intensidade)} cor="#b56cff" />
        </Secao>

        <Secao titulo="TAPE SIMULADO">
          <Linha label="SALDO" valor={dataInfo.saldo ?? "-"} cor="#ffffff" />
          <Linha label="DELTA" valor={dataInfo.delta ?? "-"} cor="#ffffff" />
          <Linha label="VOLUME" valor={dataInfo.volume ?? "-"} cor="#ffffff" />
          <Linha label="EXPLOSÃO" valor={dataInfo.explosao || "SEM EXPLOSÃO"} cor="#ffaa00" />
        </Secao>

        <Secao titulo={leituraDominante}>
          <PressaoBar compra={dataInfo.compra} venda={dataInfo.venda} />
        </Secao>
      </div>
    </div>
  );
}

function formatar(valor) {
  if (valor === null || valor === undefined) return "-";
  const n = Number(valor);
  if (!Number.isFinite(n)) return valor;
  return n.toFixed(2);
}

function Radar({ cor, intensidade }) {
  return (
    <div
      style={{
        height: 160,
        background:
          "radial-gradient(circle at center, rgba(0,255,200,0.08), #05101d 62%)",
        border: `1px solid ${cor}`,
        borderRadius: 12,
        marginBottom: 8,
        position: "relative",
        overflow: "hidden",
        boxShadow: `0 0 26px ${cor}`,
      }}
    >
      <div
        style={{
          width: 116,
          height: 116,
          borderRadius: "50%",
          border: `2px solid ${cor}`,
          position: "absolute",
          left: "50%",
          top: "50%",
          marginLeft: -58,
          marginTop: -58,
          animation: "pulseRadar 1.4s infinite",
          boxShadow: `0 0 35px ${cor}`,
        }}
      />

      <div
        style={{
          width: 2,
          height: 72,
          background: cor,
          position: "absolute",
          left: "50%",
          top: "14%",
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
        <span>RADAR WS</span>
        <span>{formatar(intensidade)}</span>
      </div>
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
        borderRadius: 7,
        fontWeight: "900",
        textAlign: "center",
        letterSpacing: 0.5,
        boxShadow: "0 0 16px #00ffc8",
      }}
    >
      {children}
    </div>
  );
}

function Secao({ titulo, children }) {
  return (
    <div
      style={{
        background: "rgba(0,0,0,0.34)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 8,
        padding: 8,
        marginBottom: 8,
      }}
    >
      <div
        style={{
          color: "#8fbbe8",
          fontSize: 11,
          fontWeight: "900",
          marginBottom: 6,
          letterSpacing: 0.8,
        }}
      >
        {titulo}
      </div>
      {children}
    </div>
  );
}

function Linha({ label, valor, cor }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        background: "#101722",
        color: "#ffffff",
        padding: "6px 8px",
        marginBottom: 5,
        borderRadius: 5,
        fontWeight: "800",
        fontSize: 12,
      }}
    >
      <span style={{ color: "#9fb3c8" }}>{label}</span>
      <span style={{ color: cor }}>{valor}</span>
    </div>
  );
}

function BoxDestaque({ children, cor }) {
  return (
    <div
      style={{
        backgroundColor: cor,
        color: "white",
        padding: 8,
        marginBottom: 5,
        borderRadius: 5,
        fontWeight: "900",
        border: "1px solid rgba(255,255,255,0.08)",
      }}
    >
      {children}
    </div>
  );
}

function PressaoBar({ compra, venda }) {
  return (
    <div>
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

      <div style={{ color: "#00ffc8", marginBottom: 10, fontWeight: "900" }}>
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

      <div style={{ color: "#ff4444", fontWeight: "900" }}>
        VENDA: {venda || 0}%
      </div>
    </div>
  );
}