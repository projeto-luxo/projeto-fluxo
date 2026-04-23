import React from "react";

function ScorePanel({ score }) {
  return (
    <div style={container}>
      <div style={title}>SCORE</div>
      <div style={value}>{score}</div>
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

const title = {
  color: "#888",
  fontSize: "14px",
  marginBottom: "10px"
};

const value = {
  fontSize: "48px",
  color: "#00ffc3",
  fontWeight: "bold"
};

export default ScorePanel;