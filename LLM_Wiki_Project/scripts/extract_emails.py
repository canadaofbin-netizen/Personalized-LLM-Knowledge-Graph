import json
import os
import re
import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.abspath(os.path.join(script_dir, ".."))
import_file = os.path.join(base_dir, "raw", "imports", "outlook_emails.json")
out_dir = os.path.join(base_dir, "raw", "assets", "emails")
log_file = os.path.join(base_dir, "raw", "imports", ".extract_emails_log.json")

def load_log():
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_log(log_data):
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2)

def clean_line(text):
    """Remove PUA glyphs (\ue000-\uf8ff) and other non-printable/control symbols."""
    cleaned = re.sub(r'[\ue000-\uf8ff]', '', text)
    cleaned = "".join(c for c in cleaned if c.isprintable() or c in '\n\t')
    return cleaned.strip()

def parse_email_metadata(preview, body):
    """
    Parse sender and subject/title cleanly from OWA preview_text and reading pane body.
    OWA message rows often contain:
      Line 0: glyph (\ue488, etc.)
      Line 1: avatar initials (e.g. 'JD', 'AS')
      Line 2: sender name (e.g. 'Jane Doe; Alex Smith')
      Line 3: subject/title (e.g. 'Project Architecture Review')
    """
    raw_lines = [l.strip() for l in preview.split('\n')]
    clean_lines = []
    ignored_phrases = {
        'reply', 'reply all', 'forward', 'summarise this email',
        'summarize this email', 'no preview is available.'
    }
    for l in raw_lines:
        c = clean_line(l)
        if c and c.lower() not in ignored_phrases:
            clean_lines.append(c)

    sender = "Unknown Sender"
    title = "Untitled Email"

    # Check for avatar initials: 1-3 letters alone on a line when more lines exist
    idx = 0
    if idx < len(clean_lines) and re.match(r'^[A-Za-z]{1,3}$', clean_lines[idx]) and len(clean_lines) > 1:
        idx += 1  # Skip avatar initials

    if idx < len(clean_lines):
        sender = clean_lines[idx]
        idx += 1

    if idx < len(clean_lines):
        title = clean_lines[idx]
    elif body:
        # Fall back to first non-empty line of body
        body_lines = [clean_line(l) for l in body.split('\n')]
        for bl in body_lines:
            if bl and bl.lower() not in ignored_phrases and bl != sender:
                title = bl[:80]
                break

    # If title still empty or looks like sender, try other lines
    if title == "Untitled Email" and len(clean_lines) == 1:
        title = clean_lines[0]

    # Clean double quotes for YAML safety
    sender = sender.replace('"', "'").strip()
    title = title.replace('"', "'").strip()

    # Limit lengths
    sender = sender[:60]
    title = title[:100]

    return sender, title

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

    log_data = load_log()
    processed_ids = set(log_data.get('processed_emails', []))

    extracted = 0
    for e in emails:
        eid = str(e.get("id", "unknown"))
        if eid in processed_ids:
            continue
            
        folder = e.get("folder", "unknown").replace('"', '')
        preview = e.get("preview_text", "")
        body = e.get("full_body", "")
        date = e.get("scraped_at", "")
        
        sender, title = parse_email_metadata(preview, body)

        safe_sender = "".join([c for c in sender if c.isalnum() or c.isspace()]).strip()
        safe_sender = re.sub(r'\s+', '_', safe_sender)[:20]

        safe_title = "".join([c for c in title if c.isalnum() or c.isspace()]).strip()
        safe_title = re.sub(r'\s+', '_', safe_title)[:30]

        safe_part = f"{safe_sender}_{safe_title}".strip("_")
        fname = f"Email_{eid}_{safe_part}.md" if safe_part else f"Email_{eid}.md"
        out_path = os.path.join(out_dir, fname)
        
        # Classify if sender or preview is automated newsletter
        is_newsletter = any(term in (sender + " " + preview).lower() for term in [
            'no-reply', 'noreply', 'notification', 'moodle', 'students union', 'newsletter', 'digest', 'announcements'
        ])
        email_tags = "tags: [email-newsletter]" if is_newsletter else "tags: [email-contact]"

        # Must include all schema.yaml required fields
        content = f"""---
type: email
title: "{title}"
description: "Extracted Outlook Email"
{email_tags}
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
        
        processed_ids.add(eid)
        extracted += 1

    log_data['processed_emails'] = list(processed_ids)
    save_log(log_data)
    
    print(f"Extracted {extracted} new emails to raw/assets/emails/")

if __name__ == "__main__":
    extract_emails()

