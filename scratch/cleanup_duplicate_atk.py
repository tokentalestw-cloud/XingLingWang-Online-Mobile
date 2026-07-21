# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    content = open(filepath, encoding="utf-8").read()
    
    # We target the second copy of the block starting with R-ORC-0007 鐵獸人 and ending with 有打有嘉獎! (ORC-0020) Buff
    target = """  // R-ORC-0007 鐵獸人
  if ((c.id === "R-ORC-0007" || c.name?.includes("鐵獸人")) && isBeingAttacked) {
    baseAtk += 2;
  }
  // R-FMS-0005 臭豆腐屍 正前方攻擊降低 2
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
  }
  // R-ORC-0033 阿庫瑪的戰錘
  if (unit.equipments && unit.equipments.some(eq => eq.includes("戰錘") || eq.includes("阿庫瑪的戰錘"))) {
    baseAtk += 1;
  }
  // 彩虹幻象喵 (R-CAT-0030) Buff
  if (unit.attacking) {
    const sideIsPlayer = zone && zone.startsWith("player_");
    if (sideIsPlayer && window.XLW_rainbowCatAtkBuffActive) {
      baseAtk += 1;
    } else if (!sideIsPlayer && window.XLW_enemyRainbowCatAtkBuffActive) {
      baseAtk += 1;
    }
  }
  // R-ORC-0033 阿庫瑪的戰錘
  if (unit.equipments && unit.equipments.some(eq => eq.includes("戰錘") || eq.includes("阿庫瑪的戰錘"))) {
    baseAtk += 1;
  }
  // 彩虹幻象喵 (R-CAT-0030) Buff
  if (unit.attacking) {
    const sideIsPlayer = zone && zone.startsWith("player_");
    if (sideIsPlayer && window.XLW_rainbowCatAtkBuffActive) {
      baseAtk += 1;
    } else if (!sideIsPlayer && window.XLW_enemyRainbowCatAtkBuffActive) {
      baseAtk += 1;
    }
  }
  // SR-ORC-0062 戰爭巨象 艾勒粉
  if (c.id === "SR-ORC-0062" || c.name?.includes("艾勒粉") || c.name?.includes("戰爭巨象")) {
    const orcEquipCount = (unit.equipments || []).filter(eqName => {
      return ["帽", "菜刀", "狼牙棒", "弓", "牛排", "斧", "戰錘", "盾牌", "面具"].some(x => eqName.includes(x));
    }).length;
    baseAtk += orcEquipCount * 2;
  }
  // ORC-0002 背刺獸人
  if ((c.id === "ORC-0002" || c.name?.includes("背刺獸人")) && unit.attacking && unit.target) {
    const defUnit = field[unit.target.zone][unit.target.idx];
    if (defUnit && defUnit.tapped) {
      baseAtk += 3;
    }
  }
  // 有打有嘉獎! (ORC-0020) Buff
  const sideIsPlayer = zone && zone.startsWith("player_");
  if (c.faction === "獸人" || c.id?.includes("ORC")) {
    if ((sideIsPlayer && window.XLW_playerOrcAwardActiveUntil >= turn) || (!sideIsPlayer && window.XLW_enemyOrcAwardActiveUntil >= turn)) {
      baseAtk += 1;
    }
  }"""

    # We want to replace only the SECOND occurrence of this block, or we can replace it with empty string
    # Let's count occurrences
    occ = content.count(target)
    if occ >= 2:
        # Replace only the second one by splitting or using replace with count=1 from the right
        parts = content.rsplit(target, 1)
        content = "".join(parts)
        open(filepath, "w", encoding="utf-8").write(content)
        print("Successfully removed second duplicate block.")
    elif occ == 1:
        # If it occurs only once but has duplication inside it, let's see.
        # Actually, let's replace the single big target with just a single copy.
        # Wait, the target above already has duplicate "阿庫瑪的戰錘" and "彩虹幻象喵" blocks inside it!
        # Let's inspect the target.
        # In target:
        # "阿庫瑪的戰錘" is present twice!
        # "彩虹幻象喵" is present twice!
        # So we can clean up the duplication inside the first block too!
        cleaned_block = """  // R-ORC-0007 鐵獸人
  if ((c.id === "R-ORC-0007" || c.name?.includes("鐵獸人")) && isBeingAttacked) {
    baseAtk += 2;
  }
  // R-FMS-0005 臭豆腐屍 正前方攻擊降低 2
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
  }
  // R-ORC-0033 阿庫瑪的戰錘
  if (unit.equipments && unit.equipments.some(eq => eq.includes("戰錘") || eq.includes("阿庫瑪的戰錘"))) {
    baseAtk += 1;
  }
  // 彩虹幻象喵 (R-CAT-0030) Buff
  if (unit.attacking) {
    const sideIsPlayer = zone && zone.startsWith("player_");
    if (sideIsPlayer && window.XLW_rainbowCatAtkBuffActive) {
      baseAtk += 1;
    } else if (!sideIsPlayer && window.XLW_enemyRainbowCatAtkBuffActive) {
      baseAtk += 1;
    }
  }
  // SR-ORC-0062 戰爭巨象 艾勒粉
  if (c.id === "SR-ORC-0062" || c.name?.includes("艾勒粉") || c.name?.includes("戰爭巨象")) {
    const orcEquipCount = (unit.equipments || []).filter(eqName => {
      return ["帽", "菜刀", "狼牙棒", "弓", "牛排", "斧", "戰錘", "盾牌", "面具"].some(x => eqName.includes(x));
    }).length;
    baseAtk += orcEquipCount * 2;
  }
  // ORC-0002 背刺獸人
  if ((c.id === "ORC-0002" || c.name?.includes("背刺獸人")) && unit.attacking && unit.target) {
    const defUnit = field[unit.target.zone][unit.target.idx];
    if (defUnit && defUnit.tapped) {
      baseAtk += 3;
    }
  }
  // 有打有嘉獎! (ORC-0020) Buff
  const sideIsPlayer = zone && zone.startsWith("player_");
  if (c.faction === "獸人" || c.id?.includes("ORC")) {
    if ((sideIsPlayer && window.XLW_playerOrcAwardActiveUntil >= turn) || (!sideIsPlayer && window.XLW_enemyOrcAwardActiveUntil >= turn)) {
      baseAtk += 1;
    }
  }"""
        # We replace target with cleaned_block in the whole file
        content = content.replace(target, cleaned_block)
        open(filepath, "w", encoding="utf-8").write(content)
        print("Cleaned up duplicates within the single block.")
    else:
        print("Target block not found.")

if __name__ == '__main__':
    main()
