import React from "react";

function BoxDestaque(props) {
  return <div style={{border: "1px solid #0ff", padding: "5px"}}>{props.children}</div>;
}

export default BoxDestaque;