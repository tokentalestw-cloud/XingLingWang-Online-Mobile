with open('walkthrough.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Slice off the last few lines (from line 2259) to update deck_builder.html bullet points
trimmed_lines = lines[:2258]

new_content = """* [static/deck_builder.html](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/deck_builder.html) [MODIFY]
  - 於 controls 區域新增 `presetSelect` 下拉框及「新增」、「重命名」、「刪除」控制按鈕與對應樣式。
  - 新增 `populatePresetsDropdown()`、`changePresetDeck()`、`addPresetDeck()`、`renamePresetDeck()` 與 `deletePresetDeck()` 處理自訂自建牌組的本地和遠程生命週期。
  - 重構 `loadDeckBuilderData()` 與 `changeEditingDeck()` 使其配合雙下拉選單運作。
  - 重構 `populatePresetsDropdown()`，使其主動讀取當前「當前構築牌組」選中的基礎種族（如 `藝術品`），並**僅展示**歸屬於該種族的自訂/預設牌組（如 `藝術品_珍藏`），極大清爽了介面並實現了種族鎖定篩選。
  - 重構 `addPresetDeck()`，不再要求手動挑選種族，而是**自動繼承並鎖定**當前處於選中狀態的種族作為名稱前綴，僅提示用戶輸入後綴（例如：輸入 `速攻` 即自動創建並儲存為 `藝術品_速攻`），徹底杜絕命名錯亂。
  - 在 `renderLibrary()` 中對主/副牌組過濾種族的條件替換為對歸一化後的種族名稱檢索，確保自訂牌組卡牌庫不會渲染為空。
  - 新增 `.deck-select option` 樣式規則，強制下拉選單的選項使用深色背景（`#1a1a24`）與白色文字，完美解決了部分瀏覽器在反白/點選時文字顏色與背景同為白色導致的不可見 Bug。
"""

with open('walkthrough.md', 'w', encoding='utf-8') as f:
    f.writelines(trimmed_lines)
    f.write(new_content)

print("Updated walkthrough.md successfully with preset filtering details!")
