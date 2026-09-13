# ingestor.py
"""
CLI entrypoint and queue inspector for Wiki Ingestion.
Scans raw/assets/ for pending ingestion queue, analyzes file sizes for adaptive dispatch
(Large >= 15KB/200 lines vs Small < 15KB/200 lines), and forwards reduce calls.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_ASSETS = os.path.join(BASE_DIR, "raw", "assets")

def check_queue():
    if not os.path.exists(RAW_ASSETS):
        print(f"Directory not found: {RAW_ASSETS}")
        return []

    pending = []
    for root, _, files in os.walk(RAW_ASSETS):
        for f in files:
            if f.endswith(".md") or f.endswith(".txt"):
                pending.append(os.path.join(root, f))
    return pending

def main():
    args = sys.argv[1:]
    if args and args[0] == "--reduce":
        # Forward to reduce.py
        import reduce
        reduce.main()
        return

    pending = check_queue()
    print(f"=== Wiki Ingestion Queue Status ===")
    print(f"Pending raw files in raw/assets/: {len(pending)}")

    large_files = []
    small_files = []

    for fpath in pending:
        size_kb = os.path.getsize(fpath) / 1024
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                lines = len(f.readlines())
        except Exception:
            lines = 0

        rel = os.path.relpath(fpath, RAW_ASSETS)
        if size_kb >= 15 or lines >= 200:
            large_files.append((rel, size_kb, lines))
        else:
            small_files.append((rel, size_kb, lines))

    print(f"\nAdaptive Dispatch Breakdown:")
    print(f"- Large Files (1:1 dedicated subagent, >=15KB or >=200 lines): {len(large_files)}")
    for rel, sz, ln in large_files[:5]:
        print(f"    * {rel} ({sz:.1f} KB, {ln} lines)")
    if len(large_files) > 5:
        print(f"    ... and {len(large_files) - 5} more")

    print(f"- Small Files (1:N bundled up to 10 files/50KB, <15KB and <200 lines): {len(small_files)}")
    for rel, sz, ln in small_files[:5]:
        print(f"    * {rel} ({sz:.1f} KB, {ln} lines)")
    if len(small_files) > 5:
        print(f"    ... and {len(small_files) - 5} more")

    print("\nTo run the map-reduce pipeline, follow .agents/skills/ingest/SKILL.md")

if __name__ == "__main__":
    main()
