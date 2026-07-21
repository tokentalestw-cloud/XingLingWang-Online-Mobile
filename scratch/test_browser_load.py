import subprocess
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

print("Starting Uvicorn in background...")
proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"])

time.sleep(3)  # Wait for server to start

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--log-level=3")

try:
    print("Initializing webdriver...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    print("Loading page...")
    driver.get("http://127.0.0.1:8000/")
    time.sleep(3)
    
    # Get browser console logs
    logs = driver.get_log('browser')
    print("=== Browser Console Logs ===")
    if not logs:
        print("No logs/errors found.")
    for entry in logs:
        print(f"[{entry['level']}] {entry['message']}")
    
    driver.quit()
except Exception as e:
    print("Selenium error:", e)

print("Terminating server...")
proc.terminate()
proc.wait()
print("Done.")
