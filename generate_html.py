#!/usr/bin/env python3
"""Entry point for generating HTML review."""

import sys
sys.path.insert(0, '.')

from src.html_generator import generate_html


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_html.py <snapshot_file>")
        print("Example: python generate_html.py achievements_snapshot_Gamertag_latest.json")
        sys.exit(1)
    
    try:
        path = generate_html(sys.argv[1])
        print(f"Generated: {path}")
    except FileNotFoundError as e:
        print(f"Error: file not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

