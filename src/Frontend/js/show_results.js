(() => {
  const showResultsButton = document.getElementById("showResultsButton");

  if (!showResultsButton) {
    return;
  }

  showResultsButton.addEventListener("click", () => {
    if (window.stopLiveSpeech) {
      window.stopLiveSpeech();
    }

    const speechData = window.getLiveSpeechData
      ? window.getLiveSpeechData()
      : { transcript: "" };

    const transcript = speechData.transcript;

    if (!transcript) {
      alert("No transcript available yet.");
      return;
    }

    sessionStorage.setItem(
      "bullshiftTranscript",
      JSON.stringify({
        transcript: transcript
      })
    );

    window.location.href = "result.html";
  });
})();