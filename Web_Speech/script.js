// ===============================
// WEB SPEECH API SETUP
// ===============================

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

// ===============================
// DOM ELEMENTS
// ===============================

const languageSelect = document.getElementById("languageSelect");

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const clearBtn = document.getElementById("clearBtn");

const statusElement = document.getElementById("status");
const finalTextElement = document.getElementById("finalText");
const interimTextElement = document.getElementById("interimText");
const sentencesList = document.getElementById("sentences");

// ===============================
// APP STATE
// ===============================

let recognition;
let finalTranscript = "";
let lastProcessedText = "";

let shouldKeepListening = false;

// ===============================
// SPEECH RECOGNITION INITIALIZATION
// ===============================

if (!SpeechRecognition) {
  statusElement.innerText =
    "Your browser does not support the Web Speech API. Try Chrome.";

  startBtn.disabled = true;
  stopBtn.disabled = true;
  languageSelect.disabled = true;
} else {
  recognition = new SpeechRecognition();

  recognition.lang = languageSelect.value;
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onresult = handleSpeechResult;
  recognition.onerror = handleSpeechError;
  recognition.onend = handleSpeechEnd;
}

// ===============================
// EVENT LISTENERS
// ===============================

startBtn.addEventListener("click", startListening);
stopBtn.addEventListener("click", stopListening);
clearBtn.addEventListener("click", clearTranscript);
languageSelect.addEventListener("change", changeLanguage);

// ===============================
// LISTENING CONTROLS
// ===============================

function startListening() {
  if (!recognition) return;

  shouldKeepListening = true;

  recognition.lang = languageSelect.value;
  recognition.start();

  statusElement.innerText =
    "Status: listening in " +
    languageSelect.options[languageSelect.selectedIndex].text;
}

function stopListening() {
  if (!recognition) return;

  shouldKeepListening = false;

  recognition.stop();
  statusElement.innerText = "Status: stopped";
}

function changeLanguage() {
  if (!recognition) return;

  recognition.lang = languageSelect.value;

  clearTranscript();

  statusElement.innerText =
    "Language changed to: " +
    languageSelect.options[languageSelect.selectedIndex].text;
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
// SPEECH RECOGNITION EVENTS
// ===============================

function handleSpeechResult(event) {
  let interimTranscript = "";

  for (let i = event.resultIndex; i < event.results.length; i++) {
    const transcriptPart = event.results[i][0].transcript;

    if (event.results[i].isFinal) {
      finalTranscript += transcriptPart + " ";
    } else {
      interimTranscript += transcriptPart;
    }
  }

  finalTextElement.innerText = finalTranscript;
  interimTextElement.innerText = interimTranscript;

  detectSentences(finalTranscript);
}

function handleSpeechError(event) {
  console.error("Speech recognition error:", event.error);
  statusElement.innerText = "Error: " + event.error;
}

function handleSpeechEnd() {
  if (shouldKeepListening) {
    recognition.start();

    statusElement.innerText =
      "Status: listening in " +
      languageSelect.options[languageSelect.selectedIndex].text +
      "...";

    return;
  }

  statusElement.innerText = "Status: stopped";
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

  // Later, this is where you send the sentence to the backend:
  // sendToBackend(sentence);
}

// ===============================
// BACKEND COMMUNICATION
// ===============================

async function sendToBackend(sentence) {
  try {
    const response = await fetch("http://localhost:3000/claim", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: sentence }),
    });

    const data = await response.json();
    console.log("Backend response:", data);
  } catch (error) {
    console.error("Error sending sentence to backend:", error);
  }
}