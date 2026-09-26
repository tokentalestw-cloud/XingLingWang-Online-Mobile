import codecs

with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
    text = f.read()

summon_injection = """
        // 妖精女王 梅瑟琳 (EVL-0002)
        if (card.id === "EVL-0002" || card.name?.includes("妖精女王")) {
          const isPlayer = zone.startsWith("player_");
          const myHand = isPlayer ? hand : (window.XLW_ENEMY?.hand || []);
          if (isPlayer) {
            const unitChoices = myHand.map((c, i) => {
              if (c && (c.type === "unit" || c.type === "character") && getCardTributeCost(c) === 0) {
                return { text: c.name, value: i };
              }
              return null;
            }).filter(x => x !== null);
            if (unitChoices.length > 0) {
              const confirmQueen = await showXLWConfirm("妖精女王 特召", "是否從手牌額外打出 1 張無須祭品的單位？");
              if (confirmQueen) {
                const chosen = await showXLWChoiceModal("妖精女王 特召", "請選擇：", unitChoices);
                if (chosen !== null && chosen !== undefined) {
                  const targetCard = myHand[chosen];
                  myHand.splice(chosen, 1);
                  await window.xlwSpecialSummonUnit(targetCard, true);
                  logBattle(`✨ 妖精女王 特召了 ${targetCard.name}！`);
                }
              }
            }
          }
        }

        // 淨化老妖精 (EVL-0013)
        if (card.id === "EVL-0013" || card.name?.includes("淨化老妖精")) {
          const isPlayer = zone.startsWith("player_");
          if (isPlayer) {
            const confirmPurify = await showXLWConfirm("淨化老妖精 淨化", "是否選擇場上一單位，將其配戴的所有魔法卡/裝備送入墓地？");
            if (confirmPurify) {
              const validTargets = [];
              for (const z of ["player_front", "player_back", "enemy_front", "enemy_back"]) {
                field[z].forEach((u, i) => {
                  if (u && u.equipments && u.equipments.length > 0) {
                    validTargets.push({ zone: z, idx: i, name: u.card.name, u: u });
                  }
                });
              }
              if (validTargets.length > 0) {
                const choices = validTargets.map((t, idx) => ({ text: `${t.name} (${t.zone.includes("player")?"我方":"對方"}${t.zone.includes("front")?"前排":"後排"}${t.idx+1})`, value: idx }));
                const chosen = await showXLWChoiceModal("選擇淨化目標", "請選擇要淨化的單位：", choices);
                if (chosen !== null && chosen !== undefined) {
                  const t = validTargets[chosen];
                  t.u.equipments = [];
                  if (t.u.effects) t.u.effects = [];
                  logBattle(`✨ 淨化老妖精 解除了 ${t.name} 身上的所有裝備與狀態！`);
                  render();
                }
              } else {
                alert("場上無身上配備魔法卡的單位。");
              }
            }
          }
        }

        // 妖精預言家 (EVL-0015)
        if (card.id === "EVL-0015" || card.name?.includes("妖精預言家")) {
          const isPlayer = zone.startsWith("player_");
          const myDeck = isPlayer ? deck : (window.XLW_ENEMY?.deck || []);
          if (myDeck.length >= 3 && isPlayer) {
            const confirmProphet = await showXLWConfirm("妖精預言家 占卜", "是否查看牌庫頂 3 張牌並調換順序？");
            if (confirmProphet) {
              const top3 = myDeck.splice(myDeck.length - 3, 3);
              const choices1 = top3.map((c, i) => ({ text: c.name, value: i }));
              const topChoice = await showXLWChoiceModal("選擇置於最頂端", "請選擇置於最頂端(馬上抽到)的卡片：", choices1);
              let topCard = top3[0], midCard = top3[1], botCard = top3[2];
              if (topChoice !== null && topChoice !== undefined) {
                topCard = top3.splice(topChoice, 1)[0];
                const choices2 = top3.map((c, i) => ({ text: c.name, value: i }));
                const midChoice = await showXLWChoiceModal("選擇置於第二張", "請選擇置於第二張的卡片：", choices2);
                if (midChoice !== null && midChoice !== undefined) {
                  midCard = top3.splice(midChoice, 1)[0];
                  botCard = top3[0];
                } else {
                  midCard = top3[0]; botCard = top3[1];
                }
                myDeck.push(botCard);
                myDeck.push(midCard);
                myDeck.push(topCard);
                logBattle(`✨ 妖精預言家 重新排列了牌庫頂的卡片。`);
              } else {
                myDeck.push(top3[0], top3[1], top3[2]); // return unchanged
              }
            }
          }
        }
"""

anchor = '  } catch (err) {\r\n    console.error("Error inside performSummonToSlot:", err);'
if anchor not in text:
    anchor = '  } catch (err) {\n    console.error("Error inside performSummonToSlot:", err);'

if 'EVL-0002' not in text:
    if anchor in text:
        text = text.replace(anchor, summon_injection + '\n' + anchor)
        with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
            f.write(text)
        print("Successfully injected performSummonToSlot effects.")
    else:
        print("Failed to find performSummonToSlot catch block anchor!")
else:
    print("Already injected.")
