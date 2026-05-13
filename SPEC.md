# /deep-search Skill — Design SPEC

> **Owner**: any ML / research project that maintains a decision log + paper priors + per-experiment notes. Built to turn each experiment outcome into a defensible knowledge update without re-doing structurally-identical failures.
> **Author of SKILL.md files**: delegated to Codex via `/codex:rescue`. This SPEC is the contract.
> **Frame of mind**: retrieval > synthesis. Skill is a librarian, not an oracle. Major calls always go to chips with plain-language framing.

---

## 1. Entry point

`/deep-search <subcommand> [args]` — three subcommands, one skill.

| Subcommand | Usage | Trigger |
|---|---|---|
| `postmortem <job_id>` | After an experiment run hits terminal state | Manual (later: auto via hook) |
| `inquiry "<question>"` | Hunch / cross-experiment question | Manual |
| `precheck "<proposed exp idea>"` | Evidence search for a proposed experiment direction | Manual |

**Mandatory announcement rule**: every invocation, BEFORE doing tool calls, output one line stating:
- Subcommand chosen
- Mode (local-only / local+external)
- Why this mode (one short clause)

Example: `[deep-search] postmortem 98238, mode=local-only — both jobs not yet terminal, only a curve-based pre-mortem possible.`

---

## 2. Gates (shared by all three subcommands)

### Gate A — Decide whether to invoke external paper search

**Trigger conditions** (any one matches → propose external):
- `postmortem`: result is a PROMOTE (LB ≥ +0.003 over current SOTA), OR a surprise KILL (Mechanism not covered by `docs/paper_priors.md`), OR contradicts a Semantic prior
- `inquiry`: local evidence < 3 hits across {decision_log, experiment_logs, memory, paper_priors}
- `precheck`: proposed mechanism not found in `docs/paper_priors.md` AND not in `docs/paper_analysis.md`

**Protocol**:
1. Claude drafts 2–3 candidate search angles. Format: `<keyword>; venue/year filter; expected evidence type`.
2. Invoke `/codex:rescue` with: "Challenge these search angles for /deep-search Gate A. 1 round only. Reply: ACCEPT / ADD <angle> / DROP <angle> / REFRAME <angle to angle>."
3. Claude resolves Codex's reply (1 round, per [[feedback-delegate-to-codex]] memory rule and CLAUDE.md «讨论协议»). If Codex disagrees, Claude restates final list with rationale.
4. AskUserQuestion chips:
   - `question`: "Gate A — 准备外部搜查，选角度（可多选）"
   - `header`: "Search angle"
   - `multiSelect: true`
   - First option labeled `<angle> (Recommended)`; remaining options follow; always include a "都不搜，仅靠本地" option last
5. On user pick: invoke `/codex:rescue` with: "Deep search arXiv + Semantic Scholar for: <angles>. Return for each: paper title, authors, year, venue, arxiv URL, DOI, 2-sentence finding, relevance to your project's ML pipeline. Max 5 papers per angle."
6. Verify EVERY citation Codex returns: WebFetch each arxiv URL, parse title from `<meta>`, confirm match. Bad citations → drop with note `[unverified: <reason>]`.
7. Append verified findings to `external_research.md` under output dir.

### Gate C — Surface major findings to user as chips

**Trigger conditions** (any one):
- Proposed prior PROMOTION (Working → Episodic, or Episodic → Semantic)
- Proposed prior DEMOTION (Semantic flagged for review)
- A KILL with mechanism not previously documented
- A PROMOTE with LB lift ≥ +0.003

**Protocol**:
1. Write a plain-language summary (≤3 sentences, no jargon, what changes for next experiment).
2. AskUserQuestion chips:
   - `question`: 通俗版结论 + "要不要把这条写进 prior？"
   - options: ["写进 [[domain-hints-semantic]]", "写进 [[memory]] feedback_*", "暂不写，下次实验复现再说 (Recommended)", or context-specific]
   - Use `preview` field on at least one option to show the proposed diff lines
3. On user pick: write to `prior_updates.diff`; never auto-commit.

---

## 3. Subcommand specs

### 3.1 `/deep-search postmortem <job_id>`

**Steps**:
1. Read `outputs/<platform>/jobs-summary.csv`. If row not found → abort with "job_id not found in your platform export; refresh your job/run metadata first".
2. If `status` not in `{SUCCEED, FAILED, KILLED, CANCELED, FINISHED, COMPLETED}` → mode = `pre-mortem` (curve-only).
3. Token-safe metric pull: invoke `scripts/_deep_search_metric_query.py <job_id>` (helper to be written) → returns `(metric, n, last_step, last_value, max_value)` rows, ≤20 rows.
4. Pull eval result for this job: read `outputs/<platform>/evaluation/` and match by `mould_id` or `name` containing job tag.
5. Find experiment metadata:
   - `manifest.json` — find entry by job name (`name` field substring match)
   - `experiments/<experiment-id>/meta.md` if exists
   - `decision_log.md` last 200 lines, grep for the ExpX tag
   - `experiment_logs/<experiment-id>.md` if exists
6. Find structurally similar past experiments:
   - Same axis (decode from `tags` and `ablation_removes` in manifest)
   - Similar val-vs-LB delta pattern; the project has documented a repeated "val ↑ / LB ↓" pattern — calling that out is high-signal
7. Cross-check priors:
   - `docs/paper_priors.md` — does any prior predict this outcome?
   - `docs/domain_hints.md` Semantic layer
   - `memory/feedback_*.md` — closed-axis rules
8. Trigger Gate A check; if ON, run protocol
9. Trigger Gate C check; if ON, run protocol
10. Write outputs:
    - `docs/research/deep_search/<YYYYMMDD-HHMM>_postmortem_<experiment-id>/report.md`
    - `docs/research/deep_search/<YYYYMMDD-HHMM>_postmortem_<experiment-id>/prior_updates.diff` (optional)
    - `docs/research/deep_search/<YYYYMMDD-HHMM>_postmortem_<experiment-id>/external_research.md` (optional)
11. Final message: a 5-line summary + paths.

### 3.2 `/deep-search inquiry "<question>"`

**Steps**:
1. Parse question for keywords: experiment IDs (for example `ExpA`, `EXP-123`, or your platform IDs), axis names ({gating, calibration, focal, sequence, item-id, time-feature, architecture, ...}), mechanism phrases.
2. Local retrieval (in order, stop when ≥5 hits):
   - grep `decision_log.md` for IDs and keywords
   - grep `experiment_logs/*.md` for IDs and keywords
   - grep `memory/feedback_*.md` for axis names
   - grep `docs/paper_priors.md` for keywords
   - grep `outputs/<platform>/jobs-summary.csv` `name` column
3. If hits < 3 → Gate A chip "证据不足，搜外部？"; else proceed.
4. Synthesize: a one-paragraph answer + bulleted citations (file:line for each claim).
5. Trigger Gate C only if answer reveals a previously-undocumented mechanism.
6. Output: `docs/research/deep_search/<YYYYMMDD-HHMM>_inquiry/report.md`.

### 3.3 `/deep-search precheck "<proposed exp>"`

**Steps**:
1. Classify proposed experiment by axis. Recognize at least: `gating`, `loss-reweighting`, `calibration`, `sequence-replacement`, `item-id-feature`, `time-feature`, `multi-cate`, `userpair`, `architecture-{compressor,attention-bias,etc}`, `regularization`.
2. Read all `memory/feedback_*axis_closed*.md` (and similar closed-axis files) — for each match, mark `CLOSED-AXIS-HIT`.
3. If `CLOSED-AXIS-HIT`: check whether proposed mechanism is structurally different from what closed the axis (read the "Why:" / "How to apply:" in the feedback file).
4. Pull paper priors from `docs/paper_priors.md`: does any predict +EV or -EV for this proposal?
5. Decision recommendation:
   - **GO** — axis open, paper +EV, no recent similar KILL
   - **NEEDS-JUSTIFICATION** — limited prior evidence; proceed with explicit rationale
   - **REDUCED-PRIORITY** — N prior attempts on this axis closed at lower scores. Doesn't mean the axis is dead, but you should: (a) confirm your variant is structurally different from prior failures (see citations), OR (b) combine with another axis that compensates for the prior failure mode, OR (c) deprioritize unless other axes are exhausted.
6. Trigger Gate A only if proposed mechanism references a paper not in `paper_priors.md` AND user wants paper-grounded sanity check.
7. Output: `docs/research/deep_search/<YYYYMMDD-HHMM>_precheck/report.md` + optional `experiment_meta_template.md` if GO.

---

## 4. Token-safe retrieval rules (HARD RULES)

**Never directly Read or grep these paths**:
- `outputs/<platform>/all-metrics-long.csv` (250k+ rows)
- `outputs/<platform>/logs/<job-id>/*.txt`
- `outputs/<platform>/code/<job-id>/files/*` (unless user explicitly asks for a specific file)

**Always use**:
- `outputs/<platform>/jobs-summary.csv` (≤50 rows usually)
- `outputs/<platform>/all-checkpoints.csv` (≤200 rows)
- `outputs/<platform>/evaluation/` (already trimmed)
- Per-job metrics: `python scripts/_deep_search_metric_query.py <job_id>` (helper, output ≤20 rows). Helper to be written by Codex.
- Per-job log errors: use your platform CLI or log-export tool to extract Errors/Tracebacks only

**Project conventions to honor**:
- Don't auto-commit (per CLAUDE.md «Git Rules»)
- Output dir is gitignored by default (deep_search outputs are working memory, promoted to durable docs only after user review)
- `docs/research/deep_search/` is the canonical output root

---

## 5. File layout to produce (Codex deliverables)

```
.claude/skills/deep-search/
├── SKILL.md                          # main entrypoint — frontmatter + the announcement rule + dispatches to workflows/
├── workflows/
│   ├── postmortem.md                 # detailed steps per §3.1
│   ├── inquiry.md                    # detailed steps per §3.2
│   └── precheck.md                   # detailed steps per §3.3
├── gates/
│   ├── gate_a_external_search.md     # protocol per §2 Gate A, incl. Codex challenge round
│   └── gate_c_major_finding.md       # protocol per §2 Gate C
├── retrieval/
│   ├── data_sources.md               # the full data-source map (where each fact lives)
│   ├── token_safety.md               # the HARD RULES from §4
│   └── codex_collaboration.md        # how to invoke /codex:rescue + verification rules for citations
├── templates/
│   ├── report.md                     # report.md template (sections: Context, Evidence, Findings, Citations, Next steps)
│   ├── prior_updates.diff            # diff template stub
│   ├── external_research.md          # external research findings template
│   └── experiment_meta.md            # meta.md template emitted by precheck GO
└── SPEC.md                           # this file (don't edit it)
```

Also produce:
```
scripts/_deep_search_metric_query.py  # token-safe metric query helper
                                       # usage: python scripts/_deep_search_metric_query.py <job_id>
                                       # output: table rows (metric, chart, n, last_step, last_value, max_value)
                                       # reads outputs/<platform>/all-metrics-long.csv with a single-pass filter
.gitignore                              # add `docs/research/deep_search/` line if not present
```

---

## 6. SKILL.md frontmatter (Codex must use exactly this)

```yaml
---
name: deep-search
description: |
  Project-local skill that turns experiment outcomes into knowledge updates.
  Three subcommands: postmortem (after a job hits terminal state), inquiry (cross-experiment Q&A),
  precheck (search prior evidence for a proposed experiment direction). Uses your experiment platform exports + local
  docs + memory; delegates external paper search to Codex via a 1-round challenge protocol and
  verifies citations with WebFetch. Surfaces major findings as plain-language chips to the user.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash
  - WebFetch
  - WebSearch
  - AskUserQuestion
  - Skill
  - Agent
---
```

(`Skill` is needed to invoke `/codex:rescue`. `Agent` enables fallback subagent calls.)

---

## 7. Constraints Codex MUST respect when writing these files

1. **Don't invent file paths**. Use the paths in §5 verbatim. If a referenced file doesn't exist yet (e.g., paper_priors.md), the skill must check and gracefully say "not present, skipped".
2. **Don't promise capabilities the skill can't deliver**. e.g., "auto-detects similar past failures" — the skill matches on tags + names + grep, NOT on semantic similarity, and the docs should say so.
3. **Mandatory announcement line** (§1) must be the FIRST output of every invocation.
4. **Gate A `(Recommended)` marker** — when claude_code surfaces AskUserQuestion at Gate A, the option Claude believes is best must be FIRST with `(Recommended)` appended (per the AskUserQuestion convention).
5. **Codex collaboration** — Gate A's Codex round is capped at 1 round, not 3 (per the user's "节 token" preference).
6. **Citation verification** — every external citation Codex returns must be WebFetched to confirm the title matches. Unverified citations get tagged `[unverified]` and excluded from prior diffs.
7. **No auto-commit** anywhere. Output directory writes only.
8. **All output paths are absolute** in references (start from the repo root).
9. **Cite using `file:line` notation** in the report so Claude Code's UI auto-links them.
10. **Chinese OK in body text** since the project is bilingual; keep frontmatter and code identifiers English.

---

## 8. Out-of-scope (do NOT add)

- Don't bake in arxiv/Semantic-Scholar HTTP calls inside the skill — delegate to Codex via `/codex:rescue`.
- Don't try to auto-promote priors. Promotion is a user decision via Gate C.
- Don't add a "watch jobs" mode — that belongs in a separate monitoring tool.
- Don't write hooks. Hooks are out of scope for v0.

---

## 9. Acceptance test (Claude will run this after Codex delivers)

1. `/deep-search precheck "ExpA add layer-norm gating"` should:
   - Detect `gating` axis
   - Flag CLOSED-AXIS-HIT against `memory/feedback_gating_axis_closed.md` (if exists; otherwise note prior pattern from decision_log)
   - Return `REDUCED-PRIORITY` recommendation with citations to ExpB and ExpC
   - Produce report.md at the documented path
2. `/deep-search inquiry "为什么 valid ↑ 不预测 LB ↑？"` should:
   - Pull at least 3 hits from decision_log.md and experiment_logs/
   - Mention the repeated pattern
   - NOT trigger external search (sufficient local evidence)
3. `/deep-search postmortem 98238` (when terminal) should:
   - Read jobs-summary.csv for the row
   - Pull metrics summary via the helper
   - Produce report.md
   - If LB > current SOTA → trigger Gate C and produce chips for the user

---

## 10. Delivery

Codex returns a single message with:
- Confirmation each file in §5 was written
- A short list of any deviations from this SPEC, each with rationale
- The exit code of a `node --check` style sanity check (e.g., grep the SKILL.md frontmatter exists with `python -c 'import yaml; yaml.safe_load(open(".claude/skills/deep-search/SKILL.md").read().split("---")[1])'`)
