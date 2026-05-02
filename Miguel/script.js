// ===============================
// DOM ELEMENTS
// ===============================

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const clearBtn = document.getElementById("clearBtn");

const statusElement = document.getElementById("status");
const finalTextElement = document.getElementById("finalText");
const interimTextElement = document.getElementById("interimText");
const sentencesList = document.getElementById("sentences");

// Optional: your HTML still has this dropdown
const languageSelect = document.getElementById("languageSelect");

// ===============================
// APP STATE
// ===============================

let socket = null;
let finalTranscript = "";

// ===============================
// EVENT LISTENERS
// ===============================

startBtn.addEventListener("click", startListening);
stopBtn.addEventListener("click", stopListening);
clearBtn.addEventListener("click", clearTranscript);

// ===============================
// WEBSOCKET CONTROLS
// ===============================

function startListening() {
  if (socket && socket.readyState === WebSocket.OPEN) {
    return;
  }

  socket = new WebSocket("ws://localhost:8000/ws/transcript");

  socket.onopen = () => {
    statusElement.innerText = "Status: connected to Deepgram backend";
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "interim") {
      interimTextElement.innerText = data.text;
    }

    if (data.type === "final") {
      finalTranscript += data.text + " ";

      finalTextElement.innerText = finalTranscript;
      interimTextElement.innerText = "";
    }

    if (data.type === "fact_check") {
      handleFactCheck(data);
    }

    if (data.type === "error") {
      statusElement.innerText = "Error: " + data.text;
    }
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
    statusElement.innerText = "WebSocket error";
  };

  socket.onclose = () => {
    statusElement.innerText = "Status: disconnected";
  };
}

function stopListening() {
  if (socket) {
    socket.close();
    socket = null;
  }

  statusElement.innerText = "Status: stopped";
}

function clearTranscript() {
  finalTranscript = "";

  finalTextElement.innerText = "";
  interimTextElement.innerText = "";
  sentencesList.innerHTML = "";

  statusElement.innerText = "Status: cleared";
}

// ===============================
// FACT CHECK RESULTS
// ===============================

function handleFactCheck(data) {
  if (data.status === "claim_detected") {
    addFactCheckResult(data.text, data.verdict);
  }

  if (data.status === "no_context") {
    console.log("No context:", data.text);
  }

  if (data.status === "ignored") {
    console.log("Ignored:", data.text);
  }
}

function addFactCheckResult(sentence, verdict) {
  const li = document.createElement("li");

  li.innerHTML = `
    <strong>${sentence}</strong>
    <br>
    <span>${verdict}</span>
  `;

  sentencesList.appendChild(li);
}