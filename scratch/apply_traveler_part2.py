import codecs

def inject_part2():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # R-SPT-0008
    r_spt_0008_code = '''window.xlwResolveTurnStartEffects = async function(isPlayerSide) {
const prefix = isPlayerSide ? "player_" : "enemy_";
// 特殊旅人預組 - R-SPT-0008 旅店常客 (主要階段開始，召喚 1 個小旅人)
for (const z of [prefix + "front", prefix + "back"]) {
  for (let i = 0; i < 5; i++) {
    const u = field[z][i];
    if (u && u.card && (u.card.id === "R-SPT-0008" || u.card.name?.includes("旅店常客")) && !window.isUnitSilenced(u, z, i)) {
      logBattle(`✨ ${isPlayerSide ? "我方" : "對手"} 旅店常客 效果觸發：主要階段開始，召喚 1 個小旅人！`);
      await promptAndSummonTraveler(isPlayerSide ? "player" : "enemy", 1, "旅店常客");
    }
  }
}
'''
    if 'R-SPT-0008' not in content[content.find('window.xlwResolveTurnStartEffects'):content.find('window.xlwResolveTurnStartEffects')+1000]:
        content = content.replace('window.xlwResolveTurnStartEffects = async function(isPlayerSide) {\nconst prefix = isPlayerSide ? "player_" : "enemy_";', r_spt_0008_code)
    
    # R-SPT-0014
    r_spt_0014_code = '''function isMagicImmune(unit, zone, idx) {
  if (!unit || !unit.card) return false;
  const c = unit.card;
  // 特殊旅人預組 - R-SPT-0014 魔法旅人 (小旅人獲得魔法抗性)
  if (c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人")) {
    const side = zone.startsWith("player_") ? "player_" : "enemy_";
    const hasMagicTraveler = field[side + "front"].concat(field[side + "back"]).some(u => u && u.card && (u.card.id === "R-SPT-0014" || u.card.name?.includes("魔法旅人")) && !window.isUnitSilenced(u, side, field[side+"front"].includes(u)?field[side+"front"].indexOf(u):field[side+"back"].indexOf(u)));
    if (hasMagicTraveler) return true;
  }
'''
    if 'R-SPT-0014' not in content[content.find('function isMagicImmune'):content.find('function isMagicImmune')+1000]:
        content = content.replace('function isMagicImmune(unit, zone, idx) {', r_spt_0014_code)
    
    # SPT-0013
    spt_0013_code = '''  // 不可獻祭判定
  const c = unit.card || unit;
  
  // 特殊旅人預組 - SPT-0013 黃金旅人 獻祭限制
  const targetCardForTribute = window.playerHand[selectedHandForTribute];
  if (targetCardForTribute && (targetCardForTribute.id === "SPT-0013" || targetCardForTribute.name?.includes("黃金旅人"))) {
      if (!(c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人"))) {
          setStatus(`【獻祭失敗】黃金旅人的祭品必須是小旅人！`);
          return;
      }
  }
'''
    if 'SPT-0013' not in content[content.find('function toggleTributeSelection'):content.find('function toggleTributeSelection')+1000]:
        content = content.replace('  // 不可獻祭判定\n  const c = unit.card || unit;', spt_0013_code)

    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected part 2 successfully.")

inject_part2()
