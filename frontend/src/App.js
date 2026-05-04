import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const buscar = () => {
      fetch("http://127.0.0.1:8000/data")
        .then((r) => r.json())
        .then(setData);
    };

    buscar();
    const i = setInterval(buscar, 600);
    return () => clearInterval(i);
  }, []);

  const dadosGrafico =
    data?.historico?.slice(-30).map((v, i) => ({
      index: i,
      valor: v,
    })) || [];

  const cor =
    data?.sinal === "COMPRA FORTE"
      ? "#00ff88"
      : data?.sinal === "VENDA FORTE"
      ? "#ff3b3b"
      : data?.sinal === "ATENCAO"
      ? "#ffd84d"
      : "#8a8f98";

  return (
    <div
      style={{
        background: "radial-gradient(circle at center, #010203, #000)",
        color: "#fff",
        minHeight: "100vh",
        padding: "20px",
        fontFamily: "Arial",
      }}
    >
      <h1 style={{ letterSpacing: "2px" }}>TRIN FLOW PRO</h1>

      {data && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 2fr 1fr",
            gap: "15px",
          }}
        >
          {/* BOOK */}
          <div style={{ background: "#05090f", padding: "10px", borderRadius: "10px" }}>
            <p>Book</p>

            {[...Array(20)].map((_, i) => (
              <div
                key={i}
                style={{
                  height: "8px",
                  marginBottom: "4px",
                  background:
                    i % 2 === 0
                      ? "rgba(0,255,136,0.5)"
                      : "rgba(255,59,59,0.5)",
                  width: `${Math.random() * 100}%`,
                }}
              />
            ))}
          </div>

          {/* CENTRO */}
          <div style={{ position: "relative", background: "#05090f", borderRadius: "10px", padding: "15px" }}>
            <p>Fluxo</p>

            <div style={{ height: "350px" }}>
              <ResponsiveContainer>
                <LineChart data={dadosGrafico}>
                  <CartesianGrid stroke="#111" />
                  <XAxis dataKey="index" />
                  <YAxis />
                  <Tooltip />
                  <Line
                    dataKey="valor"
                    stroke={cor}
                    strokeWidth={4}
                    dot={false}
                    style={{
                      filter: `drop-shadow(0 0 12px ${cor})`,
                    }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* RADAR PULSANTE */}
            <div
              style={{
                position: "absolute",
                bottom: "30px",
                left: "50%",
                transform: "translateX(-50%)",
                width: "140px",
                height: "140px",
                borderRadius: "50%",
                border: `2px solid ${cor}`,
                boxShadow: `0 0 40px ${cor}`,
                animation: "pulse 2s infinite",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              TRIN CORE
            </div>

            {/* BARRA */}
            <div style={{ marginTop: "15px" }}>
              <p>Força do Fluxo</p>

              <div style={{ background: "#111", height: "10px", borderRadius: "5px" }}>
                <div
                  style={{
                    width: `${data.score * 10}%`,
                    background: cor,
                    height: "100%",
                    boxShadow: `0 0 15px ${cor}`,
                    transition: "0.3s",
                  }}
                />
              </div>
            </div>
          </div>

          {/* LATERAL */}
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <Card titulo="SINAL" valor={data.sinal} cor={cor} forte />
            <Card titulo="SCORE" valor={`${data.score}/10`} cor="#00d4ff" />
            <Card titulo="DIREÇÃO" valor={data.direcao} cor={cor} />
            <Card titulo="FASE" valor={data.fase} cor="#fff" />
            <Card titulo="PREÇO" valor={data.preco_atual} cor="#fff" />

            <div style={{ background: "#05090f", padding: "10px", borderRadius: "10px" }}>
              <p>Pressão</p>

              <div style={{ display: "flex", height: "12px", borderRadius: "5px", overflow: "hidden" }}>
                <div style={{ width: `${data.pressao_compra}%`, background: "#00ff88" }} />
                <div style={{ width: `${data.pressao_venda}%`, background: "#ff3b3b" }} />
              </div>

              <p style={{ fontSize: "12px" }}>
                Compra {data.pressao_compra}% | Venda {data.pressao_venda}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ANIMAÇÃO */}
      <style>
        {`
        @keyframes pulse {
          0% { box-shadow: 0 0 10px ${cor}; }
          50% { box-shadow: 0 0 40px ${cor}; }
          100% { box-shadow: 0 0 10px ${cor}; }
        }
        `}
      </style>
    </div>
  );
}

function Card({ titulo, valor, cor, forte }) {
  return (
    <div
      style={{
        border: `1px solid ${cor}`,
        padding: "10px",
        borderRadius: "10px",
        boxShadow: forte ? `0 0 25px ${cor}` : "none",
      }}
    >
      <p>{titulo}</p>

      <h2
        style={{
          color: cor,
          textShadow: `0 0 15px ${cor}`,
        }}
      >
        {valor}
      </h2>
    </div>
  );
}

export default App;