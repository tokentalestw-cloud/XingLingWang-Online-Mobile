"""List every catalogue row with effect text and literal runtime evidence."""
import argparse
import csv
import re
from pathlib import Path
from audit_cards import ROOT, read_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Destination CSV path")
    args = parser.parse_args()
    cards = read_json(ROOT / "data/cards.json")
    runtime = (ROOT / "static/game_v8.js").read_text(encoding="utf-8")
    literals = set(re.findall(r"""["']([^"'\r\n]{1,120})["']""", runtime))
    with args.output.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["卡號", "卡名", "種族", "卡文", "程式線索", "實戰驗證"])
        for card in cards:
            effect = (card.get("effect_text") or "").strip()
            evidence = "卡號" if card["id"] in literals else "卡名" if card["name"] in literals else "無精確字串"
            writer.writerow([card["id"], card["name"], card.get("faction"), effect, evidence, "待逐項驗證" if effect else "無效果文字，待核對"])
    print(f"Exported {len(cards)} catalogue rows.")


if __name__ == "__main__":
    main()
