import sys

with open('old-orthography/manannan03.md', 'rb') as f:
    content = f.read()
    # Find "go "
    idx = content.find(b'go ')
    if idx != -1:
        # Print next few bytes
        print(content[idx:idx+10])
        print([hex(b) for b in content[idx:idx+10]])
