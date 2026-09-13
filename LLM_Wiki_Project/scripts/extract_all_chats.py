import os
import glob
import json
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
CUSTOM_TRANSCRIPT_DIR = os.environ.get("AGENT_TRANSCRIPT_DIR", "").strip()
if CUSTOM_TRANSCRIPT_DIR:
    brain_dir = os.path.expanduser(CUSTOM_TRANSCRIPT_DIR)
else:
    brain_dir = os.path.expanduser("~/.gemini/antigravity/brain")
output_dir = os.path.join(project_dir, "raw", "assets")
processed_dir = os.path.join(project_dir, "raw", "processed")
log_file = os.path.join(project_dir, "raw", "imports", ".extract_all_log.json")

SUBAGENT_SIGNATURES = [
    "Domain Semantic Auditor", "Read all `.md` files", "Find hidden semantic duplicates",
    "You are an Ingest Mapper", "ingest_mapper", "Proactive Research Hunter",
    "proactive_hunter", "drive_scanner"
]

def load_log():
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"Warning loading log: {e}")
    return {}

def save_log(log_data):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

def migrate_legacy_log(log_data):
    """
    Migrate old flat 'processed_conversations' list to structured metadata dict.
    Ensures conversations that were marked processed without ever being archived
    (or conversations with subsequent new activity) are properly recognized.
    """
    conversations = log_data.get('conversations', {})
    subagents = set(log_data.get('subagents', []))
    legacy_ids = set(log_data.get('processed_conversations', []))
    
    if legacy_ids and not conversations:
        print(f"Migrating legacy log with {len(legacy_ids)} processed conversation IDs...")
        for cid in legacy_ids:
            arch_files = glob.glob(os.path.join(processed_dir, f"archive_chat_{cid}*.md")) + \
                         glob.glob(os.path.join(output_dir, f"archive_chat_{cid}*.md"))
            
            t_path = os.path.join(brain_dir, cid, ".system_generated", "logs", "transcript.jsonl")
            if not os.path.exists(t_path):
                t_path = os.path.join(brain_dir, cid, ".system_generated", "logs", "transcript_full.jsonl")
                
            if not os.path.exists(t_path):
                subagents.add(cid)
                continue
                
            try:
                t_mtime = os.path.getmtime(t_path)
            except:
                t_mtime = 0.0

            if arch_files:
                arch_mtime = max(os.path.getmtime(f) for f in arch_files)
                try:
                    with open(t_path, 'r', encoding='utf-8') as tf:
                        total_lines = sum(1 for _ in tf)
                except:
                    total_lines = 0

                if t_mtime > arch_mtime + 60:
                    # Subsequent chat activity occurred after archival
                    conversations[cid] = {
                        "last_line": 0,
                        "parts_count": len(arch_files),
                        "last_mtime": arch_mtime
                    }
                else:
                    conversations[cid] = {
                        "last_line": total_lines,
                        "parts_count": len(arch_files),
                        "last_mtime": t_mtime
                    }
            else:
                # No archive file was ever created
                is_subagent = False
                try:
                    with open(t_path, 'r', encoding='utf-8') as tf:
                        sample = tf.read(8192)
                        if any(sig in sample for sig in SUBAGENT_SIGNATURES):
                            is_subagent = True
                except:
                    pass

                if is_subagent:
                    subagents.add(cid)
                else:
                    conversations[cid] = {
                        "last_line": 0,
                        "parts_count": 0,
                        "last_mtime": 0.0
                    }

        log_data['conversations'] = conversations
        log_data['subagents'] = list(subagents)
        log_data.pop('processed_conversations', None)
        save_log(log_data)
        print("Legacy log migration complete.")
        
    return log_data

def extract_chats():
    log_data = load_log()
    log_data = migrate_legacy_log(log_data)
    
    conversations = log_data.setdefault('conversations', {})
    subagents = set(log_data.setdefault('subagents', []))
    
    conv_dirs = [d for d in os.listdir(brain_dir) if os.path.isdir(os.path.join(brain_dir, d)) and d not in ["Temp", "tempmediaStorage"]]
    
    new_conversations = 0
    total_chunks = 0
    
    for conv_id in conv_dirs:
        if conv_id in subagents:
            continue
            
        transcript_path = os.path.join(brain_dir, conv_id, ".system_generated", "logs", "transcript.jsonl")
        if not os.path.exists(transcript_path):
            transcript_path = os.path.join(brain_dir, conv_id, ".system_generated", "logs", "transcript_full.jsonl")
            if not os.path.exists(transcript_path):
                subagents.add(conv_id)
                continue

        try:
            current_mtime = os.path.getmtime(transcript_path)
        except:
            current_mtime = 0.0

        conv_meta = conversations.get(conv_id, {})
        last_line = conv_meta.get("last_line", 0)
        last_mtime = conv_meta.get("last_mtime", 0.0)
        parts_count = conv_meta.get("parts_count", 0)

        # Fast skip if mtime is unchanged and lines were already read
        if last_line > 0 and current_mtime <= last_mtime:
            continue

        new_content = ""
        current_line_count = 0
        is_subagent = False
        start_step = None
        end_step = None

        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                for idx, line in enumerate(f):
                    current_line_count += 1
                    if idx < last_line:
                        continue
                    
                    if not line.strip():
                        continue
                    try:
                        step = json.loads(line)
                        step_idx = step.get('step_index', idx)
                        content_text = step.get('content', '')
                        # Only detect subagents on the very first prompt of a new conversation
                        if parts_count == 0 and idx < 5 and step.get('type') == 'USER_INPUT' and step.get('source') != 'USER_EXPLICIT':
                            if any(sig in content_text for sig in SUBAGENT_SIGNATURES):
                                is_subagent = True
                                break
                            
                        if step.get('type') in ['USER_INPUT', 'PLANNER_RESPONSE']:
                            if content_text:
                                speaker = "USER" if step.get('type') == 'USER_INPUT' else "AGENT"
                                new_content += f"### {speaker}\n{content_text}\n\n"
                                if start_step is None:
                                    start_step = step_idx
                                end_step = step_idx
                    except:
                        pass
        except Exception as e:
            print(f"Error reading {conv_id}: {e}")
            continue

        if is_subagent:
            subagents.add(conv_id)
            continue

        if len(new_content.strip()) > 50:
            parts_count += 1
            if parts_count == 1:
                chunk_filename = f"archive_chat_{conv_id}.md"
                title_header = f"# Chat Archive: {conv_id}"
            else:
                chunk_filename = f"archive_chat_{conv_id}_part{parts_count}.md"
                title_header = f"# Chat Archive Continuation (Part {parts_count}): {conv_id}"
                
            out_path = os.path.join(output_dir, chunk_filename)
            date_str = datetime.now().strftime("%Y-%m-%d")
            
            md = f"""---
type: chat_extract
date: "{date_str}"
source: "Antigravity Chat Archive {conv_id} (part {parts_count})"
conversation_id: "{conv_id}"
part: {parts_count}
step_range: [{start_step if start_step is not None else 0}, {end_step if end_step is not None else 0}]
---

{title_header}

{new_content}
"""
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(md)
                
            new_conversations += 1
            total_chunks += 1
            
            conversations[conv_id] = {
                "last_line": current_line_count,
                "parts_count": parts_count,
                "last_mtime": current_mtime,
                "last_extracted_at": datetime.now().isoformat()
            }
        else:
            if conv_id not in conversations:
                conversations[conv_id] = {
                    "last_line": current_line_count,
                    "parts_count": parts_count,
                    "last_mtime": current_mtime,
                    "last_extracted_at": datetime.now().isoformat()
                }
            else:
                conversations[conv_id]["last_line"] = current_line_count
                conversations[conv_id]["last_mtime"] = current_mtime

    log_data['conversations'] = conversations
    log_data['subagents'] = list(subagents)
    save_log(log_data)
    
    print(f"Extraction complete. Harvested {new_conversations} updated/new conversations into {total_chunks} markdown files.")

if __name__ == "__main__":
    extract_chats()

