import sys
sys.stdout.reconfigure(encoding='utf-8')

import glob
for fpath in glob.glob("*.*") + glob.glob("static/*.*"):
    if ".js" in fpath or ".py" in fpath or ".html" in fpath:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
                if "cards.json" in content or "decks.json" in content:
                    print(f"File {fpath} references card/deck data.")
        except Exception as e:
            pass
