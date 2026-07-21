import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
for sub in ["data", "backup"]:
    dir_path = os.path.join(base_dir, sub)
    if os.path.exists(dir_path):
        print(f"=== Files in {sub} ===")
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                full_path = os.path.join(root, file)
                rel = os.path.relpath(full_path, base_dir)
                print(f"  {rel} ({os.path.getsize(full_path)} bytes)")
