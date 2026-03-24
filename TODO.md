# ClóScaoil Engine To-Do List

## 🚀 Testing Tasks
- [ ] **Heuristic Verification (Chapter Test)**: Run one or more chapters through the Stage 2 pipeline (OCR Fixer) to specifically observe the new v2.0 heuristics in action:
    - **Speck-to-Ponc**: Verify if `b.`, `c'`, `d*`, etc., are correctly converted to `ḃ`, `ċ`, `ḋ`.
    - **Vowel Harmony**: Check the "Ambiguous Matches" report for words prefixed with ⚠️ (e.g., `⚠️fílan`). Ensure the AI/User can manually resolve these harmony violations.
    - **Tironian Et**: Confirm standalone `7`, `>`, or `&` symbols are correctly normalized to `agus`.

## 🛠️ Next Steps (Phase B)
- [ ] **Contextual Deep Repair**: Transition from regex-based heuristics to more advanced contextual patterns for ambiguous words (e.g., better `ar` vs `ár` handling).
- [ ] **Reporting Improvements**: Enhance the Streamlit "Ambiguous Matches" dashboard to allow one-click corrections for discovered harmony violations.
