# -*- coding: utf-8 -*-
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    cards = json.load(open('data/cards.json', encoding='utf-8'))
    for c in cards:
        if c.get('deck') == '勇者公會':
            print(f"ID: {c.get('id')} | Name: {c.get('name')} | Subtype: {c.get('art_subtype')} | Effect: {c.get('effect_text')}")

if __name__ == '__main__':
    main()
