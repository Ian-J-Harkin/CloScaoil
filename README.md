# 🛡️ ClóScaoil: Manannán Digitization Engine (v5.1)
**Surgical OCR Correction, Heuristic Intelligence & Linguistic Modernization for 1940s Irish Orthography**

ClóScaoil is a specialized Python-based digitization pipeline designed to process and correct OCR output from the 1943 *Manannán* series. It combines multi-stage **Heuristic Intelligence**, **LLM-powered arbitration**, **Multimodal Vision auditing**, and **2012 Caighdeán Modernization** into a complete production system—from raw OCR to archival-quality EPUB.

---

## 🚀 Core Features

### 📖 Surgical Dictionary Lookup
Prioritizes human-verified corrections from `config/corrections_dict.json`. If a word is verified, it is fixed instantly, skipping all automated heuristics to preserve precision.

### ✝️ Shorthand Normalization (Tironian Et)
Automatically restores the Tironian Et symbol (`⁊`) by targeting isolated `7` and `>` OCR misreads. Supports both literal symbol restoration and full expansion to `agus`.

### ✨ Visual Heuristics (Speck-to-Ponc)
A fallback intelligence layer that identifies lenitable consonants followed by OCR noise (specks, dots, and quotes) and restores them to their correct lenited forms (e.g., `b'` or `b*` ➔ `ḃ`).

### ⚖️ Linguistic Validation (Vowel Harmony)
A built-in validator that checks every word against "Caol le Caol" (Slender with Slender) Irish orthography rules. Words failing this check are flagged for human review or AI arbitration.

### 🌐 Universal LLM Integration (Phase F)
Integrates **LiteLLM** for provider-agnostic AI arbitration. Supports **Gemini**, **OpenAI**, **Anthropic (Claude)**, and **OpenRouter** — switchable live from the UI sidebar. Uses a local **3-word context cache** to minimize API calls.

### ✨ 2012 Caighdeán Modernization (Phase G)
An optional post-processing pass that translates the 1958 "New Orthography" into the 2012 Official Revised Standard (*An Caighdeán Oifigiúil Athbhreithnithe*), including:
- **Lexical Simplification:** e.g., `beirbhiughadh` ➔ `beiriú`, `tráigh` ➔ `trá`
- **Nominative-for-Genitive:** LLM-assisted grammar rule application
- **Synthetic-to-Analytic Verbs:** e.g., `mholamar` ➔ `mhol muid`

### 📽️ Multimodal Vision Audit
Cross-references your corrected text against original manuscript scans using any vision-capable LLM. Supports automated **Silent Mode** for batch runs and case-insensitive image matching (`.jpg`, `.JPG`, `.png`, `.PNG`).

### 📦 EPUB Archival Export (Phase E)
Generates Unicode-compliant EPUB 3.0 archives with nested Table of Contents parsed from Markdown headers, ready for modern e-readers.

---

## 🖥️ Interactive Streamlit Interface
The repository includes a modern, interactive dashboard for real-time text processing:

- **Live Preview:** View processed text with strict highlighting of linguistic violations.
- **Anomaly Dashboard:** A real-time log of harmony violations, auto-fixes, and modernization events.
- **LLM Provider Selector:** Switch providers (Gemini, OpenAI, Claude, OpenRouter) on-the-fly from the sidebar.
- **2012 Modernization Toggle:** Enable/disable the modernization pass per run.
- **Batch Production Pipeline:** Process entire manuscript directories with configurable Vision Audit policies.
- **Golden Copy & EPUB Export:** One-click finalization into reading editions or archival e-books.

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

3.  **Set up API keys (OS Environment Variables):**
    The engine reads keys directly from your operating system. Set at least one:
    - **Windows:** Open *System Properties > Environment Variables* and add a new User variable (e.g., `GEMINI_API_KEY`). Restart your terminal.
    - **macOS/Linux:** Add `export GEMINI_API_KEY="your_key_here"` to `~/.bashrc` or `~/.zshrc` and run `source ~/.zshrc`.

4.  **Verify your setup (optional):**
    ```bash
    python test_api.py
    ```

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
python ocr_fixer.py input.md --output final_output.md --expand-abbreviations --strict --report errors.json
```

---

## ⚙️ Configuration
The engine's behavior is defined in `config/corrections_dict.json`. You can manage:
- `dictionary.verified`: Reliable 1-to-1 word corrections.
- `dictionary.contextual`: Phrase-level grammatical rules.
- `dictionary.ambiguous`: Words requiring human/AI arbitration.

The 2012 modernization mappings live in `config/caighdean_2012.json`:
- `exact_matches`: Direct word replacements (e.g., `tráigh` ➔ `trá`).
- `suffix_replacements`: Suffix-based transformations (e.g., `-ughadh` ➔ `-ú`).

---

## 🧪 Testing
Run the full test suite:
```bash
# Windows
$env:PYTHONPATH="."; python -m pytest tests/ -v

# macOS / Linux
PYTHONPATH=. python -m pytest tests/ -v
```

---

## 📂 Project Structure
```
CloScaoil/
├── ocr_fixer.py          # Core engine: OCRFixer, UniversalLLMManager, StandardModernizer, BatchProcessor, EpubBuilder
├── streamlit_app.py       # Interactive Streamlit UI
├── test_api.py            # API connection diagnostics utility
├── config/
│   ├── corrections_dict.json    # Dictionary mappings & heuristic rules
│   └── caighdean_2012.json      # 2012 Caighdeán modernization map
├── tests/
│   ├── test_ocr_fixer.py        # Core engine unit tests (14 tests)
│   └── test_modernizer.py       # Modernizer unit tests
├── reference-docs/              # Phase specification documents
├── USER_GUIDE.md                # Comprehensive user documentation
├── WAYPOINT.md                  # Project roadmap & progress log
└── requirements.txt             # Python dependencies
```

---

## 🤝 Contributing
Contributions to the dictionary mappings, heuristic patterns, and modernization rules are welcome. Please refer to the phase summary documents for detailed technical context.

*Manannán Digitization Lab | Phase G: 2012 Linguistic Modernization Complete (v5.1-ARCHIVAL STABLE)*
