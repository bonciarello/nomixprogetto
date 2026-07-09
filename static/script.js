/**
 * NomixProgetto — Frontend logic
 * Handles form submission, API calls, name display with split-color effect.
 */

(function () {
  "use strict";

  /* ── DOM refs ─────────────────────────────────────────────────── */
  const form = document.getElementById("generator-form");
  const textarea = document.getElementById("descrizione");
  const charCounter = document.getElementById("char-count");
  const errorEl = document.getElementById("desc-error");
  const generateBtn = document.getElementById("generate-btn");
  const resultsSection = document.getElementById("results-section");
  const namesGrid = document.getElementById("names-grid");
  const resultsCount = document.getElementById("results-count");
  const loadingState = document.getElementById("loading-state");
  const emptyState = document.getElementById("empty-state");
  const regenerateBtn = document.getElementById("regenerate-btn");

  /* ── State ────────────────────────────────────────────────────── */
  let currentDescription = "";

  /* ── Character counter ────────────────────────────────────────── */
  textarea.addEventListener("input", function () {
    const len = textarea.value.length;
    charCounter.textContent = len + " / 500";
    if (len > 450) {
      charCounter.classList.add("over-limit");
    } else {
      charCounter.classList.remove("over-limit");
    }
    // Clear error on input
    if (errorEl.textContent) {
      errorEl.textContent = "";
      textarea.removeAttribute("aria-invalid");
    }
  });

  /* ── Validate on blur ─────────────────────────────────────────── */
  textarea.addEventListener("blur", function () {
    const val = textarea.value.trim();
    if (val && val.split(/\s+/).filter(Boolean).length < 3) {
      showFieldError(
        "Inserisci almeno 3 parole significative per ottenere buoni risultati."
      );
    }
  });

  /* ── Form submit ──────────────────────────────────────────────── */
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const descrizione = textarea.value.trim();

    // Clear previous error
    errorEl.textContent = "";
    textarea.removeAttribute("aria-invalid");

    // Validation
    if (!descrizione) {
      showFieldError("Inserisci una descrizione.");
      textarea.focus();
      return;
    }

    const parole = descrizione.split(/\s+/).filter(Boolean);
    if (parole.length < 3) {
      showFieldError(
        "Inserisci almeno 3 parole significative nella descrizione (trovate: " +
          parole.length +
          ")."
      );
      textarea.focus();
      return;
    }

    currentDescription = descrizione;
    generateNames(descrizione);
  });

  /* ── Regenerate ───────────────────────────────────────────────── */
  regenerateBtn.addEventListener("click", function () {
    if (currentDescription) {
      generateNames(currentDescription);
    }
  });

  /* ── API call ─────────────────────────────────────────────────── */
  function generateNames(descrizione) {
    // Show loading
    hideAll();
    loadingState.hidden = false;
    generateBtn.disabled = true;
    emptyState.setAttribute("aria-hidden", "true");

    fetch("api/genera", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ descrizione: descrizione }),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) {
            throw new Error(data.errore || "Errore del server");
          }
          return data;
        });
      })
      .then(function (data) {
        loadingState.hidden = true;
        generateBtn.disabled = false;

        if (data.nomi && data.nomi.length > 0) {
          renderNames(data.nomi);
          resultsSection.hidden = false;
          emptyState.setAttribute("aria-hidden", "true");
        }
      })
      .catch(function (err) {
        loadingState.hidden = true;
        generateBtn.disabled = false;
        showFieldError(err.message);
        textarea.focus();
      });
  }

  /* ── Render names ─────────────────────────────────────────────── */
  function renderNames(nomi) {
    namesGrid.innerHTML = "";
    resultsCount.textContent = nomi.length + " nomi generati";

    nomi.forEach(function (nome, index) {
      var card = createNameCard(nome, index);
      namesGrid.appendChild(card);
    });

    // Scroll results into view
    resultsSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  /* ── Create name card ─────────────────────────────────────────── */
  function createNameCard(nome, index) {
    var card = document.createElement("article");
    card.className = "name-card";
    card.setAttribute("role", "listitem");
    card.setAttribute("tabindex", "0");
    card.setAttribute("aria-label", "Nome: " + nome);

    // Split at camelCase boundaries for the signature split-color effect
    var parts = splitCamelCase(nome);

    var textEl = document.createElement("span");
    textEl.className = "name-card-text";

    if (parts.length >= 2) {
      var spanA = document.createElement("span");
      spanA.className = "name-part-a";
      spanA.textContent = parts[0];

      var spanB = document.createElement("span");
      spanB.className = "name-part-b";
      spanB.textContent = parts.slice(1).join("");

      textEl.appendChild(spanA);
      textEl.appendChild(spanB);
    } else {
      // Single part: use primary color
      var spanSingle = document.createElement("span");
      spanSingle.className = "name-part-a";
      spanSingle.textContent = nome;
      textEl.appendChild(spanSingle);
    }

    // Copy button
    var copyBtn = document.createElement("button");
    copyBtn.className = "name-card-copy";
    copyBtn.setAttribute("aria-label", "Copia " + nome);
    copyBtn.innerHTML =
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
    copyBtn.insertAdjacentText("beforeend", " Copia");

    copyBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      copyToClipboard(nome, copyBtn);
    });

    // Click on card copies too
    card.addEventListener("click", function () {
      copyToClipboard(nome, copyBtn);
    });

    // Keyboard: Enter/Space on card copies
    card.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        copyToClipboard(nome, copyBtn);
      }
    });

    var tooltip = document.createElement("span");
    tooltip.className = "copy-tooltip";
    tooltip.setAttribute("aria-hidden", "true");
    tooltip.textContent = "Copiato!";

    card.appendChild(textEl);
    card.appendChild(copyBtn);
    card.appendChild(tooltip);

    return card;
  }

  /* ── Split camelCase into parts ───────────────────────────────── */
  function splitCamelCase(str) {
    // Split at boundaries where lowercase/number is followed by uppercase
    // e.g., "SpesaConquista" → ["Spesa", "Conquista"]
    // e.g., "DividiCasa" → ["Dividi", "Casa"]
    // e.g., "SuperSpesa" → ["Super", "Spesa"]
    var parts = [];
    var current = "";
    for (var i = 0; i < str.length; i++) {
      var ch = str[i];
      if (
        i > 0 &&
        /[A-Z]/.test(ch) &&
        /[a-zàèéìòóù0-9]/.test(str[i - 1])
      ) {
        parts.push(current);
        current = ch;
      } else {
        current += ch;
      }
    }
    if (current) {
      parts.push(current);
    }
    // If only one part, try to split after a prefix
    if (parts.length === 1) {
      var prefixes = [
        "Super", "Mega", "Ultra", "Iper", "Neo", "Multi", "Eco", "Micro",
        "Fast", "Smart", "Top", "Prime", "Next", "Max", "Mini",
        "Cyber", "Tech", "Cloud", "Data", "Code", "Web",
      ];
      for (var j = 0; j < prefixes.length; j++) {
        var p = prefixes[j];
        if (str.startsWith(p) && str.length > p.length) {
          return [p, str.slice(p.length)];
        }
      }
      // Try to split at common compound boundary (halfway-ish for longer names)
      if (str.length >= 8 && parts.length === 1) {
        var mid = Math.floor(str.length / 2);
        // Find an uppercase letter near the middle
        for (var k = mid; k < str.length; k++) {
          if (/[A-Z]/.test(str[k]) && k > 1) {
            return [str.slice(0, k), str.slice(k)];
          }
        }
        // Just split at middle as fallback for all-lowercase compounds
        if (!/[A-Z]/.test(str) && str.length >= 6) {
          return [str.slice(0, mid), str.slice(mid)];
        }
      }
    }
    return parts.length > 0 ? parts : [str];
  }

  /* ── Copy to clipboard ────────────────────────────────────────── */
  function copyToClipboard(text, btn) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard
        .writeText(text)
        .then(function () {
          showCopiedFeedback(btn);
        })
        .catch(function () {
          fallbackCopy(text, btn);
        });
    } else {
      fallbackCopy(text, btn);
    }
  }

  function fallbackCopy(text, btn) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    ta.style.top = "-9999px";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try {
      document.execCommand("copy");
      showCopiedFeedback(btn);
    } catch (e) {
      // silent fail
    }
    document.body.removeChild(ta);
  }

  function showCopiedFeedback(btn) {
    var card = btn.closest(".name-card");
    var tooltip = card ? card.querySelector(".copy-tooltip") : null;

    btn.classList.add("copied");
    btn.innerHTML =
      '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>';
    btn.insertAdjacentText("beforeend", " Copiato!");

    if (tooltip) {
      tooltip.classList.add("visible");
    }

    setTimeout(function () {
      btn.classList.remove("copied");
      btn.innerHTML =
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
      btn.insertAdjacentText("beforeend", " Copia");
      if (tooltip) {
        tooltip.classList.remove("visible");
      }
    }, 1800);
  }

  /* ── Field error ──────────────────────────────────────────────── */
  function showFieldError(msg) {
    errorEl.textContent = msg;
    textarea.setAttribute("aria-invalid", "true");
  }

  /* ── Hide all states ──────────────────────────────────────────── */
  function hideAll() {
    resultsSection.hidden = true;
    loadingState.hidden = true;
    namesGrid.innerHTML = "";
    errorEl.textContent = "";
    textarea.removeAttribute("aria-invalid");
  }
})();
