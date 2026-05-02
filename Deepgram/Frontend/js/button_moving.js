const startButton = document.getElementById("startButton");
const homeScreen = document.getElementById("homeScreen");
const analysisScreen = document.getElementById("analysisScreen");

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
      window.startLiveSpeech();
    }, 900);
  });
}