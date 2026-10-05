# Reliable Resources for Agent

**让 AI 可靠，让信息安全。**

一个**人工审核、持续验证**的互联网可信资源库——同时服务人类用户和 AI Agent。

> 🌐 English version: [README.md](README.md)

🌐 **在线浏览**：https://fangwenky.github.io/reliable-resources-for-agent/
🤖 **Agent 安装 skill**：见[安装](#安装)

## 安装

一条命令——复制、粘贴、回车：

```bash
npx skills add https://github.com/Fangwenky/reliable-resources-for-agent -g
```

常用变体：

```bash
# 只装给某个 Agent（claude-code、codex、cursor 等）
npx skills add https://github.com/Fangwenky/reliable-resources-for-agent -a claude-code

# 先预览，不安装
npx skills add https://github.com/Fangwenky/reliable-resources-for-agent --list
```

装完重启你的 Agent，然后试一句："我想下载的那个工具，官网是哪个？"
skill 每次使用时自动拉取最新数据——数据更新无需重装（只有 skill 本体发新版时才需重装，Agent 会主动提醒你）。

## 为什么做这个

- AI 时代，"官网地址是什么"这类问题的答案经常是错的：搜索引擎前排可能是**钓鱼仿冒站**，AI 也可能**编造**一个看似合理的域名。
- 有些实用资源的域名频繁变化，用户和 Agent 都难以分辨哪个是真的。
- 本仓库的核心锚点：**可信可靠**——每一条收录都经过人工审核与官方渠道交叉验证，并持续探活；**双受众**——人类可读，Agent 可直接消费。

### 场景：AI 配环境

让 Agent 帮你配环境（装 Python、Node、JDK、数据库……）时，它不再去搜索引擎前排碰运气，也不再凭记忆编一个"看似正确"的下载地址——而是从这份人工审核过的库里拿**官方地址**，用版本管理器（pyenv / nvm / conda-forge）装**对的版本**。结果：更顺利、更安全，兼容性问题和版本错误更少。

## 信任机制

1. **人工审核**：所有条目进入主分支前需维护者审核，验证依据写进 `verification.evidence`，可追溯。
2. **官方渠道背书**：镜像类条目必须有官方公告、官方账号或官方 API 佐证（见 `CONTRIBUTING.zh-CN.md`）。
3. **CI 持续探活**：GitHub Actions 定期检查所有收录 URL 的可用性，homepage 连续 2 次失败自动降级（`active` → `degraded`，只能人工恢复）。探活仅验证可达性，不验证下载文件安全性、版本号正确性与环境兼容性。HTTP 403（反爬虫拒绝探活）不计入失败；`dead` 资源移入"已失效"归档，不再出现在默认浏览与推荐筛选中。
4. **防投毒**：不接受短链接/跳转链接；灰色地带资源明确标注 `risk: gray-area`；失效域名保留记录，用于警示仿冒。
5. **收录哲学**：双层收录——`endorsed` 推荐开源与公共利益项目，`reference` 仅提供大厂等高仿冒风险站点的官方地址用于防伪（不背书）；永不收录靠垄断攫取价值的中间商（详见 `CONTRIBUTING.zh-CN.md`）。

## 如何使用

**人类用户**：直接阅读 [`data/resources.yaml`](data/resources.yaml)，或在网站上按分类/`tags` 检索（支持中文/英文切换）。

**Agent**：安装本 skill（[SKILL.md](SKILL.md)，中英双语），按 skill 中的"拉取最新数据 → 查询 → 选址 → 呈现"流程使用。
skill 每次使用时会从 `https://fangwenky.github.io/reliable-resources-for-agent/data.json` 拉取最新数据（CI 在每次数据变更后自动重新生成），无需重装即可获得最新收录。
Claude Code 等支持 skills 的 Agent 可直接把本仓库加入 skill 目录。

**Agent 数据接口**（不装 skill 也能用）：`https://fangwenky.github.io/reliable-resources-for-agent/data.json`，看 `updated_at` 判断新鲜度。
按分类取数：`/api/by-category/<category>.json`（分类列表见 `/api/index.json`）。

## 仓库结构

```
.
├── skills/
│   └── reliable-resources/
│       └── SKILL.md          # Agent 使用说明（skill 入口，中英双语）
├── README.md                 # English version
├── data/
│   ├── resources.yaml        # 资源数据（single source of truth，名称/描述中英双语）
│   ├── SCHEMA.md             # Field definitions & status lifecycle (EN)
│   └── SCHEMA.zh-CN.md       # 数据字段定义与状态流转规则（中文）
├── docs/
│   ├── index.html            # 静态站点（GitHub Pages，中文/EN 切换）
│   ├── data.json             # 由 scripts/build_site.py 自动生成，请勿手改
│   └── api/
│       ├── index.json        # 分类列表（自动生成）
│       └── by-category/      # 按分类拆分的数据文件（自动生成）
├── scripts/
│   ├── check_links.py        # URL 探活脚本（CI 调用）
│   └── build_site.py         # resources.yaml → docs/data.json
├── .github/workflows/
│   ├── link-check.yml        # 定时探活 workflow
│   └── build-site.yml        # 数据变更时自动重新生成站点数据
├── CONTRIBUTING.zh-CN.md     # 贡献与验证流程（中文）
├── CONTRIBUTING.md           # Contribution & verification process (EN)
└── LICENSE
```

## 当前状态

早期骨架阶段。欢迎按 `CONTRIBUTING.zh-CN.md` 提交资源收录 PR，或提 issue 报告失效/仿冒地址。

## License

MIT
