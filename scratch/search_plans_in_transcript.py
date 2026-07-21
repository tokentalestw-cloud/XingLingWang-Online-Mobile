import json

logfile = r"C:\Users\a2132\.gemini\antigravity\brain\5403ad39-7956-4efa-b742-0d467aeb905c\.system_generated\logs\transcript.jsonl"

with open(logfile, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get("content") or ""
            tool_calls = data.get("tool_calls") or []
            
            # Check if implementation_plan.md is created/modified or shown
            for tc in tool_calls:
                if "implementation_plan.md" in str(tc.get("args")):
                    print(f"Step {data.get('step_index')} ({data.get('type')}): Tool {tc.get('name')}")
                    # Print the explanation content of this step
                    print("  Content summary:", content.strip().split("\n")[0])
        except Exception:
            pass
