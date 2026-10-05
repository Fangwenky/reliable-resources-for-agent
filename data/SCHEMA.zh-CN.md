# Reliable Resources for Agent — 数据 Schema（v1）

本仓库的 single source of truth 是 `data/resources.yaml`。
人类可读，Agent 可解析，CI 可校验。

> 🌐 English version: [SCHEMA.md](SCHEMA.md)

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
| `id` | 是 | 全局唯一 slug，小写短横线，如 `open-ebooks` |
| `name` | 是 | 显示名（中文） |
| `name_en` | 否 | 显示名（英文）；缺失时回退到 `name` |
| `category` | 是 | 分类，见下 |
| `description` | 是 | 一句话中文描述，说明这是什么、解决什么问题 |
| `description_en` | 否 | 一句话英文描述；缺失时回退到 `description` |
| `listing_type` | 是 | 收录层级：`endorsed`（推荐收录）/ `reference`（防伪收录），见下 |
| `homepage` | 是 | 官方主页（canonical URL），不允许使用短链接 |
| `official_channels` | 否 | 官方渠道列表：官网公告页、官方社交账号、官方 API（如返回当前域名列表的官方接口）。这是验证镜像的依据 |
| `mirrors` | 否 | 镜像列表，见下 |
| `verification` | 是 | 验证信息，见下 |
| `tags` | 否 | 标签数组，便于检索（请用英文标签） |
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
| `note` | 否 | 备注，如"跳转到 xxx，后端会轮换"（可用贡献者自己的语言书写） |

## verification 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `method` | 是 | 验证方式，见下 |
| `verified_at` | 是 | 验证日期 `YYYY-MM-DD` |
| `verified_by` | 是 | `maintainer` 或 GitHub 用户名 |
| `evidence` | 是 | 验证依据的一句话说明，如"官网公告页 2026-09-01 确认该域名"（可用贡献者自己的语言书写） |

### method 枚举

- `official-domain` — 长期稳定的官方域名（如项目长期使用的官方主域名），无需频繁复验
- `official-announcement` — 有官方渠道（公告/官方账号/官方 API）背书的地址或镜像
- `community-consensus` — 无官方背书，但经维护者实测 + 社区交叉验证（如某镜像站）
- 不接受 `unverified` 的条目进入主分支

## category 枚举（初始）

`academic` 学术 / `ebooks` 电子书 / `dev-tools` 开发工具 / `ai-tools` AI 工具 /
`media` 影音 / `dataset` 数据集 / `mirror` 镜像站 / `other` 其他

新增分类需在 PR 中说明理由，由维护者批准。

## 状态流转与探活范围

- `active` → `degraded`：自动。当某条资源的 homepage **连续 2 次**探活失败，
  `scripts/check_links.py --apply-degrade` 自动将其状态改为 degraded
  （CI 每周运行；失败计数持久化在 `data/link-health.json`）。
  镜像失败只记录，不触发整站降级。
- `degraded` → `active`：仅人工恢复。维护者复验后手动改回（防抖动）。
- `active`/`degraded` → `dead`：仅人工，需经人工复验。

**探活只验证 URL 可达**（跟随跳转后的 HTTP 200/3xx），**不验证**下载文件完整性/
安全性、版本号正确性、环境兼容性——这些需要人工审核，用户请自行判断。
文档与宣传中不得作超出此范围的承诺。

## 数据契约稳定性承诺（面向 skill 消费者）

本 skill（`skills/reliable-resources/SKILL.md`）的设计目标是安装一次、永不更新。它只依赖以下稳定契约：

- 顶层：`version`、`updated_at`、`skill_version`、`resources[]`（分类文件中还有 `category` / `count`）
- 每条资源：`id`、`name`、`name_en`、`description`、`description_en`、`homepage`、`mirrors[]`、`listing_type`、`status`、`verification{method, verified_at, verified_by, evidence}`、`tags`、`risk`

承诺：

- 我们可能随时**新增**可选字段——消费者必须忽略未知字段。
- **不会**在不升级顶层 `version` 并公告迁移方案的情况下，重命名、删除或改变已有字段的含义。
- `skill_version` 永远与 skill frontmatter 的 `version` 一致（由 `scripts/build_site.py` 自动注入）；当它领先时，Agent 会建议用户重装 skill。

这就是 skill 可以冻结、而库可以持续演进的原因。

## 状态流转

- `active` → 连续 2 次 CI 探活失败 → `degraded`（仍展示，带警告）
- `degraded` → 人工复验失败 → `dead`（移出默认展示，进入归档）
- 任何 `dead` 的 URL 不得直接删除，保留记录以便追溯钓鱼仿冒
