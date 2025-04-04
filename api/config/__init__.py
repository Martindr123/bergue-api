# app/config/__init__.py

import json
import os

# Si vous voulez que "from app.config import config" fonctionne, assurez-vous
# qu'une variable nommée "config" existe VRAIMENT ici.

CURRENT_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(CURRENT_DIR, "config.json")

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:
    print(f"[DEBUG] Erreur lors du chargement config.json: {e}")
    config = {}

# Optionnellement, vous pouvez déclarer __all__ :
__all__ = ["config"]
