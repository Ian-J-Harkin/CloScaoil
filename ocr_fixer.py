import re
import json
import os
import argparse
import sys

class OCRFixer:
    def __init__(self, config_path):
        self.config_path = config_path
        self.data = self.load_config(config_path)
    
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
            # Use [^\S\r\n] to match horizontal whitespace ONLY (excludes \n, \r)
            # Remove loose spacing before punctuation: " word . " -> " word."
            text = re.sub(r'[^\S\r\n]+([?!.,:;])', r'\1', text)
            # Ensure single space after punctuation: "word.next" -> "word. next"
            text = re.sub(r'([?!.,:;])([^\S\r\n]+)', r'\1 ', text)
            
            # Remove space after opening quotes: “ Níl -> “Níl
            text = re.sub(r'([“"‘])[^\S\r\n]+', r'\1', text)
            # Remove space before closing quotes: seisean. ” -> seisean.”
            text = re.sub(r'[^\S\r\n]+([”"’])', r'\1', text)

            # Fix multiple horizontal spaces
            text = re.sub(r'[^\S\r\n]{2,}', ' ', text)
        
        return text

    def dehyphenate(self, text):
        # Regex: word boundary, word chars, hyphen, horizontal space, newline, optional horizontal space, word chars
        # Conservative: do not rejoin if first part is n, t, h (Irish prefixes)
        pattern = r'(\b\w+)-[^\S\r\n]*\n[^\S\r\n]*(\w+)'
        
        def repl(match):
            w1 = match.group(1)
            w2 = match.group(2)
            
            # Constraint: Do not rejoin if it is an Irish mutative prefix
            if w1.lower() in ('n', 't', 'h'):
                return f"{w1}-{w2}\n"
            
            # Otherwise assume it is an OCR split word
            print(f"INFO: De-hyphenating '{w1}-{w2}'", file=sys.stderr)
            return f"{w1}{w2}\n"

        return re.sub(pattern, repl, text, flags=re.MULTILINE)

    def apply_stray_caps_fix(self, text):
        # 1. Single letter capitals in the middle of sentences.
        def lower_single(match):
            return match.group(1) + match.group(2).lower()
        
        # Avoid lowering if preceded by sentence endings or quotes
        text = re.sub(r'([^.!?“”"’\n]\s+)([A-ZÁÉÍÓÚḂĊḊḞĠṀṖṠṪ])(?=[\s.,;!?“”"’]|$)', lower_single, text)
        
        # 2. Mixed case words that start with a lowercase letter.
        def lower_mixed(match):
            word = match.group(1)
            # Valid Irish mutative prefixes
            m = re.match(r'^(t|h|n|m|g|d|b|bh|mh|ts)([A-ZÁÉÍÓÚḂĊḊḞĠṀṖṠṪ])(.*)$', word)
            if m:
                return m.group(1) + m.group(2) + m.group(3).lower()
            else:
                return word.lower()
                
        # Find words starting with lowercase letter and containing an uppercase letter.
        text = re.sub(r'\b([a-záéíóúḃċḋḟġṁṗṡṫ]+[A-ZÁÉÍÓÚḂĊḊḞĠṀṖṠṪ][\w\'’]*)\b', lower_mixed, text)
        
        return text

    def apply_contextual_heuristics(self, line):
        for rule in self.data["dictionary"].get("contextual", []):
            pattern = rule["pattern"]
            replacement = rule["replacement"]
            
            if pattern in line:
                line = line.replace(pattern, replacement)
                print(f"INFO: Applied Contextual Fix: {rule['reason']}", file=sys.stderr)
        
        return line

    def find_last_page_number(self, current_file_path):
        """
        Scans back through previous chapters to find the last page marker.
        """
        # First check the current file (if it already has markers)
        if os.path.exists(current_file_path):
            with open(current_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r'\[l\.(\d+)\]: #', content)
                if matches:
                    return int(matches[-1])
        
        # Determine previous file
        match = re.search(r'manannan(\d+)', os.path.basename(current_file_path))
        if not match:
            return 30 # Default fallback if no context
        
        chapter_num = int(match.group(1))
        
        # Search backward from previous chapter
        for i in range(chapter_num - 1, 0, -1):
            file_name = f"manannan{i:02d}.md"
            dir_path = os.path.dirname(current_file_path)
            path = os.path.join(dir_path, file_name)
            
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = re.findall(r'\[l\.(\d+)\]: #', content)
                    if matches:
                        return int(matches[-1])
        
        return 30 # Fallback

    def is_page_header(self, line):
        text = line.strip()
        if not text: return False
        
        # Don't match if it's already a page marker
        if re.match(r'^\[l\.\d+\]: #', text): return False

        # Load patterns from JSON configuration: config['global_replacements']['page_header_patterns']
        global_replacements = self.data.get("global_replacements", {})
        patterns = global_replacements.get("page_header_patterns", [])
        
        # Heuristic: headers are short (usually < 40 chars)
        if len(text) > 40: return False

        for p in patterns:
            try:
                if re.match(p, text, re.IGNORECASE):
                    # Safety: Ensure it has key characters to avoid matching small dialogue lines
                    if "N" in text.upper() or "Á" in text.upper():
                        return True
            except re.error:
                continue
        return False

    def process_text(self, text, file_path=None):
        # Normalize line endings to \n for internal processing
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 0. Handle Page Header replacement
        page_counter = 0
        if file_path:
            page_counter = int(self.find_last_page_number(file_path))
        
        # 1. De-hyphenation
        text = self.dehyphenate(text)
        
        # 2. Global replacements
        text = self.apply_global_replacements(text)
        
        # 3. Fix stray capitals (using generalized rules)
        text = self.apply_stray_caps_fix(text)
        
        dictionary = self.data.get("dictionary", {})
        verified = dictionary.get("verified", {})
        ambiguous = dictionary.get("ambiguous", {})
        
        new_patterns = []
        raw_lines = text.split('\n')
        processed_lines = []
        
        for i, line in enumerate(raw_lines):
            # Preserve existing page markers or replace headers
            stripped = line.strip()
            if re.match(r'^\[l\.\d+\]: #', stripped):
                # Update counter if we hit an existing one
                m = re.match(r'^\[l\.(\d+)\]: #', stripped)
                if m:
                    page_counter = int(m.group(1))
                processed_lines.append(line)
                continue
            
            if self.is_page_header(line):
                page_counter += 1
                print(f"INFO: Replaced header '{line.strip()}' with [l.{page_counter}]", file=sys.stderr)
                processed_lines.append(f"[l.{page_counter}]: #")
                continue

            # We split by words but keep everything else
            # Include apostrophes in word boundaries for Irish words like d'ól or ṫei’lg
            parts = re.split(r"(\b[\w'’]+\b)", line)
            new_line_parts = []
            for part in parts:
                if re.match(r"^[\w'’]+$", part):
                    # Check verified
                    if part in verified:
                        new_line_parts.append(verified[part])
                    elif part in ambiguous:
                        new_patterns.append({
                            "word": part, 
                            "options": ambiguous[part], 
                            "context": line.strip(),
                            "line": i + 1,
                            "type": "ambiguous"
                        })
                        new_line_parts.append(part)
                    else:
                        # Potential new pattern (mixed case, etc.)
                        if re.search(r'[a-z][A-Z]|[A-Z][a-z][A-Z]|[:]', part):
                             new_patterns.append({
                                "word": part,
                                "context": line.strip(),
                                "line": i + 1,
                                "type": "potential_new"
                            })
                        new_line_parts.append(part)
                else:
                    new_line_parts.append(part)
            
            new_line = "".join(new_line_parts)
            
            # 4. Contextual Heuristics
            new_line = self.apply_contextual_heuristics(new_line)
            
            processed_lines.append(new_line)

        # Reconstruct with blank line before page markers
        final_output = []
        for i, line in enumerate(processed_lines):
            if re.match(r'^\[l\.\d+\]: #', line):
                if i > 0 and final_output and final_output[-1].strip() != "":
                    final_output.append("")
            # Avoid duplicating empty lines if they are already present
            final_output.append(line)
            
        return "\n".join(final_output), new_patterns

def main():
    parser = argparse.ArgumentParser(description="OCR Fixer for 1943 Cló Gaelach")
    parser.add_argument("input_file", help="Path to the input markdown file")
    parser.add_argument("--output", help="Path to the output markdown file (default: overwrite input)")
    parser.add_argument("--report", help="Path to the ambiguous matches report file")
    
    args = parser.parse_args()
    
    fixer = OCRFixer("config/corrections_dict.json")
    
    with open(args.input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    processed_content, new_patterns = fixer.process_text(content, file_path=args.input_file)
    
    output_path = args.output if args.output else args.input_file
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(processed_content)
    
    if new_patterns:
        report_json = json.dumps({"ambiguous_matches": new_patterns}, indent=2, ensure_ascii=False)
        if args.report:
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write(report_json)
        else:
            try:
                if hasattr(sys.stdout, 'reconfigure'):
                    sys.stdout.reconfigure(encoding='utf-8')
                print(report_json)
            except Exception:
                print(report_json.encode('utf-8', errors='replace').decode('utf-8'))

if __name__ == "__main__":
    main()