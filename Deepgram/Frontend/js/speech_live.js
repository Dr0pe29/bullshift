const liveText = document.getElementById("liveText");
const interimText = document.getElementById("interimText");
const charCounter = document.getElementById("charCounter");
const factsPanel = document.getElementById("factsPanel");
const analysisBrandName = document.querySelector(".analysis-brand-name");

let speechSocket = null;
let finalTranscript = "";
let lastProcessedText = "";

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

    if (data.type === "fact") {//REVER
      addFact(data.text, data.label);
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

    if (analysisBrandName) {
      analysisBrandName.textContent = "Stopped"; //SEE
    }
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
  updateCounter();
}

function addFinalText(text) {
  if (!liveText || !interimText) return;

  finalTranscript += text + " ";
  liveText.textContent = finalTranscript;
  interimText.textContent = "";
  updateCounter();
}

function updateCounter() {
  if (!liveText || !charCounter) return;

  const finalLength = liveText.textContent.trim().length;
  const interimLength = interimText ? interimText.textContent.trim().length : 0;

  charCounter.textContent = `${finalLength + interimLength}/1000 CHARACTERS`;
}

// AINDA EM TESTE
function addFact(text, label) {
  if (!factsPanel) return;
  const factCard = document.createElement("article");
  factCard.classList.add("fact-card");

  const normalizedLabel = label.toLowerCase();
  factCard.classList.add(normalizedLabel);
  
  factCard.innerHTML = `
    <div class="fact-label">${label}</div>
    <p>${text}</p>
  `;

  factsPanel.appendChild(factCard);
}

function clearLiveSpeech() {
  finalTranscript = "";
  lastProcessedText = "";

  if (liveText) {
    liveText.textContent = "";
  }

  if (interimText) {
    interimText.textContent = "";
  }

  if (factsPanel) {
    factsPanel.innerHTML = "";
  }

  updateCounter();
}

// Isto permite que o button_moving.js consiga chamar startLiveSpeech()
window.startLiveSpeech = startLiveSpeech;
window.stopLiveSpeech = stopLiveSpeech;
window.clearLiveSpeech = clearLiveSpeech;