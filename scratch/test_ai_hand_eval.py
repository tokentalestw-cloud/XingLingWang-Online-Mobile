# -*- coding: utf-8 -*-
import json, random, sys

def test_eval():
    sys.stdout.reconfigure(encoding='utf-8')
    cards = json.load(open('data/cards.json', encoding='utf-8'))
    decks = json.load(open('data/decks.json', encoding='utf-8'))
    card_map = {c['id']: c for c in cards}

    def get_deck_cards(dname):
        ids = decks.get(dname, [])
        return [card_map[i] for i in ids if i in card_map]

    for dname in ['妖怪村莊', '發電獸', '碳碳族', '藝術品', '喵喵賊', '獸人', '虛擬世界', '勇者公會', '歡樂島']:
        full_deck = get_deck_cards(dname)
        null_count = 0
        valid_count = 0
        
        for _ in range(100):
            deck_copy = list(full_deck)
            random.shuffle(deck_copy)
            hand = [deck_copy.pop() for _ in range(6) if deck_copy]
            
            # Evaluate units in hand
            candidates = []
            for h_idx, c in enumerate(hand):
                if not c or c.get('type') not in ['unit', '單位']:
                    continue
                effect_text = c.get('effect_text', '')
                if '只能通' in effect_text or '只能透過' in effect_text:
                    continue
                
                tribute = int(c.get('tribute', 0) or 0)
                atk = int(c.get('attack', 0) if str(c.get('attack', '')).isdigit() else 0)
                
                if tribute <= 0:
                    candidates.append((100 + atk, c))
            
            if not candidates:
                null_count += 1
            else:
                valid_count += 1
                
        print(f"Deck: {dname:8s} | Valid 0-tribute in 6-card hand: {valid_count}% | Hands with ONLY spells/tribute units: {null_count}%")

if __name__ == '__main__':
    test_eval()
