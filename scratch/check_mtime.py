import os
import time

f1 = r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\deck_unimplemented_summary.txt"
f2 = r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js"

for filepath in [f1, f2]:
    if os.path.exists(filepath):
        mtime = os.path.getmtime(filepath)
        print(f"{os.path.basename(filepath)} modified: {time.ctime(mtime)}")
    else:
        print(f"{os.path.basename(filepath)} does not exist")
