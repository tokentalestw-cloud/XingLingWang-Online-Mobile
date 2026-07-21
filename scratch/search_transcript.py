# -*- coding: utf-8 -*-
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    path = r"C:\Users\a2132\.gemini\antigravity\brain\bccfde50-ebcc-4b3b-8cae-ba8bd4474145\.system_generated\logs\transcript_full.jsonl"
    with open(path, encoding='utf-8') as f:
        for line in f:
            item = json.loads(line)
            content = item.get('content', '')
            if '滑行' in content and item.get('source') != 'MODEL':
                print(f"Step {item.get('step_index')}: {content}")

if __name__ == '__main__':
    main()
