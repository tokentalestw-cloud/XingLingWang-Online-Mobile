with open('walkthrough.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Slice off the last few lines (lines 2259 to 2263) to expand the deck_builder.html bullet points
trimmed_lines = lines[:2258]

new_content = """* [static/deck_builder.html](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/deck_builder.html) [MODIFY]
  - 於 controls 區域新增 `presetSelect` 下拉框及「新增」、「重命名」、「刪除」控制按鈕與對應樣式。
  - 新增 `populatePresetsDropdown()`、`changePresetDeck()`、`addPresetDeck()`、`renamePresetDeck()` 與 `deletePresetDeck()` 處理自訂自建牌組的本地和遠程生命週期。
  - 重構 `loadDeckBuilderData()` 與 `changeEditingDeck()` 使其配合雙下拉選單運作。
  - 在 `renderLibrary()` 中對主/副牌組過濾種族的條件替換為對歸一化後的種族名稱檢索，確保自訂牌組卡牌庫不會渲染為空。
  - 新增 `.deck-select option` 樣式規則，強制下拉選單的選項使用深色背景（`#1a1a24`）與白色文字，完美解決了部分瀏覽器在反白/點選時文字顏色與背景同為白色導致的不可見 Bug。
"""

with open('walkthrough.md', 'w', encoding='utf-8') as f:
    f.writelines(trimmed_lines)
    f.write(new_content)

print("Updated walkthrough.md successfully with CSS fix details!")
