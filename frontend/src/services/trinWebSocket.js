let socket = null;
let manualDisconnect = false;
let reconnectTimer = null;

export function connectTrinWebSocket(onMessage, onStatus) {
  if (
    socket &&
    (
      socket.readyState === WebSocket.OPEN ||
      socket.readyState === WebSocket.CONNECTING
    )
  ) {
    console.log("TRIN WS já conectado ou conectando.");

    if (onStatus && socket.readyState === WebSocket.OPEN) {
      onStatus("ONLINE");
    }

    return socket;
  }

  manualDisconnect = false;

  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }

  const WS_URL = `ws://${window.location.hostname}:8000/ws`;

  console.log("Conectando TRIN WS em:", WS_URL);

  socket = new WebSocket(WS_URL);

  socket.onopen = () => {
    console.log("TRIN WS conectado.");
    if (onStatus) onStatus("ONLINE");
  };

  socket.onmessage = (event) => {
    let data;

    try {
      data = JSON.parse(event.data);
    } catch (erro) {
      console.error("Erro ao ler JSON do TRIN:", erro);
      if (onStatus) onStatus("ERRO_JSON");
      return;
    }

    if (onStatus) onStatus("ONLINE");

    try {
      if (onMessage) {
        onMessage(data);
      }
    } catch (erro) {
      console.error("Erro no processamento do App:", erro);
      if (onStatus) onStatus("ONLINE");
    }
  };

  socket.onerror = (erro) => {
    console.error("Erro WebSocket TRIN:", erro);

    if (!manualDisconnect && onStatus) {
      onStatus("RECONECTANDO");
    }
  };

  socket.onclose = () => {
    console.log("TRIN WS desconectado.");

    socket = null;

    if (manualDisconnect) {
      if (onStatus) onStatus("DESCONECTADO");
      return;
    }

    if (onStatus) onStatus("RECONECTANDO");

    reconnectTimer = setTimeout(() => {
      connectTrinWebSocket(onMessage, onStatus);
    }, 2000);
  };

  return socket;
}

export function disconnectTrinWebSocket() {
  manualDisconnect = true;

  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }

  if (socket) {
    socket.close();
    socket = null;
  }
}

export function getTrinWebSocket() {
  return socket;
}