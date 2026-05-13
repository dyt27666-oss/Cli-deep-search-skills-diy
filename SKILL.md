---
name: deep-search
description: |
  Project-local skill that turns experiment outcomes into knowledge updates.
  Three subcommands: postmortem (after a job hits terminal state), inquiry (cross-experiment Q&A),
  precheck (validate a proposed experiment against closed axes). Uses your experiment platform exports + local
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

# /deep-search

Use this project-local skill when the user invokes `/deep-search <subcommand> [args]` to turn experiment evidence into a defensible knowledge update.

## First Output: Mandatory Announcement

Before any Read, Grep, Glob, Bash, WebFetch, WebSearch, AskUserQuestion, Skill, Agent, Write, or Edit call, output exactly one short announcement line:

`[deep-search] <subcommand> <args>, mode=<local-only|local+external> — <why this mode>`

Examples:

- `[deep-search] postmortem 98238, mode=local-only — terminal status is not confirmed yet, so only local scrape evidence is safe.`
- `[deep-search] inquiry "为什么 valid ↑ 不预测 LB ↑？", mode=local-only — prior local evidence is expected to be sufficient.`
- `[deep-search] precheck "ExpA add layer-norm gating", mode=local-only — closed-axis evidence must be checked before any external search.`

If Gate A later proposes paper search, announce the transition before external retrieval: `[deep-search] Gate A, mode=local+external — local evidence is insufficient or contradicted.`

If Gate A targets a community platform (XHS / Zhihu / B站 etc.) instead of papers, follow `retrieval/external_sources.md`'s phased protocol (Phase 1 WebSearch+WebFetch by default; Phase 2 MediaCrawler CDP mode only with explicit user approval and daily quota intact).

## Dispatch

- For `/deep-search postmortem <job_id>`, follow `workflows/postmortem.md`.
- For `/deep-search inquiry "<question>"`, follow `workflows/inquiry.md`.
- For `/deep-search precheck "<proposed exp idea>"`, follow `workflows/precheck.md`.

Load shared rules as needed:

- Gate A external paper search: `gates/gate_a_external_search.md`.
- Gate C major finding chips: `gates/gate_c_major_finding.md`.
- Token-safe retrieval: `retrieval/token_safety.md`.
- Data-source map: `retrieval/data_sources.md`.
- Codex collaboration and citation verification: `retrieval/codex_collaboration.md`.
- External web + community sources (XHS, Zhihu, B站, etc., staged Phase 1 / Phase 2 protocol with MediaCrawler at `<MEDIACRAWLER_ROOT>/`): `retrieval/external_sources.md`.
- Output templates: `templates/`.

## Operating Rules

- Retrieval comes before synthesis. Act as a librarian, not an oracle.
- Do not auto-commit. Write only output artifacts and optional `prior_updates.diff` for user review.
- Use repo-root absolute output paths in final references, especially under `<PROJECT_ROOT>/docs/research/deep_search/`.
- Cite factual claims with `file:line` notation whenever the source is local.
- If an expected source file is missing, state `not present, skipped` and continue with the remaining sources.
- Do not direct-read or grep token-heavy files listed in `retrieval/token_safety.md`; use the helper or safe summaries instead.
- Do not bake inline arXiv or Semantic Scholar API calls into the workflow; external paper retrieval is delegated through `/codex:rescue` and then verified with WebFetch.
- Gate A Codex challenge is capped at one round.
- Gate A AskUserQuestion must put the best option first and append `(Recommended)` to that option label.
- Gate C never auto-promotes or auto-demotes priors; the user decides via chips.
