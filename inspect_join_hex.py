with open('old-orthography/manannan03.md', 'rb') as f:
    content = f.read()
    # Find "roimis."
    # Note: roimis. in UTF-8 is 'roimis' + \x2e
    search = 'roimis.'.encode('utf-8')
    idx = content.find(search)
    if idx != -1:
        # Print next 20 bytes
        print(f"Index: {idx}")
        print(f"Bytes: {content[idx:idx+30]}")
        print(f"Hex: {[hex(b) for b in content[idx:idx+30]]}")
    else:
        print("Not found")
