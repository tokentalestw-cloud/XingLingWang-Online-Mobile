# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    content = open(filepath, encoding="utf-8").read()
    
    target = """      // SR-FMS-0036 麻祖 AI 限制檢查
      if (card.id === "SR-FMS-0036" || card.name?.includes("麻祖")) {
        const oppExile = enemyExileZone || [];
        const hasHu = oppExile.some(c => c && (c.id === "SR-FMS-0016" || c.id === "R-FMS-0017" || c.name?.includes("大三元") || c.name?.includes("小四喜")));
        if (!hasHu) okToSummon = false;
      }
        const oppGrave = window.XLW_ENEMY.grave || [];
        const catCount = oppGrave.filter(c => c && (c.deck === "喵喵賊" || c.faction === "喵喵賊" || c.id?.includes("CAT") || c.id?.includes("cat"))).length;
        if (catCount < 3) okToSummon = false;
      }"""

    replacement = """      // SR-FMS-0036 麻祖 AI 限制檢查
      if (card.id === "SR-FMS-0036" || card.name?.includes("麻祖")) {
        const oppExile = enemyExileZone || [];
        const hasHu = oppExile.some(c => c && (c.id === "SR-FMS-0016" || c.id === "R-FMS-0017" || c.name?.includes("大三元") || c.name?.includes("小四喜")));
        if (!hasHu) okToSummon = false;
      }"""

    if target in content:
        content = content.replace(target, replacement)
        open(filepath, "w", encoding="utf-8").write(content)
        print("Cleanup successful.")
    else:
        print("Target not found. Let's inspect raw lines.")

if __name__ == '__main__':
    main()
