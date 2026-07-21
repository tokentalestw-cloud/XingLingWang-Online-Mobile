import os

walkthrough_path = r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\walkthrough.md"

wave12_content = """

---

## 第十二波：博物館接待員效果與自定義位置高優先級特召實裝摘要

### 1. `博物館接待員` (SSR-ART-0033) 效果實裝
- **召喚小旅人觸發條件**:
  - 當戰鬥階段（Combat Phase）結束時，若該角色場上存活有未被沉默的 `博物館接待員`，且此時場上有至少 1 個處於橫置狀態（`tapped === true`）的「藝術品」單位，則可以特殊召喚 1 個 `小旅人` (ART-0020)。
- **自主選擇召喚位置與前排優先機制**:
  - 當效果發動時，玩家可自主點選我方場上的任何空格進行召喚。
  - 系統限制前排優先：若我方前排有空格，玩家必須優先召喚至前排（後排空格會以紅色高亮表示不可選用並阻斷點擊）。
  - 對手 AI 發動效果時，會自動隨機選擇一個符合前排優先規則的空格進行特召。
  - 在聯網雙人模式中，同步向對方發送特召同步訊息，以保證狀態一致。

### 2. 變更檔案對照 (新增第十二波)
* [static/game_v8.js](file:///c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js) [MODIFY]
  - 於 `xlwResolvePlayerDefensePhase` (防守戰鬥結算結束時) 與 `xlwResolveEnemyLaneSafe` (進攻戰鬥結算結束時) 的結尾處，分別添加了博物館接待員效果判定 `triggerMuseumReceptionistEffect(role)`。
  - 新增 `triggerMuseumReceptionistEffect(role)` 異步函式，處理點選插槽的高亮與 Promise 抉擇流程。
  - 於 `slot.onclick` 中整合了 `window.XLW_receptionistPlacementActive` 狀態，處理玩家的點選反饋與位置法規檢驗。
  - 於手牌渲染與插槽渲染流中，配合該特召狀態對非法位置和合法位置渲染不同的科技感高亮邊框。
"""

with open(walkthrough_path, "a", encoding="utf-8") as f:
    f.write(wave12_content)

print("Walkthrough updated successfully with Wave 12!")
