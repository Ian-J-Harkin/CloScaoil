import pytest
import os
import json
from ocr_fixer import StandardModernizer, UniversalLLMManager

@pytest.fixture
def modernizer():
    mgr = UniversalLLMManager(api_key=None, model_name="gemini/gemini-1.5-flash")
    return StandardModernizer(mgr)

def test_lexical_modernization(modernizer):
    # Test spelling simplifications from caighdean_2012.json
    # beirbhiughadh -> beiriú
    assert modernizer.apply_lexical("beirbhiughadh") == "beiriú"
    assert modernizer.apply_lexical("tráigh") == "trá"
    assert modernizer.apply_lexical("cluaidhe") == "cluaí"
    
    # Test case sensitivity
    assert modernizer.apply_lexical("TRÁIGH") == "trá" # re.IGNORECASE makes it lower if the replacement is lower
    
    # Test suffixes
    # -idhe -> -í
    assert modernizer.apply_lexical("staraidhe") == "staraí"
    assert modernizer.apply_lexical("múchughadh") == "múchú"
    
def test_modernization_integration(modernizer):
    from ocr_fixer import OCRFixer
    config_dir = os.path.join(os.getcwd(), "config")
    config_path = os.path.join(config_dir, "corrections_dict_test.json")
    
    fixer = OCRFixer(config_path, model_name="gemini/gemini-1.5-flash")
    
    # Mock some text that needs modernization
    input_text = "bhí sé ag tráigh" # 'tráigh' should become 'trá'
    # By default, modernization is OFF
    processed, _, _ = fixer.process_text(input_text, modernize_2012=False)
    assert "tráigh" in processed
    
    # Turn it ON
    processed, patterns, _ = fixer.process_text(input_text, modernize_2012=True)
    assert "trá" in processed
    assert any(p['type'] == 'modernized' for p in patterns)

if __name__ == "__main__":
    pytest.main([__file__])
