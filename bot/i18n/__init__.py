import json
from pathlib import Path

# Load translations
translations_dir = Path(__file__).parent

with open(translations_dir / "uk.json", "r", encoding="utf-8") as f:
    UK_MESSAGES = json.load(f)

with open(translations_dir / "en.json", "r", encoding="utf-8") as f:
    EN_MESSAGES = json.load(f)


def get_message(key: str, language: str = "uk") -> str:
    """Get translated message by key."""
    messages = UK_MESSAGES if language == "uk" else EN_MESSAGES
    return messages.get(key, key)
