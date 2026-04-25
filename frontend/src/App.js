import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";
import { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState(null);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    const buscarDados = () => {
      fetch("http://127.0.0.1:8000/data")
        .then(res => {
          if (!res.ok) {
            throw new Error("Erro na resposta da API");
          }
          return res.json();
        })
        .then(res => {
          setData(res);
          setErro(null);
        })
        .catch(err => {
          console.error(err);
          setErro("Não conseguiu conectar com o backend");
        });
    };

    buscarDados();
    const interval = setInterval(buscarDados, 2000);

    return () => clearInterval(interval);
  }, []);

const dadosGrafico = Array.isArray(data?.historico)
  ? data.historico.map((valor, index) => ({
      index,
      valor
    }))
  : [];
  return (
    <div>
      <h1>Resultado</h1>

      {erro && <p style={{ color: "red" }}>{erro}</p>}

      {data ? (
        <>
          <p>Score: {data.score}</p>
          <p>Direção: {data.direcao}</p>
          <p>Fase: {data.fase}</p>

          <p>Histórico: {data.historico.join(", ")}</p>

         <div style={{ display: "flex", justifyContent: "center" }}>
  {dadosGrafico.length > 0 && (
    <LineChart width={800} height={400} data={dadosGrafico}>
      <CartesianGrid strokeDasharray="3 3" stroke="#ccc" />
      <XAxis dataKey="index" />
      <YAxis />
      <Tooltip />
      <Line 
        type="monotone" 
        dataKey="valor" 
        stroke="#00bcd4" 
        strokeWidth={3} 
        dot={false} 
      />
    </LineChart>
  )}
</div>
        </>
      ) : (
        !erro && <p>Carregando...</p>
      )}
    </div>
  );
}

export default App;