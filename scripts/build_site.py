#!/usr/bin/env python3
"""把 data/resources.yaml 编译成 docs/data.json，供静态站点消费。

用法：python scripts/build_site.py [--data data/resources.yaml] [--out docs/data.json]
"""

import argparse
import json
import sys
from datetime import date


try:
    import yaml
except ImportError:
    sys.exit("需要 pyyaml：pip install pyyaml")


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
    payload = to_jsonable(
        {
            "version": data.get("version", 1),
            "updated_at": data.get("updated_at", date.today().isoformat()),
            "generated_at": date.today().isoformat(),
            "count": len(resources),
            "resources": resources,
        }
    )
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"wrote {args.out} ({len(resources)} resources)")


if __name__ == "__main__":
    main()
