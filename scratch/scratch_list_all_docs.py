import os

base_dir = "c:/Users/a2132/Documents/星靈王"
doc_files = []

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith((".txt", ".md", ".json", ".html", ".js")):
            full_path = os.path.join(root, file)
            # Skip node_modules or large build folders if any
            if "node_modules" in full_path or ".git" in full_path:
                continue
            doc_files.append((full_path, os.path.getsize(full_path)))

print(f"Found {len(doc_files)} files:")
for path, size in sorted(doc_files, key=lambda x: x[0]):
    rel = os.path.relpath(path, base_dir)
    print(f"  {rel} ({size} bytes)")
