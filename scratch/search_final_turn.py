import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

found = False
for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f.endswith(('.js', '.py', '.html', '.txt')):
            f_path = os.path.join(root, f)
            try:
                with open(f_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                if "FINAL_TURN" in content or "final_turn" in content:
                    found = True
                    print(f"Found in {f_path}")
                    # print matching lines
                    lines = content.split('\n')
                    for idx, line in enumerate(lines):
                        if "FINAL_TURN" in line or "final_turn" in line:
                            print(f"  L{idx+1}: {line.strip()}")
            except Exception as e:
                pass

if not found:
    print("FINAL_TURN was not found in any file.")
