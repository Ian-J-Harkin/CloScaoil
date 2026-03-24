import re
import json
import os
import argparse
import sys

class OCRFixer:
    VERSION = "2.0-CLÓSCAOIL"

    def __init__(self, config_path):
        self.config_path = config_path
        self.data = self.load_config(config_path)
        print(f"INFO: Initializing OCRFixer {self.VERSION}", file=sys.stderr)
    
    def load_config(self, path):
        if not os.path.exists(path):
            return {"global_replacements": {}, "dictionary": {"verified": {}, "ambiguous": {}, "contextual": []}}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def apply_global_replacements(self, text):
        global_replacements = self.data.get("global_replacements", {})
        chars = global_replacements.get("chars", {})
        for old, new in chars.items():
            text = text.replace(old, new)
        
        if global_replacements.get("punctuation_spacing"):
            text = re.sub(r'[^\S\r\n]+([?!.,:;])', r'\1', text)
            text = re.sub(r'([?!.,:;])(?=\w)', r'\1 ', text)
            text = re.sub(r'([“"‘])[^\S\r\n]+', r'\1', text)
            text = re.sub(r'[^\S\r\n]+([”"’])', r'\1', text)
            text = re.sub(r'[^\S\r\n]{2,}', ' ', text)
        
        return text

    def dehyphenate(self, text):
        pattern = r'(\b\w+)-[^\S\r\n]*\n[^\S\r\n]*(\w+)'
        def repl(match):
            w1 = match.group(1)
            w2 = match.group(2)
            if w1.lower() in ('n', 't', 'h'):
                return f"{w1}-{w2}\n"
            return f"{w1}{w2}\n"
        return re.sub(pattern, repl, text, flags=re.MULTILINE)

    def apply_stray_caps_fix(self, text):
        def lower_single(match):
            return match.group(1) + match.group(2).lower()
        text = re.sub(r'([^.!?“”"’\n]\s+)([A-ZÁÉÍÓÚḂĊḊḞĠṀṖṠṪ])(?=[\s.,;!?“”"’]|$)', lower_single, text)
        
        def lower_mixed(match):
            word = match.group(1)
            m = re.match(r'^(t|h|n|m|g|d|b|bh|mh|ts)([A-ZÁÉÍÓÚḂĊḊḞĠṀṖṠṪ])(.*)$', word)
            if m:
                return m.group(1) + m.group(2) + m.group(3).lower()
            else:
                return word.lower()
        text = re.sub(r'\b([a-záéíóúḃċḋḟġṁṗṡṫ]+[A-ZÁÉÍÓÚḂĊḊḞĠṀṖṠṪ][\w\'’]*)\b', lower_mixed, text)
        return text

    def apply_contextual_heuristics(self, line):
        for rule in self.data["dictionary"].get("contextual", []):
            pattern = rule["pattern"]
            replacement = rule["replacement"]
            if pattern in line:
                line = line.replace(pattern, replacement)
        return line

    def find_last_page_number(self, current_file_path):
        if os.path.exists(current_file_path):
            with open(current_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r'\[l\.(\d+)\]: #', content)
                if matches:
                    return int(matches[-1])
        match = re.search(r'manannan(\d+)', os.path.basename(current_file_path))
        if not match: return 30
        chapter_num = int(match.group(1))
        for i in range(chapter_num - 1, 0, -1):
            file_name = f"manannan{i:02d}.md"
            path = os.path.join(os.path.dirname(current_file_path), file_name)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = re.findall(r'\[l\.(\d+)\]: #', content)
                    if matches: return int(matches[-1])
        return 30

    def is_page_header(self, line):
        text = line.strip()
        if not text or re.match(r'^\[l\.\d+\]: #', text): return False
        patterns = self.data.get("global_replacements", {}).get("page_header_patterns", [])
        if len(text) > 40: return False
        for p in patterns:
            try:
                if re.match(p, text, re.IGNORECASE):
                    if "N" in text.upper() or "Á" in text.upper(): return True
            except re.error: continue
        return False

    def apply_visual_heuristics(self, text: str) -> str:
        """FALLBACK ONLY: Restores lenited consonants misidentified as noise."""
        lenition_map = {
            'b': 'ḃ', 'c': 'ċ', 'd': 'ḋ', 'f': 'ḟ', 'g': 'ġ', 
            'm': 'ṁ', 'p': 'ṗ', 's': 'ṡ', 't': 'ṫ',
            'B': 'Ḃ', 'C': 'Ċ', 'D': 'Ḋ', 'F': 'Ḟ', 'G': 'Ġ', 
            'M': 'Ṁ', 'P': 'Ṗ', 'S': 'Ṡ', 'T': 'Ṫ'
        }
        def replace_func(match):
            char = match.group(1)
            return lenition_map.get(char, match.group(0))
        pattern = r"([bcdfgmpstBCDFGMPST])['\.,`\*·]"
        return re.sub(pattern, replace_func, text)

    def normalize_shorthand(self, text: str, expand: bool = False) -> str:
        """Target 7 or > when isolated by whitespace."""
        pattern = r"(?<=\s)[7>](?=\s)"
        replacement = "agus" if expand else "\u204a"
        return re.sub(pattern, replacement, text)

    def check_vowel_harmony(self, word: str) -> bool:
        """Linguistic Validator: Checks 'Caol le Caol'."""
        if len(word) <= 3: return True
        broad, slender = "aoúáóu", "eíéi"
        pattern_violation = rf"([{broad}][^aeiouáéíóú]+[{slender}])|([{slender}][^aeiouáéíóú]+[{broad}])"
        return not re.search(pattern_violation, word, re.IGNORECASE)

    def process_text(self, text, file_path=None, expand_abbreviations=False, strict_mode=False):
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        page_counter = int(self.find_last_page_number(file_path)) if file_path else 0
        text = self.dehyphenate(text)
        text = self.apply_global_replacements(text)
        text = self.apply_stray_caps_fix(text)
        
        dictionary = self.data.get("dictionary", {})
        verified = dictionary.get("verified", {})
        ambiguous = dictionary.get("ambiguous", {})
        
        new_patterns = []
        processed_lines = []
        
        for i, line in enumerate(text.split('\n')):
            if re.match(r'^\[l\.\d+\]: #', line.strip()):
                m = re.match(r'^\[l\.(\d+)\]: #', line.strip())
                if m: page_counter = int(m.group(1))
                processed_lines.append(line)
                continue
            
            if self.is_page_header(line):
                page_counter += 1
                processed_lines.append(f"[l.{page_counter}]: #")
                continue

            parts = re.split(r"(\b[\w'’7>]+\b)", line)
            new_line_parts = []
            for part in parts:
                if re.match(r"^[\w'’7>]+$", part):
                    if part in verified:
                        new_line_parts.append(verified[part])
                        continue
                    if part in ambiguous:
                        new_patterns.append({"word": part, "options": ambiguous[part], "context": line.strip(), "line": i+1, "type": "ambiguous"})
                        new_line_parts.append(part)
                        continue
                    
                    # Hierarchy 2-4
                    processed = self.normalize_shorthand(f" {part} ", expand=expand_abbreviations).strip()
                    if processed == part:
                        processed = self.apply_visual_heuristics(part)
                    
                    if not self.check_vowel_harmony(processed):
                        new_patterns.append({"word": f"⚠️{processed}", "context": line.strip(), "line": i+1, "type": "harmony_violation"})
                        if strict_mode: processed = f"=={processed}=="
                    
                    new_line_parts.append(processed)
                else:
                    new_line_parts.append(part)
            
            processed_lines.append(self.apply_contextual_heuristics("".join(new_line_parts)))

        final_output = []
        for i, line in enumerate(processed_lines):
            if re.match(r'^\[l\.\d+\]: #', line) and i > 0 and final_output and final_output[-1].strip() != "":
                final_output.append("")
            final_output.append(line)
            
        return "\n".join(final_output), new_patterns

def main():
    parser = argparse.ArgumentParser(description="OCR Fixer for 1943 Cló Gaelach")
    parser.add_argument("input_file", help="Path to input markdown file")
    parser.add_argument("--output", help="Path to output markdown file")
    parser.add_argument("--report", help="Path to ambiguous matches report")
    parser.add_argument("--expand-abbreviations", action="store_true", help="Expand 7 to 'agus'")
    parser.add_argument("--strict", action="store_true", help="Enable strict highlighting")
    args = parser.parse_args()
    
    fixer = OCRFixer("config/corrections_dict.json")
    if not os.path.exists(args.input_file):
        print(f"ERROR: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    with open(args.input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    processed_content, new_patterns = fixer.process_text(content, file_path=args.input_file, 
                                                       expand_abbreviations=args.expand_abbreviations, 
                                                       strict_mode=args.strict)
    
    output_path = args.output if args.output else args.input_file
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(processed_content)
    
    if new_patterns:
        report = json.dumps({"ambiguous_matches": new_patterns}, indent=2, ensure_ascii=False)
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f: f.write(report)
        else:
            try:
                if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
                print(report)
            except Exception:
                print(report.encode('utf-8', errors='replace').decode('utf-8'))

if __name__ == "__main__":
    main()
