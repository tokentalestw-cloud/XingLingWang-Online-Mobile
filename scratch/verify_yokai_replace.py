with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js', 'r', encoding='utf-8') as f:
    content = f.read()

target = """        if (unit.card.name.includes("晴天娃娃")) {
          const choices = [];
          if ($("playerField").dataset.card) choices.push({ text: "破壞我方場地牌", value: "player" });
          if ($("enemyField").dataset.card) choices.push({ text: "破壞敵方場地牌", value: "enemy" });
          if (choices.length > 0) {
            const chosen = await showXLWChoiceModal("晴天娃娃 獻祭效果", "請選擇要破壞的場地牌：", choices);
            if (chosen === "player") {
              const fCard = JSON.parse($("playerField").dataset.card);
              if (fCard && fCard.indestructible) {
                logBattle("晴天娃娃 效果：因【力場保護】效果，我方場地牌免疫破壞！");
              } else {
                delete $("playerField").dataset.card;
                graveyard.push(fCard);
                logBattle("晴天娃娃 效果：我方場地牌被破壞。");
              }
            } else if (chosen === "enemy") {
              const fCard = JSON.parse($("enemyField").dataset.card);
              if (fCard && fCard.indestructible) {
                logBattle("晴天娃娃 效果：因【力場保護】效果，敵方場地牌免疫破壞！");
              } else {
                delete $("enemyField").dataset.card;
                window.XLW_ENEMY.grave.push(fCard);
                logBattle("晴天娃娃 效果：敵方場地牌被破壞。");
              }
            }
          }
        }
        // (b) 嘴裂的女孩: 破壞前方第一個敵方單位
        if (unit.card.name.includes("嘴裂的女孩")) {
          const col = t.idx;
          let targetUnit = field["enemy_front"][col] || field["enemy_back"][col];
          if (targetUnit) {
            const targetZone = field["enemy_front"][col] ? "enemy_front" : "enemy_back";
            logBattle(`嘴裂的女孩 效果：破壞其前方第一格的敵方單位 ${targetUnit.card.name}！`);
            await destroyUnit(targetZone, col, "enemy");
          }
        }
        // (c) 河童: 放置在對手場地
        if (unit.card.name.includes("河童")) {
          const confirm = await showXLWConfirm("河童 獻祭效果", "是否將河童作為被動效果放置於對手場地？");
          if (confirm) {
            const enemyField = $("enemyField");
            if (enemyField) {
              if (enemyField.dataset.card) {
                window.XLW_ENEMY.grave.push(JSON.parse(enemyField.dataset.card));
              }
              enemyField.dataset.card = JSON.stringify(unit.card);
              logBattle(`河童 效果：河童被放置在對手的場地中！對手前排進攻單位攻擊力 -1。`);
            }
          }
        }
        // (d) 瓶子長長: 移動敵方單位
        if (unit.card.name.includes("瓶子長長")) {
          let hasEnemyUnit = false;
          for (const zone of ["enemy_front", "enemy_back"]) {
            if (field[zone].some(u => u !== null)) hasEnemyUnit = true;
          }
          if (hasEnemyUnit) {
            setStatus("【瓶子長長 效果】請點選敵方場上一個單位進行移動！");
            window.XLW_bottleMovingActive = true;
            render();
            await new Promise(r => { window.XLW_bottleResolve = r; });
          }
        }"""

count = content.count(target)
first_index = content.find(target)
if first_index != -1:
    start_line = content[:first_index].count('\n') + 1
    end_line = start_line + target.count('\n')
    print("Match count: {}, start line: {}, end line: {}".format(count, start_line, end_line))
else:
    print("Not found")
