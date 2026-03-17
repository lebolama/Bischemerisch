const inputText = document.getElementById("inputText");
const outputText = document.getElementById("outputText");
const modeSelect = document.getElementById("mode");
const modeUsed = document.getElementById("modeUsed");
const translateBtn = document.getElementById("translateBtn");
const clearBtn = document.getElementById("clearBtn");

async function translate() {
  const text = inputText.value.trim();
  if (!text) {
    outputText.value = "";
    modeUsed.textContent = "-";
    return;
  }

  translateBtn.disabled = true;
  translateBtn.textContent = "Übersetze...";

  try {
    const response = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        mode: modeSelect.value,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    outputText.value = data.translated_text || "";
    modeUsed.textContent = data.mode_used || "-";
  } catch (error) {
    outputText.value = "Fehler bei der Übersetzung. Bitte später erneut versuchen.";
    modeUsed.textContent = "Fehler";
    console.error(error);
  } finally {
    translateBtn.disabled = false;
    translateBtn.textContent = "Übersetzen";
  }
}

translateBtn.addEventListener("click", translate);
clearBtn.addEventListener("click", () => {
  inputText.value = "";
  outputText.value = "";
  modeUsed.textContent = "-";
});
