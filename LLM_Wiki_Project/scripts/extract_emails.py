import json
import os
import re
import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(script_dir, ".."))
import_file = os.path.join(base_dir, "raw", "imports", "outlook_emails.json")
out_dir = os.path.join(base_dir, "raw", "assets", "emails")

def extract_emails():
    if not os.path.exists(import_file):
        print("outlook_emails.json not found.")
        return
        
    os.makedirs(out_dir, exist_ok=True)
    
    with open(import_file, "r", encoding="utf-8") as f:
        try:
            emails = json.load(f)
        except json.JSONDecodeError:
            print("Failed to decode JSON.")
            return

    extracted = 0
    for e in emails:
        eid = e.get("id", "unknown")
        folder = e.get("folder", "unknown").replace('"', '')
        preview = e.get("preview_text", "").replace('"', "'")
        body = e.get("full_body", "")
        date = e.get("scraped_at", "")
        
        sender = "Unknown Sender"
        if "\n" in preview:
            sender = preview.split('\n')[0][:50]
            
        safe_preview = "".join([c for c in preview if c.isalnum() or c.isspace()]).strip()
        safe_preview = re.sub(r'\s+', '_', safe_preview)[:30]
        
        # Ensure it has a valid title for the filename and YAML
        title = preview.split(chr(10))[0] if chr(10) in preview else preview[:50]
        
        fname = f"Email_{eid}_{safe_preview}.md"
        out_path = os.path.join(out_dir, fname)
        
        # Must include all schema.yaml required fields
        content = f"""---
type: email
title: "{title}"
description: "Extracted Outlook Email"
tags: [email-contact]
timestamp: "{datetime.datetime.now().strftime("%Y-%m-%d")}"
sources: ["outlook_emails.json"]
sender: "{sender}"
date: "{date}"
folder: "{folder}"
sentiment: "neutral"
domain: personal
---
# {title}

{body}
"""
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(content)
        extracted += 1

    print(f"Extracted {extracted} emails to raw/assets/emails/")

if __name__ == "__main__":
    extract_emails()
