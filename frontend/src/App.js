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

  const carregouHistoricoRef = useRef(false);

  const [dataInfo, setDataInfo] = useState({});

  const fetchData = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/data");
      const data = await res.json();

      if (!data.historico || data.historico.length === 0) return;
      if (!candleSeriesRef.current) return;

      const ultimoCandle = data.historico[data.historico.length - 1];
      const primeiroTime = data.historico[0].time;
      const ultimoTime = ultimoCandle.time;

      setDataInfo({
        score: data.forca,
        reversao: data.reversao,
        zonaQuente: data.zona_quente_absorcao
          ? "ZONA QUENTE"
          : "SEM ZONA QUENTE",
        exaustao: data.exaustao ? "EXAUSTÃO" : "SEM EXAUSTÃO",
        entrada: data.entrada,
        direcao: data.tendencia,
        padrao: data.sinal,
        preco: data.preco_atual,
        stop: data.stop,
        parcial: data.parcial,
        alvo: data.alvo,
        saldo: data.saldo_agressor,
        delta: data.delta,
        volume: data.volume,
        pressao: `${data.pressao_compra ?? 0}% x ${data.pressao_venda ?? 0}%`,
      });

      if (!carregouHistoricoRef.current) {
        candleSeriesRef.current.setData(data.historico);
        vwapLineRef.current.setData(data.vwap || []);
        carregouHistoricoRef.current = true;
      } else {
        candleSeriesRef.current.update(ultimoCandle);

        if (data.vwap && data.vwap.length > 0) {
          const ultimoVwap = data.vwap[data.vwap.length - 1];
          vwapLineRef.current.update(ultimoVwap);
        }
      }

      if (data.stop !== null && data.stop !== undefined) {
        stopLineRef.current.setData([
          { time: primeiroTime, value: data.stop },
          { time: ultimoTime, value: data.stop },
        ]);
      }

      if (data.parcial !== null && data.parcial !== undefined) {
        parcialLineRef.current.setData([
          { time: primeiroTime, value: data.parcial },
          { time: ultimoTime, value: data.parcial },
        ]);
      }

      if (data.alvo !== null && data.alvo !== undefined) {
        alvoLineRef.current.setData([
          { time: primeiroTime, value: data.alvo },
          { time: ultimoTime, value: data.alvo },
        ]);
      }

      const markers = data.historico
        .filter((candle) => candle.reversao_detectada === true)
        .map((candle) => ({
          time: candle.time,
          position: "aboveBar",
          color: "yellow",
          shape: "arrowDown",
          text: "REV",
        }));

      candleSeriesRef.current.setMarkers(markers);
    } catch (err) {
      console.error("Erro ao buscar dados:", err);
    }
  };

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: window.innerHeight - 20,
      layout: {
        backgroundColor: "#0b111f",
        textColor: "#ffffff",
      },
      grid: {
        vertLines: { color: "#334158" },
        horzLines: { color: "#334158" },
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
      upColor: "#00d4aa",
      downColor: "#ff4d4d",
      borderVisible: false,
      wickUpColor: "#00d4aa",
      wickDownColor: "#ff4d4d",
    });

    stopLineRef.current = chart.addLineSeries({
      color: "red",
      lineWidth: 1,
    });

    parcialLineRef.current = chart.addLineSeries({
      color: "yellow",
      lineWidth: 1,
    });

    alvoLineRef.current = chart.addLineSeries({
      color: "green",
      lineWidth: 1,
    });

    vwapLineRef.current = chart.addLineSeries({
      color: "blue",
      lineWidth: 2,
    });

    fetchData();

    const interval = setInterval(fetchData, 1200);

    const handleResize = () => {
      if (!chartContainerRef.current || !chartRef.current) return;

      chartRef.current.applyOptions({
        width: chartContainerRef.current.clientWidth,
        height: window.innerHeight - 20,
      });
    };

    window.addEventListener("resize", handleResize);

    return () => {
      clearInterval(interval);
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, []);

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        padding: 10,
        background: "#050915",
        boxSizing: "border-box",
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <div ref={chartContainerRef} style={{ height: "100%" }} />
      </div>

      <div style={{ width: 230, marginLeft: 10 }}>
        <Box color="#1b5e20">SCORE INSTITUCIONAL: {dataInfo.score}</Box>
        <Box color="#827717">{dataInfo.reversao}</Box>
        <Box color="#1a1a2e">{dataInfo.zonaQuente}</Box>
        <Box color="#1a1a2e">{dataInfo.exaustao}</Box>
        <Box color="#424242">ENTRADA: {dataInfo.entrada}</Box>
        <Box color="#424242">DIREÇÃO: {dataInfo.direcao}</Box>
        <Box color="#424242">PADRÃO: {dataInfo.padrao}</Box>
        <Box color="#424242">PREÇO: {dataInfo.preco}</Box>
        <Box color="#424242">STOP: {dataInfo.stop}</Box>
        <Box color="#424242">PARCIAL: {dataInfo.parcial}</Box>
        <Box color="#424242">ALVO: {dataInfo.alvo}</Box>
        <Box color="#424242">SALDO: {dataInfo.saldo}</Box>
        <Box color="#424242">DELTA: {dataInfo.delta}</Box>
        <Box color="#424242">VOLUME: {dataInfo.volume}</Box>
        <Box color="#424242">PRESSÃO: {dataInfo.pressao}</Box>
      </div>
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
        borderRadius: 4,
        fontSize: 13,
        fontWeight: "bold",
      }}
    >
      {children}
    </div>
  );
}