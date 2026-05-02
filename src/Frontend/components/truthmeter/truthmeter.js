function getTruthMeterLabel(value) {
  if (value < 20) return "Not Trusted";
  if (value < 40) return "Low Trust";
  if (value < 60) return "Questionable";
  if (value < 80) return "Almost Trusted";
  return "Trusted";
}

function getTruthMeterColor(value) {
  if (value < 20) return "#c51d1d";
  if (value < 40) return "#e75b20";
  if (value < 60) return "#e8b835";
  if (value < 80) return "#78b948";
  return "#27a74b";
}

function updateTruthMeter(meter, value) {
  const safeValue = Math.max(0, Math.min(100, Number(value)));

  const needle = meter.querySelector(".truthmeter-needle");
  const label = meter.querySelector(".truthmeter-label");
  const percentageText = meter.querySelector(".truthmeter-percentage-value");
  const range = meter.querySelector(".truthmeter-range");

  const minAngle = 172;
  const maxAngle = 368;

  const angle = minAngle + (safeValue / 100) * (maxAngle - minAngle);

  needle.style.transform = `rotate(${angle}deg)`;

  label.textContent = getTruthMeterLabel(safeValue);
  label.style.color = getTruthMeterColor(safeValue);

  percentageText.textContent = safeValue;

  if (range) {
    range.value = safeValue;
  }

  meter.dataset.value = safeValue;
}

function initTruthMeter(meter) {
  const initialValue = Number(meter.dataset.value || 0);
  const range = meter.querySelector(".truthmeter-range");

  updateTruthMeter(meter, initialValue);

  if (range) {
    range.addEventListener("input", function () {
      updateTruthMeter(meter, Number(range.value));
    });
  }
}

function initTruthMeters() {
  const meters = document.querySelectorAll(".truthmeter");

  meters.forEach((meter) => {
    initTruthMeter(meter);
  });
}

document.addEventListener("DOMContentLoaded", initTruthMeters);