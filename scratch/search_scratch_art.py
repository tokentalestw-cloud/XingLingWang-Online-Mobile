import os

scratch_dir = r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch"
for f in os.listdir(scratch_dir):
    filepath = os.path.join(scratch_dir, f)
    if os.path.isfile(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                if "ART-" in content:
                    print(f"File {f} contains 'ART-'")
        except Exception:
            pass
