import time
import sys
import os

os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "playwright", "-q"])
    from playwright.sync_api import sync_playwright

time.sleep(5)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 1200})

    try:
        page.goto("http://localhost:8501", wait_until="networkidle", timeout=30000)
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        screenshot_path = r"C:\test\dashboard_screenshot.png"
        page.screenshot(path=screenshot_path, full_page=True)

        print("Screenshot saved: " + screenshot_path)
    except Exception as e:
        print("Error: " + str(e))
    finally:
        browser.close()
