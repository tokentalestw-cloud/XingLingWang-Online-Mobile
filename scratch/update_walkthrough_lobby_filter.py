with open('walkthrough.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Trim the old file changes block at the end (from line 2248)
trimmed_lines = lines[:2247]

new_content = """* [static/game_v8.js](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js) [MODIFY]
  - 於 `xlwResolvePlayerDefensePhase` 與 `xlwResolveEnemyLaneSafe` 的結尾處，分別添加了博物館接待員效果判定 `triggerMuseumReceptionistEffect(role)`。
  - 新增 `triggerMuseumReceptionistEffect(role)` 異步函式，處理點選插槽的高亮與 Promise 抉擇流程。
  - 於 `slot.onclick` 中整合了 `window.XLW_receptionistPlacementActive` 狀態，處理玩家的點選反饋與位置法規檢驗。
  - 於手牌渲染與插槽渲染流中，配合該特召狀態對非法位置和合法位置渲染不同的科技感高亮邊框。
  - 於 `confirmTribute()` 中記錄 `hadUmbrellaInGraveBefore`，並將雨傘妖怪自召條件限制為僅在該變數為 `true` 時始能觸發。
  - 於 `isUnitConfined()` 中重構長脖子的女人的效果判定，將其範圍限制於正前方 1 格，且在其處於後排時不生效。
  - 於 `castSpell` 中移除單機 AI 的短路式直接反制分支，將單機與聯網模式統合成同一個 Promise 連鎖堆疊與 UI 發動流程。
  - 新增 `aiRespondToSpellChain()` 函式以處理單機對局中 AI 的連鎖反制發動判定。
  - 在 `promptNextChainAction` 與 `resolveLocalSpellChain` 流程中對全體 `ws.send` 施加 guard 保障，並在 `resolveLocalSpellChain` 頂部動態補強 `enemyGraveyard` 對應指針。
  - 新增 `populateLobbyDecksDropdown()` 函式，由選中的種族 (`#factionSelect`) 動態過濾並填入對應的牌組 (`#deckSelect`)，使大廳大槽位顯示極致清爽。
  - 重構 `populateDeckSelect()` 與 `init()` 中對 `urlDeck` 的解析，使大廳在載入連線房間參數時能同時定位種族和預設牌組。
* [static/deck_builder.html](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/deck_builder.html) [MODIFY]
  - 於 controls 區域新增 `presetSelect` 下拉框及「新增」、「重命名」、「刪除」控制按鈕與對應樣式。
  - 新增 `populatePresetsDropdown()`、`changePresetDeck()`、`addPresetDeck()`、`renamePresetDeck()` 與 `deletePresetDeck()` 處理自訂自建牌組的本地和遠程生命週期。
  - 重構 `loadDeckBuilderData()` 與 `changeEditingDeck()` 使其配合雙下拉選單運作。
  - 重構 `populatePresetsDropdown()`，使其主動檢索「當前構築牌組」選中的基礎種族，並**僅展示**歸屬於該種族的自訂/預設牌組。
  - 重構 `addPresetDeck()`，使其**自動繼承並鎖定**當前處於選中狀態的種族作為名稱前綴，僅提示用戶輸入後綴。
  - 在 `renderLibrary()` 中對主/副牌組過濾種族的條件替換為對歸一化後的種族名稱檢索，確保自訂牌組卡牌庫不會渲染為空。
  - 新增 `.deck-select option` 樣式規則，強制下拉選單的選項使用深色背景（`#1a1a24`）與白色文字，解決選單選取項反白時白色字體白色背景的不可見 Bug。
* [static/index.html](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/index.html) [MODIFY]
  - 在大廳頂部的 `#deckSelect` 左側，新增 `#factionSelect` 下拉選單供玩家在進入遊戲前進行種族過濾，並動態關聯其右側的預設牌組選單。
"""

with open('walkthrough.md', 'w', encoding='utf-8') as f:
    f.writelines(trimmed_lines)
    f.write(new_content)

print("Updated walkthrough.md successfully with lobby filtering details!")
