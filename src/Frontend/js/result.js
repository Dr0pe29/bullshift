const waitingScreen = document.getElementById("waitingScreen");
const resultsScreen = document.getElementById("resultsScreen");

const backButton = document.getElementById("backButton");

const trueCountElement = document.getElementById("trueCount");
const falseCountElement = document.getElementById("falseCount");
const inconclusiveCountElement = document.getElementById("inconclusiveCount");
const confidenceScoreElement = document.getElementById("confidenceScore");
const factsList = document.getElementById("factsList");
const keyTakeawayElement = document.getElementById("keyTakeaway");
const gaugeArc = document.getElementById("gaugeArc");

let resultsSocket = null;

// ===============================
// LOAD RESULTS FROM BACKEND
// ===============================

document.addEventListener("DOMContentLoaded", async () => {
  const storedTranscript = sessionStorage.getItem("bullshiftTranscript");

  if (!storedTranscript) {
    showResultError("No transcript found.");
    return;
  }

  const parsedData = JSON.parse(storedTranscript);
  const transcript = parsedData.transcript;

  if (!transcript) {
    showResultError("Transcript is empty.");
    return;
  }

  try {
    const response = await fetch("http://localhost:8000/transcript/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        transcript: transcript
      })
    });

    if (!response.ok) {
      throw new Error("Backend analysis failed");
    }

    const analysis = await response.json();

    sessionStorage.setItem(
      "bullshiftResults",
      JSON.stringify({
        transcript: transcript,
        analysis: analysis
      })
    );

    showResults(analysis);
  } catch (error) {
    console.error(error);
    showResultError("Could not analyze transcript.");
  }
});

/**
 setTimeout(() => {
   const mockData = [
     {
       type: "results",
        text: "Portugal won the UEFA Euro 2016 tournament.",
        confidence: 92,
        explanation:
          "Portugal won UEFA Euro 2016 after defeating France in the final.",
        sources: ["Source 1...", "Source 2..."]
      },
      {
        type: "results",
        text: "The Earth orbits around the Sun.",
        confidence: 99,
        explanation:
          "This is a well-established astronomical fact.",
          sources: ["Source 1..."]
      },
      {
        type: "results",
        text: "Portugal has more than 20 million inhabitants.",
        confidence: 18,
        explanation:
          "Portugal does not have more than 20 million inhabitants. Its population is around 10 million, so this claim is considered false. But it has a rich cultural heritage, and the people like tomatos",
        sources: ["Source 1..."]
      },
      {
        type: "results",
        text: "Cristiano Ronaldo is the Best footballer.",
        confidence: 61,
        explanation:
          "A lot of people consider Cristiano Ronaldo to be the best footballer of all time.",
          sources: ["Source 1...", "Source 2..."]
      },
      {
        type: "resume",
        text:
        "Overall, the transcript is mostly reliable, with high-confidence factual claims and some subjective statements ignored."
      }
    ];

    showResults(mockData);
  }, 2500);
}
*/
// ===============================
// NORMALIZE BACKEND DATA
// ===============================
function normalizeBackendData(data) {
  /*
    Aceita este formato:

    [
      {
        type: "results",
        text: "...",
        confidence: 92,
        explanation: "...",
        sources: [...]
      },
      {
        type: "resume",
        text: "..."
      }
    ]

    E transforma em:

    {
      facts: [...],
      resume: "..."
    }
  */

  const normalizedData = {
    facts: [],
    resume: ""
  };

  if (!Array.isArray(data)) {
    return normalizedData;
  }

  data.forEach((item) => {
    if (item.type === "results") {
      normalizedData.facts.push({
        text: item.text,
        confidence: item.confidence,
        explanation: item.explanation,
        sources: item.sources
      });
    }

    if (item.type === "resume") {
      normalizedData.resume = item.text;
    }
  });

  return normalizedData;
}

// ===============================
// PREPARE RESULT DATA
// ===============================
function prepareResultStats(facts) {
  const stats = {
    total: facts.length,
    trueCount: 0,
    falseCount: 0,
    inconclusiveCount: 0,
    confidenceScore: 0
  };

  let confidenceSum = 0;
  let confidenceCount = 0;

  facts.forEach((fact) => {
    const confidence =
      typeof fact.confidence === "number" ? Math.round(fact.confidence) : null;

    const label = getLabelFromConfidence(confidence);

    if (label === "true") {
      stats.trueCount++;
    }

    if (label === "false") {
      stats.falseCount++;
    }

    if (label === "inconclusive") {
      stats.inconclusiveCount++;
    }

    if (confidence !== null && !Number.isNaN(confidence)) {
      confidenceSum += confidence;
      confidenceCount++;
    }
  });

  if (confidenceCount > 0) {
    stats.confidenceScore = Math.round(confidenceSum / confidenceCount);
  }

  return stats;
}

// ===============================
// SHOW RESULTS PAGE
// ===============================
function showResults(rawData) {
  const data = normalizeBackendData(rawData);

  const facts = data.facts;
  const stats = prepareResultStats(facts);

  trueCountElement.textContent = stats.trueCount;
  falseCountElement.textContent = stats.falseCount;
  inconclusiveCountElement.textContent = stats.inconclusiveCount;

  confidenceScoreElement.textContent = stats.confidenceScore;

  renderFacts(facts);
  updateGauge(stats);
  updateKeyTakeaway(data.resume);

  waitingScreen.classList.add("hidden");
  resultsScreen.classList.remove("hidden");
}

// ===============================
// DYNAMIC GAUGE
// ===============================
function updateGauge(stats) {
  if (!gaugeArc) return;

  const score = Math.max(0, Math.min(100, stats.confidenceScore));
  const scoreDegrees = (score / 100) * 180;

  let activeColor = "#55d26a";

  if (score < 40) {
    activeColor = "#ff4b45";
  } else if (score < 65) {
    activeColor = "#ffd84d";
  }

  gaugeArc.style.setProperty("--score-deg", `${scoreDegrees}deg`);
  gaugeArc.style.setProperty("--score-color", activeColor);
}

// ===============================
// RENDER FACTS
// ===============================
function renderFacts(facts) {
  factsList.innerHTML = "";

  if (!facts.length) {
    factsList.innerHTML = `
      <div class="fact-row inconclusive">
        <strong>No facts detected</strong>
        <span>Bullshift did not receive any detected facts for this analysis.</span>
      </div>
    `;
    return;
  }

  facts.forEach((fact, index) => {
    const confidence =
      typeof fact.confidence === "number" ? Math.round(fact.confidence) : null;

    const normalizedLabel = getLabelFromConfidence(confidence);
    const displayLabel = getDisplayLabelFromConfidence(confidence);

    const factRow = document.createElement("div");
    factRow.classList.add("fact-row", normalizedLabel);

    factRow.innerHTML = `
      <div class="fact-row-header">
        <strong>
          ${escapeHtml(displayLabel)}
          ${confidence !== null ? `<span class="fact-confidence">${confidence}%</span>` : ""}
        </strong>

        <button class="fact-details-button" type="button" data-fact-index="${index}">
          View details
        </button>
      </div>

      <span>${escapeHtml(fact.text)}</span>
    `;

    factsList.appendChild(factRow);
  });

  document.querySelectorAll(".fact-details-button").forEach((button) => {
    button.addEventListener("click", () => {
      const factIndex = Number(button.dataset.factIndex);
      openFactModal(facts[factIndex]);
    });
  });
}

// ===============================
// KEY TAKEAWAY / RESUME FROM BACKEND
// ===============================
function updateKeyTakeaway(resumeText) {
  if (!keyTakeawayElement) return;

  if (typeof resumeText === "string" && resumeText.trim() !== "") {
    keyTakeawayElement.textContent = resumeText;
    return;
  }

  keyTakeawayElement.textContent =
    "No summary was provided by the backend for this analysis.";
}

// ===============================
// LABELS FROM CONFIDENCE
// ===============================
function getLabelFromConfidence(confidence) {
  if (confidence === null || Number.isNaN(confidence)) {
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

function getDisplayLabelFromConfidence(confidence) {
  const label = getLabelFromConfidence(confidence);

  if (label === "true") {
    return "True";
  }

  if (label === "false") {
    return "Bullshift";
  }

  return "Inconclusive";
}

// ===============================
// SECURITY
// ===============================
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

// ===============================
// BACK BUTTON
// ===============================
if (backButton) {
  backButton.addEventListener("click", () => {
    window.location.href = "home.html";
  });
}

// ===============================
// FACT DETAILS MODAL
// ===============================
function openFactModal(fact) {
  const modal = document.getElementById("factModal");
  const modalLabel = document.getElementById("modalFactLabel");
  const modalConfidence = document.getElementById("modalFactConfidence");
  const modalText = document.getElementById("modalFactText");
  const modalExplanation = document.getElementById("modalFactExplanation");
  const modalSources = document.getElementById("modalFactSources");

  if (!modal) return;

  const confidence =
    typeof fact.confidence === "number" ? Math.round(fact.confidence) : null;

  const normalizedLabel = getLabelFromConfidence(confidence);
  const displayLabel = getDisplayLabelFromConfidence(confidence);

  modalLabel.textContent = displayLabel;
  modalLabel.className = `modal-label ${normalizedLabel}`;

  modalConfidence.textContent =
    confidence !== null ? `${confidence}% confidence` : "No confidence score";

  modalText.textContent = fact.text || "No fact text available.";

  modalExplanation.textContent =
    fact.explanation || "No detailed explanation was provided for this fact.";

  modalSources.innerHTML = "";

  const sources = Array.isArray(fact.sources) ? fact.sources : [];

  if (sources.length === 0) {
    modalSources.innerHTML = `<li>No sources provided by the backend.</li>`;
  } else {
    sources.forEach((source) => {
      const li = document.createElement("li");
      li.textContent = source;
      modalSources.appendChild(li);
    });
  }

  modal.classList.remove("hidden");
}

function closeFactModal() {
  const modal = document.getElementById("factModal");

  if (modal) {
    modal.classList.add("hidden");
  }
}

document.addEventListener("click", (event) => {
  if (event.target.id === "factModal") {
    closeFactModal();
  }

  if (event.target.id === "closeFactModal") {
    closeFactModal();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeFactModal();
  }
});

