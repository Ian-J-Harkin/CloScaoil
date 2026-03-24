import re

def test_regex():
    pattern = r"(?:^|(?<=\s))[7>](?=(?:\s|$))"
    
    test_cases = [
        "7 is at the start",
        "It ends with 7",
        "Isolated 7 in middle",
        "Multiple 7 7 here",
        "7", # Line with only 7
        "No shorthand here7", # Attached to word
        "Not7shorthand", # Middle of word
        "> start with arrow",
        "end with arrow >",
        "Isolated > here"
    ]
    
    for text in test_cases:
        matches = re.findall(pattern, text)
        print(f"Text: '{text}' | Matches: {matches}")

if __name__ == "__main__":
    test_regex()
