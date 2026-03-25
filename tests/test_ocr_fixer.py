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
        
    return OCRFixer(config_path, model_name="gemini/gemini-1.5-flash")

def test_version(fixer):
    assert fixer.VERSION == "5.1-ARCHIVAL"

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
    from ocr_fixer import UniversalLLMManager
    mgr = UniversalLLMManager(api_key=None, model_name="gemini/gemini-1.5-flash")
    assert os.path.isabs(mgr.cache_path)
    assert "config" in mgr.cache_path

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
    fixer.data["dictionary"]["verified"]["7"] = "SEVEN"
    processed, _, _ = fixer.process_text("7")
    assert processed == "SEVEN" 

# === Phase A/B Foundation Tests ===

def test_shorthand_expansion_mode(fixer):
    """Tironian Et expansion to 'agus' when configured."""
    assert fixer.normalize_shorthand(" 7 ", expand=True).strip() == "agus"
    assert fixer.normalize_shorthand(" > ", expand=True).strip() == "agus"
    # Standard mode should give the symbol
    assert fixer.normalize_shorthand(" 7 ", expand=False).strip() == "\u204a"

def test_visual_heuristics_uppercase(fixer):
    """Speck-to-Ponc must also handle uppercase consonants."""
    assert fixer.apply_visual_heuristics("B.") == "Ḃ"
    assert fixer.apply_visual_heuristics("S'") == "Ṡ"
    assert fixer.apply_visual_heuristics("T*") == "Ṫ"
    assert fixer.apply_visual_heuristics("M.") == "Ṁ"

def test_global_replacements(fixer):
    """Phase A: Character substitutions and punctuation spacing."""
    # Set up config with global replacements
    fixer.data["global_replacements"] = {
        "chars": {"ſ": "s"},
        "punctuation_spacing": True
    }
    # Long s replacement
    result = fixer.apply_global_replacements("ſaol")
    assert result == "saol"
    
    # Punctuation spacing: remove space before punctuation, add space after
    result = fixer.apply_global_replacements("focal ,focal")
    assert result == "focal, focal"
    
    # Multiple spaces collapsed
    result = fixer.apply_global_replacements("focal    focal")
    assert result == "focal focal"

def test_dehyphenate(fixer):
    """Phase A: Line-break de-hyphenation with Irish prefix preservation."""
    # Standard hyphenation should rejoin
    result = fixer.dehyphenate("Man-\nannán")
    assert "Manannán" in result
    
    # n- prefix should be preserved (Irish eclipsis)
    result = fixer.dehyphenate("n-\náisiún")
    assert "n-áisiún" in result
    
    # t- prefix should be preserved
    result = fixer.dehyphenate("t-\nathair")
    assert "t-athair" in result

def test_stray_caps_fix(fixer):
    """Phase A: OCR capitalisation errors mid-sentence."""
    # Mid-sentence stray capital
    result = fixer.apply_stray_caps_fix("agus Focal eile")
    assert "focal" in result.lower() or "focal" in result
    
    # Mixed-case OCR error (e.g., "buaLaḋ")
    result = fixer.apply_stray_caps_fix("buaLaḋ")
    assert result == "bualaḋ"
    
    # Valid mutation prefixes should be handled
    result = fixer.apply_stray_caps_fix("bhFuil")
    assert result.startswith("bh")

def test_contextual_heuristics(fixer):
    """Phase A: Phrase-level grammatical corrections."""
    fixer.data["dictionary"]["contextual"] = [
        {"pattern": "go ṁ", "replacement": "go m"},
        {"pattern": " nior ", "replacement": " níor "}
    ]
    
    result = fixer.apply_contextual_heuristics("agus go ṁaith é")
    assert "go maith" in result
    
    result = fixer.apply_contextual_heuristics("dúirt sé nior ṫáinig sí")
    assert "níor" in result

def test_page_header_detection(fixer):
    """Phase A: Configurable page header patterns."""
    fixer.data["global_replacements"]["page_header_patterns"] = [
        "^MANANNÁN.*$"
    ]
    # Short line matching pattern with key character
    assert fixer.is_page_header("MANANNÁN") is True
    # Regular text should not match
    assert fixer.is_page_header("This is a regular sentence about the day.") is False
    # Empty lines should not match
    assert fixer.is_page_header("") is False
    # Page markers should not match
    assert fixer.is_page_header("[l.30]: #") is False

def test_image_fallback_naming(fixer):
    from ocr_fixer import BatchProcessor
    bp = BatchProcessor(fixer)
    
    # Create temp directory with various naming conventions
    import tempfile
    import shutil
    tmp_dir = tempfile.mkdtemp()
    try:
        # Create dummy images
        open(os.path.join(tmp_dir, "page_045.jpg"), 'w').close()
        open(os.path.join(tmp_dir, "046.png"), 'w').close()
        open(os.path.join(tmp_dir, "p47.jpg"), 'w').close()
        
        assert bp._find_image(tmp_dir, 45) is not None
        assert "page_045.jpg" in bp._find_image(tmp_dir, 45)
        
        assert bp._find_image(tmp_dir, 46) is not None
        assert "046.png" in bp._find_image(tmp_dir, 46)
        
        assert bp._find_image(tmp_dir, 47) is not None
        assert "p47.jpg" in bp._find_image(tmp_dir, 47)
        
        # Negative test
        assert bp._find_image(tmp_dir, 99) is None
    finally:
        shutil.rmtree(tmp_dir)

def test_golden_copy_logic(fixer):
    import tempfile
    import shutil
    tmp_in = tempfile.mkdtemp()
    tmp_out_file = os.path.join(tmp_in, "golden.txt")
    
    try:
        # Create mock chapters with page markers
        with open(os.path.join(tmp_in, "ch1.md"), 'w', encoding='utf-8') as f:
            f.write("[l.1]: #\nFirst page content.\n[l.2]: #\nSecond page.")
            
        fixer.generate_golden_copy(tmp_in, tmp_out_file)
        
        with open(tmp_out_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Headers should be gone
            assert "[l.1]: #" not in content
            assert "[l.2]: #" not in content
            assert "First page content." in content
            assert "Second page." in content
            assert "PROCESSED BY CLÓSCAOIL" in content
    finally:
        shutil.rmtree(tmp_in)

def test_image_case_insensitive(fixer):
    """v3.4: Scanner output may use .JPG or .PNG uppercase extensions."""
    from ocr_fixer import BatchProcessor
    bp = BatchProcessor(fixer)
    
    import tempfile
    import shutil
    tmp_dir = tempfile.mkdtemp()
    try:
        open(os.path.join(tmp_dir, "page_045.JPG"), 'w').close()
        open(os.path.join(tmp_dir, "046.PNG"), 'w').close()
        
        result_45 = bp._find_image(tmp_dir, 45)
        assert result_45 is not None
        assert "page_045.JPG" in result_45
        
        result_46 = bp._find_image(tmp_dir, 46)
        assert result_46 is not None
        assert "046.PNG" in result_46
    finally:
        shutil.rmtree(tmp_dir)

def test_golden_copy_newline_consistency(fixer):
    """v3.4: Golden copy must enforce Unix-standard newlines regardless of host OS."""
    import tempfile
    import shutil
    tmp_in = tempfile.mkdtemp()
    tmp_out_file = os.path.join(tmp_in, "golden.txt")
    
    try:
        with open(os.path.join(tmp_in, "ch1.md"), 'w', encoding='utf-8') as f:
            f.write("[l.1]: #\nLine one.\n[l.2]: #\nLine two.")
            
        fixer.generate_golden_copy(tmp_in, tmp_out_file)
        
        with open(tmp_out_file, 'rb') as f:
            raw_bytes = f.read()
            # Must NOT contain Windows CRLF
            assert b'\r\n' not in raw_bytes
            # Must contain Unix LF
            assert b'\n' in raw_bytes
    finally:
        shutil.rmtree(tmp_in)

def test_highlight_rendering():
    """v3.4: ==word== must be converted to <mark> tags BEFORE orphaned == are stripped."""
    import re
    
    # Simulate strict mode output from the engine
    engine_output = "This is ==badword== in a sentence."
    
    # Correct order: regex first, strip second
    display = re.sub(r"==([^=]+)==", r"<mark>\1</mark>", engine_output)
    display = display.replace("==", "")
    
    assert "<mark>badword</mark>" in display
    assert "==" not in display
    
    # Verify the OLD (broken) order would fail
    broken_display = engine_output.replace("==", "")
    broken_display = re.sub(r"==([^=]+)==", r"<mark>\1</mark>", broken_display)
    assert "<mark>" not in broken_display  # Confirms the bug existed

def test_modernization_toggle_integrity(fixer):
    """v5.1: When modernization is OFF, the text must remain in its diplomatic 1943/1958 state."""
    # Text with old-orthography words that WOULD be modernized
    old_text = "[l.30]: #\ntráigh agus urdhubhadh"
    
    # Process WITHOUT modernization
    processed_off, patterns_off, _ = fixer.process_text(old_text, modernize_2012=False)
    
    # The old forms should survive (not be replaced by trá / urú)
    assert "tráigh" in processed_off
    assert "urdhubhadh" in processed_off
    
    # No "modernized" entries should exist in the pattern log
    modernized_entries = [p for p in patterns_off if p.get("type") == "modernized"]
    assert len(modernized_entries) == 0
    
    # Process WITH modernization
    processed_on, patterns_on, _ = fixer.process_text(old_text, modernize_2012=True)
    
    # The old forms SHOULD now be replaced
    assert "trá" in processed_on
    assert "urú" in processed_on
    
    # Modernized entries should exist
    modernized_entries_on = [p for p in patterns_on if p.get("type") == "modernized"]
    assert len(modernized_entries_on) > 0

if __name__ == "__main__":
    pytest.main([__file__])

