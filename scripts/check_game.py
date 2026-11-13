"""Run the same catalogue and game checks locally and in CI."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    steps = [
        ("卡牌資料掃描", [sys.executable, "-X", "utf8", "scripts/audit_cards.py"]),
        ("遊戲腳本語法", ["node", "--check", "static/game_v8.js"]),
        ("卡牌效果與對戰回歸", ["node", "--test", *sorted(str(p.relative_to(ROOT)) for p in (ROOT / "tests").glob("test_*.cjs"))]),
        ("伺服器與房間回歸", [sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"]),
        ("雙用戶端 WebSocket", [sys.executable, "-X", "utf8", "tests/smoke_websocket.py"]),
    ]
    for label, command in steps:
        print(f"\n=== {label} ===", flush=True)
        try:
            result = subprocess.run(command, cwd=ROOT, check=False)
        except FileNotFoundError:
            print(f"找不到執行程式：{command[0]}", file=sys.stderr)
            return 1
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())

