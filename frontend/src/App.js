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

        explosao:
          data.tipo_explosao,

        frequencia:
          data.frequencia_mercado,

        intensidade:
          data.intensidade_fluxo,

        scoreAgressao:
          data.score_agressao,

        leituraAgressao:
          data.leitura_agressao,

        saldo:
          data.saldo_agressor,

        delta:
          data.delta,

        volume:
          data.volume,

        pressao:
          `${data.pressao_compra}% x ${data.pressao_venda}%`,
      });

      const historicoComGlow =
        data.historico.map((candle) => {

          if (candle.explosao_detectada) {

            return {
              ...candle,
              color: "#ffffff",
              borderColor: "#00ffcc",
              wickColor: "#00ffcc",
            };
          }

          if (candle.reversao_detectada) {

            return {
              ...candle,
              color: "#ffff00",
              borderColor: "#ffff00",
              wickColor: "#ffff00",
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

        if (candle.explosao_detectada) {

          markers.push({
            time: candle.time,
            position: "belowBar",
            color: "#00ffcc",
            shape: "circle",
            text: "⚡",
          });
        }
      });

      candleSeriesRef.current.setMarkers(markers);

      let fundo = "#050915";

      if (data.tipo_explosao === "BUY EXPLOSION") {

        fundo = "#021b11";

      } else if (
        data.tipo_explosao === "SELL EXPLOSION"
      ) {

        fundo = "#1b0505";

      } else if (
        data.score_agressao > 15
      ) {

        fundo = "#061b11";

      } else if (
        data.score_agressao < -15
      ) {

        fundo = "#1b0909";
      }

      chartRef.current.applyOptions({

        layout: {

          background: {
            type: "solid",
            color: fundo,
          },

          textColor: "#ffffff",
        },
      });

    } catch (err) {

      console.error(err);
    }
  };

  useEffect(() => {

    if (!chartContainerRef.current) return;

    const chart = createChart(
      chartContainerRef.current,
      {
        width:
          chartContainerRef.current.clientWidth,

        height:
          window.innerHeight - 20,

        layout: {

          background: {
            type: "solid",
            color: "#050915",
          },

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

    const handleResize = () => {

      if (
        !chartContainerRef.current ||
        !chartRef.current
      ) return;

      chartRef.current.applyOptions({

        width:
          chartContainerRef.current.clientWidth,

        height:
          window.innerHeight - 20,
      });
    };

    window.addEventListener(
      "resize",
      handleResize
    );

    return () => {

      clearInterval(interval);

      window.removeEventListener(
        "resize",
        handleResize
      );

      chart.remove();
    };

  }, []);

  const glowPainel =

    dataInfo.explosao === "BUY EXPLOSION"

      ? "0 0 45px rgba(0,255,180,0.55)"

      : dataInfo.explosao === "SELL EXPLOSION"

      ? "0 0 45px rgba(255,40,40,0.55)"

      : dataInfo.scoreAgressao > 15

      ? "0 0 35px rgba(0,255,180,0.35)"

      : dataInfo.scoreAgressao < -15

      ? "0 0 35px rgba(255,60,60,0.35)"

      : "0 0 18px rgba(0,255,200,0.15)";

  const heatmapColor =

    dataInfo.scoreAgressao > 15

      ? "rgba(0,255,140,0.08)"

      : dataInfo.scoreAgressao < -15

      ? "rgba(255,50,50,0.08)"

      : "rgba(255,255,0,0.03)";

  return (

    <div
      style={{
        display: "flex",

        height: "100vh",

        padding: 10,

        background:
          "radial-gradient(circle at top, #111a33 0%, #050915 55%, #02040a 100%)",

        boxSizing: "border-box",
      }}
    >

      <style>
        {`
          @keyframes radarPulse {

            0% {
              transform: scale(0.85);
              opacity: 0.35;
            }

            50% {
              transform: scale(1.08);
              opacity: 1;
            }

            100% {
              transform: scale(0.85);
              opacity: 0.35;
            }
          }

          @keyframes scannerSpin {

            from {
              transform: rotate(0deg);
            }

            to {
              transform: rotate(360deg);
            }
          }
        `}
      </style>

      <div
        style={{
          flex: 1,

          minWidth: 0,

          border: "2px solid #1c2f4a",

          borderRadius: 8,

          overflow: "hidden",

          boxShadow: glowPainel,

          background: heatmapColor,

          transition:
            "all 0.4s ease",
        }}
      >

        <div
          ref={chartContainerRef}
          style={{ height: "100%" }}
        />
      </div>

      <div
        style={{
          width: 330,
          marginLeft: 10,
        }}
      >

        <Titulo>
          TRIN FLOW PRO 5.2
        </Titulo>

        <Radar
          explosao={dataInfo.explosao}
          scoreAgressao={
            dataInfo.scoreAgressao
          }
        />

        <Box color="#0b5d1e">
          SCORE:
          {dataInfo.score}
        </Box>

        <Box color="#263238">
          EXPLOSÃO:
          {dataInfo.explosao}
        </Box>

        <Box color="#004d40">
          FREQUÊNCIA:
          {dataInfo.frequencia}
        </Box>

        <Box color="#4a148c">
          INTENSIDADE:
          {dataInfo.intensidade}
        </Box>

        <Box color="#263238">
          SCORE AGRESSÃO:
          {dataInfo.scoreAgressao}
        </Box>

        <Box color="#311b92">
          {dataInfo.leituraAgressao}
        </Box>

        <Box color="#424242">
          SALDO:
          {dataInfo.saldo}
        </Box>

        <Box color="#424242">
          DELTA:
          {dataInfo.delta}
        </Box>

        <Box color="#424242">
          VOLUME:
          {dataInfo.volume}
        </Box>

        <Box color="#424242">
          PRESSÃO:
          {dataInfo.pressao}
        </Box>

      </div>
    </div>
  );
}

function Radar({
  explosao,
  scoreAgressao
}) {

  let cor = "#263238";

  let texto = "RADAR NEUTRO";

  if (explosao === "BUY EXPLOSION") {

    cor = "#00ff99";

    texto = "BUY EXPLOSION";

  } else if (
    explosao === "SELL EXPLOSION"
  ) {

    cor = "#ff3333";

    texto = "SELL EXPLOSION";

  } else if (
    scoreAgressao > 15
  ) {

    cor = "#00ffc8";

    texto = "COMPRA AGRESSIVA";

  } else if (
    scoreAgressao < -15
  ) {

    cor = "#ff4444";

    texto = "VENDA AGRESSIVA";
  }

  return (

    <div
      style={{
        position: "relative",

        height: 150,

        marginBottom: 10,

        borderRadius: 12,

        background: "#06101f",

        border: `1px solid ${cor}`,

        boxShadow: `0 0 25px ${cor}`,

        overflow: "hidden",
      }}
    >

      <div
        style={{
          position: "absolute",

          width: 110,

          height: 110,

          borderRadius: "50%",

          left: "50%",

          top: "50%",

          marginLeft: -55,

          marginTop: -55,

          border: `2px solid ${cor}`,

          boxShadow:
            `0 0 30px ${cor}`,

          animation:
            "radarPulse 1.3s infinite",
        }}
      />

      <div
        style={{
          position: "absolute",

          width: 2,

          height: 65,

          background: cor,

          left: "50%",

          top: "12%",

          transformOrigin:
            "bottom center",

          animation:
            "scannerSpin 2s linear infinite",

          boxShadow:
            `0 0 15px ${cor}`,
        }}
      />

      <div
        style={{
          position: "absolute",

          bottom: 12,

          width: "100%",

          textAlign: "center",

          color: cor,

          fontWeight: "900",

          fontSize: 14,

          letterSpacing: 1,
        }}
      >

        {texto}

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
      }}
    >
      {children}
    </div>
  );
}

function Box({
  children,
  color
}) {

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
      }}
    >
      {children}
    </div>
  );
}