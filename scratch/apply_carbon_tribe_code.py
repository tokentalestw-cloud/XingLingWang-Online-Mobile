# -*- coding: utf-8 -*-
import sys

def apply_code():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = 'static/game_v8.js'
    content = open(filepath, encoding='utf-8').read()

    # Add Green Consumer Little Traveler return hook if not present
    if "greenConsumerCheck" not in content:
        hook = """
// 綠色消費人 (CRB-0011): 每當你的小旅人回森林時, 獎勵+1 (一回合限一次）
window.xlwCheckGreenConsumerReward = function(isPlayer) {
  const key = isPlayer ? "XLW_greenConsumerTriggeredPlayer" : "XLW_greenConsumerTriggeredEnemy";
  if (window[key]) return;
  const zones = isPlayer ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
  const hasConsumer = zones.some(z => field[z].some(u => u && u.card && (u.card.id === "CRB-0011" || u.card.name?.includes("綠色消費人"))));
  if (hasConsumer) {
    window[key] = true;
    if (isPlayer) playerBonusScore += 1; else enemyBonusScore += 1;
    logBattle(`✨ 綠色消費人 效果：小旅人返回森林，獎勵 +1 分！`);
  }
};
"""
        content = content.replace("window.isTransportUnit =", hook + "\nwindow.isTransportUnit =")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added Carbon Tribe runtime hooks to static/game_v8.js")

if __name__ == '__main__':
    apply_code()
