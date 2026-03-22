Filename: PROMPT_LEARNING_LOOP.md

Markdown
# Antigravity Agent Task: Self-Correcting Infrastructure

### Infrastructure
1. **External Knowledge:** Create `config/corrections_dict.json` to store word mappings. The script must read this to apply fixes.
2. **Learning Primitive:** Enable a feedback loop where the user can provide new corrections after a run. The agent must update the JSON and re-apply logic to subsequent files.
3. **QA Verification:** Generate a Walkthrough Artifact after every run highlighting specific linguistic changes for human approval.


Here is the recommended refined structure for config/corrections_dict.json:

1. Refined JSON Structure
JSON
{
  "metadata": {
    "project": "Manannán 1943",
    "last_updated": "2025-10-24",
    "version": "1.2"
  },
  "global_replacements": {
    "chars": {
      "ſ": "s"
    },
    "punctuation_spacing": true
  },
  "dictionary": {
    "verified": {
      "uasaal": "uasaal",
      "garsun": "garsún",
      "an": "an"
    },
    "contextual": [
      {
        "pattern": " nior ",
        "replacement": " níor ",
        "reason": "Missing síneadh fada on common particle"
      }
    ],
    "ambiguous": {
      "mo": ["mo", "moċ"],
      "ar": ["ar", "ár"]
    }
  },
  "statistics": {
    "pages_completed": 3,
    "manual_overrides_count": 12
  }
}
2. Key Refinements Explained
Categorization by Confidence (verified vs. ambiguous):

Verified: Words that are always corrected the same way. The agent can apply these automatically without asking.

Ambiguous: Words like "ar" which could remain "ar" (on) or become "ár" (our). When the agent hits these, it should trigger an Antigravity Walkthrough to ask you for the specific choice.

Contextual Patterns:

Instead of just word-for-word, we add patterns with surrounding spaces (e.g., " nior "). This prevents the script from accidentally changing "nior" if it appears as part of a longer, unrelated string.

Linguistic Metadata (reason):

Adding a reason field helps the AI agent understand why a change is being made. In the future, the agent can use these reasons to suggest corrections for new, unknown words that follow similar grammatical rules.

Traceability (statistics):

By tracking manual_overrides_count, the program can identify which rules are "noisy" (causing too many errors) and suggest that they be moved from verified to ambiguous.

3. Updated Prompt for the Agent
When presenting this refined JSON to your Antigravity agent, add this instruction:

"Update the ocr_fixer.py logic to prioritize the verified dictionary for silent corrections. For any keys found in the ambiguous section, generate a Decision Artifact and wait for my selection before proceeding to the next page".

This refinement turns the script from a simple search-and-replace tool into a sophisticated Linguistic Assistant that respects the complexity of Old Irish orthography while maintaining the layout required for your QA.

### Rule Validation Protocol (No Hallucinations)
1. **Evidence-Based Learning Only**: You are strictly forbidden from proposing or adding any new correction rules (Verified, Ambiguous, or Contextual) based on general linguistic knowledge or external training data.
2. **Provenance Requirement**: Every new rule must be derived EXCLUSIVELY from a visible difference (diff) between the raw OCR and your manual corrections found in the GitHub repository (specifically `manannan00.md` through `manannan02.md`).
3. **Verification Step**: Before suggesting a new rule, you must cite the specific file and line number from the repo where the manual fix occurred. If you cannot point to a specific "Before vs. After" example in the project files, you must not suggest the rule.
4. **Negative Constraint**: If you encounter an error you do not recognize, flag it as `potential_new` for human review, but do NOT attempt to "guess" the fix or the underlying grammar rule.