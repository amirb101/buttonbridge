"""PyInstaller entry point — keep minimal so analysis picks up ``buttonbridge``."""
from __future__ import annotations

from buttonbridge.__main__ import main

if __name__ == "__main__":
    main()
