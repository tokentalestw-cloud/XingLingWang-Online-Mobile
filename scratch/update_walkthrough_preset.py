with open('walkthrough.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Trim the old file changes block at the end (from line 2240)
trimmed_lines = lines[:2232]

new_content = """### 5. 獨立自訂/預設牌組管理與編輯功能 (完成)
- **修正牌組編輯器下拉選單項目過多的問題**:
  - 將牌組編輯器 [static/deck_builder.html](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/deck_builder.html) 頂部的「當前構築牌組」選單還原為僅顯示 5 個基本種族，避免多個子構築混雜在同一個選單中。
  - 在右側新增獨立的「預設/自訂牌組」選單與管理按鈕（「新增」、「重命名」、「刪除」）。
  - 當玩家點選「預設/自訂牌組」後，會自動將其加載至主/副牌組，並自動將「當前構築牌組」定位至其所屬的種族，藉此維持卡牌庫與編輯狀態的正確篩選。
  - 點選「新增」時，會要求輸入種族與子名稱（如 `喵喵賊_神速`），並自動將當前構築中的卡牌配置複製到新牌組，同時寫入伺服器與新增至選單中。
  - 點選「重命名」與「刪除」時，會調用後端新增的接口，動態更新 `decks.json` 並與本地緩存、UI 視圖同步，非常靈活便捷。

### 6. 變更檔案對照 (新增第十二波修復成果)
* [app.py](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/app.py) [MODIFY]
  - 將牌組卡片種族驗證規則改為包含性匹配（`in`），以支持諸如 `喵喵賊_神速` 的子構築。
  - 新增 POST 接口 `/api/decks/delete` 以執行自訂牌組的刪除（基礎種族牌組禁止刪除）。
  - 新增 POST 接口 `/api/decks/rename` 以執行自訂牌組的重命名，在重命名時強制檢驗新名稱必須包含所屬種族名稱。
* [data/decks.json](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/data/decks.json) [MODIFY]
  - 新增多款不同風格的預設牌組，並新加入「虛擬世界」的兩款預設構築與額外牌組。
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
  - 於 controls 區域新增 `presetSelect` 下拉框及「新增」、「重命名」、「刪除」控制按鈕與對應樣式。
  - 新增 `populatePresetsDropdown()`、`changePresetDeck()`、`addPresetDeck()`、`renamePresetDeck()` 與 `deletePresetDeck()` 處理自訂自建牌組的本地和遠程生命週期。
  - 重構 `loadDeckBuilderData()` 與 `changeEditingDeck()` 使其配合雙下拉選單運作。
  - 在 `renderLibrary()` 中對主/副牌組過濾種族的條件替換為對歸一化後的種族名稱檢索，確保自訂牌組卡牌庫不會渲染為空。
"""

with open('walkthrough.md', 'w', encoding='utf-8') as f:
    f.writelines(trimmed_lines)
    f.write(new_content)

print("Updated walkthrough.md successfully!")
