---
name: scrape_emails
description: Scrapes emails from Outlook OWA and outputs raw JSON for ingestion.
---

# Outlook Email Scraper Skill

This skill executes the Playwright-based Outlook OWA scraper (`LLM_Wiki_Project/scripts/outlook_scraper/outlook_scraper.py`) to extract emails from a user's Inbox, Sent Items, and Archive folders. The extracted emails are saved to `LLM_Wiki_Project/raw/imports/outlook_emails.json`.

## Modes

1. **`/scrape_emails login`**: 
   - Launches a visible browser for the user to log in to their Microsoft account.
   - Saves the authentication cookies to `auth.json`.
   - **Command**: `python LLM_Wiki_Project/scripts/outlook_scraper/outlook_scraper.py --login`
   - *Note*: Run this first if `auth.json` is missing or expired.

2. **`/scrape_emails run [limit]`**: 
   - Runs a headless browser using the saved `auth.json` to scrape emails.
   - Supports an optional limit for the number of emails per folder (0 for unlimited).
   - **Command**: `python LLM_Wiki_Project/scripts/outlook_scraper/outlook_scraper.py --scrape --limit [N]` (default limit: 0)

3. **`/scrape_emails update`**: 
   - Runs the scraper in **incremental mode**. It remembers the last scraped email from previous runs and stops scraping as soon as it hits an email it has already seen.
   - **Command**: `python LLM_Wiki_Project/scripts/outlook_scraper/outlook_scraper.py --scrape --incremental`

## Post-Scraping Action
After scraping successfully completes, you **MUST** run the `/all` pipeline (or at least `/extract` followed by `/ingest`) to process the newly generated `LLM_Wiki_Project/raw/imports/outlook_emails.json`.

## Technical Details
- **Directory**: `LLM_Wiki_Project/scripts/outlook_scraper/`
- **Output**: `LLM_Wiki_Project/raw/imports/outlook_emails.json`
- **Requirements**: Playwright must be installed. The user must not have 2FA blocks requiring manual intervention unless running in `--login` mode.
