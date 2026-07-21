import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

replacements = [
    # 1. confirmMulligan definition
    (
        "function confirmMulligan() {",
        "async function confirmMulligan() {"
    ),
    # 2. checkMulliganCompletion definition
    (
        "function checkMulliganCompletion() {",
        "async function checkMulliganCompletion() {"
    ),
    # 3. checkMulliganCompletion calls
    (
        "    checkMulliganCompletion();",
        "    await checkMulliganCompletion();"
    )
]

for f_name in ["static/game.js", "static/game_v8.js"]:
    f_path = os.path.join(base_dir, f_name)
    print(f"\nProcessing {f_name}...")
    with open(f_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    content_lf = content.replace("\r\n", "\n")
    
    # Verify exact match counts
    all_ok = True
    for idx, (target, replacement) in enumerate(replacements, 1):
        target_lf = target.replace("\r\n", "\n")
        cnt = content_lf.count(target_lf)
        
        # Pattern 3 (call) is expected to match exactly 2 times
        expected = 2 if idx == 3 else 1
        if cnt != expected:
            print(f"  [ERROR] Pattern {idx} ({repr(target)}) found {cnt} times instead of {expected}!")
            all_ok = False
            
    if not all_ok:
        print(f"  [ABORT] Aborting changes for {f_name} due to verification failure.")
        continue
        
    # Apply replacements
    new_content = content_lf
    for target, replacement in replacements:
        target_lf = target.replace("\r\n", "\n")
        replacement_lf = replacement.replace("\r\n", "\n")
        new_content = new_content.replace(target_lf, replacement_lf)
        
    # Write back
    with open(f_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [SUCCESS] All patterns replaced successfully in {f_name}.")
