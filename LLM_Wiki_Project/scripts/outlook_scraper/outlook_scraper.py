import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
import time
import json
import argparse
import os

def login():
    """Runs a visible browser for the user to log in and save cookies."""
    print("Launching browser for login...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # User must see it to log in
        context = browser.new_context()
        page = context.new_page()
        
        print("Navigating to Outlook login...")
        page.goto('https://outlook.office.com/mail/')
        
        print("Please log in. The script is waiting for the Inbox to load...")
        # Wait until the message list element appears (indicates successful login)
        page.wait_for_selector('div[aria-label="Message list"]', timeout=300000) # 5 minutes timeout
        
        print("Inbox detected! Saving session state to auth.json...")
        context.storage_state(path='auth.json')
        print("✅ Session saved successfully. You can close this window and run with --scrape.")
        
        browser.close()

def scrape_folder(page, folder_name, emails_data, limit, is_incremental, sync_state):
    print(f"\n--- Navigating to folder: {folder_name} ---")
    try:
        # Try to click the folder name in the sidebar
        folder_elem = page.locator(f'span:text-is("{folder_name}")').first
        if folder_elem.count() == 0:
            print(f"Folder '{folder_name}' not found in the sidebar!")
            return
        folder_elem.click()
        time.sleep(3) # Wait for the folder to load
    except Exception as e:
        print(f"Failed to navigate to {folder_name}: {e}")
        return

    # Wait for message list
    message_list = page.locator('div[aria-label="Message list"]').first
    if message_list.count() == 0:
         print("Message list not found in this folder.")
         return
    message_list.focus()
    
    unique_emails = set()
    print(f"Extracting full emails from {folder_name} (Target: {limit if limit > 0 else 'Unlimited'}, Incremental: {is_incremental})...")
    
    last_known_email = sync_state.get(folder_name)
    first_email_scraped = False
    stop_scraping = False
    
    scroll_attempts = 0
    while True:
        if limit > 0 and len(unique_emails) >= limit:
            break
            
        rows = page.locator('div[aria-label="Message list"] [role="option"]')
        if rows.count() == 0:
             break
             
        for i in range(rows.count()):
            if stop_scraping:
                break
                
            row = rows.nth(i)
            try:
                row_preview_text = row.inner_text().strip()
                if not row_preview_text:
                    continue
                    
                if is_incremental and last_known_email and row_preview_text == last_known_email:
                    print(f"Reached previously scraped email in {folder_name}. Stopping incremental scrape.")
                    stop_scraping = True
                    break
                    
                if row_preview_text not in unique_emails:
                    if not first_email_scraped:
                        sync_state[folder_name] = row_preview_text
                        first_email_scraped = True
                        
                    # Click to load reading pane
                    row.click()
                    time.sleep(1.5) # Wait for reading pane to load
                    
                    pane = page.locator('[aria-label="Reading Pane"]')
                    full_body = ""
                    if pane.count() > 0:
                        full_body = pane.first.inner_text()
                    else:
                        full_body = "Reading pane not found."
                        
                    emails_data.append({
                        "id": len(emails_data) + 1,
                        "folder": folder_name,
                        "preview_text": row_preview_text,
                        "full_body": full_body,
                        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    unique_emails.add(row_preview_text)
                    print(f"[{folder_name}] Extracted email {len(unique_emails)}...")
            except Exception as e:
                print("Error extracting row:", e)
                
            if limit > 0 and len(unique_emails) >= limit: # Break early for the test
                break
                
        if stop_scraping or (limit > 0 and len(unique_emails) >= limit):
            break
            
        # Check if we are stuck scrolling
        scroll_attempts += 1
        if scroll_attempts > 100: # safety breaker
            print("Reached maximum scroll attempts.")
            break
            
        # Scroll down via JS
        page.locator('[data-testid="virtuoso-scroller"]').first.evaluate("el => el.scrollBy(0, 800)")
        time.sleep(1.5)
        
    print(f"Finished folder {folder_name}. Extracted: {len(unique_emails)}")


def scrape(limit=0, is_incremental=False):
    """Runs a headless browser using the saved session to extract data."""
    if not os.path.exists('auth.json'):
        print("Error: auth.json not found. Please run with --login first.")
        return

    emails_data = []
    
    sync_state_path = "sync_state.json"
    sync_state = {}
    if is_incremental and os.path.exists(sync_state_path):
        try:
            with open(sync_state_path, "r", encoding="utf-8") as f:
                sync_state = json.load(f)
            print(f"Loaded sync state: {sync_state}")
        except Exception as e:
            print(f"Failed to load sync state: {e}")
    
    with sync_playwright() as p:
        print("Starting background scraping V2...")
        browser = p.chromium.launch(headless=True)
        # Use 1920x1080 to ensure Reading Pane is open beside the list
        context = browser.new_context(storage_state='auth.json', viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("Navigating to Outlook...")
        page.goto('https://outlook.office.com/mail/')
        page.wait_for_selector('div[aria-label="Message list"]', timeout=60000)
        print("✅ Inbox loaded.")
        
        target_folders = ["Inbox", "Sent Items", "Archive"]
        for folder in target_folders:
            scrape_folder(page, folder, emails_data, limit, is_incremental, sync_state)
            
        browser.close()
        
    if is_incremental:
        try:
            with open(sync_state_path, "w", encoding="utf-8") as f:
                json.dump(sync_state, f, ensure_ascii=False, indent=4)
            print("✅ Sync state updated.")
        except Exception as e:
            print(f"Failed to save sync state: {e}")

    # Save to JSON
    out_path = "../../raw/imports/outlook_emails.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(emails_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ V2 Scraping complete! {len(emails_data)} emails saved to: {out_path}")
    print("You can now run the `/all` pipeline in the agent chat to ingest this data.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outlook OWA Scraper V2")
    parser.add_argument("--login", action="store_true", help="Run interactive login to generate auth.json")
    parser.add_argument("--scrape", action="store_true", help="Run headless scraping using auth.json")
    parser.add_argument("--limit", type=int, default=0, help="Maximum number of emails to scrape per folder (0 for unlimited)")
    parser.add_argument("--incremental", action="store_true", help="Stop scraping when reaching the last known email from previous runs")
    
    args = parser.parse_args()

    if args.login:
        login()
    elif args.scrape:
        scrape(limit=args.limit, is_incremental=args.incremental)
    else:
        print("Please specify --login or --scrape")
