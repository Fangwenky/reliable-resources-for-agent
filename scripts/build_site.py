#!/usr/bin/env python3
"""把 data/resources.yaml 编译成 docs/data.json，供静态站点消费。

用法：python scripts/build_site.py [--data data/resources.yaml] [--out docs/data.json]
"""

import argparse
import json
import os
import re
import sys
from datetime import date


try:
    import yaml
except ImportError:
    sys.exit("需要 pyyaml：pip install pyyaml")


def read_skill_version(repo_root: str) -> str:
    """从 skills/reliable-resources/SKILL.md 的 frontmatter 读取 version。

    数据里带的 skill_version 与 skill 本体永远一致，改 skill 时只需改一处。
    """
    p = os.path.join(repo_root, "skills", "reliable-resources", "SKILL.md")
    try:
        with open(p, encoding="utf-8") as f:
            lines = f.read().splitlines()
        if lines and lines[0].strip() == "---":
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                m = re.match(r'^version:\s*["\']?([^"\'\s]+)', line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return "1.0.0"


def to_jsonable(obj):
    """把 date/datetime 转成 ISO 字符串，其余原样。"""
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(v) for v in obj]
    return obj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/resources.yaml")
    ap.add_argument("--out", default="docs/data.json")
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    resources = data.get("resources", [])
    today = date.today().isoformat()
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(args.data)))
    base = {
        "version": data.get("version", 1),
        "updated_at": data.get("updated_at", today),
        "generated_at": today,
        "skill_version": read_skill_version(repo_root),
    }

    # 全量数据
    payload = to_jsonable({**base, "count": len(resources), "resources": resources})
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"wrote {args.out} ({len(resources)} resources)")

    # 按分类拆分：Agent 按需拉取，避免全量传输
    out_dir = os.path.dirname(os.path.abspath(args.out))
    api_dir = os.path.join(out_dir, "api", "by-category")
    os.makedirs(api_dir, exist_ok=True)

    by_cat: dict[str, list] = {}
    for r in resources:
        by_cat.setdefault(r.get("category") or "other", []).append(r)

    for cat in sorted(by_cat):
        rs = by_cat[cat]
        cat_payload = to_jsonable(
            {**base, "category": cat, "count": len(rs), "resources": rs}
        )
        cat_path = os.path.join(api_dir, f"{cat}.json")
        with open(cat_path, "w", encoding="utf-8") as f:
            json.dump(cat_payload, f, ensure_ascii=False, indent=2)
        print(f"wrote {cat_path} ({len(rs)} resources)")

    # 分类索引
    index_payload = to_jsonable(
        {**base, "categories": sorted(by_cat), "counts": {c: len(v) for c, v in sorted(by_cat.items())}}
    )
    index_path = os.path.join(out_dir, "api", "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_payload, f, ensure_ascii=False, indent=2)
    print(f"wrote {index_path} ({len(by_cat)} categories)")


if __name__ == "__main__":
    main()
