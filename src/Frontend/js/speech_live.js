const liveText = document.getElementById("liveText");
const interimText = document.getElementById("interimText");
const factsPanel = document.getElementById("factsPanel");
const analysisBrandName = document.querySelector(".analysis-brand-name");
const analysisTruthMeter = document.getElementById("analysisTruthMeter");

let speechSocket = null;
let finalTranscript = "";
let lastProcessedText = "";
let factConfidences = [];

// ===============================
// WEBSOCKET CONTROLS
// ===============================
function startLiveSpeech() {
  if (speechSocket && speechSocket.readyState === WebSocket.OPEN) {
    return;
  }

  speechSocket = new WebSocket("ws://localhost:8000/ws/transcript");

  speechSocket.onopen = () => {
    console.log("Connected to speech backend");

    if (analysisBrandName) {
      analysisBrandName.textContent = "Recording...";
    }
  };

  // Quando chega uma mensagem do backend
  speechSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "interim") {
      showInterimText(data.text);
    }

    if (data.type === "final") {
      addFinalText(data.text);
    }

    if (data.type === "fact" || data.type === "fact_check") {
      addFact(data);

      if (typeof data.confidence === "number") {
        factConfidences.push(data.confidence);

        const averageConfidence =
          factConfidences.reduce((sum, value) => sum + value, 0) / factConfidences.length;

        if (window.updateTruthMeter && analysisTruthMeter) {
          window.updateTruthMeter(analysisTruthMeter, Math.round(averageConfidence));
        }
      }
    }

    if (data.type === "error") {
      console.error("Speech backend error:", data.text);

      if (analysisBrandName) {
        analysisBrandName.textContent = "Error";
      }
    }
  };

  // Erro na ligação WebSocket
  speechSocket.onerror = (error) => {
    console.error("WebSocket error:", error);

    if (analysisBrandName) {
      analysisBrandName.textContent = "Connection error";
    }
  };

  speechSocket.onclose = () => {
    console.log("Speech socket closed");
  };
}

function stopLiveSpeech() {
  if (speechSocket) {
    speechSocket.close();
    speechSocket = null;
  }
}

function showInterimText(text) {
  if (!interimText) return;
  interimText.textContent = text;
}

function addFinalText(text) {
  if (!liveText || !interimText) return;

  finalTranscript += text + " ";
  liveText.textContent = finalTranscript;
  interimText.textContent = "";

  localStorage.setItem("bullshiftFinalTranscript", finalTranscript.trim());
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function getFactCardClass(data, confidence) {
  if (data.status === "no_context" || data.status === "ignored" || confidence === null) {
    return "inconclusive";
  }

  if (confidence < 40) {
    return "false";
  }

  if (confidence < 65) {
    return "inconclusive";
  }

  return "true";
}

function getFactLabel(data, confidence) {
  if (data.status === "no_context") return "Needs Context";
  if (data.status === "ignored") return "Non-Claim";
  if (confidence === null) return "Unscored Claim";
  if (confidence < 40) return "Low Confidence";
  if (confidence < 65) return "Mixed Evidence";
  return "Verifiable Claim";
}

function addFact(data) {
  if (!factsPanel) return;

  const confidence = typeof data.confidence === "number" ? Math.round(data.confidence) : null;
  const factClass = getFactCardClass(data, confidence);
  const statusLabel = getFactLabel(data, confidence);

  const factCard = document.createElement("article");
  factCard.classList.add("fact-card");

  factCard.classList.add(factClass);

  factCard.innerHTML = `
    <div class="percentage">${confidence === null ? "—" : `${confidence}%`}</div>
    <div class="fact-label">${escapeHtml(statusLabel)}</div>
    <p class="fact-text">${escapeHtml(data.text)}</p>
  `;

  factsPanel.prepend(factCard);
}

function clearLiveSpeech() {
  finalTranscript = "";
  lastProcessedText = "";
  factConfidences = [];

  if (liveText) {
    liveText.textContent = "";
  }

  if (interimText) {
    interimText.textContent = "";
  }

  if (factsPanel) {
    factsPanel.innerHTML = "";
  }

  if (window.updateTruthMeter && analysisTruthMeter) {
    window.updateTruthMeter(analysisTruthMeter, 0);
  }
  localStorage.removeItem("bullshiftFinalTranscript");
}

// ===============================
// PUBLIC API
// ===============================
// These functions are exposed globally so other scripts can
// start/stop recording, clear the UI, or get the final transcript.
window.startLiveSpeech = startLiveSpeech;
window.stopLiveSpeech = stopLiveSpeech;
window.clearLiveSpeech = clearLiveSpeech;

window.getLiveSpeechData = function () {
  return {
    transcript: finalTranscript.trim(),
  };
};