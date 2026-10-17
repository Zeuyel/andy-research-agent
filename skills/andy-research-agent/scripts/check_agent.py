#!/usr/bin/env python3
"""Validate the Andy Research Agent skill without external dependencies."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT / "SKILL.md",
    ROOT / "references/agent-contract.md",
    ROOT / "references/method-routing.md",
    ROOT / "references/evidence-policy.md",
    ROOT / "references/corpus-scope.md",
    ROOT / "references/evaluation-rubric.md",
]

errors = []
for path in required:
    if not path.exists():
        errors.append(f"missing: {path.relative_to(ROOT)}")

skill = ROOT / "SKILL.md"
if skill.exists():
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("SKILL.md missing YAML frontmatter")
    if not re.search(r"^name:\s*andy-research-agent\s*$", text, re.M):
        errors.append("frontmatter name mismatch")
    if not re.search(r"^description:\s*.+", text, re.M):
        errors.append("frontmatter description missing")
    for ref in (
        "references/agent-contract.md",
        "references/method-routing.md",
        "references/evidence-policy.md",
        "references/corpus-scope.md",
        "references/evaluation-rubric.md",
    ):
        if ref not in text:
            errors.append(f"SKILL.md does not link {ref}")

for path in required[1:]:
    if path.exists() and not path.read_text(encoding="utf-8").strip():
        errors.append(f"empty: {path.relative_to(ROOT)}")

if errors:
    print("[FAIL]")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)

print("[OK] andy-research-agent structure is valid")
print(f"[OK] checked {len(required)} required files")
