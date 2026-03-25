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
