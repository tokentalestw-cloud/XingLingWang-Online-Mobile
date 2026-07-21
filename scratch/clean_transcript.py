import json
import re

logfile = r"C:\Users\a2132\.gemini\antigravity\brain\5403ad39-7956-4efa-b742-0d467aeb905c\.system_generated\logs\transcript.jsonl"

user_inputs = []
with open(logfile, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get("type") == "USER_INPUT":
                user_inputs.append({
                    "step_index": data.get("step_index"),
                    "content": data.get("content")
                })
        except Exception as e:
            pass

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\user_requests_utf8.txt", 'w', encoding='utf-8') as out:
    for ui in user_inputs:
        # Strip out metadata
        content = ui["content"]
        content = re.sub(r'<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>', '', content, flags=re.DOTALL)
        content = content.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "").strip()
        out.write(f"Step {ui['step_index']}:\n{content}\n\n")
