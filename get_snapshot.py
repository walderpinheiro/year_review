#!/usr/bin/env python3
"""Entry point for generating achievement snapshot."""

import asyncio
import sys
sys.path.insert(0, '.')

from src.snapshot import create_snapshot
from src.config import DEFAULT_MAX_GAMES


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    max_games = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MAX_GAMES
    
    try:
        if target:
            if target.isdigit():
                asyncio.run(create_snapshot(target_xuid=target, max_games=max_games))
            else:
                asyncio.run(create_snapshot(target_gamertag=target, max_games=max_games))
        else:
            asyncio.run(create_snapshot(max_games=max_games))
    except FileNotFoundError:
        print("Error: tokens not found. Run authenticate.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

