# 🛡️ ClóScaoil Engine (v3.3-STABLE) User Guide
**Manannán Digitization Lab | Phase D: Production Hardening**

Welcome to the **ClóScaoil Engine**, the surgical OCR correction system designed specifically for the 1943 Cló Gaelach (Gaelic Type) digitization of the *Manannán* series. This engine transitions from a single-page "Laboratory" to a full-book **Production Pipeline** with **LLM Vision** and **Batch Automation**.

---

## 🚀 Getting Started

### 🔑 Setting up API Keys
To enable the **LLM Providers** (Automated Choice Resolution, Vision, Modernization), you must provide the respective API Keys (e.g. `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`). The engine looks directly at your Operating System's environment variables.

1. **Windows:**
   - Open Start Menu and search for "Environment Variables".
   - Click "Edit the system environment variables".
   - Click the "Environment Variables..." button.
   - Under "User variables", click "New...".
   - Variable name: `ANTHROPIC_API_KEY` (or whichever provider you are using).
   - Variable value: `your_key_here`. 
   - Click OK and **restart your terminal/IDE**.
2. **macOS / Linux:**
   - Open your terminal.
   - Edit your shell profile (e.g., `nano ~/.bashrc` or `nano ~/.zshrc`).
   - Add the line: `export ANTHROPIC_API_KEY="your_key_here"`
   - Save and reload your profile (`source ~/.zshrc`).
3. **Streamlit Cloud (Optional):**  
   If deploying to Streamlit Cloud, add the keys directly to your app's "Secrets" dashboard.

### 📦 Option 2: Full-Book Batch Production
For high-scale processing of the entire manuscript:
1.  **Tab:** Select the **"🚀 Batch Production"** tab in the UI.
2.  **Directories:** Define your **Input Directory** (folder of `.md` chapters) and **Output Directory**.
3.  **Policy:** Choose a **Vision Audit Policy**:
    *   `manual`: The engine stops if noise is detected.
    *   `always`: Automated **Silent Mode** triggers Gemini Vision for any high-noise page.
4.  **Run:** Click **"Start Batch Run"** to process all files sequentially.
5.  **Finalize:** Once the batch completes, use the **"✨ Generate Golden Copy"** button to consolidate the full manuscript into a single edition.

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
2.  **Supported Formats:** The engine automatically searches for several naming conventions:
    *   `page_045.jpg / .png`
    *   `045.jpg / .png`
    *   `p45.jpg / .png` (Expanded in v3.2)
3.  **Manual Upload:** If no local file is found in the **Lab**, use the **"Upload Scan"** widget above the output preview.

### 🔍 Triggering a Visual Audit
If the engine detects a **High Error Density** (>5 linguistic violations), it will flag the page.
1.  **Lab Mode:** Click **"Trigger Gemini Visual Audit"** in the UI.
2.  **Production Mode:** If **"Vision Audit Policy: Always"** is selected, the audit triggers automatically in the background.
3.  **API Throttling:** The engine includes a `time.sleep(1)` delay during batch vision audits to ensure API stability and avoid rate limits.

---

## 🌍 Cross-Platform Compatibility

The ClóScaoil Engine is fully compatible with **Windows, macOS, and Linux**.

- **Dynamic Path Construction:** Hardcoded OS-specific paths have been eliminated. The engine uses dynamic path joining (e.g., `os.path.join(os.getcwd(), ...)`) to automatically conform to the host operating system (`/` vs `\`).
- **Universal Line Endings:** Text inputted from Windows (`\r\n`) is automatically sanitized to Unix-standard (`\n`) before any regex algorithms process it, eliminating brittle logic bugs.
- **Strict Encoding:** All file operations explicitly enforce `UTF-8` to prevent platform-specific defaults (like Windows CP-1252) from corrupting the Gaelic characters.

---

## ⚙️ Configuration & Fine-Tuning

You can improve the engine's accuracy by editing `config/corrections_dict.json` or using the `fine_tune.py` utility.

### Adding New Fixes:
1.  **Single Word:** Add entries to `dictionary.verified`.
2.  **Contextual Phrase:** Add multi-word rules to `dictionary.contextual` (e.g., fixing `go ṁ` to `go m`).
3.  **Ambiguous Sets:** Add words to `dictionary.ambiguous` to force user choice in the UI.

---

*For detailed technical implementation notes, refer to [ocr_fixer.py](file:///c:/Github/CloScaoil/ocr_fixer.py) or our [WAYPOINT.md](file:///c:/Github/CloScaoil/WAYPOINT.md) progress log.*
