# 星靈王卡牌與對戰檢查

安裝 Python 3.11 以上、Node.js 24 及 `python -m pip install -r requirements.txt` 後，在專案根目錄執行 `python -X utf8 scripts/check_game.py`。只掃描卡庫可執行 `python -X utf8 scripts/audit_cards.py`。

掃描會攔截重複主卡號、缺少必要欄位、未知牌組卡號、兩份牌組資料不一致，以及超過既有筆數的新重複。現有同牌組重複列在 `data/deck_duplicate_baseline.json`，包含額外區和測試牌組。確認某組重複的用途後，可移除對應記錄並同步兩份牌組資料。不同版本有不同卡號，依原版本保留。

需精確檢查效果引用時，可以在卡牌資料加上 `effect_card_ids` 卡號陣列。卡文中的卡號和關鍵字掃描只提供人工核對線索。效果是否正確仍由對戰案例驗證。

新增回歸案例時，直接建立最小場面並使用固定的選牌或選位結果。覆蓋卡牌從來源區移除、只進入目標區一次、回合與階段，以及對方視角的同一結果。現有入口包括 `test_duel_consistency.cjs`、`test_combat_targeting.cjs`、`test_end_turn_settlement.cjs` 和 `test_turn_handoff.cjs`。

GitHub Actions 在 main 更新或收到 PR 時跑相同檢查。Render 服務的 **Settings → Auto-Deploy → After CI Checks Pass** 決定正式站是否等待 CI，使用 Blueprint 管理的服務可同步 `render.yaml`。即使 Render 尚未同步此設定，日常部署也應先執行本機檢查再推送。

