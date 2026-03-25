# ClóScaoil Manual Testing Protocols

This document outlines the final system validation tasks for the ClóScaoil Archival Engine (v5.1-ARCHIVAL STABLE). These specific tests cannot be automated in the standard CI/CD or agentic environments, as they rely strictly on either **private API keys** or **external hardware inspection**.

---

## 🔒 1. Linguistic Benchmarking (Live Inference)

The automated test suite (`test_ocr_fixer.py`) successfully asserts that the `UniversalLLMManager` constructs the correct payloads, but it uses mocked API responses. 

**Objective:** Run a full-book performance test on Chapters 04–10 to verify LLM arbitration speeds and accuracy for the new 2017 Nominative/Genitive prompts.
**Dependencies:** A valid `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY` injected into the local terminal environment.

### Steps to Execute:
1. Ensure your `.env` file contains your private API key, or export it into your shell (e.g., `set GEMINI_API_KEY=your_key_here`).
2. Run the connection diagnostic:
   ```bash
   python test_api.py
   ```
3. Once the handshake succeeds, execute the batch processor over the Manannán manuscript:
   ```bash
   python ocr_fixer.py C:\Github\Manannan\caibidlí\old-orthography\ --output C:\Github\CloScaoil\out\ --batch
   ```
4. **Validation:** Review the resulting markdown files to ensure the LLM successfully resolved ambiguous terms (e.g., `ar`/`ár`) according to sentence context.

---

## 📱 2. EPUB Visual Quality Audit

The `EpubBuilder` component successfully outputs structurally valid, W3C-compliant EPUB 3.0 archives. However, the exact rendering of embedded Gaelic typefaces is strictly hardware-dependent.

**Objective:** Test the generated e-books on physical e-reader devices (Kindle, Kobo, Apple Books) to verify sideloaded font rendering.
**Dependencies:** Physical e-reader hardware (or corresponding desktop reader application).

### Steps to Execute:
1. Run the EPUB Export block inside the Streamlit Lab (`streamlit run streamlit_app.py`) to generate `manannan_archival.epub`.
2. Sideload the EPUB onto your target device (e.g., via "Send to Kindle" or USB transfer).
3. **Validation:** 
   - Verify that the custom **Gadelica** font renders correctly.
   - Specifically check that traditional lenition dots (*ponc séimhithe*, e.g., ḃ, ċ, ḋ) format without breaking line-heights or causing square artifact boxes.
   - Verify the nested Chapter Table of Contents functions correctly within the device's native UI.

---

## 🧠 3. Advanced Semantic Repair (Dialect Tuning)

The 2017 Official Standard rules for "Nominative-for-Genitive" have been injected into the prompt. However, historical Munster sub-dialects inherently contain edge-case phrasing not fully addressed by standard government policy.

**Objective:** Iteratively tune the LLM instructions to handle specific Munster idioms without false-flagging them as grammatical errors.
**Dependencies:** Live LLM Inference Access.

### Steps to Execute:
1. Using an active API Key, run `ocr_fixer.py` specifically targeting a mechanically dense chapter (e.g. Chapter 08 or 12).
2. **Validation:** Review the LLM's corrections. If the LLM incorrectly "modernizes" a perfectly valid dialectical phrase (e.g., forcibly altering a *Cúige Mumhan* proverb to the Caighdeán), the prompt sequence inside `UniversalLLMManager.modernize_sentence` must be manually tuned.

---

## 🔬 4. Multi-Phase Regression Diffs (Value Verification)

As we transition from the core pipeline (Phase F), through our manual 2017 ruleset (Phase G), and into the open-source dictionary ingester (Phase H), it is critical to definitively prove the delta of value added by each new layer of complexity.

**Objective:** Maintain diffable copies of processed chapters (specifically Chapters 00–05) across all three pipeline modes to verify exactly which words each phase is catching or missing.
**Dependencies:** A standard diff tool (e.g., VS Code diff, `git diff`, or `vimdiff`).

### Steps to Execute:
To prove the architecture's efficiency, run the same untreated manuscript file through the pipeline under three different flags/modes, generating three separate output files:

1. **Phase F Output (Clean Transcription, No Modernization):**
   Run the engine with `--no-modernize` (or skip the modernizer).
   ```bash
   python ocr_fixer.py C:\Github\Manannan\caibidlí\old-orthography\manannan00.md --output C:\Github\CloScaoil\diffs\manannan00_PhaseF.md
   ```
   *Expected Result:* Basic OCR cleanup only; old mid-century spellings left intact.

2. **Phase G Output (Curated JSON List + LLM Prompt):**
   Run the engine with the standard 2012 toggle enabled (which currently hits our 30+ word `caighdean_2012.json` map).
   ```bash
   python ocr_fixer.py C:\Github\Manannan\caibidlí\old-orthography\manannan00.md --output C:\Github\CloScaoil\diffs\manannan00_PhaseG.md
   ```
   *Expected Result:* Extremely common historical suffixes (e.g., *ughadh* to *ú*, *tráigh* to *trá*) and the specific Genitive/Nominative shifts are updated.

3. **Phase H Output (Full BuNaMo Interrogation):**
   *(Once Phase H is built)* Run the engine using the massive open-source dictionary validator script.
   ```bash
   python dictionary_validator.py C:\Github\Manannan\caibidlí\old-orthography\manannan00.md --output C:\Github\CloScaoil\diffs\manannan00_PhaseH.md
   ```

### The Verification:
By running a diff across `PhaseG.md` and `PhaseH.md` (`git diff --no-index manannan00_PhaseG.md manannan00_PhaseH.md`), you will see *exactly* the irregular words that the 40,000-word dictionary caught that our simple custom JSON map missed. If there are very few differences, it may prove that Phase G was sufficient for this specific book, saving computational overhead!
