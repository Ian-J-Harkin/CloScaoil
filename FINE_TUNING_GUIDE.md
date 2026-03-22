# Fine-Tuning Guide: Refining OCR Corrections

This guide outlines the systematic process for fine-tuning the OCR correction pipeline after an initial pass. This process ensures that the text is polished without introducing "hallucinations" or breaking valid Irish grammar.

## 1. The Workflow Loop

The fine-tuning process is a continuous loop of **Review -> Identify -> Classify -> Update -> Rerun**.

1. **Review:** Read the generated output (e.g., `manannan04.md`).
2. **Identify:** Spot any remaining OCR errors, stray punctuation, or incorrect grammar.
3. **Classify:** Determine the *type* of error (Simple Word, Contextual/Grammar, Global Pattern).
4. **Update:** Add the rule to `config/corrections_dict.json` or modify `ocr_fixer.py`.
5. **Rerun:** Execute the pipeline script to apply the changes automatically.

## 2. Classifying Errors & Adding Rules

When you spot an error, you must decide how to fix it based on the architecture:

### A. Simple 1-to-1 Word Errors (`verified`)
**Use when:** A specific misspelled word should *always* be replaced by the correct word, regardless of context.
**Examples:** `eitiLt` -> `eitilt`, `ḋeaiiaṁ` -> `ḋeanaṁ`, `igurb` -> `gurb`.

**How to update:**
Open `config/corrections_dict.json` and add the mapping to the `"verified"` dictionary. Keep them alphabetized if possible.
```json
"dictionary": {
  "verified": {
    "ḋeaiiaṁ": "ḋeanaṁ",
    "eitiLt": "eitilt"
  }
}
```

### B. Contextual or Multi-Word Errors (`contextual`)
**Use when:** The error involves multiple words, incorrect spacing around punctuation, or grammar rules that shouldn't affect the whole book indiscriminately.
**Examples:** `caiṫeaḋ.siar` (erroneous period), `go ṁ` -> `go m` (Grammar rule), `ii` -> `nn` (Systemic OCR misread).

**How to update:**
Open `config/corrections_dict.json` and add a new object to the `"contextual"` array.
```json
"contextual": [
  {
    "pattern": "caiṫeaḋ.siar",
    "replacement": "caiṫeaḋ siar",
    "reason": "OCR error: erroneous period connecting words."
  }
]
```
*Tip:* Always include a `"reason"` so future reviewers understand why the rule exists.

### C. Generalized Formatting Anomalies (`ocr_fixer.py`)
**Use when:** There is a systemic formatting issue that requires regular expressions (Regex) because dictionary replacements are too rigid.
**Examples:** Stray mid-sentence capital letters (`stróinséir A raġaḋ`), mixed-case words (`baLl`), or hyphenation bridging two line breaks.

**How to update:**
These require modifying the Python logic in `ocr_fixer.py`. For example, tweaking the `apply_stray_caps_fix()` method or adjusting the `split` logic to handle apostrophes.

### D. Ambiguous Words (`ambiguous`)
**Use when:** A misspelled word could map to multiple valid Irish words depending on the sentence.
**Examples:** `ar` could be the preposition `ar` (on) or the possessive adjective `ár` (our).

**How to update:**
Add it to the `"ambiguous"` section in the JSON. The script will skip it and flag it in the generated report (`m4_ambiguous.json`) for you to manually inspect later.
```json
"ambiguous": {
  "ar": ["ar", "ár"]
}
```

## 3. Rerunning and Testing

Once you have added your rules to the JSON config, you must rerun the fixer script against the **backup** file to regenerate the clean output safely.

**The Command:**
```bash
python ocr_fixer.py old-orthography/manannanXX_backup.md --output old-orthography/manannanXX.md
```
*(Replace `XX` with your chapter number, e.g., `04`).*

Check the regenerated `manannanXX.md` file to verify that your new rules worked perfectly and didn't accidentally break surrounding text.

## 4. Rule Validation Protocol (Safety Checks)
To prevent the dictionary from becoming corrupted (hallucinating mappings like `atá` -> `daoine`):
* **Never use automated guessing tools** to bulk-import words unless you are mathematically validating the Levenshtein distance (how many letters changed).
* If an OCR error completely mangled a word to the point where it shares no root letters with the correct word, add it as a `contextual` phrase surrounding the broken word, or fix it manually in the text file rather than poisoning the `verified` dictionary.

## 5. Using the `fine_tune.py` Utility

To speed up the data entry process, you can use the `fine_tune.py` script located in `/caibidlí/`. It accepts JSON files or raw JSON strings containing your fixes and mathematically categorizes them into either the `verified` (single words) or `contextual` (multi-word phrases/punctuation) dictionary sections safely.

**Input Structure Example:**
```json
[
  {
    "FineTuneEntry": {
      "Incorrect": "aċ a ineireaiina fein",
      "Corrected": "aċ a méireanna féin"
    }
  },
  {
    "FineTuneEntry": {
      "Incorrect": "speire",
      "Corrected": "spéire"
    }
  }
]
```

**Executing from CLI via File:**
```bash
python fine_tune.py --file my_fixes.json
```

**Executing from CLI via Raw String:**
*(Note: Wrap the JSON string in single quotes)*
```bash
python fine_tune.py --json '{"FineTuneEntry": {"Incorrect": "ii", "Corrected": "nn"}}'
```
