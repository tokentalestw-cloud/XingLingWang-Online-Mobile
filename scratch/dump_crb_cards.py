# -*- coding: utf-8 -*-
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    cards = json.load(open('data/cards.json', encoding='utf-8'))
    crb_cards = [c for c in cards if c.get('faction') == '碳碳族' and c.get('deck_eligible', True)]
    
    with open('scratch/crb_cards_detail.txt', 'w', encoding='utf-8') as out:
        out.write(f"Count: {len(crb_cards)}\n\n")
        for c in crb_cards:
            out.write(f"ID: {c.get('id')} | Name: {c.get('name')} | Type: {c.get('type')} | Atk: {c.get('attack')} | Score: {c.get('score')} | Tribute: {c.get('tribute')} | Subtype: {c.get('art_subtype')}\n")
            out.write(f"Keywords: {c.get('keywords')}\n")
            out.write(f"Effect: {c.get('effect_text')}\n")
            out.write("-" * 50 + "\n")
    print(f"Dumped {len(crb_cards)} Carbon Tribe cards to scratch/crb_cards_detail.txt")

if __name__ == '__main__':
    main()
