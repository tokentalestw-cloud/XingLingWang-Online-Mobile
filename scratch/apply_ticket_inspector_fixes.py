import re

filename = 'static/game_v8.js'

with open(filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Reset flag in initGameMultiplayer (around line 403)
# We look for "  // 重置標記\n  turn = 0;"
found_lobby_reset = False
for idx in range(350, 450):
    if "重置標記" in lines[idx] and "turn = 0;" in lines[idx+1]:
        lines[idx+1] = "  turn = 0;\n  window.XLW_playerActionsPerformedThisTurn = false;\n"
        found_lobby_reset = True
        break
print("Lobby Reset replaced:", found_lobby_reset)

# 2. Reset flag in newGame (around line 654)
found_newgame_reset = False
for idx in range(600, 700):
    if "重置標記" in lines[idx] and "turn = 0;" in lines[idx+1]:
        lines[idx+1] = "  turn = 0;\n  window.XLW_playerActionsPerformedThisTurn = false;\n"
        found_newgame_reset = True
        break
print("NewGame Reset replaced:", found_newgame_reset)

# 3. Reset flag in playerUntap (around line 10811)
found_untap_reset = False
for idx in range(10750, 10850):
    if "function playerUntap()" in lines[idx]:
        for sub_idx in range(idx, idx+15):
            if "window.XLW_callGameNegatedThisTurn = false;" in lines[sub_idx]:
                lines[sub_idx] = "  window.XLW_callGameNegatedThisTurn = false;\n  window.XLW_playerActionsPerformedThisTurn = false;\n"
                found_untap_reset = True
                break
        if found_untap_reset:
            break
print("PlayerUntap Reset replaced:", found_untap_reset)

# 4. Set flag in performSummonToSlot (around line 4189)
found_summon_set = False
for idx in range(4100, 4250):
    if 'if (zone.startsWith("player_")) {' in lines[idx]:
        if "XLW_playerSummonCountThisTurn" in lines[idx+1]:
            lines[idx+1] = lines[idx+1] + "      window.XLW_playerActionsPerformedThisTurn = true;\n"
            found_summon_set = True
            break
print("Summon Set replaced:", found_summon_set)

# 5. Set flag in castSpell (around line 2059)
found_castspell_set = False
for idx in range(2050, 2080):
    if "async function castSpell(handIndex) {" in lines[idx]:
        for sub_idx in range(idx, idx+15):
            if 'if (!card || card.type !== "magic") return;' in lines[sub_idx]:
                lines[sub_idx] = lines[sub_idx] + "\n  window.XLW_playerActionsPerformedThisTurn = true;\n"
                found_castspell_set = True
                break
        if found_castspell_set:
            break
print("CastSpell Set replaced:", found_castspell_set)

# 6. Set flag in tactical move (around line 5690)
found_move_set = False
for idx in range(5600, 5720):
    if "window.XLW_tacticalMoveUsed = true;" in lines[idx]:
        lines[idx] = "  window.XLW_tacticalMoveUsed = true;\n  window.XLW_playerActionsPerformedThisTurn = true;\n"
        found_move_set = True
        break
print("Move Set replaced:", found_move_set)

# 7. Add start phase check to Museum Ticket Inspector (around line 12407)
found_ticket_inspector_check = False
for idx in range(12390, 12430):
    if 'const isTicketCollector = obj.card?.id === "R-ART-0050" || obj.card?.name?.includes("博物館剪票員");' in lines[idx]:
        # Insert check after isTicketCollector if block starts
        if "if (isTicketCollector) {" in lines[idx+1]:
            lines[idx+1] = "            if (isTicketCollector) {\n              if (window.XLW_playerActionsPerformedThisTurn) {\n                setStatus(\"【博物館剪票員】的效果只能在我方主要階段開始時發動（尚未執行任何行動前）！\");\n                showModal(obj.card, obj.equipments);\n                return;\n              }\n"
            found_ticket_inspector_check = True
            break
print("Ticket Inspector check replaced:", found_ticket_inspector_check)

# 8. Set flag inside confirmUse blocks
# Line indices (1-indexed in file)
confirm_use_lines = [12188, 12259, 12333, 12383, 12441, 12511, 12631, 12694, 12765, 12814, 12897, 12971, 13041]
modified_confirm_use = 0

for line_num in confirm_use_lines:
    idx = line_num - 1
    if "if (confirmUse) {" in lines[idx]:
        lines[idx] = "              if (confirmUse) {\n                window.XLW_playerActionsPerformedThisTurn = true;\n"
        modified_confirm_use += 1
    else:
        # Fallback check around the line
        for offset in range(-5, 6):
            check_idx = idx + offset
            if 0 <= check_idx < len(lines) and "if (confirmUse) {" in lines[check_idx]:
                lines[check_idx] = "              if (confirmUse) {\n                window.XLW_playerActionsPerformedThisTurn = true;\n"
                modified_confirm_use += 1
                break

print("Modified confirmUse blocks count:", modified_confirm_use)

with open(filename, 'w', encoding='utf-8') as f:
    f.writelines(lines)
