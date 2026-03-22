Filename: PROMPT_SYSTEM_RULES.md

Markdown
# Antigravity Agent Task: Irish OCR Rules

### Objective
Implement the following rules in a Python post-processor to correct 1943 Cló Gaelach OCR artifacts while maintaining a strictly side-by-side QA layout.

### Ruleset
1. **Lenition (Ponc Séimhithe):** Restore dots to consonants (ḃ, ċ, ḋ, ḟ, ġ, ṁ, ṗ, ṡ, ṫ) based on manual patterns in chapters 00-02.
2. **De-hyphenation:** Rejoin words split by line-end hyphens (e.g., ua- \n saal -> uasaal).
3. **Punctuation:** Remove "loose" spacing (e.g., " An mar sin é ? " -> "An mar sin é?").
4. **Layout Preservation:**
   - Keep ALL original line breaks.
   - Retain page numbers and headers.
   - Blank line before page markers `[l.XX]: #`.
   - Blank line after marker ONLY for new paragraphs.