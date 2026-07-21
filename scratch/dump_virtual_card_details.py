import json
import sys

def main():
    with open('data/cards.json', 'r', encoding='utf-8') as f:
        cards = json.load(f)
        
    virtual_cards = []
    for c in cards:
        if c.get('deck') == '虛擬世界' or (c.get('id') and 'VIR' in c.get('id')):
            virtual_cards.append(c)
            
    with open('scratch/virtual_card_details.txt', 'w', encoding='utf-8') as out:
        out.write(f"Total Virtual World cards: {len(virtual_cards)}\n")
        for c in sorted(virtual_cards, key=lambda x: x.get('id') or ''):
            out.write(f"ID: {c.get('id')} | Name: {c.get('name')} | Type: {c.get('type')}\n")
            out.write(f"Effect: {c.get('effect_text')}\n")
            out.write("-" * 50 + "\n")

if __name__ == '__main__':
    main()
