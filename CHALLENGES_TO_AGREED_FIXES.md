# Challenges to Strict Application of AGREED_FIXES

*This document records instances where blanket application of proofreading rules ("Agreed Fixes") from the original Manannan repository has been challenged due to grammatical or morphological nuances in Irish.*

When processing raw OCR output (1943 Cló Gaelach), there is a strong temptation to categorize unfamiliar spellings or mixed-case words as "OCR noise" and permanently correct them across the dataset. However, being overly strict with these global rules can destroy semantic meaning and valid grammatical forms.

## Case Studies

### 1. `tÁrd-Ṁáiġistir` vs `tárd-Ṁáiġistir`
- **The Rule Challenged:** `- tÁrd-Ṁáiġistir -> tárd-Ṁáiġistir (OCR uppercase accent issue in prefixed form)`
- **The Problem:** The proofreader assumed the capitalization of `A` to `Á` was an OCR hallucination triggered by the accent mark, since it occurred immediately after a lowercase `t`. They corrected it to `tárd-Ṁáiġistir`.
- **The Grammatical Reality:** "Árd-Ṁáiġistir" (High-Master) is a capitalized proper title. When preceded by the definite article "an" (the), Irish grammar requires *t-prothesis* before the vowel. Therefore, `an tÁrd-Ṁáiġistir` is grammatically correct.
- **The Lesson:** Lowercasing proper nouns because the prefixing patterns look like "mixed-case OCR noise" permanently breaks the intended noun structure. 

### 2. The `mbóṫari` Trailing Character
- **The Rule Challenged:** `- mbóṫari -> mbóṫar (spurious trailing character)`
- **The Problem:** The proofreader assumed the trailing `i` was simply a spurious character (a stray pixel read as an `i`) and stripped it, reverting the word to the base nominative noun.
- **The Grammatical Reality:** The trailing `i` is highly unlikely to be random noise. It introduces two strong morphological possibilities:
  1. **Missing Accent (`mbóṫarí`)**: Some Irish dialects form plurals using `-í` rather than standard `-e` (`bóiṫre`). Stripping it entirely deletes the plural marker "roads" and forces it to be singular.
  2. **Transposition (`mbóṫair`)**: The genitive singular of road is `bóṫair` ("of the road"). The OCR or original typesetter may have transposed the `i` and `r`. Stripping the `i` completely destroys the genitive case marker.
- **The Lesson:** Blindly stripping letters from the ends of words as "spurious noise" without analyzing the context can silently erase critical grammatical morphology (case and number). 

🚨 The Editorial Conflicts:
1. The tÁrd-Ṁáiġistir Rule (Line 20 in AGREED_FIXES)

Agreed Fixes says: Lowercase it to tárd-Ṁáiġistir (assuming the A to Á was an OCR hallucination triggered by the accent mark).
The Grammatical Reality: As noted in our challenges document, "Árd-Ṁáiġistir" is a capitalized proper title. When preceded by "an", t-prothesis applies. an tÁrd-Ṁáiġistir is 100% grammatically correct. Lowercasing the "Á" strips the proper noun status entirely.
2. The mbóṫari Rule (Line 13 in AGREED_FIXES)

Agreed Fixes says: Strip the trailing i to make it mbóṫar (assuming it's a spurious trailing character).
The Grammatical Reality: Dropping that i destroys either the plural marker (mbóṫarí - roads) or the genitive case (mbóṫair - of the road). We cannot automatically prune it without knowing the sentence context.
3. The gCiandracán Rule (Line 26 in AGREED_FIXES)

Agreed Fixes says: Lowercase it to gciandracán after an eclipsis.
The Grammatical Reality: If "Ciandracán" is a proper noun (which the capital C implies), standard Irish orthography retains the capital letter after the lowercase eclipsing consonant (e.g., i nGaillimh). Lowercasing it destroys the proper noun.
How we should proceed for Chapter 04:
If I blindly run 

ocr_fixer.py
 with these rules loaded into 

config/corrections_dict.json
, it is going to auto-butcher Chapter 04 wherever those words appear.

Before we process the file, I strongly recommend we:

Purge tÁrd-Ṁáiġistir, mbóṫari, and gCiandracán from the verified section of 

corrections_dict.json
 so they are not auto-replaced.
We must move them instead to the ambiguous section, so the Universal LLM Manager (Gemini/Claude) is forced to look at the surrounding sentence and decide if the i is a plural marker, a genitive, or actual OCR noise based on the context.