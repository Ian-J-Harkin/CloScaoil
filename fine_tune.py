import json
import sys
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Inject fine-tuning entries into the OCR corrections dictionary.")
    parser.add_argument('--file', type=str, help='Path to a JSON file containing fine-tune entries.')
    parser.add_argument('--json', type=str, help='Raw JSON string containing fine-tune entries (wrap in single quotes).')
    args = parser.parse_args()

    if not args.file and not args.json:
        print("Usage error: Please provide either --file <path> or --json '<json_string>'")
        sys.exit(1)

    # Standardize the config path
    config_path = os.path.join('config', 'corrections_dict.json')
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found. Please run this script from the 'caibidlí' directory.")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Parse user input
    try:
        if args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                entries = json.load(f)
        else:
            entries = json.loads(args.json)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON input: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)

    # Normalize to iterable list of entries
    if isinstance(entries, dict):
        # If the user passed a single JSON object instead of an array
        if "FineTuneEntry" not in entries:
            # Maybe the root itself is the {"Incorrect": ..., "Corrected": ...} dictionary?
            if "Incorrect" in entries and "Corrected" in entries:
                entries = [{"FineTuneEntry": entries}]
            else:
                entries = [entries]
        else:
            entries = [entries]

    added_verified = 0
    added_contextual = 0

    for idx, entry in enumerate(entries):
        # Allow shortcut format directly bypassing "FineTuneEntry" wrapping if desired
        if "FineTuneEntry" in entry:
            data = entry["FineTuneEntry"]
        else:
            data = entry
        
        incorrect = data.get("Incorrect")
        corrected = data.get("Corrected")
        
        if not incorrect or not corrected:
            print(f"Skipping entry {idx+1}: Invalid format (Missing 'Incorrect' or 'Corrected' keys).")
            continue

        # Smart classification: If the snippet contains spaces or explicit punctuation,
        # it is vastly safer to treat it as a contextual phrase rather than a 1-to-1 word swap.
        is_contextual = any(char in incorrect for char in [' ', '.', ',', ';', ':', '!', '?'])

        if is_contextual:
            contextual_rules = config['dictionary'].get('contextual', [])
            
            # Prevent duplicates
            if not any(r['pattern'] == incorrect for r in contextual_rules):
                contextual_rules.append({
                    "pattern": incorrect,
                    "replacement": corrected,
                    "reason": "User-added fine tuning phrase"
                })
                added_contextual += 1
            else:
                print(f"Skipping '{incorrect}': Already exists in contextual rules.")
                
            config['dictionary']['contextual'] = contextual_rules
        else:
            # Standard single-word entry
            verified_dict = config['dictionary'].get('verified', {})
            
            if incorrect not in verified_dict or verified_dict[incorrect] != corrected:
                verified_dict[incorrect] = corrected
                added_verified += 1
            else:
                print(f"Skipping '{incorrect}': Already exists in verified dictionary.")
            
            # Alphabetize dictionary for clean upkeep
            config['dictionary']['verified'] = dict(sorted(verified_dict.items()))

    # Save the updated configuration
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\nSuccess! Applied:")
    print(f"- {added_verified} single-word mapping(s) into 'verified'")
    print(f"- {added_contextual} phrase-level mapping(s) into 'contextual'")

if __name__ == "__main__":
    main()
