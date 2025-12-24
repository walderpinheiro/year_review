#!/usr/bin/env python3
"""Entry point for Xbox authentication."""

import asyncio
import sys
sys.path.insert(0, '.')

from src.auth import Authenticator


def main():
    auth = Authenticator()
    try:
        asyncio.run(auth.authenticate())
    except KeyboardInterrupt:
        print("\nCancelled")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
