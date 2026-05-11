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

        pressaoCompra:
          data.pressao_compra || 0,

        pressaoVenda:
          data.pressao_venda || 0,
      });

      if (!carregouHistoricoRef.current) {

        candleSeriesRef.current.setData(
          data.historico
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
          ultimoCandle
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

      let fundo = "#050915";

      if (data.score_agressao > 15) {

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

        boxSizing: "border-box",
      }}
    >

      <div
        style={{
          flex: 1,

          border: "2px solid #1c2f4a",

          borderRadius: 8,

          overflow: "hidden",

          boxShadow:
            "0 0 30px rgba(0,255,180,0.25)",
        }}
      >

        <div
          ref={chartContainerRef}
          style={{ height: "100%" }}
        />
      </div>

      <div
        style={{
          width: 340,
          marginLeft: 10,
        }}
      >

        <Titulo>
          TRIN FLOW PRO 5.3
        </Titulo>

        <Radar
          scoreAgressao={
            dataInfo.scoreAgressao
          }
        />

        <Box color="#0b5d1e">
          SCORE:
          {dataInfo.score}
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

        <PressaoBar
          compra={dataInfo.pressaoCompra}
          venda={dataInfo.pressaoVenda}
        />

      </div>
    </div>
  );
}

function PressaoBar({
  compra,
  venda
}) {

  return (

    <div
      style={{
        background: "#121212",

        padding: 10,

        borderRadius: 6,

        marginTop: 8,
      }}
    >

      <div
        style={{
          marginBottom: 8,
          fontWeight: "bold",
        }}
      >
        PRESSÃO INSTITUCIONAL
      </div>

      <div
        style={{
          height: 18,

          background: "#222",

          borderRadius: 10,

          overflow: "hidden",

          marginBottom: 8,
        }}
      >

        <div
          style={{
            width: `${compra}%`,

            height: "100%",

            background:
              "linear-gradient(90deg,#00ff99,#00ffc8)",

            transition:
              "all 0.4s ease",
          }}
        />
      </div>

      <div
        style={{
          color: "#00ffc8",
          marginBottom: 10,
        }}
      >
        COMPRA: {compra}%
      </div>

      <div
        style={{
          height: 18,

          background: "#222",

          borderRadius: 10,

          overflow: "hidden",

          marginBottom: 8,
        }}
      >

        <div
          style={{
            width: `${venda}%`,

            height: "100%",

            background:
              "linear-gradient(90deg,#ff4444,#ff0000)",

            transition:
              "all 0.4s ease",
          }}
        />
      </div>

      <div
        style={{
          color: "#ff5555",
        }}
      >
        VENDA: {venda}%
      </div>

    </div>
  );
}

function Radar({
  scoreAgressao
}) {

  let cor = "#00ffc8";

  if (scoreAgressao < -15) {
    cor = "#ff3333";
  }

  return (

    <div
      style={{
        height: 150,

        borderRadius: 12,

        marginBottom: 10,

        background: "#06101f",

        border: `1px solid ${cor}`,

        boxShadow:
          `0 0 30px ${cor}`,

        position: "relative",
      }}
    >

      <div
        style={{
          position: "absolute",

          width: 110,

          height: 110,

          borderRadius: "50%",

          border: `2px solid ${cor}`,

          left: "50%",

          top: "50%",

          marginLeft: -55,

          marginTop: -55,

          boxShadow:
            `0 0 25px ${cor}`,
        }}
      />

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