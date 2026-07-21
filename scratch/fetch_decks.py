import urllib.request
import json

try:
    response = urllib.request.urlopen("http://127.0.0.1:8000/api/decks")
    data = json.loads(response.read().decode('utf-8'))
    print("API Decks:")
    for k, v in data.items():
        print(f"  {k}: {len(v)} cards")
except Exception as e:
    print("Failed to fetch decks from server:", e)
