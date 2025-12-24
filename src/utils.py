"""Utility functions."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .config import TOKENS_FILE, OUTPUT_DIR


def load_json(filepath: Path) -> dict:
    """Load JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict, filepath: Path) -> None:
    """Save data to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_tokens() -> dict:
    """Load authentication tokens."""
    return load_json(TOKENS_FILE)


def save_tokens(tokens: dict) -> None:
    """Save authentication tokens."""
    save_json(tokens, TOKENS_FILE)


def tokens_exist() -> bool:
    """Check if tokens file exists."""
    return TOKENS_FILE.exists()


def format_hours(hours: float) -> str:
    """Format hours in Brazilian format (1.234,5)."""
    return f"{hours:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_number(num: int) -> str:
    """Format number in Brazilian format (1.234)."""
    return f"{num:,}".replace(",", ".")


def parse_iso_date(date_str: str) -> Optional[datetime]:
    """Parse ISO date string to datetime."""
    if not date_str or date_str.startswith("0001"):
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def get_year_from_date(date_str: str) -> Optional[str]:
    """Extract year from date string."""
    if date_str and len(date_str) >= 4:
        return date_str[:4]
    return None


def get_month_key(date_str: str) -> Optional[str]:
    """Extract YYYY-MM from date string."""
    dt = parse_iso_date(date_str)
    if dt:
        return dt.strftime("%Y-%m")
    return None


def save_snapshot(data: dict, gamertag: str) -> tuple[Path, Path]:
    """Save snapshot with timestamp and latest version."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    timestamped = OUTPUT_DIR / f"achievements_snapshot_{gamertag}_{timestamp}.json"
    latest = OUTPUT_DIR / f"achievements_snapshot_{gamertag}_latest.json"
    
    save_json(data, timestamped)
    save_json(data, latest)
    
    return timestamped, latest

