# Reliable Resources for Agent — 数据 Schema（v1）

本仓库的 single source of truth 是 `data/resources.yaml`。
人类可读，Agent 可解析，CI 可校验。

## 顶层结构

```yaml
version: 1
updated_at: 2026-10-05   # 最后一次人工/CI 更新日期
resources:
  - <resource>           # 见下
```

## resource 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | 是 | 全局唯一 slug，小写短横线，如 `z-library` |
| `name` | 是 | 显示名 |
| `category` | 是 | 分类，见下 |
| `description` | 是 | 一句话中文描述，说明这是什么、解决什么问题 |
| `listing_type` | 是 | 收录层级：`endorsed`（推荐收录）/ `reference`（防伪收录），见下 |
| `homepage` | 是 | 官方主页（canonical URL），不允许使用短链接 |
| `official_channels` | 否 | 官方渠道列表：官网公告页、官方社交账号、官方 API（如 z-lib 的 `/eapi/info/domains`）。这是验证镜像的依据 |
| `mirrors` | 否 | 镜像列表，见下 |
| `verification` | 是 | 验证信息，见下 |
| `tags` | 否 | 标签数组，便于检索 |
| `status` | 是 | `active` / `degraded` / `dead` |
| `risk` | 否 | `none`（默认）/ `gray-area`（涉及版权等灰色地带，需在描述中说明） |

## listing_type：双层收录

- `endorsed`（推荐收录）：符合本仓库开源精神与价值观、值得向用户推荐的站点。人类浏览时优先展示，Agent 可主动推荐。
- `reference`（防伪收录）：仅提供官方地址用于辨认真伪、防范钓鱼，**不做任何推荐背书**，展示时明确标注"仅防伪"。适用于大厂产品等"暂不收录"但仿冒高发的站点。

两层共用同一套验证标准（verification 必填），区别只在是否推荐。

## mirror 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `url` | 是 | 镜像 URL，不允许短链接、跳转链接 |
| `region` | 否 | 可用地区标注，如 `cn-direct`（国内直连）、`global`、`needs-proxy` |
| `last_verified` | 是 | 最后一次验证可用日期 `YYYY-MM-DD` |
| `verified_by` | 是 | `maintainer` 或 GitHub 用户名 |
| `note` | 否 | 备注，如"跳转到 xxx，后端会轮换" |

## verification 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `method` | 是 | 验证方式，见下 |
| `verified_at` | 是 | 验证日期 `YYYY-MM-DD` |
| `verified_by` | 是 | `maintainer` 或 GitHub 用户名 |
| `evidence` | 是 | 验证依据的一句话说明，如"官网公告页 2026-09-01 确认该域名" |

### method 枚举

- `official-domain` — 长期稳定的官方域名（如 arxiv.org），无需频繁复验
- `official-announcement` — 有官方渠道（公告/官方账号/官方 API）背书的地址或镜像
- `community-consensus` — 无官方背书，但经维护者实测 + 社区交叉验证（如某镜像站）
- 不接受 `unverified` 的条目进入主分支

## category 枚举（初始）

`academic` 学术 / `ebooks` 电子书 / `dev-tools` 开发工具 / `ai-tools` AI 工具 /
`media` 影音 / `dataset` 数据集 / `mirror` 镜像站 / `other` 其他

新增分类需在 PR 中说明理由，由维护者批准。

## 状态流转

- `active` → 连续 2 次 CI 探活失败 → `degraded`（仍展示，带警告）
- `degraded` → 人工复验失败 → `dead`（移出默认展示，进入归档）
- 任何 `dead` 的 URL 不得直接删除，保留记录以便追溯钓鱼仿冒
