#!/usr/bin/env python3
"""URL 探活脚本：检查 data/resources.yaml 中所有 homepage 与 mirrors 的可用性。

探活范围（诚实声明）：只验证 URL 可达（HTTP 200/3xx 跟随跳转后），不验证下载文件
完整性/安全性、版本号正确性、环境兼容性。这些需要人工审核，用户请自行判断。

失败累计与自动降级（"持续验证"闭环）：
    --state data/link-health.json   启用失败计数持久化（文件不存在则新建）
    --apply-degrade                 达到阈值时自动把 resources.yaml 对应条目标记 degraded
规则：
  - homepage 连续 2 次探活失败  →  status: active → degraded（同时同步顶层 updated_at）
  - HTTP 403 / TLS 错误视为"无法判断"（反爬虫拒绝探活 / 需另行复验），
    不计入连续失败、不触发降级；这类站点可用 probe_url 指定官方 API/页面
    作为替代存活信号（见 SCHEMA）
  - mirror 失败只记录进 state，不触发整站降级（镜像坏了不代表主站坏了）
  - 探活成功则清零该 URL 的失败计数；degraded → active 的恢复必须人工操作（防抖动）
  - status 已是 degraded/dead 的条目仍会被探活（用于计数清零），但不再自动改状态
  - state 文件只在 --apply-degrade 同时给出时才写回（PR 检查只报告、不写状态）

CI 用法（.github/workflows/link-check.yml）：
  定时/手动触发：python scripts/check_links.py --state data/link-health.json --apply-degrade --report link-report.json
  PR 检查：      python scripts/check_links.py --report link-report.json

只用标准库 + pyyaml。CI 中通过 `pip install pyyaml` 安装依赖。

用法：
    python scripts/check_links.py [--data data/resources.yaml]
                                  [--only <resource-id>]
                                  [--timeout 15]
                                  [--report report.json]
                                  [--state link-health.json]
                                  [--apply-degrade]
                                  [--strict]

退出码：0 = 无不可达的 active URL（"无法判断"不计入失败）；1 = 有 active URL 不可达（--strict 下 degraded 也算失败）。
"""

import argparse
import concurrent.futures
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.request
from datetime import date

try:
    import yaml
except ImportError:
    sys.exit("需要 pyyaml：pip install pyyaml")

DEGRADE_THRESHOLD = 2  # homepage 连续失败达到此次数 → degraded

# 用浏览器 UA 做探活：部分站点会拦截非浏览器 UA 的请求导致误判。
# 探活仍只做可达性检查，不伪装成真实用户行为。
PROBE_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _is_tls_error(exc: BaseException) -> bool:
    """判断异常是否为 TLS/证书类错误（需另行复验，不能判定网站失效）。"""
    if isinstance(exc, ssl.SSLError):
        return True
    reason = getattr(exc, "reason", None)
    if isinstance(reason, ssl.SSLError):
        return True
    text = f"{type(exc).__name__} {exc} {type(reason).__name__} {reason}".lower()
    return any(k in text for k in ("ssl", "tls", "certificate"))


def _result(url, ok, status, final_url, error, tls_error=False):
    return {
        "url": url,
        "ok": ok,
        "status": status,
        "final_url": final_url,
        "error": error,
        # blocked=True：HTTP 403，站点存在但拒绝探活（反爬虫）。
        # tls_error=True：TLS/证书错误，需另行复验。
        # 两者都是"无法判断"而非"失效"，不计入降级所需的连续失败。
        "blocked": (status == 403 and not ok),
        "tls_error": (tls_error and not ok),
    }


def check_url(url: str, timeout: int) -> dict:
    """返回 {'url', 'ok', 'status', 'final_url', 'error', 'blocked', 'tls_error'}。"""
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(
            url, headers={"User-Agent": PROBE_UA}, method=method
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if method == "GET":
                    resp.read(1)  # 只读 1 字节，避免下载大文件
                return _result(url, True, resp.status, resp.url, None)
        except urllib.error.HTTPError as e:
            if method == "HEAD":
                continue  # HEAD 被拒，降级为 GET 再试
            return _result(url, False, e.code, None, f"HTTP {e.code}")
        except Exception as e2:  # noqa: BLE001 - 探活需要捕获所有网络异常
            if method == "HEAD":
                continue
            return _result(
                url, False, None, None,
                f"{type(e2).__name__}: {e2}",
                tls_error=_is_tls_error(e2),
            )


def load_state(path: str) -> dict:
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"updated_at": None, "entries": {}}


def apply_degrade_to_yaml(data_path: str, resource_ids: set, today: str) -> list:
    """Surgical 文本替换：只改目标条目的 `status: active` → `status: degraded`，
    并同步更新顶层 `updated_at`（数据变了，日期也要变）。

    不用 yaml.dump 重写整个文件，避免注释丢失和大面积重排。
    返回实际被修改的 resource id 列表。
    """
    with open(data_path, encoding="utf-8") as f:
        lines = f.readlines()

    pending = set(resource_ids)
    current_id = None
    changed = []
    out = []
    for line in lines:
        # 顶层 updated_at（无缩进）：数据变更则同步到今天
        if re.match(r"^updated_at:\s*\S+\s*$", line):
            out.append(f"updated_at: {today}\n")
            continue
        m = re.match(r"^(\s*)- id:\s*(\S+)\s*$", line)
        if m:
            current_id = m.group(2)
        if (
            current_id in pending
            and re.match(r"^(\s*)status:\s*active\s*$", line)
        ):
            indent = re.match(r"^(\s*)", line).group(1)
            out.append(f"{indent}status: degraded\n")
            changed.append(current_id)
            pending.discard(current_id)
            continue
        out.append(line)

    if changed:
        with open(data_path, "w", encoding="utf-8") as f:
            f.writelines(out)
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/resources.yaml")
    ap.add_argument("--only", default=None, help="只检查指定 resource id")
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--report", default=None, help="把 JSON 报告写到文件")
    ap.add_argument("--state", default=None, help="失败计数状态文件（如 data/link-health.json）")
    ap.add_argument(
        "--apply-degrade",
        action="store_true",
        help="达到阈值时自动降级 resources.yaml 中的 status（需同时给 --state）",
    )
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    today = date.today().isoformat()
    state = load_state(args.state) if args.state else {"entries": {}}
    entries = state.setdefault("entries", {})

    with open(args.data, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    resources = {r["id"]: r for r in data.get("resources", [])}
    targets = []  # (resource_id, label, url, status)
    for r in data.get("resources", []):
        if args.only and r["id"] != args.only:
            continue
        if r.get("status") == "dead":
            continue
        # probe_url：反爬虫站点用官方 API/页面作为存活信号（见 SCHEMA）
        probe = r.get("probe_url") or r["homepage"]
        targets.append((r["id"], "homepage", probe, r.get("status")))
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
                    "checked_at": today,
                }
            )
            results.append(res)

    # 更新失败计数
    degrade_candidates = set()
    for r in results:
        key = f"{r['resource']}::{r['url']}"
        e = entries.setdefault(
            key,
            {
                "resource": r["resource"],
                "kind": r["kind"],
                "url": r["url"],
                "consecutive_failures": 0,
                "last_check": None,
                "last_ok": None,
                "last_error": None,
            },
        )
        e["last_check"] = today
        if r["ok"]:
            e["consecutive_failures"] = 0
            e["last_ok"] = today
            e["last_error"] = None
            e["blocked_hits"] = 0
            e["tls_hits"] = 0
        elif r.get("blocked") or r.get("tls_error"):
            # 无法判断：403（反爬虫拒绝探活）或 TLS 错误（需另行复验），
            # 不计入连续失败、不触发降级
            key = "blocked_hits" if r.get("blocked") else "tls_hits"
            e[key] = e.get(key, 0) + 1
            e["last_inconclusive"] = today
            e["inconclusive_reason"] = (
                "blocked-403" if r.get("blocked") else "tls-error"
            )
            e["last_error"] = r["error"]
        else:
            e["consecutive_failures"] = e.get("consecutive_failures", 0) + 1
            e["last_error"] = r["error"]
            # 只有 homepage 的连续失败能触发整站降级
            if (
                r["kind"] == "homepage"
                and e["consecutive_failures"] >= DEGRADE_THRESHOLD
                and resources.get(r["resource"], {}).get("status") == "active"
            ):
                degrade_candidates.add(r["resource"])

    # 自动降级（surgical 改 yaml）
    degraded_now = []
    if args.apply_degrade and args.state and degrade_candidates:
        degraded_now = apply_degrade_to_yaml(args.data, degrade_candidates, today)

    # 写回 state（只在 --apply-degrade 时，避免 PR 检查污染状态）
    if args.apply_degrade and args.state:
        state["updated_at"] = today
        with open(args.state, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"状态已写回 {args.state}")

    failed = [
        r
        for r in results
        if not r["ok"]
        and not r.get("blocked")  # 403 只是探活被拒，不算失败
        and not r.get("tls_error")  # TLS 错误需另行复验，不算失败
        and (args.strict or r["resource_status"] == "active")
    ]

    report = {
        "checked_at": today,
        "total": len(results),
        "failed": len(failed),
        "blocked": sum(1 for r in results if r.get("blocked")),
        "tls_errors": sum(1 for r in results if r.get("tls_error")),
        "degraded_now": sorted(degraded_now),
        "results": sorted(results, key=lambda x: (x["resource"], x["kind"])),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    if degraded_now:
        print(f"\n自动降级（连续 {DEGRADE_THRESHOLD} 次失败）：{', '.join(sorted(degraded_now))}")
    if failed:
        print("\n不可达的 active URL：", file=sys.stderr)
        for r in failed:
            print(f"  - [{r['resource']}] {r['url']}: {r['error']}", file=sys.stderr)
        return 1
    inconclusive = [r for r in results if r.get("blocked") or r.get("tls_error")]
    if inconclusive:
        print(f"\n{len(inconclusive)} 个 URL 无法判断（不计入失败），其余 active URL 可达：")
        for r in inconclusive:
            reason = "403 拒绝探活" if r.get("blocked") else "TLS 错误，需人工复验"
            print(f"  - [{r['resource']}] {r['url']}: {reason}（{r['error']}）")
        return 0
    print("\n全部 active URL 可达。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
