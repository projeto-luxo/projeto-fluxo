import React from "react";

function SignalCard({ direcao, fase }) {
  const cor =
    direcao === "COMPRA"
      ? "#00ff99"
      : direcao === "VENDA"
      ? "#ff4444"
      : "#aaaaaa";

  return (
    <div style={container}>
      <div style={label}>DIREÇÃO</div>
      <div style={{ ...value, color: cor }}>{direcao}</div>

      <div style={label}>FASE</div>
      <div style={faseStyle}>{fase}</div>
    </div>
  );
}

const container = {
  background: "#111",
  borderRadius: "12px",
  padding: "20px",
  textAlign: "center",
  boxShadow: "0 0 20px rgba(0,255,200,0.2)"
};

const label = {
  color: "#888",
  fontSize: "12px",
  marginTop: "10px"
};

const value = {
  fontSize: "24px",
  fontWeight: "bold"
};

const faseStyle = {
  fontSize: "18px",
  color: "#ffaa00"
};

export default SignalCard;