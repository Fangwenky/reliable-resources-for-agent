---
name: reliable-resources
description: Query a human-verified registry of trustworthy internet resources (official homepages and working mirrors) to avoid phishing clones and AI hallucinations. Use when the user asks for the official or latest working address of a resource (e.g. "z-lib 最新地址"), or when an agent task needs a reliable source URL instead of trusting raw search results.
---

# Reliable Resources for Agent

> 🌐 中文版见下方 · Chinese version below

## English

This skill provides a **human-reviewed, continuously verified** registry of trustworthy internet resources.
It solves one core problem: an "official address" taken from a search engine may be a phishing clone or a dead domain, leading to hallucinations and malicious injection.

Data source: `data/resources.yaml` in this repo (single source of truth); field definitions in `data/SCHEMA.md`. Resource names and descriptions are bilingual (`name`/`description` in Chinese, `name_en`/`description_en` in English) — present them in the user's language.

### Workflow

1. **Locate the resource**: search `data/resources.yaml` by `id` / `name` / `name_en` / `tags`.
   If not found → honestly tell the user it is "not yet in the registry", **never invent an address**. You may suggest they file a listing request per `CONTRIBUTING.md`.

2. **Pick an address** (highest priority first):
   - Only `status: active` entries may be used directly; `degraded` requires a risk warning; `dead` must never be used.
   - Prefer `homepage` (the official homepage); when a mirror is needed, pick from `mirrors` one with healthy `status` and a `region` matching the user's network (e.g. `cn-direct` for users in China).
   - Check `last_verified` / `verified_at`: if a mirror hasn't been verified for over 90 days, probe it once before handing it to the user.

3. **When presenting to the user, always include**:
   - The URL being used
   - The entry's `verification.evidence` (one-line basis of trust)
   - If `listing_type` is `reference` (anti-phishing listing), explicitly state: "this address is for authenticity checks only; the registry does not endorse it"
   - If `risk: gray-area`, explicitly warn about copyright/compliance risks

4. **Prohibited**:
   - Inventing or guessing mirror addresses
   - Using URL shorteners or redirect links
   - Serving a `dead` address as if it were usable

### Reporting dead or phishing URLs

- Health-check failure: open an issue in this repo with the resource `id` and the dead URL; maintainers will handle the status transition per `SCHEMA.md`.
- Phishing clone found: open an issue with evidence (clone domain, technique); once confirmed it is recorded in the resource's `note` as a warning.

### Contributing new resources

Follow the verification process in `CONTRIBUTING.md`: new mirrors need official-channel backing or maintainer testing + cross-verification. `unverified` entries are not accepted.

---

## 中文

本 skill 提供一份**人工审核、持续验证**的可信互联网资源库。
解决的核心问题：AI 从搜索引擎拿到的"官网地址"可能是钓鱼仿冒站，或已失效的旧域名，导致幻觉与恶意注入。

数据源：本仓库 `data/resources.yaml`（single source of truth），字段定义见 `data/SCHEMA.md`。资源名称与描述为双语（`name`/`description` 中文，`name_en`/`description_en` 英文）——按用户的语言呈现。

### 使用流程

1. **定位资源**：在 `data/resources.yaml` 中按 `id` / `name` / `name_en` / `tags` 查找。
   找不到 → 如实告知用户"库中暂未收录"，**不要编造地址**，可建议用户按 `CONTRIBUTING.md` 提交收录申请。

2. **选择地址**（优先级从高到低）：
   - `status: active` 的条目才可直接使用；`degraded` 必须向用户说明风险；`dead` 不得使用。
   - 优先 `homepage`（官方主页）；需要镜像时从 `mirrors` 中选 `status` 正常且 `region` 匹配用户网络环境的条目（如国内用户优先 `cn-direct`）。
   - 检查 `last_verified` / `verified_at` 日期：超过 90 天未验证的镜像，先做一次连通性探活再交给用户。

3. **呈现给用户时必须包含**：
   - 使用的 URL
   - 该条目的 `verification.evidence`（一句话验证依据）
   - 如 `listing_type` 为 `reference`（防伪收录），必须明确说明"该地址仅用于辨认真伪，本库不做推荐背书"
   - 如有 `risk: gray-area`，必须明确提示版权/合规风险

4. **禁止事项**：
   - 禁止编造、猜测镜像地址
   - 禁止使用 URL 短链接、跳转链接
   - 禁止把 `dead` 状态的地址当作可用地址提供

### 发现失效或钓鱼地址

- 探活失败：在本仓库提 issue，标注资源 `id` 与失效 URL，维护者会按 `SCHEMA.md` 的状态流转处理。
- 发现仿冒钓鱼站：提 issue 并附证据（仿冒域名、仿冒手法），经核实后记入该资源的 `note` 做警示。

### 贡献新资源

按 `CONTRIBUTING.md` 的验证流程提交 PR：新镜像必须有官方渠道背书或维护者实测 + 交叉验证，不接受 unverified 条目。
