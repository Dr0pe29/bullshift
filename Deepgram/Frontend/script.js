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
let lastProcessedText = "";

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

      detectSentences(finalTranscript);
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
  lastProcessedText = "";

  finalTextElement.innerText = "";
  interimTextElement.innerText = "";
  sentencesList.innerHTML = "";

  statusElement.innerText = "Status: cleared";
}

// ===============================
// SENTENCE DETECTION
// ===============================

function detectSentences(text) {
  const newText = text.slice(lastProcessedText.length);

  const sentenceRegex = /[^.!?]+[.!?]+/g;
  const sentences = newText.match(sentenceRegex);

  if (!sentences) return;

  sentences.forEach((sentence) => {
    const cleanSentence = sentence.trim();

    if (cleanSentence.length > 0) {
      addSentence(cleanSentence);
    }
  });

  lastProcessedText = text;
}

function addSentence(sentence) {
  const li = document.createElement("li");
  li.innerText = sentence;
  sentencesList.appendChild(li);

  // Next step:
  // sendToBackend(sentence);
}

// ===============================
// BACKEND COMMUNICATION FOR CLAIMS
// ===============================

async function sendToBackend(sentence) {
  try {
    const response = await fetch("http://localhost:8000/claim", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: sentence }),
    });

    const data = await response.json();
    console.log("Claim response:", data);
  } catch (error) {
    console.error("Error sending sentence to backend:", error);
  }
}