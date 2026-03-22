# Antigravity Task: Irish Grammar Heuristics

### Rule: Preposition "Go" (To)
- **Constraint:** "Go" before a noun starting with a consonant does NOT cause lenition.
- **Action:** Add a contextual rule to `ocr_fixer.py` via the JSON:
  - `pattern`: "go ṁ" -> `replacement`: "go M"
  - `reason`: "Preposition 'go' does not lenite consonants.".

### Rule: Conservative De-hyphenation
- **Constraint:** Do not rejoin words if the first part is `n`, `t`, or `h` (Irish mutative prefixes).