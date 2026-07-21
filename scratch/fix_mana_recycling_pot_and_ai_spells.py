# -*- coding: utf-8 -*-
import sys, re

def fix_ai_spells():
    sys.stdout.reconfigure(encoding='utf-8')
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    # Replacement for Mana Recycling Pot (法力回收壺) in castSpell
    old_pot_code = """  } else if (card.name?.includes("法力回收壺") || card.id === "R-NMG-0023") {
    const spellsInGrave = graveyard.filter(c => c && c.type === "magic");
    if (spellsInGrave.length > 0) {
      const choices = spellsInGrave.map((c, i) => ({ text: `${c.name} (墓地)`, value: i }));
      const chosenIdx = await showXLWChoiceModal("法力回收壺 效果：選擇一張墓地魔法卡回手", "選擇魔法卡：", choices);
      if (chosenIdx !== null && chosenIdx !== undefined) {
        const chosenSpell = spellsInGrave[chosenIdx];
        const gIdx = graveyard.indexOf(chosenSpell);
        if (gIdx >= 0) graveyard.splice(gIdx, 1);
        hand.push(chosenSpell);
        logBattle(`✨ 法力回收壺 效果：將墓地魔法卡 ${chosenSpell.name} 回收至手牌！`);
      }
    } else {
      setStatus("墓地中無魔法卡可回收！");
      return;
    }
  }"""

    new_pot_code = """  } else if (card.name?.includes("法力回收壺") || card.id === "R-NMG-0023") {
    if (!isMyTurn) {
      // 對手 AI 發動：自動從對手墓地回收魔法卡至對手手牌
      const enemyGraveSpells = (window.XLW_ENEMY.grave || []).filter(c => c && (c.type === "magic" || c.type === "魔法"));
      if (enemyGraveSpells.length > 0) {
        const recycled = enemyGraveSpells[0];
        const gIdx = window.XLW_ENEMY.grave.indexOf(recycled);
        if (gIdx >= 0) window.XLW_ENEMY.grave.splice(gIdx, 1);
        window.XLW_ENEMY.hand.push(recycled);
        logBattle(`✨ 對手發動【法力回收壺】效果：將墓地魔法卡【${recycled.name}】回收至對手手牌！`);
        render();
      } else {
        logBattle("✨ 對手發動【法力回收壺】：其墓地無魔法卡可回收。");
      }
      return;
    }

    // 我方發動
    const spellsInGrave = graveyard.filter(c => c && (c.type === "magic" || c.type === "魔法"));
    if (spellsInGrave.length > 0) {
      const choices = spellsInGrave.map((c, i) => ({ text: `${c.name} (墓地)`, value: i }));
      const chosenIdx = await showXLWChoiceModal("法力回收壺 效果：選擇一張墓地魔法卡回手", "選擇魔法卡：", choices);
      if (chosenIdx !== null && chosenIdx !== undefined) {
        const chosenSpell = spellsInGrave[chosenIdx];
        const gIdx = graveyard.indexOf(chosenSpell);
        if (gIdx >= 0) graveyard.splice(gIdx, 1);
        hand.push(chosenSpell);
        logBattle(`✨ 法力回收壺 效果：將墓地魔法卡 ${chosenSpell.name} 回收至手牌！`);
        render();
      }
    } else {
      setStatus("墓地中無魔法卡可回收！");
      return;
    }
  }"""

    if old_pot_code in js_content:
        js_content = js_content.replace(old_pot_code, new_pot_code)
        print("1. Replaced Mana Recycling Pot (法力回收壺) in castSpell successfully!")

    # Replacement for Force Field Protection (力場保護) in castSpell
    old_field_prot = """  } else if (card.name?.includes("力場保護") || card.id === "NMG-0040") {
    while (true) {
      const opt = await showXLWChoiceModal(
        "力場保護 效果選擇",
        "請選擇要發動的效果：",
        [
          { text: "🛡️ 讓我方已在場上的一張場地卡具備破壞抗性", value: "protect_field" },
          { text: "🎴 抽一張牌", value: "draw_card" }
        ]
      );
      if (opt === "protect_field") {
        const playerField = $("playerField");
        if (playerField && playerField.dataset.card) {
          const fCard = JSON.parse(playerField.dataset.card);
          fCard.indestructible = true;
          playerField.dataset.card = JSON.stringify(fCard);
          logBattle(`✨ 力場保護 效果：使我方場上的場地卡【${fCard.name}】具備破壞抗性！`);
          if (isMultiplayer) {
            ws.send(JSON.stringify({ action: "field_indestructible" }));
          }
          break;
        } else {
          await showXLWConfirm("力場保護", "我方場上目前沒有場地卡，無法發動此效果！請選擇「抽一張牌」！", "確定");
        }
      } else if (opt === "draw_card") {
        draw(1);
        logBattle("✨ 力場保護 效果：我方抽 1 張牌。");
        break;
      }
    }
  }"""

    new_field_prot = """  } else if (card.name?.includes("力場保護") || card.id === "NMG-0040") {
    if (!isMyTurn) {
      // AI 發動：自動抽 1 張牌
      if (window.XLW_ENEMY.deck && window.XLW_ENEMY.deck.length > 0) {
        window.XLW_ENEMY.hand.push(window.XLW_ENEMY.deck.pop());
      }
      logBattle("✨ 對手發動【力場保護】效果：對手抽 1 張牌。");
      render();
      return;
    }

    while (true) {
      const opt = await showXLWChoiceModal(
        "力場保護 效果選擇",
        "請選擇要發動的效果：",
        [
          { text: "🛡️ 讓我方已在場上的一張場地卡具備破壞抗性", value: "protect_field" },
          { text: "🎴 抽一張牌", value: "draw_card" }
        ]
      );
      if (opt === "protect_field") {
        const playerField = $("playerField");
        if (playerField && playerField.dataset.card) {
          const fCard = JSON.parse(playerField.dataset.card);
          fCard.indestructible = true;
          playerField.dataset.card = JSON.stringify(fCard);
          logBattle(`✨ 力場保護 效果：使我方場上的場地卡【${fCard.name}】具備破壞抗性！`);
          if (isMultiplayer) {
            ws.send(JSON.stringify({ action: "field_indestructible" }));
          }
          break;
        } else {
          await showXLWConfirm("力場保護", "我方場上目前沒有場地卡，無法發動此效果！請選擇「抽一張牌」！", "確定");
        }
      } else if (opt === "draw_card") {
        draw(1);
        logBattle("✨ 力場保護 效果：我方抽 1 張牌。");
        break;
      }
    }
  }"""

    if old_field_prot in js_content:
        js_content = js_content.replace(old_field_prot, new_field_prot)
        print("2. Replaced Force Field Protection (力場保護) in castSpell successfully!")

    open(js_path, 'w', encoding='utf-8').write(js_content)

    # Update cache-buster in static/index.html to v=11.00-mana-recycling-pot-fix
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=11.00-mana-recycling-pot-fix', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=11.00-mana-recycling-pot-fix', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_ai_spells()
