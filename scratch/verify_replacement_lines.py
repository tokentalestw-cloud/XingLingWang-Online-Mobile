with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\replacement_lines_verified.txt", "w", encoding="utf-8") as out:
    def print_range(start, end, label):
        out.write(f"=== {label} (Lines {start}-{end}) ===\n")
        for i in range(start-1, end):
            if i < len(lines):
                out.write(f"{i+1}: {lines[i]}")
        out.write("\n")

    print_range(925, 936, "getUnitAtk Start")
    print_range(1013, 1022, "getUnitAtk End")
    print_range(1622, 1630, "startTributeSummon Start")
    print_range(1680, 1718, "toggleTributeSelection")
    print_range(1720, 1735, "confirmTribute Start")
    print_range(2290, 2305, "performSummonToSlot triggers")
    print_range(3740, 3760, "resolveUnitCombat checks")
    print_range(3989, 3995, "destroyUnit Start")
    print_range(4297, 4315, "runEnemyTurn summon 1")
    print_range(4399, 4421, "runEnemyTurn summon 2")
    print_range(5201, 5210, "cardEl.onclick Equip Start")
    print_range(5320, 5333, "cardEl.onclick Magic Immune checks")
    print_range(7323, 7336, "ws.onmessage End")
