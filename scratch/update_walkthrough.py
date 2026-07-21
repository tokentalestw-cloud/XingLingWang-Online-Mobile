with open('walkthrough.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Slice off the last 11 lines (lines 2233 to 2243)
trimmed_lines = lines[:2232]

new_content = """### 5. 多預設牌組支援 (完成)
- **修正各個種族預設牌組單一且虛擬世界缺乏預設牌組的問題**:
  - 擴展了預設牌組資料庫 [data/decks.json](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/data/decks.json)，為每個種族（妖怪村莊、喵喵賊、藝術品、獸人、虛擬世界）各配置了 2 套合法的 20 張預設主牌組和對應的額外牌組。
  - 主牌組卡牌皆經由自動化驗證程式校驗，確保牌組卡數剛好為 20 張，且全體法力值總和不高於 15 點，完全符合規則限制。
  - 在 `static/game_v8.js` 系統初始化 `init()` 時新增 `populateDeckSelect()` 函式，以動態解析 `decks.json` 中的鍵值，排除 `_extra` 與 `中立單位` 後動態填充首頁的 `#deckSelect` 下拉選單。
  - 配合動態牌組，在 `static/deck_builder.html` 的 `loadDeckBuilderData()` 中一併新增動態選單填充邏輯，且在卡牌庫篩選 `renderLibrary()` 時，將對比所屬種族的檢索欄位切換為歸一化後的種族名（`normDeckName(selectedDeckName)`），使如「喵喵賊_神速」等子構築能正常載入所屬種族的全部卡牌，不再顯示為空。

### 6. 變更檔案對照 (新增第十二波修復成果)
* [app.py](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/app.py) [MODIFY]
  - 在牌組儲存接口 `/api/decks/save` 中，將種族排他性檢驗（`==`）修改為包含性檢驗（`in`），從而能完美放行如「喵喵賊_神速」這類子牌組的儲存與卡牌合法性驗證。
* [data/decks.json](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/data/decks.json) [MODIFY]
  - 新增並覆寫預設牌組資料，提供多個不同戰術風格的種族牌組，並新加入「虛擬世界」的兩款預設構築與額外牌組。
* [static/game_v8.js](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js) [MODIFY]
  - 於 `xlwResolvePlayerDefensePhase` 與 `xlwResolveEnemyLaneSafe` 的結尾處，分別添加了博物館接待員效果判定 `triggerMuseumReceptionistEffect(role)`。
  - 新增 `triggerMuseumReceptionistEffect(role)` 異步函式，處理點選插槽的高亮與 Promise 抉擇流程。
  - 於 `slot.onclick` 中整合了 `window.XLW_receptionistPlacementActive` 狀態，處理玩家的點選反饋與位置法規檢驗。
  - 於手牌渲染與插槽渲染流中，配合該特召狀態對非法位置和合法位置渲染不同的科技感高亮邊框。
  - 於 `confirmTribute()` 中記錄 `hadUmbrellaInGraveBefore`，並將雨傘妖怪自召條件限制為僅在該變數為 `true` 時始能觸發。
  - 於 `isUnitConfined()` 中重構長脖子的女人的效果判定，將其範圍限制於正前方 1 格，且在其處於後排時不生效。
  - 於 `castSpell` 中移除單機 AI 的短路式直接反制分支，將單機與聯網模式統合成同一個 Promise 連鎖堆疊與 UI 發動流程。
  - 新增 `aiRespondToSpellChain()` 函式以處理單機對局中 AI 的連鎖反制發動判定。
  - 在 `promptNextChainAction` 與 `resolveLocalSpellChain` 流程中對全體 `ws.send` 施加 guard 保障，並在 `resolveLocalSpellChain` 頂部動態補強 `enemyGraveyard` 對應指針。
  - 新增並調用 `populateDeckSelect()` 函式，由後端返回的預設牌組動態初始化首頁牌組選擇器下拉框。
* [static/deck_builder.html](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/deck_builder.html) [MODIFY]
  - 在 `loadDeckBuilderData()` 中新增動態下拉選單的選項生成與當前選擇狀態恢復。
  - 在 `renderLibrary()` 中對主/副牌組過濾種族的條件替換為對歸一化後的種族名稱檢索，確保子牌組卡牌庫不會渲染為空。
"""

with open('walkthrough.md', 'w', encoding='utf-8') as f:
    f.writelines(trimmed_lines)
    f.write(new_content)

print("Updated walkthrough.md successfully!")
