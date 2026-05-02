(() => {
  const cancelRecordingButton = document.getElementById("cancelRecordingButton");

  const startButton = document.getElementById("startButton");
  const homeScreen = document.getElementById("homeScreen");
  const analysisScreen = document.getElementById("analysisScreen");

  const originalButtonContainer = document.querySelector(".hero-right");
  const recordText = document.querySelector(".record-text");
  const analysisBrandName = document.querySelector(".analysis-brand-name");

  if (!cancelRecordingButton || !startButton || !homeScreen || !analysisScreen) {
    return;
  }

  cancelRecordingButton.addEventListener("click", () => {
    // Stop recording / websocket
    if (window.stopLiveSpeech) {
      window.stopLiveSpeech();
    }

    // Clear transcript and fact cards
    if (window.clearLiveSpeech) {
      window.clearLiveSpeech();
    }

    // Reset truthmeter
    const meter = document.getElementById("analysisTruthMeter");

    if (meter && window.updateTruthMeter) {
      window.updateTruthMeter(meter, 0);
    }

    // Reset analysis title
    if (analysisBrandName) {
      analysisBrandName.textContent = "Recording...";
    }

    // Hide analysis and show home
    analysisScreen.classList.remove("show-analysis");
    homeScreen.classList.remove("hide-home");

    // Reset the animated start button
    startButton.classList.remove("is-moving", "move-to-corner", "final-logo");

    startButton.style.left = "";
    startButton.style.top = "";
    startButton.style.width = "";
    startButton.style.height = "";

    // Put the start button back in its original place
    if (originalButtonContainer && recordText) {
      originalButtonContainer.insertBefore(startButton, recordText);
    }
  });
})();