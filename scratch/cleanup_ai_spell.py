# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    content = open(filepath, encoding="utf-8").read()
    
    target = """let roaredCardBackup = null;
let roaredCardIdx = -1;
if (window.XLW_enemyCannotUseCardIdThisTurn && window.XLW_ENEMY.hand) {
roaredCardIdx = window.XLW_ENEMY.hand.findIndex(c => c && c.id === window.XLW_enemyCannotUseCardIdThisTurn);
if (roaredCardIdx >= 0) {
roaredCardBackup = window.XLW_ENEMY.hand.splice(roaredCardIdx, 1)[0];
}
}

let roaredCardBackup = null;
let roaredCardIdx = -1;
if (window.XLW_enemyCannotUseCardIdThisTurn && window.XLW_ENEMY.hand) {
roaredCardIdx = window.XLW_ENEMY.hand.findIndex(c => c && c.id === window.XLW_enemyCannotUseCardIdThisTurn);
if (roaredCardIdx >= 0) {
roaredCardBackup = window.XLW_ENEMY.hand.splice(roaredCardIdx, 1)[0];
}
}"""

    replacement = """let roaredCardBackup = null;
let roaredCardIdx = -1;
if (window.XLW_enemyCannotUseCardIdThisTurn && window.XLW_ENEMY.hand) {
roaredCardIdx = window.XLW_ENEMY.hand.findIndex(c => c && c.id === window.XLW_enemyCannotUseCardIdThisTurn);
if (roaredCardIdx >= 0) {
roaredCardBackup = window.XLW_ENEMY.hand.splice(roaredCardIdx, 1)[0];
}
}"""

    content_norm = content.replace("\r\n", "\n")
    target_norm = target.replace("\r\n", "\n")
    replacement_norm = replacement.replace("\r\n", "\n")
    
    if target_norm in content_norm:
        content_norm = content_norm.replace(target_norm, replacement_norm)
        open(filepath, "w", encoding="utf-8").write(content_norm)
        print("Cleanup successful.")
    else:
        # Try with spacing/tabs
        target_spaces = """let roaredCardBackup = null;
let roaredCardIdx = -1;
if (window.XLW_enemyCannotUseCardIdThisTurn && window.XLW_ENEMY.hand) {
  roaredCardIdx = window.XLW_ENEMY.hand.findIndex(c => c && c.id === window.XLW_enemyCannotUseCardIdThisTurn);
  if (roaredCardIdx >= 0) {
    roaredCardBackup = window.XLW_ENEMY.hand.splice(roaredCardIdx, 1)[0];
  }
}

let roaredCardBackup = null;
let roaredCardIdx = -1;
if (window.XLW_enemyCannotUseCardIdThisTurn && window.XLW_ENEMY.hand) {
  roaredCardIdx = window.XLW_ENEMY.hand.findIndex(c => c && c.id === window.XLW_enemyCannotUseCardIdThisTurn);
  if (roaredCardIdx >= 0) {
    roaredCardBackup = window.XLW_ENEMY.hand.splice(roaredCardIdx, 1)[0];
  }
}"""
        # Let's just do a direct split/join replacement by splitting on the duplicate
        # We can find where the function starts, and remove the second block
        # Actually, let's look at the content around 'roaredCardBackup'
        # Since 'roaredCardBackup = null;' appears twice, let's see.
        target_spaces_norm = target_spaces.replace("\r\n", "\n")
        replacement_spaces_norm = replacement.replace("\r\n", "\n")
        
        # If we just do simple string find & replace for the exact lines printed:
        lines = content_norm.split("\n")
        # Find where roaredCardBackup is declared
        decls = [i for i, line in enumerate(lines) if "let roaredCardBackup = null;" in line]
        if len(decls) >= 2:
            # We want to remove the second declaration block (which is lines decls[1] to decls[1]+7)
            start_idx = decls[1]
            # Verify it matches the block
            if "roaredCardIdx = -1" in lines[start_idx+1] and "window.XLW_enemyCannotUseCardIdThisTurn" in lines[start_idx+2]:
                del lines[start_idx:start_idx+8]
                open(filepath, "w", encoding="utf-8").write("\n".join(lines))
                print("Successfully removed second copy by line indices.")
                return
        print("Target not found.")

if __name__ == '__main__':
    main()
