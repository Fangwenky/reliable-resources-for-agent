# Reliable Resources for Agent

一个**人工审核、持续验证**的互联网可信资源库——同时服务人类用户和 AI Agent。

🌐 **在线浏览**：https://fangwenky.github.io/reliable-resources-for-agent/
🤖 **Agent 安装 skill**：`npx skills add https://github.com/Fangwenky/reliable-resources-for-agent`

## 为什么做这个

- AI 时代，"官网地址是什么"这类问题的答案经常是错的：搜索引擎前排可能是**钓鱼仿冒站**，AI 也可能**编造**一个看似合理的域名。
- 很多实用资源的域名频繁变化（如 Z-Library），用户和 Agent 都难以分辨哪个是真的。
- 本仓库的核心锚点：**可信可靠**——每一条收录都经过人工审核与官方渠道交叉验证，并持续探活；**双受众**——人类可读，Agent 可直接消费。

## 信任机制

1. **人工审核**：所有条目进入主分支前需维护者审核，验证依据写进 `verification.evidence`，可追溯。
2. **官方渠道背书**：镜像类条目必须有官方公告、官方账号或官方 API 佐证（见 `CONTRIBUTING.md`）。
3. **CI 持续探活**：GitHub Actions 定期检查所有收录 URL 的可用性，连续失败自动降级状态。
4. **防投毒**：不接受短链接/跳转链接；灰色地带资源明确标注 `risk: gray-area`；失效域名保留记录，用于警示仿冒。
5. **收录哲学**：双层收录——`endorsed` 推荐开源与公共利益项目，`reference` 仅提供大厂等高仿冒风险站点的官方地址用于防伪（不背书）；永不收录靠垄断攫取价值的中间商（详见 `CONTRIBUTING.md`）。

## 如何使用

**人类用户**：直接阅读 [`data/resources.yaml`](data/resources.yaml)，或按分类/`tags` 检索。

**Agent**：安装本 skill（[SKILL.md](SKILL.md)），按 skill 中的流程查询、选址、呈现。
Claude Code 等支持 skills 的 Agent 可直接把本仓库加入 skill 目录。

## 仓库结构

```
.
├── SKILL.md                  # Agent 使用说明（skill 入口）
├── data/
│   ├── resources.yaml        # 资源数据（single source of truth）
│   └── SCHEMA.md             # 数据字段定义与状态流转规则
├── docs/
│   ├── index.html            # 静态站点（GitHub Pages）
│   └── data.json             # 由 scripts/build_site.py 自动生成，请勿手改
├── scripts/
│   ├── check_links.py        # URL 探活脚本（CI 调用）
│   └── build_site.py         # resources.yaml → docs/data.json
├── .github/workflows/
│   ├── link-check.yml        # 定时探活 workflow
│   └── build-site.yml        # 数据变更时自动重新生成站点数据
├── CONTRIBUTING.md           # 贡献与验证流程
└── LICENSE
```

## 当前状态

早期骨架阶段。欢迎按 `CONTRIBUTING.md` 提交资源收录 PR，或提 issue 报告失效/仿冒地址。

## License

MIT
