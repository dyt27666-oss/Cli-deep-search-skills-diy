<div align="center">

<h1>🔬 deep-search</h1>

<p><strong>把每次实验的「结果」变成可复用的「先验更新」</strong></p>

<p>
  <a href="./README.md"><strong>中文</strong></a>
  ·
  <a href="./README.en.md">English</a>
</p>

<p>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/Claude_Code-2.x-7c3aed.svg" alt="Claude Code 2.x">
  <img src="https://img.shields.io/badge/Python-3.10+-3776ab.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/platform-Linux_|_macOS-success.svg" alt="Linux/macOS">
  <img src="https://img.shields.io/badge/type-Skill-f59e0b.svg" alt="Type: Skill">
</p>

<p>一个 Claude Code 项目本地 skill · <code>/deep-search</code> 三 subcommand · 自动从 5 个数据源捞证据 · GPT 论文幻觉自动核查 · 永不自动 commit</p>

</div>

---

## 🤔 为什么需要它？

竞赛 / 工业 ML 工作流里有个反复出现的痛点：

- 🌫️ **同结构 KILL 重做**——3 个月前因为 X 失败过的方向，今天换个名字又跑一遍，浪费 1 GPU-day
- 📚 **决策证据散在 5 个文件**——`decision_log.md` / `eval_Logs/*.md` / `memory/feedback_*.md` / `docs/paper_priors.md` / 平台 metric CSV，人脑跨文件交叉验证容易漏
- 🔍 **新论文要 token 烧得心慌**——arXiv + Semantic Scholar 直接调用 30k+ token 一次，结果可能是 GPT 幻觉的不存在论文
- 🚧 **实验前防呆缺位**——提交训练前没有"这个轴关闭过吗"的自动检查，submission quota 就这么浪费

### 效果对比

<table>
<tr>
<th align="left">😩 Before</th>
<th align="left">✨ After</th>
</tr>
<tr>
<td>

```
人工流程（30 分钟）：
1. grep decision_log.md
2. 翻 eval_Logs/ 找相关
3. 想起来还有 memory/feedback_*
4. 不确定要不要查论文
5. 写一段总结，引用都靠回忆
6. 提交训练 → 跟去年某个 KILL 同结构
   → 24h 后才发现
```

</td>
<td>

```
/deep-search precheck "I-667 ..."  
   ↓ (1 min, 6 个 grep 自动并行)
[deep-search] precheck, mode=local-only
axis=gating → CLOSED-AXIS-HIT
3/3 历史 KILL (I-624 / I-639 / I-661)
铁证: eval_Logs/i-661.md:21
Verdict: BLOCKED
报告: docs/research/.../report.md
```

</td>
</tr>
</table>

---

## ✨ 特性

- 🔬 **三 subcommand 一个 skill** — `postmortem`（实验后复盘）/ `inquiry`（跨实验问答）/ `precheck`（提交前防呆）
- 🛡️ **Gate A 两阶段外搜** — Codex 1 轮 challenge 角度 → 用户 chips 选 → 每条引用强制 WebFetch 验证
- 💬 **Gate C 通俗 chips** — 重大发现先用人话告诉你，再问要不要更新 prior
- 📐 **Token-safe 检索** — 250k 行 metric CSV 走 helper 包装，永不直接 Read
- 📂 **本地优先 / 外搜可选** — 默认只用 repo 本地 5 个数据源；外搜需 chips 显式授权
- 🚫 **永不自动 commit** — 输出的 prior diff 是草稿，用户 review 后手动 apply
- 🔌 **MediaCrawler 接入预留** — 社群平台（小红书/知乎/B站）的 Phase 2 协议已 spec，CDP 模式低封号风险

---

## 📦 安装

### 前置条件

- Claude Code 2.x
- Python 3.10+
- 一个 ML 实验/竞赛项目（有 `decision_log.md` 之类的项目文档惯例）

### 一键安装

```bash
# 在你的项目根目录
git clone https://github.com/dyt27666-oss/Cli-deep-search-skills-diy.git .claude/skills/deep-search
```

### 路径占位符替换

Skill 用 `<PROJECT_ROOT>` / `<USER_AUTO_MEMORY>` / `<MEDIACRAWLER_ROOT>` 三个 placeholder。安装后**必须**做一次 find-replace：

```bash
PROJECT_ROOT="$(pwd)"
USER_AUTO_MEMORY="$HOME/.claude/projects/$(echo "$PROJECT_ROOT" | sed 's|/|-|g')/memory"
MEDIACRAWLER_ROOT="$HOME/MediaCrawler"   # 可选，Phase 2 才需要

cd .claude/skills/deep-search
find . -type f \( -name "*.md" -o -name "*.py" \) -print0 | xargs -0 sed -i \
  -e "s|<PROJECT_ROOT>|$PROJECT_ROOT|g" \
  -e "s|<USER_AUTO_MEMORY>|$USER_AUTO_MEMORY|g" \
  -e "s|<MEDIACRAWLER_ROOT>|$MEDIACRAWLER_ROOT|g"
```

### Helper script 部署

`scripts/_deep_search_metric_query.py` 不属于 skill 本身，要 copy 到项目的 `scripts/`：

```bash
cp .claude/skills/deep-search/scripts/_deep_search_metric_query.py scripts/
```

### 重启 / reload

Claude Code 启动时加载 skills。安装后在 Claude Code 里打开 `/hooks` 一次或重开 session，让新 skill 注册。

---

## 🚀 使用

### 基础：提交训练前防呆

```
/deep-search precheck "I-667 add temporal-decay gating on attention output"
```

效果：1 分钟内出 report，告诉你这个轴是否已关闭、有没有结构同源的历史 KILL、引用是哪几个 file:line。

### 进阶：实验后复盘

```
/deep-search postmortem 98238
```

前提：你已经用 [TAAC2026-CLI](https://github.com/ZhongKuang/TAAC2026-CLI) 或同等工具 scrape 过平台状态，`outputs/taiji-output/training/jobs-summary.csv` 存在。

### 进阶：跨实验问答

```
/deep-search inquiry "为什么 valid AUC 涨但 LB 跌？"
```

跨 `decision_log.md` + `eval_Logs/` + `memory/` 检索，本地证据 ≥3 hits 时绝不外搜；不足时 chips 问你授权。

---

## 🏷️ 三个 subcommand 总览

| Subcommand | 触发场景 | 默认模式 | Gate A 触发条件 |
|---|---|---|---|
| `postmortem <jobInternalId>` | Job 跑完后复盘 | local-only | PROMOTE ≥ +0.003 / surprise KILL / 与 Semantic prior 冲突 |
| `inquiry "<问题>"` | 跨实验问答 | local-only | 本地命中 < 3 |
| `precheck "<新实验描述>"` | 提交训练前 | local-only | 机制不在 `paper_priors.md` 且用户要论文核查 |

每次调用 skill 都会**先输出一行 announcement**，明确选了哪个 subcommand、什么模式、为什么：

```
[deep-search] precheck "I-667 ...", mode=local-only — gating axis closure check must precede any external search.
```

---

## 🏗️ How It Works

```
┌──────────────────────────────────────────────────────────────┐
│  用户调用 /deep-search <subcommand> [args]                   │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
       ┌───────────────┐
       │ Announcement  │  ← 强制第一行：subcommand / 模式 / 理由
       │     line      │
       └───────┬───────┘
               │
               ▼
       ┌───────────────────────────────────────┐
       │  Local Retrieval (token-safe)         │
       │   • jobs-summary.csv                  │
       │   • decision_log.md (grep + tail)     │
       │   • eval_Logs/*.md                    │
       │   • memory/feedback_*.md (两路径)     │
       │   • paper_priors.md                   │
       └───────┬───────────────────────────────┘
               │
               ▼
       ┌───────────────────┐  no   ┌─────────────────┐
       │   Gate A 触发？   ├──────►│ 本地证据足够    │
       └───────┬───────────┘       │   合成 report   │
               │ yes               └────────┬────────┘
               ▼                            │
       ┌──────────────────────┐             │
       │ Codex 1 轮 challenge │             │
       │   →   chips 选角度   │             │
       │   →   外部 deep      │             │
       │       search         │             │
       │   →   WebFetch       │             │
       │       核查每条引用   │             │
       └───────┬──────────────┘             │
               │                            │
               ▼                            ▼
       ┌───────────────────────────────────────┐
       │   合成 report.md (引用 file:line)     │
       └───────┬───────────────────────────────┘
               │
               ▼
       ┌───────────────────┐  no   ┌──────────────────┐
       │   Gate C 触发？   ├──────►│ 仅写 report      │
       └───────┬───────────┘       └──────────────────┘
               │ yes
               ▼
       ┌────────────────────────────┐
       │  通俗语言 chips → 用户决定 │
       │     ├─ 写进 prior          │
       │     ├─ 写进 memory         │
       │     └─ 暂不写 (Recommended)│
       └────────────┬───────────────┘
                    │
                    ▼
       ┌────────────────────────────┐
       │   prior_updates.diff       │
       │   （草稿，不自动 commit）  │
       └────────────────────────────┘
```

---

## 📁 项目结构

```
.
├── SKILL.md                   # 入口 + announcement 协议 + dispatch
├── SPEC.md                    # 设计契约（人读，不被 skill load）
├── workflows/
│   ├── postmortem.md          # 实验后复盘步骤
│   ├── inquiry.md             # 跨实验问答步骤
│   └── precheck.md            # 提交前防呆步骤
├── gates/
│   ├── gate_a_external_search.md   # 外搜协议 + Codex 1 轮 cap
│   └── gate_c_major_finding.md     # 重大发现 chips 协议
├── retrieval/
│   ├── data_sources.md        # 5 路径数据源映射
│   ├── token_safety.md        # 哪些文件绝不直接 Read
│   ├── codex_collaboration.md # 论文外搜 Codex 委托规则
│   └── external_sources.md    # XHS/Zhihu/B站 Phase 1+2 协议
├── templates/
│   ├── report.md
│   ├── prior_updates.diff
│   ├── external_research.md
│   └── experiment_meta.md
└── scripts/
    └── _deep_search_metric_query.py  # 250k 行 metric CSV 的 token-safe helper
```

---

## ❓ FAQ

<details>
<summary><strong>Q: 我的项目不是 TAAC2026 / 不用 Taiji 平台，能用吗？</strong></summary>

可以，但要改 `retrieval/data_sources.md` 里的数据源映射。Skill 的核心抽象是「跨多种证据源做 token-safe 检索 + 引用验证」，TAAC2026-CLI 的 CSV 路径只是一个具体实例。你的项目里换成 W&B / MLflow / Slurm sacct 的对应路径即可。

</details>

<details>
<summary><strong>Q: 为什么要 Codex 单独 challenge 一轮？我直接搜不行吗？</strong></summary>

Claude 出搜索角度时容易陷入"补全已有思路"的偏差。Codex 隔离上下文独立看，能 catch 到 Claude 没想到的反例方向。1 轮 cap 是因为再多就开始 token 通胀，边际收益降到零。

</details>

<details>
<summary><strong>Q: WebFetch 核查能 100% 拦截 GPT 幻觉吗？</strong></summary>

不能 100%，但能拦掉 80%+。剩下的是 GPT 用了真存在论文但断章取义的情况——这种需要人读原文。Skill 把 verified / unverified 分开标，让你能聚焦看 verified 那 ~5 篇。

</details>

<details>
<summary><strong>Q: 为什么不自动 commit prior 更新？</strong></summary>

Prior 是知识库根基，污染了很难回滚。Skill 设计假设是 librarian 不是 oracle——给你证据包，决策权永远在你。

</details>

<details>
<summary><strong>Q: MediaCrawler 装了能直接用吗？</strong></summary>

v0 是文档绑定，没接桥接代码。真要用 Phase 2，要你 (1) 单独 clone MediaCrawler (2) 装 playwright + chromium (3) 开 Chrome 带 `--remote-debugging-port=9222` 并登录小号 (4) 自己写 `scripts/_xhs_query.py`。Skill 提供协议规范但不替你装环境。

</details>

<details>
<summary><strong>Q: postmortem 是不是要等 job 终态？</strong></summary>

终态才能给"结论"。Job 还在跑时可以跑 postmortem，但会标记为 `pre-mortem (curve-only)`，只看曲线趋势不下定论。

</details>

---

## 🛡️ 兼容性

| 项 | 版本 |
|---|---|
| Claude Code | 2.x |
| Python | 3.10+ |
| 操作系统 | Linux / macOS（Windows 下 sed 需用 WSL 或 Git Bash） |
| 可选: TAAC2026-CLI | 任意版本 |
| 可选: MediaCrawler | 任意版本（Phase 2 时） |

---

## 🤝 贡献

Issue / PR 欢迎，特别是：

- 对接其他实验平台的 `retrieval/data_sources.md` 映射（W&B / MLflow / Slurm / Ray）
- Phase 2 的真桥接代码（`scripts/_xhs_query.py`）
- 更多 Gate A 触发条件的实际案例

---

## 📄 License

[MIT](./LICENSE) — fork、改、商用全 OK，留个版权声明即可。

---

<div align="center">

由 [Claude Code](https://claude.com/claude-code) skill 化封装，献给所有在跨实验决策里掉过坑的人。

</div>
