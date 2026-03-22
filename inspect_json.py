import json

with open('config/corrections_dict.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    for rule in data['dictionary'].get('contextual', []):
        pattern = rule['pattern']
        print(f"Pattern: {pattern}, Hex: {[hex(ord(c)) for c in pattern]}")
