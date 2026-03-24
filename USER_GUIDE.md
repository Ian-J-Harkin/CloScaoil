# 🛡️ ClóScaoil Engine (v2.0) User Guide
**Manannán Digitization Lab | Phase B: Ambiguity Arbitration**

Welcome to the **ClóScaoil Engine**, the surgical OCR correction system designed specifically for the 1943 Cló Gaelach (Gaelic Type) digitization of the *Manannán* series. This engine transitions the project from simple "Search & Replace" to **Heuristic Intelligence** and **LLM Arbitration** while maintaining linguistic integrity.

---

## 🚀 Getting Started

### 🔑 API Configuration
To enable the **Ambiguity Arbitrator** (Automated Choice Resolution), you must provide a Google Gemini API Key.

1.  **Set Environment Variable:** The engine prioritizes your operating system’s environment variables.
    *   **Windows:** `setx GEMINI_API_KEY "your_key_here"`
    *   **macOS/Linux:** `export GEMINI_API_KEY="your_key_here"`
2.  **Streamlit Secrets (Optional):** If deploying to Streamlit Cloud, add `GEMINI_API_KEY` to your app's secrets dashboard.

### 🖥️ Option 1: Live Interactive UI (Streamlit)
For immediate correction and real-time linguistic validation, launch the Streamlit dashboard:

```bash
streamlit run streamlit_app.py
```

1.  **Input:** Paste your raw OCR text into the **"📥 Raw OCR Input"** field.
2.  **Configuration:** Use the sidebar to toggle "Expand Abbreviations" (`agus` vs `⁊`) or "Strict Linguistic Mode" (vowel harmony highlighting).
3.  **Review:** Examine the **"Anomaly Dashboard"** in the sidebar to review potential errors.
4.  **Export:** Copy the corrected text from the **"🚀 ClóScaoil Output"** panel.

### 📜 Option 2: Command Line (Batch Processing)
For processing entire markdown files or batch operations:

```bash
# Basic usage
python ocr_fixer.py input_chapter.md --output fixed_chapter.md

# Process with full features, LLM arbitration, and a report
python ocr_fixer.py caibidil_01.md --expand-abbreviations --strict --api-key YOUR_KEY --report anomalies.json
```

---

## 🛠️ Core Processing Pipeline (Hierarchy)

ClóScaoil uses a strict execution hierarchy to ensure words are not "over-corrected." Each word passes through these four stages:

### 1. 📖 Surgical Dictionary Lookup
The engine first checks `config/corrections_dict.json`. If a word exists in the `verified` dictionary, it is replaced and **no further heuristics are applied**. This ensures human-verified fixes always take precedence.

### 2. ✝️ Shorthand Normalization (Tironian Et)
The engine targets `7` or `>` when isolated by whitespace (common OCR misreads of the Tironian Et symbol `⁊`).
- **Standard:** Normalizes to `⁊` (Unicode `\u204a`).
- **Expanded:** Normalizes to `agus` (if "Expand Abbreviations" is enabled).

### 3. ✨ Visual Heuristics (Speck-to-Ponc)
If a word is unmapped, the engine applies visual "Speck Fixing." It identifies lenitable consonants followed by OCR noise (dots, quotes, or asterisks) and converts them to the correct lenited character.
- **Example:** `b'` or `b.` or `b*` ➔ `ḃ`
- **Supported:** Characters like `d'`, `c'`, `t'`, etc.

### 4. ⚖️ Linguistic Validation (Vowel Harmony)
The final processed word is checked against the Irish **"Caol le Caol" (Slender with Slender)** rule. 
- **The Rule:** Broad vowels (`a`, `o`, `u`) must match broad, and slender vowels (`e`, `i`) must match slender across consonant clusters.
- **Anomaly Reporting:** Words failing this check are flagged with a `⚠️` icon in the Anomaly Dashboard and highlighted with `==word==` in the output if **Strict Mode** is active.

---

## 🔍 The Anomaly Dashboard

The dashboard categories help you resolve issues the engine cannot fix automatically:

| Type | Indicator | Action Needed |
| :--- | :--- | :--- |
| **Harmony Violation** | `⚠️` | A potential spelling error or OCR misread. Manually verify spelling. |
| **Ambiguous Match** | `❓` | Multiple valid corrections. Use the dropdown to select the correct form. |
| **Gated Vision Audit** | `⚠️ Warning` | Appears when >5 violations are detected. Trigger a manual **Gemini Visual Audit**. |

---

## 📽️ Multimodal Vision Support (3.0-VISION)

ClóScaoil v3.0 introduces a **Vision Auditor** capable of cross-referencing your text with original manuscript scans using Gemini 1.5 Pro.

### 🖼️ Automated Image Sourcing
1.  **Define Workspace:** Set your **Scan Directory** in the sidebar (default: `scans/`).
2.  **Matching Logic:** The engine automatically searches for images matching the `[l.XXX]` page number (e.g., `page_045.jpg` or `45.png`).
3.  **Manual Upload:** If no local file is found, use the **"Upload Scan"** widget above the output preview.

### 🔍 Triggering a Visual Audit
If the engine detects a **High Error Density** (>5 linguistic violations), it will interrupt the output with a warning.
1.  Ensure an image is loaded (either via directory matching or upload).
2.  Click **"Trigger Gemini Visual Audit"**.
3.  Gemini 1.5 Pro will analyze the "ponc" dots and shorthands in the scan and return a corrected transcription.
4.  Review the result and choose to either **Accept** or **Reset** to heuristic output.

---

## ⚙️ Configuration & Fine-Tuning

You can improve the engine's accuracy by editing `config/corrections_dict.json` or using the `fine_tune.py` utility.

### Adding New Fixes:
1.  **Single Word:** Add entries to `dictionary.verified`.
2.  **Contextual Phrase:** Add multi-word rules to `dictionary.contextual` (e.g., fixing `go ṁ` to `go m`).
3.  **Ambiguous Sets:** Add words to `dictionary.ambiguous` to force user choice in the UI.

---

*For detailed technical implementation notes, refer to [ocr_fixer.py](file:///c:/Github/CloScaoil/ocr_fixer.py) or our [WAYPOINT.md](file:///c:/Github/CloScaoil/WAYPOINT.md) progress log.*
