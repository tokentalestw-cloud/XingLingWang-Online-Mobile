# -*- coding: utf-8 -*-
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    data = json.load(open('data/decks.json', encoding='utf-8'))
    print("Type of data:", type(data))
    if isinstance(data, dict):
        for k, v in data.items():
            print(f"Deck key: {k} | Type of val: {type(v)}")
            if isinstance(v, list):
                matches = [c for c in v if '005' in c or '0052' in c or '0051' in c]
                if matches:
                    print(f"  Matches: {matches}")
            elif isinstance(v, dict):
                cards = v.get('cards', [])
                matches = [c for c in cards if '005' in c or '0052' in c or '0051' in c]
                if matches:
                    print(f"  Matches: {matches}")
    elif isinstance(data, list):
        for item in data:
            print("Item:", item)

if __name__ == '__main__':
    main()
