import json

with open('scratch_unimplemented_details.txt', encoding='utf-8') as f:
    match = json.load(f)

out = []
for c in match:
    effect = c.get('effect_text')
    if effect:
        out.append(f"{c['id']}: {c['name']} | faction: {c.get('subdir') or c.get('faction')}\n  Effect: {effect}")

with open('scratch_unimplemented_effects.txt', 'w', encoding='utf-8') as f_out:
    f_out.write('\n\n'.join(out))

print(f"Done, found {len(out)} cards with effects")
