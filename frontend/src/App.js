import { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState(null);
  const [erro, setErro] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8001/data")
      .then(res => {
        if (!res.ok) {
          throw new Error("Erro na resposta da API");
        }
        return res.json();
      })
      .then(res => setData(res))
      .catch(err => {
        console.error(err);
        setErro("Não conseguiu conectar com o backend");
      });
  }, []);

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
        </>
      ) : (
        !erro && <p>Carregando...</p>
      )}
    </div>
  );
}

export default App;