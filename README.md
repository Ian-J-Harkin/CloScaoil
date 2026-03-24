# 🛡️ ClóScaoil: Manannán Digitization Engine
**Surgical OCR Correction & Heuristic Intelligence for 1940s Irish Orthography**

![ClóScaoil Logo Placeholder](https://via.placeholder.com/800x200?text=Cl%C3%B3Scaoil+Engine+v2.0)

ClóScaoil is a specialized Python-based digitization pipeline designed to process and correct OCR output from the 1943 *Manannán* series. It transitions traditional "Search and Replace" methods into a multi-stage **Heuristic Intelligence** system that understands the nuances of Irish linguistic patterns and the specific errors found in Gaelic-type (Cló Gaelach) OCR.

---

## 🚀 Core Features

### 📖 Surgical Dictionary Lookup
Prioritizes human-verified corrections from a shared configuration file. If a word is verified, it is fixed instantly, skipping all automated heuristics to preserve precision.

### ✝️ Shorthand Normalization (Tironian Et)
Automatically restores the Tironian Et symbol (`⁊`) by targeting isolated `7` and `>` OCR misreads. Supports both literal symbol restoration and full expansion to `agus`.

### ✨ Visual Heuristics (Speck-to-Ponc)
A fallback intelligence layer that identifies lenitable consonants followed by OCR noise (specks, dots, and quotes) and restores them to their correct lenited forms (e.g., `b’` or `b*` ➔ `ḃ`).

### ⚖️ Linguistic Validation (Vowel Harmony)
A built-in validator that checks every word against "Caol le Caol" (Slender with Slender) Irish orthography rules. Words failing this check are flagged for human review or AI arbitration.

### 🤖 LLM-Powered Ambiguity Arbitrator
Integrates **Gemini 1.5** to automatically resolve ambiguous word choices (e.g., `ar` vs `ár`) by analyzing the surrounding sentence context. Uses a local **3-word context cache** to minimize API calls and latency.

---

## 🖥️ Interactive Streamlit Interface
The repository includes a modern, interactive dashboard for real-time text processing:

- **Live Preview:** View processed text with strict highlighting of linguistic violations.
- **Anomaly Dashboard:** A real-time log of harmony violations and manual choice prompts.
- **Automated Resolutions Log:** Monitor the AI arbitrator's context-aware fixes.

---

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ian-j-harkin/CloScaoil.git
    cd CloScaoil
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    It is highly recommended to set a permanent environment variable on your operating system:
    - **Windows:** `setx GEMINI_API_KEY "your_key_here"`
    - **macOS/Linux:** `export GEMINI_API_KEY="your_key_here"`

---

## 📜 Usage

### Interactive UI
Launch the Streamlit digitization lab:
```bash
streamlit run streamlit_app.py
```

### CLI Batch Processing
Process entire files directly from the terminal:
```bash
python ocr_fixer.py input.md --output final_output.md --expand-abbreviations --report errors.json
```

---

## ⚙️ Configuration
The engine's behavior is defined in `config/corrections_dict.json`. You can manage:
- `dictionary.verified`: Reliable 1-to-1 word corrections.
- `dictionary.contextual`: Phrase-level grammatical rules.
- `dictionary.ambiguous`: Words requiring human/AI arbitration.

---

## 🤝 Contributing
Contributions to the dictionary mappings and heuristic patterns are welcome. Please refer to [PHASE_A_SUMMARY.md](file:///c:/Github/CloScaoil/PHASE_A_SUMMARY.md) and [PHASE_B_SUMMARY.md](file:///c:/Github/CloScaoil/PHASE_B_SUMMARY.md) for detailed technical logs.

*Manannán Digitization Lab | Phase B: Infrastructure & Ambiguity Arbitrator Complete*
