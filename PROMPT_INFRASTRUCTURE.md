# Antigravity Task: Self-Correcting Infrastructure

### Knowledge Management
1. **Dictionary Sync:** Manage `config/corrections_dict.json`. The agent must ingest manual fixes from `manannan00.md` through `02.md` to seed this file.
2. **Ambiguity Handling:** Utilize the `ambiguous` JSON category. When the script flags an ambiguous word, the agent must generate a **Decision Artifact** to ask the user which version is correct.
3. **Walkthrough Primitive:** After processing a page, produce a diff-style report showing which "Poncanna" (dots) were added and which "Go" rules were applied.