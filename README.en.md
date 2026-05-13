<div align="center">

<h1>🔬 deep-search</h1>

<p><strong>Turn every experiment outcome into a reusable prior update</strong></p>

<p>
  <a href="./README.md">中文</a>
  ·
  <a href="./README.en.md"><strong>English</strong></a>
</p>

<p>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/Claude_Code-2.x-7c3aed.svg" alt="Claude Code 2.x">
  <img src="https://img.shields.io/badge/Python-3.10+-3776ab.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/platform-Linux_|_macOS-success.svg" alt="Linux/macOS">
  <img src="https://img.shields.io/badge/type-Skill-f59e0b.svg" alt="Type: Skill">
</p>

<p>A project-local Claude Code skill · <code>/deep-search</code> with three subcommands · auto-pulls evidence from 5 sources · WebFetch-verifies GPT paper citations · never auto-commits</p>

</div>

---

## 🤔 Why?

There is a recurring pain in competition / industrial ML workflows:

- 🌫️ **Structurally identical KILLs get re-run** — that direction you killed 3 months ago gets renamed and burns another GPU-day
- 📚 **Decision evidence is scattered across 5 files** — `decision_log.md` / `experiment_logs/*.md` / `memory/feedback_*.md` / `docs/paper_priors.md` / platform metric CSVs. Cross-checking by human memory is error-prone
- 🔍 **Paper search burns tokens** — naive arXiv + Semantic Scholar pulls cost 30k+ tokens per query, and GPT may hallucinate non-existent papers
- 🚧 **No pre-submission guardrail** — no automatic "has this axis been closed?" check before you spend a daily submission quota

### Before / After

<table>
<tr>
<th align="left">😩 Before</th>
<th align="left">✨ After</th>
</tr>
<tr>
<td>

```
Manual workflow (30 min):
1. grep decision_log.md
2. dig through experiment_logs/
3. remember memory/feedback_*
4. unclear whether to search papers
5. write a summary, citations from memory
6. submit training → turns out it's same
   structure as last quarter's KILL
   → discovered 24h later
```

</td>
<td>

```
/deep-search precheck "ExpA add layer-norm gating"  
   ↓ (1 min, 6 parallel greps)
[deep-search] precheck, mode=local-only
axis=gating → CLOSED-AXIS-HIT
3/3 historical KILL (ExpB/ExpC/ExpD)
Smoking gun: experiment_logs/exp_d.md:21
Verdict: BLOCKED
Report: docs/research/.../report.md
```

</td>
</tr>
</table>

---

## ✨ Features

- 🔬 **Three subcommands in one skill** — `postmortem` (post-job analysis) / `inquiry` (cross-experiment Q&A) / `precheck` (pre-submission guardrail)
- 🛡️ **Gate A two-stage external search** — 1-round Codex challenge on angles → user picks via chips → every citation force-verified by WebFetch
- 💬 **Gate C plain-language chips** — major findings surfaced as everyday-language chips before any prior update
- 📐 **Token-safe retrieval** — 250k-row metric CSV goes through a helper wrapper, never directly Read
- 📂 **Local-first / external opt-in** — defaults to repo-local 5 sources; external search needs explicit user authorization via chips
- 🚫 **Never auto-commits** — `prior_updates.diff` is a draft; user reviews + applies manually
- 🔌 **MediaCrawler-ready** — Phase 2 protocol for community platforms (Xiaohongshu/Zhihu/B站) is spec'd; CDP mode for low account-ban risk

---

## 📦 Installation

### Prerequisites

- Claude Code 2.x
- Python 3.10+
- An ML experiment / competition project (with conventions like `decision_log.md`)

### One-liner install

```bash
# From your project root
git clone https://github.com/dyt27666-oss/Cli-deep-search-skills-diy.git .claude/skills/deep-search
```

### Path-placeholder substitution

The skill uses three placeholders: `<PROJECT_ROOT>` / `<USER_AUTO_MEMORY>` / `<MEDIACRAWLER_ROOT>`. After install, **you must** run find-replace once:

```bash
PROJECT_ROOT="$(pwd)"
USER_AUTO_MEMORY="$HOME/.claude/projects/$(echo "$PROJECT_ROOT" | sed 's|/|-|g')/memory"
MEDIACRAWLER_ROOT="$HOME/MediaCrawler"   # optional, only for Phase 2

cd .claude/skills/deep-search
find . -type f \( -name "*.md" -o -name "*.py" \) -print0 | xargs -0 sed -i \
  -e "s|<PROJECT_ROOT>|$PROJECT_ROOT|g" \
  -e "s|<USER_AUTO_MEMORY>|$USER_AUTO_MEMORY|g" \
  -e "s|<MEDIACRAWLER_ROOT>|$MEDIACRAWLER_ROOT|g"
```

### Deploy the helper script

`scripts/_deep_search_metric_query.py` is not part of the skill itself; copy it into the project's `scripts/`:

```bash
cp .claude/skills/deep-search/scripts/_deep_search_metric_query.py scripts/
```

### Restart / reload

Claude Code loads skills at startup. After installation, open `/hooks` once in Claude Code or restart your session so the new skill registers.

---

## 🚀 Usage

### Basic: pre-submission guardrail

```
/deep-search precheck "ExpA add layer-norm gating"
```

Effect: in under a minute, get a report on whether the axis is already closed, what structurally-similar historical KILLs exist, and which `file:line` references back the conclusion.

### Advanced: post-job postmortem

```
/deep-search postmortem 98238
```

Prerequisite: you have already scraped platform state via [TAAC2026-CLI](https://github.com/ZhongKuang/TAAC2026-CLI) or your equivalent platform CLI tool, and an illustrative `outputs/<platform>/jobs-summary.csv` exists.

### Advanced: cross-experiment inquiry

```
/deep-search inquiry "Why does valid AUC rise but LB AUC fall?"
```

Retrieves across `decision_log.md` + `experiment_logs/` + `memory/`. If local hits ≥ 3, refuses external search; if insufficient, surfaces a chip asking for authorization.

---

## 🏷️ Subcommand Overview

| Subcommand | Use case | Default mode | Gate A trigger |
|---|---|---|---|
| `postmortem <job_id>` | After a job finishes | local-only | PROMOTE ≥ +0.003 / surprise KILL / conflicts with Semantic prior |
| `inquiry "<question>"` | Cross-experiment Q&A | local-only | < 3 local hits |
| `precheck "<new exp idea>"` | Before submission | local-only | Mechanism absent from `paper_priors.md` AND user wants paper-grounded check |

Every invocation outputs a **mandatory first announcement line**:

```
[deep-search] precheck "ExpA ...", mode=local-only — gating axis closure check must precede any external search.
```

---

## 🏗️ How It Works

```
┌──────────────────────────────────────────────────────────────┐
│  User invokes /deep-search <subcommand> [args]               │
└──────────────┬───────────────────────────────────────────────┘
               │
               ▼
       ┌───────────────┐
       │ Announcement  │  ← mandatory first line:
       │     line      │     subcommand / mode / reason
       └───────┬───────┘
               │
               ▼
       ┌───────────────────────────────────────┐
       │  Local Retrieval (token-safe)         │
       │   • jobs-summary.csv                  │
       │   • decision_log.md (grep + tail)     │
       │   • experiment_logs/*.md                    │
       │   • memory/feedback_*.md (two paths)  │
       │   • paper_priors.md                   │
       └───────┬───────────────────────────────┘
               │
               ▼
       ┌───────────────────┐  no   ┌─────────────────┐
       │  Gate A trigger?  ├──────►│ Local enough    │
       └───────┬───────────┘       │ → synthesize    │
               │ yes               └────────┬────────┘
               ▼                            │
       ┌──────────────────────┐             │
       │ Codex 1-round chal-  │             │
       │ lenge → chips ask    │             │
       │ user → external      │             │
       │ deep search →        │             │
       │ WebFetch-verify      │             │
       │ every citation       │             │
       └───────┬──────────────┘             │
               │                            │
               ▼                            ▼
       ┌───────────────────────────────────────┐
       │ Synthesize report.md (file:line cit.) │
       └───────┬───────────────────────────────┘
               │
               ▼
       ┌───────────────────┐  no   ┌──────────────────┐
       │  Gate C trigger?  ├──────►│ Just write report│
       └───────┬───────────┘       └──────────────────┘
               │ yes
               ▼
       ┌────────────────────────────┐
       │ Plain-language chips →     │
       │ user decides:              │
       │   ├─ write to prior        │
       │   ├─ write to memory       │
       │   └─ defer (Recommended)   │
       └────────────┬───────────────┘
                    │
                    ▼
       ┌────────────────────────────┐
       │   prior_updates.diff       │
       │ (draft, never auto-commit) │
       └────────────────────────────┘
```

---

## 📁 Project Structure

```
.
├── SKILL.md                   # entry + announcement protocol + dispatch
├── SPEC.md                    # design contract (human-only, not loaded)
├── workflows/
│   ├── postmortem.md          # post-job analysis steps
│   ├── inquiry.md             # cross-experiment Q&A steps
│   └── precheck.md            # pre-submission guardrail steps
├── gates/
│   ├── gate_a_external_search.md   # external search + 1-round Codex cap
│   └── gate_c_major_finding.md     # major-finding chips protocol
├── retrieval/
│   ├── data_sources.md        # 5-source data map
│   ├── token_safety.md        # never-direct-Read list
│   ├── codex_collaboration.md # paper search delegation rules
│   └── external_sources.md    # XHS/Zhihu/B站 Phase 1+2 protocol
├── templates/
│   ├── report.md
│   ├── prior_updates.diff
│   ├── external_research.md
│   └── experiment_meta.md
└── scripts/
    └── _deep_search_metric_query.py  # token-safe helper for 250k-row metric CSV
```

---

## ❓ FAQ

<details>
<summary><strong>Q: My project is not an ML competition / does not use a specific experiment platform. Can I use it?</strong></summary>

Yes, but you'll need to edit `retrieval/data_sources.md` to map to your platform. The skill's core abstraction is "token-safe cross-source retrieval + citation verification". TAAC2026-CLI or equivalent platform CLI CSV paths are just one concrete instance — replace them with W&B / MLflow / Slurm sacct equivalents in your project.

</details>

<details>
<summary><strong>Q: Why have Codex challenge angles in a separate round?</strong></summary>

When Claude drafts search angles, it tends to "complete its existing thinking" (confirmation bias). Codex sees an isolated context and catches angles Claude missed. The 1-round cap is because more rounds bloat tokens with diminishing returns.

</details>

<details>
<summary><strong>Q: Does WebFetch verification block GPT hallucinations 100%?</strong></summary>

No, but it blocks 80%+. The remaining cases are GPT citing real papers but mischaracterizing the finding — those need human reading. The skill tags verified vs unverified separately so you can focus on the ~5 verified ones.

</details>

<details>
<summary><strong>Q: Why no auto-commit on prior updates?</strong></summary>

Priors are the foundation of the knowledge base — polluting them is hard to roll back. The skill is designed as a librarian, not an oracle. You get the evidence pack; the decision always stays with you.

</details>

<details>
<summary><strong>Q: Can I use Phase 2 (MediaCrawler) right out of the box?</strong></summary>

v0 is documentation-bound — no bridge code is shipped. To use Phase 2 you need to (1) clone MediaCrawler separately, (2) install playwright + chromium, (3) launch Chrome with `--remote-debugging-port=9222` and log in with an alt account, (4) write your own `scripts/_xhs_query.py`. The skill provides the protocol but doesn't install the environment for you.

</details>

<details>
<summary><strong>Q: Does postmortem require the job to be in terminal state?</strong></summary>

Only for conclusive verdicts. While a job is still running, `postmortem` marks the analysis as `pre-mortem (curve-only)` and only looks at trends without final claims.

</details>

---

## 🛡️ Compatibility

| Item | Version |
|---|---|
| Claude Code | 2.x |
| Python | 3.10+ |
| OS | Linux / macOS (Windows needs WSL or Git Bash for `sed`) |
| Optional: TAAC2026-CLI or your equivalent platform CLI tool | any version |
| Optional: MediaCrawler | any version (for Phase 2) |

---

## 🤝 Contributing

Issues / PRs welcome, especially:

- New `retrieval/data_sources.md` mappings for other platforms (W&B / MLflow / Slurm / Ray)
- Real Phase 2 bridge code (`scripts/_xhs_query.py`)
- More real-world examples of when Gate A should trigger

---

## 📄 License

[MIT](./LICENSE) — fork, modify, commercial use all OK; just keep the copyright notice.

---

<div align="center">

Skill-encapsulated by [Claude Code](https://claude.com/claude-code), dedicated to everyone who has been burned by a cross-experiment decision gap.

</div>
