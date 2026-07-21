# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    content = open(filepath, encoding="utf-8").read()
    
    content_norm = content.replace("\r\n", "\n")
    
    target = """  // R-FMS-0005 臭豆腐屍 正前方攻擊降低 2
  if (zone && idx !== undefined && idx >= 0) {
    const sidePrefix = zone.startsWith("player_") ? "player_" : "enemy_";
    const oppPrefix = zone.startsWith("player_") ? "enemy_" : "player_";
    let oppStinky = false;
    
    // Check direct opposite row
    const oppositeRow = zone.includes("front") ? "front" : "back";
    const oppUnit = field[oppPrefix + oppositeRow][idx];
    if (oppUnit && oppUnit.card && (oppUnit.card.id === "R-FMS-0005" || oppUnit.card.name?.includes("臭豆腐屍")) && !window.isUnitSilenced(oppUnit, oppPrefix + oppositeRow, idx)) {
      oppStinky = true;
    }
    
    if (oppStinky) {
      baseAtk = Math.max(0, baseAtk - 2);
    }
  }"""

    replacement = """  // R-FMS-0005 臭豆腐屍 正前方攻擊降低 2
  if (zone && lane !== undefined && lane >= 0) {
    const sidePrefix = zone.startsWith("player_") ? "player_" : "enemy_";
    const oppPrefix = zone.startsWith("player_") ? "enemy_" : "player_";
    let oppStinky = false;
    
    // Check direct opposite row
    const oppositeRow = zone.includes("front") ? "front" : "back";
    const oppUnit = field[oppPrefix + oppositeRow][lane];
    if (oppUnit && oppUnit.card && (oppUnit.card.id === "R-FMS-0005" || oppUnit.card.name?.includes("臭豆腐屍")) && !window.isUnitSilenced(oppUnit, oppPrefix + oppositeRow, lane)) {
      oppStinky = true;
    }
    
    if (oppStinky) {
      baseAtk = Math.max(0, baseAtk - 2);
    }
  }"""

    if target in content_norm:
        content_norm = content_norm.replace(target, replacement)
        open(filepath, "w", encoding="utf-8").write(content_norm)
        print("Fixed stinky lane parameter successfully.")
    else:
        print("Target not found.")

if __name__ == '__main__':
    main()
