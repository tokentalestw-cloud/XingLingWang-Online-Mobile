import os

dirpath = r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed"
for f in os.listdir(dirpath):
    if f.startswith("README_v7_"):
        print("Found file:", f)
        filepath = os.path.join(dirpath, f)
        with open(filepath, 'r', encoding='utf-8') as file:
            print("Content:")
            print(file.read())
