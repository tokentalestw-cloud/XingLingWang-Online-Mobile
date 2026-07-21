import os

results = []
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.js') or f.endswith('.html') or f.endswith('.py'):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as file:
                    for i, line in enumerate(file, 1):
                        if '星空' in line or 'ART-0020' in line:
                            results.append(f'{p}:{i}: {line.strip()}')
            except Exception as e:
                pass

with open('scratch/starry_search_results.txt', 'w', encoding='utf-8') as out:
    out.write('\n'.join(results))

print(f"Done! Found {len(results)} matches.")
