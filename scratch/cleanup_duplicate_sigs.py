# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    content = open(filepath, encoding="utf-8").read()
    
    # Normalize newlines
    content_norm = content.replace("\r\n", "\n")
    
    # 1. performPlayerTurnStartDraw duplicate signature
    dup1 = "async function performPlayerTurnStartDraw() {\nasync function performPlayerTurnStartDraw() {"
    rep1 = "async function performPlayerTurnStartDraw() {"
    
    # 2. startTributeSummon duplicate if condition
    dup2 = "  if (phase === \"戰術佈陣\") {\nif (phase === \"戰術佈陣\") {"
    dup2_alt = "if (phase === \"戰術佈陣\") {\nif (phase === \"戰術佈陣\") {"
    rep2 = "  if (phase === \"戰術佈陣\") {"
    
    # 3. canSummonCard duplicate signature
    dup3 = "function canSummonCard(card, isPlayer) {\nfunction canSummonCard(card, isPlayer) {"
    rep3 = "function canSummonCard(card, isPlayer) {"
    
    modified = False
    
    if dup1 in content_norm:
        content_norm = content_norm.replace(dup1, rep1)
        print("Fixed performPlayerTurnStartDraw duplicate.")
        modified = True
        
    if dup2 in content_norm:
        content_norm = content_norm.replace(dup2, rep2)
        print("Fixed startTributeSummon duplicate (indent).")
        modified = True
    elif dup2_alt in content_norm:
        content_norm = content_norm.replace(dup2_alt, rep2)
        print("Fixed startTributeSummon duplicate (no indent).")
        modified = True
        
    if dup3 in content_norm:
        content_norm = content_norm.replace(dup3, rep3)
        print("Fixed canSummonCard duplicate.")
        modified = True
        
    if modified:
        open(filepath, "w", encoding="utf-8").write(content_norm)
        print("Successfully cleaned up signature duplicates.")
    else:
        print("No duplicates found to clean up.")

if __name__ == '__main__':
    main()
