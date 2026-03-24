import pytest
import os
import json
from ocr_fixer import OCRFixer

@pytest.fixture
def fixer():
    # Setup a mock config for testing
    config_dir = os.path.join(os.getcwd(), "config")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "corrections_dict_test.json")
    
    mock_data = {
        "global_replacements": {"chars": {}},
        "dictionary": {
            "verified": {"testword": "verifiedword"},
            "ambiguous": {"ar": ["ar", "ár"]},
            "contextual": []
        }
    }
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f)
        
    return OCRFixer(config_path)

def test_version(fixer):
    assert fixer.VERSION == "3.0-VISION"

def test_shorthand_normalization(fixer):
    # Test line boundaries
    assert fixer.normalize_shorthand("7 is start") == "\u204a is start"
    assert fixer.normalize_shorthand("at end 7") == "at end \u204a"
    assert fixer.normalize_shorthand("  7  ") == "  \u204a  "
    # Test non-boundaries (should not touch)
    assert fixer.normalize_shorthand("word7attached") == "word7attached"

def test_vowel_harmony(fixer):
    # Valid
    assert fixer.check_vowel_harmony("fírinne") is True
    assert fixer.check_vowel_harmony("focal") is True
    # Invalid (Mixed class)
    assert fixer.check_vowel_harmony("fílan") is False
    # User constraint: 'á' is broad
    assert fixer.check_vowel_harmony("d'ólá") is True # ó and á both broad

def test_violation_gating(fixer):
    # Threshold is 5. Create 6 violations.
    text = "fílan " * 6
    _, _, requires_audit = fixer.process_text(text)
    assert requires_audit is True
    
    # 5 or fewer
    text = "fílan " * 5
    _, _, requires_audit = fixer.process_text(text)
    assert requires_audit is False

def test_path_normalization(fixer):
    # Verify that paths are normalized using os.path.join and getcwd logic
    from ocr_fixer import AmbiguityArbitrator
    arb = AmbiguityArbitrator(api_key=None)
    assert os.path.isabs(arb.cache_path)
    assert "config" in arb.cache_path

def test_visual_heuristics(fixer):
    # Restores lenited consonants misidentified as noise
    assert fixer.apply_visual_heuristics("b'") == "ḃ"
    assert fixer.apply_visual_heuristics("b.") == "ḃ"
    assert fixer.apply_visual_heuristics("b*") == "ḃ"
    assert fixer.apply_visual_heuristics("d.") == "ḋ"
    assert fixer.apply_visual_heuristics("m*") == "ṁ"
    # Negative test: noise only (no consonant)
    assert fixer.apply_visual_heuristics("'.") == "'."

def test_dictionary_precedence(fixer):
    # If word is in verified, don't apply heuristics
    # 'testword' -> 'verifiedword' in mock data
    # Normal heuristics would apply to 'testword' if we added characters
    processed, _, _ = fixer.process_text("testword")
    assert processed == "verifiedword"
    
    # If shorthand is part of verified, it shouldn't be touched by regex
    # (Actually we split words before verified check, but let's confirm priority)
    fixer.data["dictionary"]["verified"]["7"] = "SEVEN"
    processed, _, _ = fixer.process_text("7")
    assert processed == "SEVEN" # Verified wins over Shorthand regex
