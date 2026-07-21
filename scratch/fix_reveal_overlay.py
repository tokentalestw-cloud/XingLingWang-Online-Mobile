# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    content = open(filepath, encoding="utf-8").read()
    content_norm = content.replace("\r\n", "\n")
    
    target = """window.xlwRevealCard = async function(card, isPlayer) {
  if (!card) return;
  logBattle(`✨ 展示卡牌：【${card.name}】（${isPlayer ? "我方" : "對手"}）`);"""

    replacement = """window.xlwShowRevealOverlay = function(card, side) {
  return new Promise((resolve) => {
    let overlay = document.getElementById("xlw-card-reveal-overlay");
    if (!overlay) {
      overlay = document.createElement("div");
      overlay.id = "xlw-card-reveal-overlay";
      overlay.className = "xlw-spell-activation-overlay";
      document.body.appendChild(overlay);
    }

    const isPlayer = side === "player" || side === "me" || side === "player_front" || side === "player_back";
    const titleText = isPlayer ? "🔮 我方展示牌庫卡牌！" : "🔮 對手展示牌庫卡牌！";
    const titleColor = isPlayer ? "#00ff7f" : "#ff4d4f";

    overlay.innerHTML = `
      <div class="xlw-spell-activation-title" style="color: ${titleColor};">${titleText}</div>
      <div class="xlw-spell-activation-card-box">
        <img class="xlw-spell-activation-card-img" src="${card.image || "/static/card_back.jpeg"}" alt="${card.name}">
        <div class="xlw-spell-activation-card-name">${card.name}</div>
        <div class="xlw-spell-activation-card-effect">${card.effect_text || ""}</div>
      </div>
    `;

    requestAnimationFrame(() => {
      overlay.classList.add("active");
    });

    setTimeout(() => {
      overlay.classList.remove("active");
      setTimeout(() => {
        resolve();
      }, 400);
    }, 1800);
  });
};

window.xlwRevealCard = async function(card, isPlayer) {
  if (!card) return;
  await window.xlwShowRevealOverlay(card, isPlayer ? "player" : "enemy");
  logBattle(`✨ 展示卡牌：【${card.name}】（${isPlayer ? "我方" : "對手"}）`);"""

    if target in content_norm:
        content_norm = content_norm.replace(target, replacement)
        open(filepath, "w", encoding="utf-8").write(content_norm)
        print("Success: Added visual reveal overlay.")
    else:
        print("Error: Target not found in game_v8.js!")

if __name__ == '__main__':
    main()
