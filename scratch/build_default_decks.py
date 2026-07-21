import json
from pathlib import Path

# Load card DB
cards_path = Path("data/cards.json")
with open(cards_path, "r", encoding="utf-8") as f:
    cards = json.load(f)

# Factions mapping
# VLG: 妖怪村莊
# CAT: 喵喵賊
# ART: 藝術品
# ORC: 獸人
# VIR: 虛擬世界
# NEU: 中立

# Filter function
def get_faction_main_cards(faction_name):
    # Faction cards (not extra deck)
    return [
        c for c in cards 
        if (c.get("faction") == faction_name or c.get("race") == faction_name)
        and not (c.get("is_extra_deck") or c.get("deck_eligible") == False)
    ]

def get_neutral_main_cards():
    return [
        c for c in cards 
        if (c.get("faction") == "中立" or c.get("race") == "中立" or c.get("deck") == "中立" or c.get("deck") == "中立單位" or c.get("faction") == "中立單位" or str(c.get("id")).upper().startswith("NEU-"))
        and not (c.get("is_extra_deck") or c.get("deck_eligible") == False)
    ]

# We will read existing decks first to preserve them
decks_path = Path("data/decks.json")
with open(decks_path, "r", encoding="utf-8") as f:
    decks_data = json.load(f)

# Let's write a builder helper
def build_deck(faction_name, suffix, select_range):
    faction_main = get_faction_main_cards(faction_name)
    neutral_main = get_neutral_main_cards()
    
    # Let's sort faction main cards by ID to be deterministic
    faction_main.sort(key=lambda x: x.get("id", ""))
    neutral_main.sort(key=lambda x: x.get("id", ""))
    
    # Choose select_range from faction_main
    chosen_cards = faction_main[select_range[0]:select_range[1]]
    
    # Fill remaining from neutral_main if needed, or more faction main
    if len(chosen_cards) < 20:
        needed = 20 - len(chosen_cards)
        chosen_cards += neutral_main[:needed]
        
    # Check total mana
    total_mana = sum(int(c.get("mana") or 0) for c in chosen_cards)
    
    # If total mana > 15, let's swap high mana cards with 0 mana neutral cards
    if total_mana > 15:
        # Sort chosen_cards by mana descending
        chosen_cards.sort(key=lambda x: int(x.get("mana") or 0), reverse=True)
        # Find 0 mana neutral cards
        zero_neutrals = [n for n in neutral_main if int(n.get("mana") or 0) == 0 and n not in chosen_cards]
        
        while total_mana > 15 and zero_neutrals:
            # Replace the highest mana card
            replaced = chosen_cards.pop(0)
            added = zero_neutrals.pop(0)
            chosen_cards.append(added)
            total_mana = sum(int(c.get("mana") or 0) for c in chosen_cards)
            
    # Verify again
    assert len(chosen_cards) == 20, f"Deck {faction_name}_{suffix} has {len(chosen_cards)} cards instead of 20"
    assert total_mana <= 15, f"Deck {faction_name}_{suffix} has total mana {total_mana} which is > 15"
    
    card_ids = [c["id"] for c in chosen_cards]
    deck_key = faction_name if suffix == "standard" else f"{faction_name}_{suffix}"
    
    # Print selection info
    print(f"Deck: {deck_key} | Cards: {len(card_ids)} | Mana Sum: {total_mana}")
    return deck_key, card_ids

# Build the new decks
# 1. 喵喵賊_神速
k1, v1 = build_deck("喵喵賊", "神速", (20, 35))
decks_data[k1] = v1
decks_data[k1 + "_extra"] = ["R-CAT-0046", "SR-CAT-0047", "R-CAT-0048"]

# 2. 妖怪村莊_怨念
k2, v2 = build_deck("妖怪村莊", "怨念", (20, 35))
decks_data[k2] = v2
decks_data[k2 + "_extra"] = ["SR-VLG-0049"]

# 3. 藝術品_珍藏
k3, v3 = build_deck("藝術品", "珍藏", (20, 35))
decks_data[k3] = v3
decks_data[k3 + "_extra"] = ["C-ART-0060", "C-ART-0060", "C-ART-0060", "C-ART-0060", "C-ART-0060"]

# 4. 獸人_狂戰
k4, v4 = build_deck("獸人", "狂戰", (20, 35))
decks_data[k4] = v4
decks_data[k4 + "_extra"] = ["R-ORC-0054", "R-ORC-0054", "R-ORC-0054", "SSSR-NMS-0064", "SSSR-NMS-0064", "SSSR-NMS-0064"]

# 5. 虛擬世界 (Since it had no default deck)
k5, v5 = build_deck("虛擬世界", "standard", (0, 20))
decks_data[k5] = v5
decks_data[k5 + "_extra"] = []

# 6. 虛擬世界_幻影
k6, v6 = build_deck("虛擬世界", "幻影", (20, 40))
decks_data[k6] = v6
decks_data[k6 + "_extra"] = []

# Save back to decks.json
with open(decks_path, "w", encoding="utf-8") as f:
    json.dump(decks_data, f, ensure_ascii=False, indent=2)

# Also sync to static/decks.json
static_path = Path("static/decks.json")
with open(static_path, "w", encoding="utf-8") as f:
    json.dump(decks_data, f, ensure_ascii=False, indent=2)

print("Saved successfully!")
