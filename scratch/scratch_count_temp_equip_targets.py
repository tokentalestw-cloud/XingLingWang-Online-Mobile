import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

target = """    } else if (data.action === "temp_equip_spell_resolved") {
      const targetUnit = field[data.zone]?.[data.idx];
      if (targetUnit) {"""

for f_name in ["static/game.js", "static/game_v8.js"]:
    f_path = os.path.join(base_dir, f_name)
    with open(f_path, "r", encoding="utf-8") as f:
        content = f.read()
    content_lf = content.replace("\r\n", "\n")
    count = content_lf.count(target.replace("\r\n", "\n"))
    print(f"{f_name}: {count} occurrences")
