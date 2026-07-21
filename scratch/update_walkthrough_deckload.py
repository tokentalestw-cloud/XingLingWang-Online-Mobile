with open('walkthrough.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Trim the old file changes block at the end (from line 2264)
trimmed_lines = lines[:2264]

new_content = """  - 修正 `castSpell()` 中對場地魔法卡的判定（原僅檢查已失效的 `magic_type` 屬性或寫死的特定名稱），將卡牌的 `art_subtype === "場地"` 納入判定，從而使博物館（`ART-0019`）等所有場地魔法卡能正確進入場地區發動效果。
  - 在 `render()` 中同步補強了敵方場地區（`#enemyField`）的場地卡渲染與綁定展示 modal 邏輯，使雙人連線模式下對手施放的場地魔法卡也能在畫面上直觀顯示。
  - 修正 `strictSourceCards()` 函式在載入卡牌時過早調用 `normDeckName()` 將自定義/預設牌組名稱（例如 `藝術品_始皇帝`）歸一化為基礎種族（例如 `藝術品`），導致直接跳過對特定預設/自建牌組查找、始終載入基礎種族的 Bug。修復後會優先尋找完整的預設/自建牌組，查找無果後再 fallback 到基礎種族的過濾池。
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

print("Updated walkthrough.md successfully with Lobby Deck Load details!")
