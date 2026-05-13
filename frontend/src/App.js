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
  const [wsStatus, setWsStatus] = useState("DESCONECTADO");

  const ordenarPorTempo = (lista) => {
    if (!Array.isArray(lista)) return [];

    const mapa = new Map();

    lista.forEach((item) => {
      if (item && item.time !== undefined) {
        mapa.set(item.time, item);
      }
    });

    return Array.from(mapa.values()).sort((a, b) => a.time - b.time);
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
    const historico = ordenarPorTempo(data.historico);
    const vwap = ordenarPorTempo(data.vwap || []);
    const vwapSuperior = ordenarPorTempo(data.vwap_superior || []);
    const vwapInferior = ordenarPorTempo(data.vwap_inferior || []);

    if (!historico.length) return;
    if (!candleSeriesRef.current) return;

    const ultimoCandle = historico[historico.length - 1];
    const primeiroTime = historico[0].time;
    const ultimoTime = ultimoCandle.time;

    setDataInfo({
      score: data.forca,
      sinal: data.sinal,
      entrada: data.entrada,
      tendencia: data.tendencia,

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
      explosaoDetectada: data.explosao_detectada,

      reversao: data.reversao,

      engineScore: data.engine_score,
      engineFase: data.engine_fase,
      engineDirecao: data.engine_direcao,
      engineTrap: data.engine_trap,
      engineAbsorcao: data.engine_absorcao,
      engineSeqDelta: data.engine_seq_delta,
    });

    if (!carregouHistoricoRef.current) {
      candleSeriesRef.current.setData(historico);
      vwapLineRef.current.setData(vwap);
      vwapSuperiorRef.current.setData(vwapSuperior);
      vwapInferiorRef.current.setData(vwapInferior);

      if (typeof candleSeriesRef.current.setMarkers === "function") {
        candleSeriesRef.current.setMarkers(gerarMarkersInstitucionais(historico));
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

    if (socketRef.current && socketRef.current.readyState <= 1) {
      return;
    }

    const socket = new WebSocket("ws://127.0.0.1:8000/ws");
    socketRef.current = socket;

    socket.onopen = () => {
      setWsStatus("ONLINE");
      console.log("TRIN WebSocket conectado.");
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        processarDados(data);
      } catch (erro) {
        console.error("Erro ao processar dados TRIN:", erro);
      }
    };

    socket.onerror = (error) => {
      setWsStatus("ERRO");
      console.error("Erro no WebSocket:", error);
    };

    socket.onclose = () => {
      setWsStatus("DESCONECTADO");
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

      if (socketRef.current === socket) {
        socket.close();
        socketRef.current = null;
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
    compra >= 65
      ? "DOMÍNIO COMPRADOR"
      : venda >= 65
      ? "DOMÍNIO VENDEDOR"
      : "FLUXO EQUILIBRADO";

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
          borderRadius: 10,
          overflow: "hidden",
          boxShadow: `0 0 35px ${glowRadar}`,
          position: "relative",
        }}
      >
        <TopBar dataInfo={dataInfo} cor={glowRadar} wsStatus={wsStatus} />
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
          boxSizing: "border-box",
          boxShadow: `0 0 25px ${glowRadar}`,
        }}
      >
        <Titulo>TRIN FLOW PRO 5.8.1 WS HARDENED</Titulo>

        <Radar cor={glowRadar} intensidade={dataInfo.intensidade} wsStatus={wsStatus} />

        <Secao titulo="REGIME INSTITUCIONAL">
          <Linha label="WS" valor={wsStatus} cor={wsStatus === "ONLINE" ? "#00ff99" : "#ff4444"} />
          <Linha label="FASE" valor={dataInfo.engineFase || "AGUARDANDO"} cor="#00d4ff" />
          <Linha label="DIREÇÃO" valor={dataInfo.engineDirecao || "NEUTRO"} cor="#00ffc8" />
          <Linha label="ENTRADA" valor={dataInfo.entrada || "AGUARDAR"} cor="#ffaa00" />
          <Linha label="SINAL" valor={dataInfo.sinal || "SEM ENTRADA"} cor="#ffffff" />
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
          <Linha label="ENGINE SCORE" valor={dataInfo.engineScore ?? "-"} cor="#00d4ff" />
          <Linha label="SEQ DELTA" valor={dataInfo.engineSeqDelta ?? "-"} cor="#ffaa00" />
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
        <span>RADAR WS {wsStatus}</span>
        <span>{formatarGlobal(intensidade)}</span>
      </div>
    </div>
  );
}

function formatarGlobal(valor) {
  if (valor === null || valor === undefined) return "-";
  const n = Number(valor);
  if (!Number.isFinite(n)) return valor;
  return n.toFixed(2);
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