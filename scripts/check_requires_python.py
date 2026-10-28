#!/usr/bin/env python3
"""Fail if pyproject.toml declares an impossible requires-python range.

This catches typos like ">=3.19" (no Python version satisfies it) that
tomllib parses fine but pip rejects at install time.
"""

import re
import sys
import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def main() -> int:
    with PYPROJECT.open("rb") as f:
        data = tomllib.load(f)

    req = data.get("project", {}).get("requires-python")
    if req is None:
        print("ERROR: requires-python is missing from [project]")
        return 1

    m = re.fullmatch(r">=\s*3\.(\d+)(?:,\s*<4)?", req.strip())
    if not m:
        print(f"ERROR: requires-python = {req!r} does not match '>=3.X,<4'")
        return 1

    minor = int(m.group(1))
    MIN_MINOR = 10
    max_plausible = max(sys.version_info.minor + 2, 15)
    if not (MIN_MINOR <= minor <= max_plausible):
        print(
            f"ERROR: requires-python minor {minor} not in "
            f"[{MIN_MINOR}, {max_plausible}] (impossible or EOL)"
        )
        return 1

    print(f"OK: requires-python = {req!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
