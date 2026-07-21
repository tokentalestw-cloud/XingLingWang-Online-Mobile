with open('walkthrough.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Trim the old file changes block at the end (from line 2259)
trimmed_lines = lines[:2259]

new_content = """  - 重構 `populateDeckSelect()` 與 `init()` 中對 `urlDeck` 的解析，使大廳在載入連線房間參數時能同時定位種族和預設牌組。
  - 將 `LITTLE_TRAVELER` (小旅人) Token 的 `image` 路由由原本的錯誤佔位圖 `/static/little_traveler_back.jpeg` (該文件為牌背卡圖) 修改為正確的卡牌前繪圖 `/static/card_images/c_nms_0071.jpeg`，完美修復了博物館剪票員召喚的小旅人在戰場上顯示為卡背的異常問題。
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

print("Updated walkthrough.md successfully with Traveler details!")
