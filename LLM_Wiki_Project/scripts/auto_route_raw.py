import os
import shutil
from pathlib import Path

def auto_route_raw_files():
    base_dir = Path(__file__).parent.parent.resolve()
    raw_dir = base_dir / "raw"
    imports_dir = raw_dir / "imports"
    
    # Ensure imports directory exists
    imports_dir.mkdir(parents=True, exist_ok=True)
    
    moved_count = 0
    # Scan raw/ directory
    for item in raw_dir.iterdir():
        # Only process files in the root of raw/
        if item.is_file():
            dest = imports_dir / item.name
            
            # If a file with the same name exists in imports, append a number
            counter = 1
            while dest.exists():
                name_parts = item.stem.split('_dup')
                base_name = name_parts[0]
                dest = imports_dir / f"{base_name}_dup{counter}{item.suffix}"
                counter += 1
                
            shutil.move(str(item), str(dest))
            print(f"[Auto-Route] Moved '{item.name}' -> 'imports/{dest.name}'")
            moved_count += 1
            
    if moved_count == 0:
        print("[Auto-Route] No stray files found in raw/ root. Everything is clean.")
    else:
        print(f"[Auto-Route] Successfully moved {moved_count} file(s) to raw/imports/.")

if __name__ == "__main__":
    auto_route_raw_files()
