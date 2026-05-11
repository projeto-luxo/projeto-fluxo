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

  const absorcaoLineRef = useRef(null);

  const carregouHistoricoRef = useRef(false);

  const [dataInfo, setDataInfo] = useState({});

  const fetchData = async () => {

    try {

      const res = await fetch(
        "http://127.0.0.1:8000/data"
      );

      const data = await res.json();

      if (!data.historico?.length) return;

      const ultimoCandle =
        data.historico[data.historico.length - 1];

      const primeiroTime =
        data.historico[0].time;

      const ultimoTime =
        ultimoCandle.time;

      setDataInfo({

        score: data.forca,

        reversao: data.reversao,

        zonaQuente:
          data.zona_quente_absorcao
            ? "🔥 ZONA QUENTE"
            : "SEM ZONA QUENTE",

        absorcao: data.absorcao,

        exaustao:
          data.exaustao
            ? "⚠ EXAUSTÃO"
            : "SEM EXAUSTÃO",

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

        pressao:
          `${data.pressao_compra}% x ${data.pressao_venda}%`,

        frequencia: data.frequencia_mercado,

        modo: data.modo_mercado,

        intensidade: data.intensidade_fluxo,

        persistenciaCompra:
          data.persistencia_compra,

        persistenciaVenda:
          data.persistencia_venda,

        scoreAgressao:
          data.score_agressao,

        leituraAgressao:
          data.leitura_agressao,

        ciclo:
          data.ciclo_institucional,

        risco:
          data.risco_ciclo,

        contexto:
          data.contexto_ciclo,
      });

      const historicoComGlow =
        data.historico.map((candle) => {

          if (candle.reversao_detectada) {

            return {
              ...candle,
              color: "#ffff00",
              borderColor: "#ffff00",
              wickColor: "#ffff00",
            };
          }

          if (
            data.zona_quente_absorcao &&
            candle.time === ultimoCandle.time
          ) {

            return {
              ...candle,
              color: "#ff9800",
              borderColor: "#ffcc00",
              wickColor: "#ffcc00",
            };
          }

          return candle;
        });

      if (!carregouHistoricoRef.current) {

        candleSeriesRef.current.setData(
          historicoComGlow
        );

        vwapLineRef.current.setData(
          data.vwap || []
        );

        vwapSuperiorRef.current.setData(
          data.vwap_superior || []
        );

        vwapInferiorRef.current.setData(
          data.vwap_inferior || []
        );

        carregouHistoricoRef.current = true;

      } else {

        candleSeriesRef.current.update(
          historicoComGlow[
            historicoComGlow.length - 1
          ]
        );

        if (data.vwap?.length > 0) {

          vwapLineRef.current.update(
            data.vwap[data.vwap.length - 1]
          );
        }

        if (data.vwap_superior?.length > 0) {

          vwapSuperiorRef.current.update(
            data.vwap_superior[
              data.vwap_superior.length - 1
            ]
          );
        }

        if (data.vwap_inferior?.length > 0) {

          vwapInferiorRef.current.update(
            data.vwap_inferior[
              data.vwap_inferior.length - 1
            ]
          );
        }
      }

      stopLineRef.current.setData([
        { time: primeiroTime, value: data.stop },
        { time: ultimoTime, value: data.stop },
      ]);

      parcialLineRef.current.setData([
        { time: primeiroTime, value: data.parcial },
        { time: ultimoTime, value: data.parcial },
      ]);

      alvoLineRef.current.setData([
        { time: primeiroTime, value: data.alvo },
        { time: ultimoTime, value: data.alvo },
      ]);

      if (
        data.zona_absorcao !== null &&
        data.zona_absorcao !== undefined
      ) {

        absorcaoLineRef.current.setData([
          {
            time: primeiroTime,
            value: data.zona_absorcao,
          },
          {
            time: ultimoTime,
            value: data.zona_absorcao,
          },
        ]);

      } else {

        absorcaoLineRef.current.setData([]);
      }

      const markers = [];

      data.historico.forEach((candle) => {

        if (candle.reversao_detectada) {

          markers.push({
            time: candle.time,
            position: "aboveBar",
            color: "yellow",
            shape: "arrowDown",
            text: "REV",
          });
        }
      });

      if (data.zona_quente_absorcao) {

        markers.push({
          time: ultimoCandle.time,
          position: "belowBar",
          color: "orange",
          shape: "arrowUp",
          text: "ABS",
        });
      }

      candleSeriesRef.current.setMarkers(markers);

    } catch (err) {

      console.error(err);
    }
  };

  useEffect(() => {

    const chart = createChart(
      chartContainerRef.current,
      {
        width:
          chartContainerRef.current.clientWidth,

        height:
          window.innerHeight - 20,

        layout: {
          backgroundColor: "#050915",
          textColor: "#ffffff",
        },

        grid: {
          vertLines: { color: "#22304a" },
          horzLines: { color: "#22304a" },
        },

        rightPriceScale: {
          borderColor: "#334158",
        },

        timeScale: {
          borderColor: "#334158",
          timeVisible: true,
          secondsVisible: true,
        },
      }
    );

    chartRef.current = chart;

    candleSeriesRef.current =
      chart.addCandlestickSeries({

        upColor: "#00ffc8",

        downColor: "#ff3b3b",

        borderUpColor: "#00ffc8",

        borderDownColor: "#ff3b3b",

        wickUpColor: "#00ffc8",

        wickDownColor: "#ff3b3b",
      });

    stopLineRef.current =
      chart.addLineSeries({
        color: "#ff0000",
        lineWidth: 1,
        lineStyle: 2,
      });

    parcialLineRef.current =
      chart.addLineSeries({
        color: "#ffff00",
        lineWidth: 1,
        lineStyle: 2,
      });

    alvoLineRef.current =
      chart.addLineSeries({
        color: "#00ff66",
        lineWidth: 1,
        lineStyle: 2,
      });

    vwapLineRef.current =
      chart.addLineSeries({
        color: "#0066ff",
        lineWidth: 3,
      });

    vwapSuperiorRef.current =
      chart.addLineSeries({
        color: "#00ffff",
        lineWidth: 1,
        lineStyle: 2,
      });

    vwapInferiorRef.current =
      chart.addLineSeries({
        color: "#00ffff",
        lineWidth: 1,
        lineStyle: 2,
      });

    absorcaoLineRef.current =
      chart.addLineSeries({
        color: "#ff9800",
        lineWidth: 3,
        lineStyle: 2,
      });

    fetchData();

    const interval =
      setInterval(fetchData, 1200);

    return () => {

      clearInterval(interval);

      chart.remove();
    };

  }, []);

  return (

    <div
      style={{
        display: "flex",
        height: "100vh",
        padding: 10,
        background:
          "radial-gradient(circle at top, #111a33 0%, #050915 55%, #02040a 100%)",
      }}
    >

      <div
        style={{
          flex: 1,
          border: "2px solid #1c2f4a",
          borderRadius: 8,
          overflow: "hidden",
          boxShadow:
            "0 0 25px rgba(0,255,200,0.15)",
        }}
      >
        <div
          ref={chartContainerRef}
          style={{ height: "100%" }}
        />
      </div>

      <div
        style={{
          width: 300,
          marginLeft: 10,
        }}
      >

        <Titulo>
          TRIN FLOW PRO 4.7
        </Titulo>

        <Box color="#0b5d1e">
          SCORE:
          {dataInfo.score}
        </Box>

        <Box color="#827717">
          {dataInfo.reversao}
        </Box>

        <Box color="#bf6b00">
          {dataInfo.zonaQuente}
        </Box>

        <Box color="#4e342e">
          ABSORÇÃO:
          {dataInfo.absorcao}
        </Box>

        <Box color="#1a1a2e">
          {dataInfo.exaustao}
        </Box>

        <Box color="#004d40">
          FREQUÊNCIA:
          {dataInfo.frequencia}
        </Box>

        <Box color="#1a237e">
          MODO:
          {dataInfo.modo}
        </Box>

        <Box color="#4a148c">
          INTENSIDADE:
          {dataInfo.intensidade}
        </Box>

        <Box color="#1b5e20">
          PERSIST COMPRA:
          {dataInfo.persistenciaCompra}%
        </Box>

        <Box color="#7f0000">
          PERSIST VENDA:
          {dataInfo.persistenciaVenda}%
        </Box>

        <Box color="#263238">
          SCORE AGRESSÃO:
          {dataInfo.scoreAgressao}
        </Box>

        <Box color="#311b92">
          {dataInfo.leituraAgressao}
        </Box>

        <Box color="#004d40">
          CICLO:
          {dataInfo.ciclo}
        </Box>

        <Box color="#b71c1c">
          RISCO:
          {dataInfo.risco}
        </Box>

        <Box color="#37474f">
          {dataInfo.contexto}
        </Box>

      </div>
    </div>
  );
}

function Titulo({ children }) {

  return (
    <div
      style={{
        background:
          "linear-gradient(90deg,#00ffc8,#0066ff)",

        color: "#001014",

        padding: 10,

        marginBottom: 8,

        borderRadius: 6,

        fontSize: 15,

        fontWeight: "900",

        textAlign: "center",

        boxShadow:
          "0 0 15px rgba(0,255,200,0.35)",
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

        fontSize: 13,

        fontWeight: "bold",

        border:
          "1px solid rgba(255,255,255,0.08)",
      }}
    >
      {children}
    </div>
  );
}