import os
import sys

def main():
    file_path = "static/game_v8.js"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. toggleTributeSelection
    tribute_old = """  const isGraffiti = card && (card.id === "R-ART-0046" || card.name?.includes("牆壁上的塗鴉"));
  if (isGraffiti && !isPigmentCard(c)) {
    setStatus("【獻祭失敗】牆壁上的塗鴉 只能使用顏料單位作為祭品！");
    return;
  }"""
    tribute_new = """  const isGraffiti = card && (card.id === "R-ART-0046" || card.name?.includes("牆壁上的塗鴉"));
  if (isGraffiti && !isPigmentCard(c)) {
    setStatus("【獻祭失敗】牆壁上的塗鴉 只能使用顏料單位作為祭品！");
    return;
  }

  // 特殊旅人預組 - SPT-0013 黃金旅人
  const isGoldenTraveler = card && (card.id === "SPT-0013" || card.name?.includes("黃金旅人"));
  if (isGoldenTraveler && !(c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人"))) {
    setStatus("【獻祭失敗】黃金旅人的祭品必須為小旅人！");
    return;
  }"""
    if tribute_old in content:
        content = content.replace(tribute_old, tribute_new)
        print("toggleTributeSelection updated.")
    else:
        print("FAILED toggleTributeSelection")

    # 2. getUnitAtk
    atk_old = """  // 特殊旅人預組 - SPT-0001 金白蘭旅人 (每有1個其他旅人，攻擊力+1)
  if (c.id === "SPT-0001" || c.name?.includes("金白蘭旅人")) {
      let travelerCount = 0;
      const isPlayer = zone && zone.startsWith("player_");
      const sidePrefix = isPlayer ? "player_" : "enemy_";
      for (const z of [sidePrefix + "front", sidePrefix + "back"]) {
          field[z].forEach((u, i) => {
              if (u && (z !== zone || i !== lane) && (u.card.id === "TOKEN_TRAVELER" || u.card.name?.includes("旅人") || u.card.name?.includes("小旅人"))) {
                  travelerCount++;
              }
          });
      }
      baseAtk += travelerCount;
  }"""
    atk_new = """  // 檢查 SPT-0001 (金白蘭旅人) 與 SPT-0016 (派對旅人) 的 Buff 效果
  if (c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人")) {
      // SPT-0001 金白蘭旅人: 同排小旅人 +1
      if (zone && field[zone]) {
          const hasGolden = field[zone].some((u, i) => u && i !== lane && (u.card.id === "SPT-0001" || u.card.name?.includes("金白蘭旅人")) && !window.isUnitSilenced(u, zone, i));
          if (hasGolden) {
              baseAtk += 1;
          }
      }
      
      // SPT-0016 派對旅人: 左右邊的小旅人 +1
      if (zone && field[zone] && lane !== undefined) {
          let hasPartyAdjacent = false;
          if (lane > 0) {
              const uLeft = field[zone][lane - 1];
              if (uLeft && (uLeft.card.id === "SPT-0016" || uLeft.card.name?.includes("派對旅人")) && !window.isUnitSilenced(uLeft, zone, lane - 1)) {
                  hasPartyAdjacent = true;
              }
          }
          if (lane < 4) {
              const uRight = field[zone][lane + 1];
              if (uRight && (uRight.card.id === "SPT-0016" || uRight.card.name?.includes("派對旅人")) && !window.isUnitSilenced(uRight, zone, lane + 1)) {
                  hasPartyAdjacent = true;
              }
          }
          if (hasPartyAdjacent) {
              baseAtk += 1;
          }
      }
  }"""
    if atk_old in content:
        content = content.replace(atk_old, atk_new)
        print("getUnitAtk updated.")
    else:
        print("FAILED getUnitAtk")

    # 3. getUnitStars
    stars_old = """  // 特殊旅人預組 - SPT-0016 派對旅人 (每有1個其他小旅人，星數+1)
  if (c.id === "SPT-0016" || c.name?.includes("派對旅人")) {
      let travelerCount = 0;
      const isPlayer = zone && zone.startsWith("player_");
      const sidePrefix = isPlayer ? "player_" : "enemy_";
      for (const z of [sidePrefix + "front", sidePrefix + "back"]) {
          field[z].forEach((u, i) => {
              if (u && (z !== zone || i !== lane) && (u.card.id === "TOKEN_TRAVELER" || u.card.name?.includes("小旅人"))) {
                  travelerCount++;
              }
          });
      }
      baseStars += travelerCount;
  }"""
    stars_new = """  // 檢查 SPT-0001 (金白蘭旅人) 與 SPT-0016 (派對旅人) 的 Buff 效果
  if (c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人")) {
      // SPT-0001 金白蘭旅人: 同排小旅人 +1
      if (zone && field[zone]) {
          const hasGolden = field[zone].some((u, i) => u && i !== lane && (u.card.id === "SPT-0001" || u.card.name?.includes("金白蘭旅人")) && !window.isUnitSilenced(u, zone, i));
          if (hasGolden) {
              baseStars += 1;
          }
      }
      
      // SPT-0016 派對旅人: 左右邊的小旅人 +1
      if (zone && field[zone] && lane !== undefined) {
          let hasPartyAdjacent = false;
          if (lane > 0) {
              const uLeft = field[zone][lane - 1];
              if (uLeft && (uLeft.card.id === "SPT-0016" || uLeft.card.name?.includes("派對旅人")) && !window.isUnitSilenced(uLeft, zone, lane - 1)) {
                  hasPartyAdjacent = true;
              }
          }
          if (lane < 4) {
              const uRight = field[zone][lane + 1];
              if (uRight && (uRight.card.id === "SPT-0016" || uRight.card.name?.includes("派對旅人")) && !window.isUnitSilenced(uRight, zone, lane + 1)) {
                  hasPartyAdjacent = true;
              }
          }
          if (hasPartyAdjacent) {
              baseStars += 1;
          }
      }
  }"""
    if stars_old in content:
        content = content.replace(stars_old, stars_new)
        print("getUnitStars updated.")
    else:
        print("FAILED getUnitStars")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
