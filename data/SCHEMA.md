# Reliable Resources for Agent — Data Schema (v1)

The single source of truth of this repo is `data/resources.yaml`.
Human-readable, agent-parseable, CI-validatable.

> 🌐 中文版：[SCHEMA.zh-CN.md](SCHEMA.zh-CN.md)

## Top-level structure

```yaml
version: 1
updated_at: 2026-10-05   # last human/CI update date
resources:
  - <resource>           # see below
```

## resource fields

| Field | Required | Description |
|---|---|---|
| `id` | yes | Globally unique slug, lowercase with dashes, e.g. `open-ebooks` |
| `name` | yes | Display name (Chinese) |
| `name_en` | no | Display name (English); falls back to `name` when absent |
| `category` | yes | Category, see below |
| `description` | yes | One-line Chinese description: what it is, what problem it solves |
| `description_en` | no | One-line English description; falls back to `description` when absent |
| `listing_type` | yes | Listing tier: `endorsed` (recommended) / `reference` (anti-phishing only), see below |
| `homepage` | yes | Official homepage (canonical URL); no short links |
| `probe_url` | no | Optional health-check override: when the homepage blocks bots but an official API/page is the reliable liveness signal, the prober checks this URL instead |
| `official_channels` | no | Official channels: announcement pages, official social accounts, official APIs (e.g. an official API endpoint that returns the current domain list). Used as the basis for verifying mirrors |
| `mirrors` | no | Mirror list, see below |
| `verification` | yes | Verification info, see below |
| `tags` | no | Tag array for search (use English tags) |
| `status` | yes | `active` / `degraded` / `dead` |
| `risk` | no | `none` (default) / `gray-area` (copyright/compliance gray area, must be explained in the description) |

## listing_type: two tiers

- `endorsed` (recommended): sites aligned with this registry's open-source spirit and values, worth recommending. Shown first for humans; agents may proactively recommend them.
- `reference` (anti-phishing): official address provided only for telling real from fake and preventing phishing — **no endorsement whatsoever**, clearly labeled "reference only". For big-tech products and other high-impersonation-risk sites.

Both tiers share the same verification bar (`verification` required); they differ only in whether we recommend them.

## mirror fields

| Field | Required | Description |
|---|---|---|
| `url` | yes | Mirror URL; no short or redirect links |
| `region` | no | Region hint, e.g. `cn-direct` (direct from China), `global`, `needs-proxy` |
| `last_verified` | yes | Last verified-working date `YYYY-MM-DD` |
| `verified_by` | yes | `maintainer` or a GitHub username |
| `note` | no | Notes, e.g. "redirects to xxx; backend rotates" |

## verification fields

| Field | Required | Description |
|---|---|---|
| `method` | yes | Verification method, see below |
| `verified_at` | yes | Verification date `YYYY-MM-DD` |
| `verified_by` | yes | `maintainer` or a GitHub username |
| `evidence` | yes | One-line basis of trust, e.g. "official announcement page confirmed this domain on 2026-09-01" (may be written in the contributor's own language) |

### method enum

- `official-domain` — a long-lived stable official domain (e.g. a project's canonical domain); no frequent re-verification needed
- `official-announcement` — an address or mirror backed by an official channel (announcement / official account / official API)
- `community-consensus` — no official backing, but maintainer-tested + community cross-verified (e.g. some mirror site)
- `unverified` entries are not accepted into `main`

## category enum (initial)

`academic` / `ebooks` / `dev-tools` / `ai-tools` / `media` / `dataset` / `mirror` / `other`

New categories need a justification in the PR and maintainer approval.

## status lifecycle & health-check scope

- `active` → `degraded`: automatic. When a resource's homepage fails health checks
  **2 consecutive times**, `scripts/check_links.py --apply-degrade` flips its status
  (CI runs this weekly; failure counts persist in `data/link-health.json`).
  Mirror failures are recorded but never trigger a resource-level degrade.
- `degraded` → `active`: manual only. A maintainer re-verifies and restores it
  (avoids flapping).
- `active`/`degraded` → `dead`: manual only, after human re-verification.

**Health checks verify URL reachability only** (HTTP 200/3xx after redirects).
They do **not** verify download file integrity/safety, version correctness, or
environment compatibility — those require human review, and users should judge
for themselves. Never claim otherwise in docs or promotion.

## Data contract stability (for skill consumers)

The skill (`skills/reliable-resources/SKILL.md`) is designed to be installed once and never updated. It depends only on this stable contract:

- Top-level: `version`, `updated_at`, `skill_version`, `resources[]` (plus `category` / `count` in per-category files)
- Per resource: `id`, `name`, `name_en`, `description`, `description_en`, `homepage`, `mirrors[]`, `listing_type`, `status`, `verification{method, verified_at, verified_by, evidence}`, `tags`, `risk`

Promises:

- We may **add** new optional fields at any time — consumers must ignore unknown fields.
- We will **not** rename, remove, or change the meaning of existing fields without bumping top-level `version` and announcing a migration.
- `skill_version` always mirrors the skill's frontmatter `version` (injected by `scripts/build_site.py`); when it moves ahead, agents advise users to reinstall the skill.

This is what lets the skill stay frozen while the registry keeps evolving.

## Status lifecycle

- `active` → 2 consecutive CI health-check failures → `degraded` (still shown, with a warning)
- `degraded` → manual re-verification fails → `dead` (removed from default view, archived)
- A `dead` URL must never be deleted outright; keep the record for tracing phishing impersonation
