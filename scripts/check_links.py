#!/usr/bin/env python3
"""URL 探活脚本：检查 data/resources.yaml 中所有 homepage 与 mirrors 的可用性。

只用标准库 + pyyaml。CI 中通过 `pip install pyyaml` 安装依赖。

用法：
    python scripts/check_links.py [--data data/resources.yaml]
                                  [--only <resource-id>]
                                  [--timeout 15]
                                  [--report report.json]
                                  [--strict]

退出码：0 = 全部 active URL 可达；1 = 有 active URL 不可达（--strict 下 degraded 也算失败）。
"""

import argparse
import concurrent.futures
import json
import sys
import urllib.request
from datetime import date

try:
    import yaml
except ImportError:
    sys.exit("需要 pyyaml：pip install pyyaml")


def check_url(url: str, timeout: int) -> dict:
    """返回 {'url', 'ok', 'status', 'final_url', 'error'}。"""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "reliable-resources-linkcheck/1.0"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {
                "url": url,
                "ok": True,
                "status": resp.status,
                "final_url": resp.url,
                "error": None,
            }
    except Exception as e:  # noqa: BLE001 - 探活需要捕获所有网络异常
        # HEAD 被拒时降级为 GET（有些站点不支持 HEAD）
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "reliable-resources-linkcheck/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                # 只读 1 字节，避免下载大文件
                resp.read(1)
                return {
                    "url": url,
                    "ok": True,
                    "status": resp.status,
                    "final_url": resp.url,
                    "error": None,
                }
        except Exception as e2:  # noqa: BLE001
            return {
                "url": url,
                "ok": False,
                "status": None,
                "final_url": None,
                "error": f"{type(e2).__name__}: {e2}",
            }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/resources.yaml")
    ap.add_argument("--only", default=None, help="只检查指定 resource id")
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--report", default=None, help="把 JSON 报告写到文件")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    targets = []  # (resource_id, label, url, status)
    for r in data.get("resources", []):
        if args.only and r["id"] != args.only:
            continue
        if r.get("status") == "dead":
            continue
        targets.append((r["id"], "homepage", r["homepage"], r.get("status")))
        for m in r.get("mirrors", []):
            targets.append((r["id"], "mirror", m["url"], r.get("status")))

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        future_map = {
            pool.submit(check_url, url, args.timeout): (rid, label, url, st)
            for rid, label, url, st in targets
        }
        for fut in concurrent.futures.as_completed(future_map):
            rid, label, url, st = future_map[fut]
            res = fut.result()
            res.update(
                {
                    "resource": rid,
                    "kind": label,
                    "resource_status": st,
                    "checked_at": date.today().isoformat(),
                }
            )
            results.append(res)

    failed = [
        r
        for r in results
        if not r["ok"] and (args.strict or r["resource_status"] == "active")
    ]

    report = {
        "checked_at": date.today().isoformat(),
        "total": len(results),
        "failed": len(failed),
        "results": sorted(results, key=lambda x: (x["resource"], x["kind"])),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    if failed:
        print("\n不可达的 active URL：", file=sys.stderr)
        for r in failed:
            print(f"  - [{r['resource']}] {r['url']}: {r['error']}", file=sys.stderr)
        return 1
    print("\n全部 active URL 可达。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
