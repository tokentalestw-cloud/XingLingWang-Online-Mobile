import json

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

# Print the last 15 user inputs
for ui in user_inputs[-15:]:
    print(f"Step {ui['step_index']}: {ui['content']}")
