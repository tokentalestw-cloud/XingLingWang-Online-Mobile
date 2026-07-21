# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    content = open(filepath, encoding="utf-8").read()
    
    # Normalize newlines
    content_norm = content.replace("\r\n", "\n")
    
    target = """  if (isMultiplayer && !isMyTurn) {
    setStatus("對手回合中，請稍候！");
    return;
  }
  const card = hand[handIndex];
  if (!card || card.type !== "magic") return;"""

    replacement = """  if (isMultiplayer && !isMyTurn) {
    setStatus("對手回合中，請稍候！");
    return;
  }
  if (!card || card.type !== "magic") return;"""

    if target in content_norm:
        content_norm = content_norm.replace(target, replacement)
        open(filepath, "w", encoding="utf-8").write(content_norm)
        print("Rebuilt castSpell cleanup successful.")
    else:
        print("Target not found. Let's try splitting on lines.")
        # Line-based fallback
        lines = content_norm.split("\n")
        decls = [i for i, line in enumerate(lines) if "const card = hand[handIndex];" in line]
        print(f"Found declarations at line indices: {decls}")
        
        # We look for the declaration inside the castSpell function range (after line 2500)
        decls_in_range = [idx for idx in decls if idx > 2500 and idx < 2800]
        if len(decls_in_range) >= 2:
            idx_to_remove = decls_in_range[1]
            if "if (!card || card.type" in lines[idx_to_remove+1]:
                print(f"Removing redundant declaration at line index {idx_to_remove}")
                del lines[idx_to_remove]
                open(filepath, "w", encoding="utf-8").write("\n".join(lines))
                print("Fallback cleanup successful.")
            else:
                print("Warning: next line did not match expected structure.")
        else:
            print("Warning: did not find at least 2 declarations in the expected line range.")

if __name__ == '__main__':
    main()
