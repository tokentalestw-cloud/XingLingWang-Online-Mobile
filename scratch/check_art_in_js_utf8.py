with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    js_content = f.read()

keywords = ["藝術品", "最後的", "顏料", "沉思的男人", "萌娜麗莎", "吶喊的人", "珍珠少女", "梵老爹"]

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\art_keywords_report.txt", "w", encoding="utf-8") as out:
    for kw in keywords:
        count = js_content.count(kw)
        out.write(f"Keyword '{kw}': {count} occurrences\n")
