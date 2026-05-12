const form = document.querySelector("#campaignForm");
const statusPill = document.querySelector("#statusPill");
const messageLine = document.querySelector("#messageLine");
const generateContentButton = document.querySelector("#generateContentButton");
const generateImageButton = document.querySelector("#generateImageButton");
const copyButton = document.querySelector("#copyButton");
const saveDraftButton = document.querySelector("#saveDraftButton");
const imagePreview = document.querySelector("#imagePreview");
const imagePlaceholder = document.querySelector("#imagePlaceholder");

const fields = {
  caption: document.querySelector("#captionField"),
  hashtags: document.querySelector("#hashtagsField"),
  callToAction: document.querySelector("#ctaField"),
  toneUsed: document.querySelector("#toneField"),
  imageAltText: document.querySelector("#altTextField"),
  imagePrompt: document.querySelector("#imagePromptField"),
};

const state = {
  form: null,
  imagePath: null,
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = readForm();

  setBusy("A gerar texto...");
  generateContentButton.classList.add("is-loading");
  disableResultActions(true);

  try {
    const data = await postJson("/api/generate-content", payload);
    state.form = payload;
    state.imagePath = null;
    writeContent(data.content);
    resetImage();
    disableResultActions(false);
    setReady("Texto gerado.");
  } catch (error) {
    setError(error.message);
  } finally {
    generateContentButton.classList.remove("is-loading");
  }
});

generateImageButton.addEventListener("click", async () => {
  const imagePrompt = fields.imagePrompt.value.trim();
  if (!imagePrompt) {
    setError("O prompt visual está vazio.");
    return;
  }

  setBusy("A gerar imagem...");
  generateImageButton.classList.add("is-loading");
  generateImageButton.disabled = true;

  try {
    const data = await postJson("/api/generate-image", { image_prompt: imagePrompt });
    state.imagePath = data.image_path;
    imagePreview.src = data.image_url;
    imagePreview.alt = fields.imageAltText.value.trim();
    imagePreview.hidden = false;
    imagePlaceholder.hidden = true;
    saveDraftButton.disabled = false;
    setReady("Imagem gerada.");
  } catch (error) {
    setError(error.message);
  } finally {
    generateImageButton.classList.remove("is-loading");
    generateImageButton.disabled = false;
  }
});

copyButton.addEventListener("click", async () => {
  const content = readContent();
  const text = [
    content.caption,
    content.call_to_action,
    content.hashtags.join(" "),
  ].filter(Boolean).join("\n\n");

  try {
    await navigator.clipboard.writeText(text);
    setReady("Texto copiado.");
  } catch {
    setError("Não foi possível copiar o texto.");
  }
});

saveDraftButton.addEventListener("click", async () => {
  if (!state.form) {
    setError("Gera primeiro o texto da publicação.");
    return;
  }

  setBusy("A guardar rascunho...");
  saveDraftButton.classList.add("is-loading");
  saveDraftButton.disabled = true;

  try {
    const data = await postJson("/api/save-draft", {
      form: state.form,
      content: readContent(),
      image_path: state.imagePath,
    });
    setReady(`Rascunho guardado: ${data.draft_path}`);
  } catch (error) {
    setError(error.message);
  } finally {
    saveDraftButton.classList.remove("is-loading");
    saveDraftButton.disabled = false;
  }
});

function readForm() {
  const data = new FormData(form);
  return {
    brand_name: requiredValue(data, "brand_name"),
    topic: requiredValue(data, "topic"),
    brand_voice: requiredValue(data, "brand_voice"),
    target_audience: requiredValue(data, "target_audience"),
    objective: requiredValue(data, "objective"),
    extra_notes: String(data.get("extra_notes") || "").trim(),
  };
}

function requiredValue(data, name) {
  return String(data.get(name) || "").trim();
}

function writeContent(content) {
  fields.caption.value = content.caption || "";
  fields.hashtags.value = Array.isArray(content.hashtags) ? content.hashtags.join(" ") : "";
  fields.callToAction.value = content.call_to_action || "";
  fields.toneUsed.value = content.tone_used || "";
  fields.imagePrompt.value = content.image_prompt || "";
  fields.imageAltText.value = content.image_alt_text || "";
}

function readContent() {
  return {
    caption: fields.caption.value.trim(),
    hashtags: fields.hashtags.value.split(/\s+/).filter(Boolean),
    call_to_action: fields.callToAction.value.trim(),
    tone_used: fields.toneUsed.value.trim(),
    image_prompt: fields.imagePrompt.value.trim(),
    image_alt_text: fields.imageAltText.value.trim(),
  };
}

function resetImage() {
  imagePreview.removeAttribute("src");
  imagePreview.hidden = true;
  imagePlaceholder.hidden = false;
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "O pedido falhou.");
  }

  return data;
}

function disableResultActions(disabled) {
  generateImageButton.disabled = disabled;
  copyButton.disabled = disabled;
  saveDraftButton.disabled = disabled;
}

function setBusy(message) {
  statusPill.textContent = "A processar";
  statusPill.className = "status-pill busy";
  messageLine.textContent = message;
}

function setReady(message) {
  statusPill.textContent = "Pronto";
  statusPill.className = "status-pill";
  messageLine.textContent = message;
}

function setError(message) {
  statusPill.textContent = "Erro";
  statusPill.className = "status-pill error";
  messageLine.textContent = message;
}
