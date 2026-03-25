# Phase H: Irish Language Dictionary Integration

## Background
During the architectural planning for Phase G (2012 Linguistic Modernization), it was proposed to utilize authoritative Irish language databases—explicitly **Teanglann.ie** (Ó Dónaill's Dictionary) and **Téarma.ie**—as the primary sources of truth to dictate orthographic and grammatical translations.

## The Discrepancy
The actual execution of Phase G skipped this step. It relied instead on a limited, manually curated set of lexical substitutions housed in `config/caighdean_2012.json` (which expanded from 10 rules to 30+). The underlying reasons for bypassing the full dictionary integration were:
1. **Scraping Limitations:** Extracting the entirety of proprietary websites like Teanglann.ie via raw web scraping is highly inefficient, unauthorized, and functionally difficult to map into structured data.
2. **Performance Constraints:** Blindly injecting a 43,000+ word dictionary into the existing JSON rule engine would have caused severe performance degradation, fundamentally breaking the lightweight regex engine parsing the manuscripts in `ocr_fixer.py`.

## The Phase H Solution
To honor the original architectural intent without compromising system performance, Phase H mandates a structured, open-source dictionary integration. 

Instead of ad-hoc scraping, we will utilize legitimate, publicly available linguistic datasets:
- **The Irish National Morphology Database (BuNaMo):** The underlying open-data engine that powers Teanglann.ie, featuring ~43,000 Irish words and their inflected forms legally available for computational use.
- **Michal Boleslav Měchura's Open Corpora:** High-quality frequency lists and spellchecking lemmas used in open-source tools like LibreOffice and Firefox.

## Implementation Strategy
Phase H will bridge the design gap via the following technical steps:
1. **Acquisition:** Download the BuNaMo dataset (CSV/XML) locally into the `reference-docs/` repository to ensure offline availability.
2. **Cross-Referencing Engine:** Build a discrete, secondary ingestion script (`dictionary_validator.py`) that operates outside the core `ocr_fixer.py` heuristic loop to prevent system bloat.
3. **Manuscript Auditing:** Run historical scripts (like Manannán Chapter 04) through the validator to cross-reference every word against the modern open-source database.
4. **Surgical Expansion:** Any mid-century spellings that fail the modern lookup will be routed to a "failed words" report. These verified anachronisms can then be surgically added to our JSON maps, dynamically creating an exhaustive, data-driven replacement matrix.

This phased approach safely aligns the development reality with the original strategic blueprint.
