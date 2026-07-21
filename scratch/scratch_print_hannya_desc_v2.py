import json
import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

decks_path = os.path.join(base_dir, "static/decks.json")
if os.path.exists(decks_path):
    with open(decks_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            print("Type of data:", type(data))
            
            def search_item(item):
                if isinstance(item, dict):
                    if any(x in item.get("name", "") for x in ["般若", "Prajna", "Hannya"]):
                        print(json.dumps(item, ensure_ascii=False, indent=2))
                    for k, v in item.items():
                        search_item(v)
                elif isinstance(item, list):
                    for x in item:
                        search_item(x)
                        
            search_item(data)
        except Exception as e:
            print("Error loading static/decks.json:", e)
            
# Also let's print all card names in decks.json to see what cards exist
            with open(decks_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                names = set()
                def collect_names(item):
                    if isinstance(item, dict):
                        if "name" in item:
                            names.add(item["name"])
                        for k, v in item.items():
                            collect_names(v)
                    elif isinstance(item, list):
                        for x in item:
                            collect_names(x)
                collect_names(data)
                print("Total unique card names found:", len(names))
                print("Sample names:", list(names)[:30])
