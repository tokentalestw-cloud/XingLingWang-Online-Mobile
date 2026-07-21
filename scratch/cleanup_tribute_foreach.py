# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    content = open(filepath, encoding="utf-8").read()
    
    # Normalize newlines
    content_norm = content.replace("\r\n", "\n")
    
    # 1. Target start with exact 4-space indentations
    target_start = "    // 檢查獻祭前墓地中是否已有雨傘妖怪 (防止雨傘妖怪自身被獻祭時觸發效果)\n    const hadUmbrellaInGraveBefore = graveyard.some(c => c && c.name.includes(\"雨傘妖怪\"));\n\n    selectedTributes.forEach(t => {"
    replacement_start = "    // 檢查獻祭前墓地中是否已有雨傘妖怪 (防止雨傘妖怪自身被獻祭時觸發效果)\n    const hadUmbrellaInGraveBefore = graveyard.some(c => c && c.name.includes(\"雨傘妖怪\"));\n\n    for (const t of selectedTributes) {"

    # 2. Target end with exact indentations (8 spaces, 6 spaces, 4 spaces)
    target_end = "        field[t.zone][t.idx] = null;\n      }\n    });\n\n    const targetIdx = selectedHandForTribute;"
    replacement_end = "        field[t.zone][t.idx] = null;\n      }\n    }\n\n    const targetIdx = selectedHandForTribute;"

    modified = False
    if target_start in content_norm:
        content_norm = content_norm.replace(target_start, replacement_start)
        print("Replaced selectedTributes.forEach start successfully.")
        modified = True
    else:
        print("Warning: loop start target not found.")
        
    if target_end in content_norm:
        content_norm = content_norm.replace(target_end, replacement_end)
        print("Replaced selectedTributes.forEach end successfully.")
        modified = True
    else:
        print("Warning: loop end target not found.")
            
    if modified:
        open(filepath, "w", encoding="utf-8").write(content_norm)
        print("Successfully updated confirmTribute to use for...of loop.")
    else:
        print("No changes applied.")

if __name__ == '__main__':
    main()
