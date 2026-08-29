import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state='auth.json')
    page = context.new_page()
    page.goto('https://outlook.office.com/mail/')
    print("Waiting for Inbox...")
    page.wait_for_selector('div[aria-label="Message list"]', timeout=30000)
    print("Inbox loaded. Extracting HTML...")
    html = page.locator('div[aria-label="Message list"]').inner_html()
    with open('dom_dump.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('DOM saved to dom_dump.html')
    browser.close()
