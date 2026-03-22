import unicodedata
import os
import argparse
import sys
import re

def modernize_irish_text(text):
    """
    Converts Old Irish dotted consonants to modern 'h' spelling.
    If a word is entirely capitals, 'Ṫ' becomes 'TH', otherwise 'Th'.
    """
    mapping = {
        'Ḃ': 'Bh', 'ḃ': 'bh', 'Ċ': 'Ch', 'ċ': 'ch', 'Ḋ': 'Dh', 'ḋ': 'dh',
        'Ḟ': 'Fh', 'ḟ': 'fh', 'Ġ': 'Gh', 'ġ': 'gh', 'Ṁ': 'Mh', 'ṁ': 'mh',
        'Ṗ': 'Ph', 'ṗ': 'ph', 'Ṡ': 'Sh', 'ṡ': 'sh', 'Ṫ': 'Th', 'ṫ': 'th'
    }
    
    mapping_all_caps = {
        'Ḃ': 'BH', 'ḃ': 'bh', 'Ċ': 'CH', 'ċ': 'ch', 'Ḋ': 'DH', 'ḋ': 'dh',
        'Ḟ': 'FH', 'ḟ': 'fh', 'Ġ': 'GH', 'ġ': 'gh', 'Ṁ': 'MH', 'ṁ': 'mh',
        'Ṗ': 'PH', 'ṗ': 'ph', 'Ṡ': 'SH', 'ṡ': 'sh', 'Ṫ': 'TH', 'ṫ': 'th'
    }

    # Split into word and non-word segments so spacing and punctuation are perfectly preserved
    parts = re.split(r"([\W_]+)", text)
    processed_parts = []

    for part in parts:
        if not part:
            continue
            
        is_upper_word = part.isupper()
        current_mapping = mapping_all_caps if is_upper_word else mapping
        
        # 1. Handle precomposed characters first
        for old, new in current_mapping.items():
            part = part.replace(old, new)
            
        # 2. Handle 'Combining Dot Above' (U+0307)
        dot_above = '\u0307'
        if dot_above in unicodedata.normalize('NFD', part):
            normalized_part = unicodedata.normalize('NFD', part)
            chars = list(normalized_part)
            result = []
            
            for i, char in enumerate(chars):
                if char == dot_above:
                    if is_upper_word:
                        result.append('H')
                    elif i > 0 and chars[i-1].isupper():
                        # If not an all-caps word, uppercase dotted letter gets a lowercase 'h' 
                        # like 'Bh' unless we want it fully capitalized. 
                        # Since the word is not all caps, use 'h' to match 'Bh' standard.
                        result.append('h')
                    else:
                        result.append('h')
                else:
                    result.append(char)
            
            part = "".join(result)
            part = unicodedata.normalize('NFC', part)
            
        processed_parts.append(part)

    return "".join(processed_parts)

def main():
    parser = argparse.ArgumentParser(description="Convert Old Irish orthography to modern 'h' spelling")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("--output", help="Path to the output file (default: overwrite input)")
    
    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    modern_content = modernize_irish_text(content)

    output_path = args.output if args.output else args.input_file
    
    # Resolve to absolute path so the user knows exactly where it went
    abs_output_path = os.path.abspath(output_path)
    output_dir = os.path.dirname(abs_output_path)
    
    if output_dir:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created new directory: {output_dir}")
        
    with open(abs_output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(modern_content)
        
    print(f"Success! Output file written to: {abs_output_path}")

if __name__ == "__main__":
    main()