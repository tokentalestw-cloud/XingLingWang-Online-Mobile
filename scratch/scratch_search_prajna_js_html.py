import os

search_terms = ["智慧的般若", "憤怒的般若", "般若"]
base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static"

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".js") or file.endswith(".html"):
            f_path = os.path.join(root, file)
            try:
                with open(f_path, "r", encoding="utf-8") as f:
                    for line_no, line in enumerate(f, 1):
                        for term in search_terms:
                            if term in line:
                                print(f"{file} Line {line_no} ({term}): {line.strip()[:150]}")
                                break
            except Exception as e:
                print(f"Error reading {file}: {e}")
