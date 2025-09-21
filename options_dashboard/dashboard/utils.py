import os
from datetime import datetime
from django.conf import settings
from pathlib import Path

# Update this path to match your current project structure
print("Current director:",Path(__file__).resolve())
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "12Dec-Nifty/"
SPOT_CSV = BASE_DIR / "nifty_underlying.csv"

# ...existing code...

def list_option_files():
    files = []
    for file in os.listdir(DATA_DIR):
        if not file.endswith('.csv'):
            continue

        parts = file.replace('.csv', '').split('_')
        if len(parts) != 3:
            continue

        try:
            strike = int(parts[0])
            opt_type = parts[1].lower()
            expiry = parts[2]
            if opt_type not in ['call', 'put']:
                continue

            files.append({
                'path': os.path.join(DATA_DIR, file),
                'strike': strike,
                'type': opt_type,
                'expiry': expiry,
                'filename': file
            })
        except:
            continue
    return files
