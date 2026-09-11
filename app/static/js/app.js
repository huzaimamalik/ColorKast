"use strict";

document.querySelectorAll("form[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!window.confirm(form.dataset.confirm)) event.preventDefault();
  });
});

const picker = document.getElementById("color-picker");
if (picker) {
  const fields = ["red", "green", "blue"].map((id) => document.getElementById(id));
  const preview = document.getElementById("color-preview");
  const readout = document.getElementById("color-readout");
  const feedback = document.getElementById("color-feedback");

  function updatePreview() {
    const valid = fields.every((field) => /^\d+$/.test(field.value) && Number(field.value) >= 0 && Number(field.value) <= 255);
    if (!valid) {
      feedback.textContent = "Invalid RGB: enter whole numbers from 0 through 255. Preview shows the last valid color.";
      return;
    }
    const rgb = fields.map((field) => Number(field.value));
    const hex = "#" + rgb.map((value) => value.toString(16).padStart(2, "0")).join("").toUpperCase();
    picker.value = hex;
    preview.style.backgroundColor = hex;
    readout.textContent = `RGB ${rgb.join(", ")} · ${hex}`;
    feedback.textContent = "Valid color. Ready to add to your palette.";
  }

  picker.addEventListener("input", () => {
    fields.forEach((field, index) => { field.value = parseInt(picker.value.slice(1 + index * 2, 3 + index * 2), 16); });
    updatePreview();
  });
  fields.forEach((field) => field.addEventListener("input", updatePreview));
  updatePreview();
}
