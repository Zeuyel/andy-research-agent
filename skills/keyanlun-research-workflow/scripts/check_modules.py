#!/usr/bin/env python3
"""Validate the dynamic module registry and linked files."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "references" / "module-registry.md"

def main() -> int:
    text = REGISTRY.read_text(encoding="utf-8")
    paths = re.findall(r"`([^`]+\.md)`", text)
    errors = []
    for name in paths:
        path = ROOT / "references" / name
        if not path.exists():
            errors.append(f"missing module: {name}")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n") or "name: keyanlun-research-workflow" not in skill:
        errors.append("invalid SKILL.md frontmatter")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"ok: {len(paths)} indexed module references")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
