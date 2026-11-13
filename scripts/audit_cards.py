"""Validate the card catalogue and report candidates for manual review."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ENERGY_MARKERS = {"STP-TOKEN001", "STP-TOKEN002"}
# Keywords with established shared runtime handlers. A text match elsewhere
# is only a review signal, since card-specific handlers and tags also exist.
SHARED_KEYWORDS = set("立即 獎勵 機械合體 偷襲 吞食合體 貫穿 獻祭 遠程攻擊 阻擋 橫放 禁錮 衰退 無法進攻 滑行 敵方魔法抗性 飛行 劇毒 上靶 開盤 合體 破壞抗性 敵方效果抗性 消逝 綁架 掩護 耗能 破甲 魔法抗性 升級 充能 灌溉".split())


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def scan(root):
    cards = read_json(root / "data/cards.json")
    decks = read_json(root / "data/decks.json")
    public_decks = read_json(root / "static/decks.json")
    source = (root / "static/game_v8.js").read_text(encoding="utf-8")
    errors, review = [], []
    duplicates = {}
    if not isinstance(cards, list) or not isinstance(decks, dict):
        raise ValueError("cards.json 須為陣列，decks.json 須為物件")
    ids = Counter(card.get("id") for card in cards if isinstance(card, dict) and isinstance(card.get("id"), str))
    errors.extend(f"卡號 {card_id} 在主卡庫出現 {count} 次" for card_id, count in sorted(ids.items()) if count > 1)
    for row, card in enumerate(cards, 1):
        if not isinstance(card, dict):
            errors.append(f"卡庫第 {row} 筆的格式錯誤")
            continue
        card_id = card.get("id")
        label = f"{card_id}（第 {row} 筆）"
        for field in ("id", "name", "image"):
            if not isinstance(card.get(field), str) or not card[field].strip():
                errors.append(f"{label} 缺少 {field}")
        if card_id not in ENERGY_MARKERS and card.get("type") not in ("unit", "magic"):
            errors.append(f"{label} 的 type 必須是 unit 或 magic")
        # Optional explicit references are checked exactly. Free-form card
        # text only yields candidates when it contains a printed card code.
        refs = card.get("effect_card_ids", [])
        if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
            errors.append(f"{label} 的 effect_card_ids 必須是卡號陣列")
        else:
            errors.extend(f"{label} 的效果引用未知卡號 {ref}" for ref in set(refs) - ids.keys())
        effect = card.get("effect_text")
        if isinstance(effect, str):
            for ref in set(re.findall(r"(?<![A-Z0-9-])(?:[A-Z]{1,5}-)?[A-Z]{3}-[0-9]{4}(?:-[A-Z0-9]+)?(?![A-Z0-9-])", effect)) - ids.keys():
                review.append(f"{label} 卡文提及未知卡號 {ref}")
        keywords = card.get("keywords") or []
        if not isinstance(keywords, list) or any(not isinstance(k, str) for k in keywords):
            errors.append(f"{label} 的 keywords 必須是文字陣列")
            continue
        # Avoid reporting faction tags or every occurrence of the same keyword.
        for keyword in {word.strip() for tag in keywords for word in re.split(r"[,，、]", tag)} & SHARED_KEYWORDS:
            if keyword not in source:
                review.append(f"{label} 找不到「{keyword}」的程式線索")
    for deck, card_ids in decks.items():
        if not isinstance(card_ids, list) or any(not isinstance(card_id, str) for card_id in card_ids):
            errors.append(f"{deck} 必須是卡號陣列")
            continue
        counts = Counter(card_ids)
        errors.extend(f"{deck} 引用未知卡號 {card_id}" for card_id in sorted(counts.keys() - ids.keys()))
        repeated = {card_id: count for card_id, count in counts.items() if count > 1}
        if repeated:
            duplicates[deck] = repeated
    if decks != public_decks:
        errors.append("data/decks.json 與 static/decks.json 的內容不一致")
    return len(cards), len(decks), errors, sorted(set(review)), duplicates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        cards, decks, errors, review, duplicates = scan(args.root)
        baseline = read_json(args.root / "data/deck_duplicate_baseline.json")
    except (OSError, ValueError, AttributeError, TypeError) as error:
        print(f"卡牌掃描失敗：{error}", file=sys.stderr)
        return 1
    for deck, repeated in duplicates.items():
        for card_id, count in repeated.items():
            message = f"{deck} 內的 {card_id} 出現 {count} 次"
            if count > baseline.get(deck, {}).get(card_id, 1):
                errors.append(message)
            else:
                review.append(message)
    print(f"已掃描 {cards} 張卡、{decks} 個牌組或牌區。錯誤 {len(errors)} 項，待核對 {len(review)} 項。")
    for message in sorted(errors):
        print(f"錯誤  {message}")
    for message in sorted(review):
        print(f"核對  {message}")
    return int(bool(errors))


if __name__ == "__main__":
    sys.exit(main())

