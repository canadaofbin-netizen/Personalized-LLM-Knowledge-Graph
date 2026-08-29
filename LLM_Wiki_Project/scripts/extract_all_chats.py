import os
import glob
import json
from datetime import datetime

brain_dir = os.path.expanduser("~/.gemini/antigravity/brain")
output_dir = "./LLM_Wiki_Project/raw/assets"
log_file = "./LLM_Wiki_Project/raw/imports/.extract_all_log.json"

def load_log():
    if os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_log(log_data):
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2)

def extract_chats():
    log_data = load_log()
    processed_ids = set(log_data.get('processed_conversations', []))
    
    # Get all conversation directories
    conv_dirs = [d for d in os.listdir(brain_dir) if os.path.isdir(os.path.join(brain_dir, d)) and d != "Temp" and d != "tempmediaStorage"]
    
    new_conversations = 0
    total_chunks = 0
    
    for conv_id in conv_dirs:
        if conv_id in processed_ids:
            continue
            
        transcript_path = os.path.join(brain_dir, conv_id, ".system_generated", "logs", "transcript.jsonl")
        if not os.path.exists(transcript_path):
            # Try transcript_full.jsonl
            transcript_path = os.path.join(brain_dir, conv_id, ".system_generated", "logs", "transcript_full.jsonl")
            if not os.path.exists(transcript_path):
                processed_ids.add(conv_id) # Mark as processed so we don't keep checking empty dirs
                continue
                
        content = ""
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        step = json.loads(line)
                        if step.get('type') in ['USER_INPUT', 'PLANNER_RESPONSE']:
                            text = step.get('content', '')
                            if text:
                                speaker = "USER" if step.get('type') == 'USER_INPUT' else "AGENT"
                                content += f"### {speaker}\n{text}\n\n"
                    except:
                        pass
        except Exception as e:
            print(f"Error reading {conv_id}: {e}")
            continue
            
        if len(content.strip()) > 50:
            # We have substantive content, save it
            chunk_filename = f"archive_chat_{conv_id}.md"
            out_path = os.path.join(output_dir, chunk_filename)
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            md = f"""---
type: chat_extract
date: "{date_str}"
source: "Antigravity Chat Archive {conv_id}"
---

# Chat Archive: {conv_id}

{content}
"""
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(md)
                
            new_conversations += 1
            total_chunks += 1
            
        processed_ids.add(conv_id)
        
    log_data['processed_conversations'] = list(processed_ids)
    save_log(log_data)
    
    print(f"Extraction complete. Harvested {new_conversations} new conversations into {total_chunks} markdown files.")

if __name__ == "__main__":
    extract_chats()
