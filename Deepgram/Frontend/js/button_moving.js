const startButton = document.getElementById("startButton");
const homeScreen = document.getElementById("homeScreen");
const analysisScreen = document.getElementById("analysisScreen");

const liveText = document.getElementById("liveText");
const charCounter = document.getElementById("charCounter");

function updateCounter() {
  if (!liveText || !charCounter) return;

  charCounter.textContent = `${liveText.textContent.trim().length}/1000 CHARACTERS`;
}

updateCounter();

if (startButton && homeScreen && analysisScreen) {
  startButton.addEventListener("click", () => {
    const rect = startButton.getBoundingClientRect();

    startButton.classList.add("is-moving");

    startButton.style.left = rect.left + "px";
    startButton.style.top = rect.top + "px";
    startButton.style.width = rect.width + "px";
    startButton.style.height = rect.height + "px";

    document.body.appendChild(startButton);

    homeScreen.classList.add("hide-home");

    requestAnimationFrame(() => {
      startButton.classList.add("move-to-corner");
    });

    setTimeout(() => {
      analysisScreen.classList.add("show-analysis");
      startButton.classList.add("final-logo");
    }, 900);
  });
}

function addFact(text, percentage) {
  const factsPanel = document.getElementById("factsPanel");

  if (!factsPanel) return;

  const factCard = document.createElement("article");
  factCard.classList.add("fact-card");

  if (percentage >= 70) {
    factCard.classList.add("true");
  } else if (percentage >= 40) {
    factCard.classList.add("warning");
  } else {
    factCard.classList.add("false");
  }

  factCard.innerHTML = `
    <div class="percentage">${percentage}%</div>
    <p>${text}</p>
  `;

  factsPanel.appendChild(factCard);
}