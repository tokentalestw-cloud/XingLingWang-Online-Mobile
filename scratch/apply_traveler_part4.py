import codecs

def inject_part4():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # SPT-0017 (大大術)
    spt_0017_code = '''} else if (card.id === "SPT-0017" || card.name?.includes("大大術")) {
      const targets = [];
      for (const z of ["player_front", "player_back"]) {
          field[z].forEach((u, i) => {
              if (u && u.card && (u.card.id === "TOKEN_TRAVELER" || u.card.name?.includes("小旅人"))) {
                  targets.push({ zone: z, idx: i, name: u.card.name, unit: u });
              }
          });
      }
      if (targets.length === 0) {
          setStatus("【大大術】我方場上沒有小旅人單位可供強化！");
          hand.splice(handIndex, 0, card);
          render();
          return;
      }
      const choices = targets.map((t, i) => ({ text: `${t.name} (${t.zone.includes("front")?"前排":"後排"}${t.idx+1})`, value: i }));
      const chosenIdx = await showXLWChoiceModal("大大術 效果發動", "請選擇我方一個小旅人賦予 +4 攻擊力：", choices);
      if (chosenIdx === null || chosenIdx === undefined) {
          hand.splice(handIndex, 0, card);
          render();
          return;
      }
      
      const targetItem = targets[chosenIdx];
      const spellCard = hand.splice(handIndex, 1)[0];
      await showSpellActivationOverlay(spellCard, "player");
      await castSpellChain(spellCard, async () => {
          targetItem.unit.atkModifier = (targetItem.unit.atkModifier || 0) + 4;
          logBattle(`✨ 大大術 效果：我方 ${targetItem.name} 獲得 +4 攻擊力！`);
          playerGrave.push(spellCard);
          render();
      });
} else if (card.id === "SR-FMS-0016" || card.name?.includes("大三元")) {'''
    if 'SPT-0017' not in content[content.find('if (card.id === "SR-FMS-0016"'):content.find('if (card.id === "SR-FMS-0016"')+1000]:
        content = content.replace('} else if (card.id === "SR-FMS-0016" || card.name?.includes("大三元")) {', spt_0017_code)


    # SPT-0018 (觀光樂園)
    spt_0018_code = '''window.xlwResolveEndPhaseEffects = async function(isPlayerSide) {
  // 特殊旅人預組 - SPT-0018 觀光樂園 (結束階段結束後召喚 3 個小旅人)
  const sidePrefix = isPlayerSide ? "player_" : "enemy_";
  for (const z of [sidePrefix + "front", sidePrefix + "back"]) {
      for (let i = 0; i < 5; i++) {
          const u = field[z][i];
          if (u && u.card && (u.card.id === "SPT-0018" || u.card.name?.includes("觀光樂園")) && !window.isUnitSilenced(u, z, i)) {
              logBattle(`✨ ${isPlayerSide ? "我方" : "對手"} 觀光樂園 效果觸發：結束階段結束後召喚 3 個小旅人！`);
              await promptAndSummonTraveler(isPlayerSide ? "player" : "enemy", 3, "觀光樂園");
          }
      }
  }
'''
    if 'SPT-0018' not in content[content.find('window.xlwResolveEndPhaseEffects'):content.find('window.xlwResolveEndPhaseEffects')+1000]:
        content = content.replace('window.xlwResolveEndPhaseEffects = async function(isPlayerSide) {', spt_0018_code)


    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected part 4 successfully.")

inject_part4()
