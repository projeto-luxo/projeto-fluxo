import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";

export default function App() {
  const chartContainerRef = useRef();
  const candleSeriesRef = useRef();
  const stopLineRef = useRef();
  const parcialLineRef = useRef();
  const alvoLineRef = useRef();
  const vwapLineRef = useRef();

  const [score, setScore] = useState(0);
  const [reversao, setReversao] = useState("SEM REVERSÃO");
  const [zonaQuente, setZonaQuente] = useState("SEM ZONA QUENTE");
  const [exaustao, setExaustao] = useState("SEM EXAUSTÃO");
  const [tendencia, setTendencia] = useState("MERCADO LATERAL");
  const [entrada, setEntrada] = useState("AGUARDAR");

  const fetchData = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/data");
      const data = await res.json();

      setScore(data.forca);
      setReversao(data.reversao);
      setZonaQuente(data.zona_quente_absorcao ? "ZONA QUENTE" : "SEM ZONA QUENTE");
      setExaustao(data.exaustao ? "EXAUSTÃO" : "SEM EXAUSTÃO");
      setTendencia(data.tendencia);
      setEntrada(data.entrada);

      // Candles
      candleSeriesRef.current.setData(data.historico);

      // Linhas de preço
      stopLineRef.current.setData([{ time: data.historico[data.historico.length-1].time, value: data.stop }]);
      parcialLineRef.current.setData([{ time: data.historico[data.historico.length-1].time, value: data.parcial }]);
      alvoLineRef.current.setData([{ time: data.historico[data.historico.length-1].time, value: data.alvo }]);
      vwapLineRef.current.setData(data.vwap);

    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: { backgroundColor: "#0b111f", textColor: "#ffffff" },
      grid: { vertLines: { color: "#334158" }, horzLines: { color: "#334158" } },
      rightPriceScale: { borderColor: "#334158" },
      timeScale: { borderColor: "#334158", timeVisible: true, secondsVisible: true },
    });

    candleSeriesRef.current = chart.addCandlestickSeries();
    stopLineRef.current = chart.addLineSeries({ color: "red", lineWidth: 1 });
    parcialLineRef.current = chart.addLineSeries({ color: "yellow", lineWidth: 1 });
    alvoLineRef.current = chart.addLineSeries({ color: "green", lineWidth: 1 });
    vwapLineRef.current = chart.addLineSeries({ color: "blue", lineWidth: 1 });

    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ display: "flex", padding: 10 }}>
      <div style={{ flex: 1 }}>
        <div ref={chartContainerRef} />
      </div>
      <div style={{ width: 220, marginLeft: 10 }}>
        <div style={{ backgroundColor: "#1b5e20", color: "white", padding: 8, marginBottom: 5 }}>
          SCORE INSTITUCIONAL: {score}
        </div>
        <div style={{ backgroundColor: "#827717", color: "white", padding: 8, marginBottom: 5 }}>
          {reversao}
        </div>
        <div style={{ backgroundColor: "#1a1a2e", color: "white", padding: 8, marginBottom: 5 }}>
          {zonaQuente}
        </div>
        <div style={{ backgroundColor: "#1a1a2e", color: "white", padding: 8, marginBottom: 5 }}>
          {exaustao}
        </div>
        <div style={{ backgroundColor: "#0b3d91", color: "white", padding: 8, marginBottom: 5 }}>
          TENDÊNCIA: {tendencia}
        </div>
        <div style={{ backgroundColor: "#333333", color: "white", padding: 8 }}>
          ENTRADA: {entrada}
        </div>
      </div>
    </div>
  );
}