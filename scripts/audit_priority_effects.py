"""Track explicit effect reviews; code string matches never count as verification."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('type', 'faction', 'deck', 'effect_text', 'keywords', 'trigger_condition',
          'usable_phases', 'tribute', 'art_subtype', 'magic_type')


def signature(card):
    values = {key: card.get(key) for key in FIELDS}
    return hashlib.sha256(json.dumps(values, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def main():
    cards = json.loads((ROOT / 'data/cards.json').read_text(encoding='utf-8-sig'))
    plan = json.loads((ROOT / 'tests/priority_effect_reviews.json').read_text(encoding='utf-8'))
    reviews = {}
    for review in plan['reviews']:
        key = review['id']
        if key in reviews or not (ROOT / review['regression_file']).is_file():
            raise ValueError('Invalid or duplicate effect review: ' + key)
        reviews[key] = review
    for faction in plan['priority']:
        rows = [c for c in cards if (c.get('faction') or c.get('deck')) == faction and c.get('effect_text')]
        current = stale = 0
        for card in rows:
            review = reviews.get(card['id'])
            if review and review.get('verified'):
                if review['signature'] == signature(card):
                    current += 1
                else:
                    stale += 1
        print(f"優先種族覆核（此輪）：{faction} 已確認 {current}／{len(rows)}，卡文變更需重查 {stale}，其餘待核對。")


if __name__ == '__main__':
    main()
