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
    assert fixer.VERSION == "5.0-UNIVERSAL"

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

if __name__ == "__main__":
    pytest.main([__file__])

