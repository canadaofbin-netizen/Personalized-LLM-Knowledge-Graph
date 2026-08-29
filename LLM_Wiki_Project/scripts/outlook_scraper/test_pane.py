import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(storage_state='auth.json', viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    page.goto('https://outlook.office.com/mail/')
    print('Waiting for Inbox...')
    page.wait_for_selector('div[aria-label="Message list"] [role="option"]', timeout=30000)
    
    # Click the first email
    print('Clicking the first email...')
    page.locator('div[aria-label="Message list"] [role="option"]').first.click()
    
    # Wait for reading pane
    page.wait_for_timeout(3000) # Give it 3 secs to load the body
    
    # Dump body text
    print('Trying to find reading pane...')
    try:
        pane = page.locator('[aria-label="Reading Pane"]')
        if pane.count() > 0:
            print('Found Reading Pane via aria-label')
            print(pane.first.inner_text()[:500])
        else:
            pane = page.locator('div[role="main"]')
            print('Found main region')
            print(pane.first.inner_text()[:500])
    except Exception as e:
        print('Error extracting:', e)
    browser.close()
