#!/usr/bin/env python3
"""Create a new candidate module for incremental research knowledge."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    parser = argparse.ArgumentParser(description="Create a candidate research-workflow module")
    parser.add_argument("slug", help="lowercase hyphen-case module name")
    parser.add_argument("title", help="human-readable module title")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.slug):
        parser.error("slug must use lowercase hyphen-case")
    path = ROOT / "references" / f"{args.slug}.md"
    if path.exists():
        parser.error(f"module already exists: {path}")
    path.write_text(
        f"# {args.title}\n\n"
        "状态：候选；补充直接来源并完成任务验证后再升级。\n\n"
        "## 触发与范围\n\n- 触发：\n- 输入：\n- 输出：\n- 失败模式与边界：\n\n"
        "## 知识记录\n\n"
        "待按 references/expansion-protocol.md 填写问题、方法、步骤、证据和复核日期。\n",
        encoding="utf-8",
    )
    print(path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
