# Gate A — External Paper Search

Purpose: decide whether local evidence is insufficient or surprising enough to justify external paper retrieval.

## Trigger Conditions

Trigger Gate A when any condition is true:

- `postmortem`: the result is a PROMOTE with LB lift at least `+0.003` over current SOTA.
- `postmortem`: the result is a surprise KILL whose mechanism is not covered by `<PROJECT_ROOT>/docs/paper_priors.md`.
- `postmortem`: the result contradicts a Semantic prior in `<PROJECT_ROOT>/docs/domain_hints.md`.
- `inquiry`: local evidence has fewer than three hits across `decision_log.md`, `eval_Logs/`, `memory/`, and `docs/paper_priors.md`.
- `precheck`: the proposed mechanism is not found in `docs/paper_priors.md` and not found in `docs/paper_analysis.md`.

If none applies, write `Gate A: OFF — sufficient local evidence` in the report.

## Protocol

1. Draft two or three candidate search angles.
   - Format each angle as `<keyword>; venue/year filter; expected evidence type`.
   - Keep angles tied to the local mechanism, not broad architecture fishing.
2. Invoke `/codex:rescue` for one challenge round only:
   - Prompt: `Challenge these search angles for /deep-search Gate A. 1 round only. Reply: ACCEPT / ADD <angle> / DROP <angle> / REFRAME <angle to angle>.`
3. Resolve Codex's challenge.
   - Accept useful `ADD`, `DROP`, or `REFRAME` feedback with a one-line rationale.
   - If Codex disagrees with the initial list, restate the final list and why.
   - Do not continue into a multi-round debate.
4. Ask the user with AskUserQuestion chips.
   - `question`: `Gate A — 准备外部搜查，选角度（可多选）`
   - `header`: `Search angle`
   - `multiSelect: true`
   - Put the best option first and append `(Recommended)` to that option label.
   - Put `都不搜，仅靠本地` last.
5. If the user chooses external angles, invoke `/codex:rescue`:
   - Prompt: `Deep search arXiv + Semantic Scholar for: <angles>. Return for each: paper title, authors, year, venue, arxiv URL, DOI, 2-sentence finding, relevance to UniRec-KDDCup2026's pCVR pipeline. Max 5 papers per angle.`
6. Verify every returned citation.
   - WebFetch each arXiv URL.
   - Parse or inspect the fetched page title and confirm it matches the returned paper title.
   - Bad citations are tagged `[unverified: <reason>]` and excluded from `prior_updates.diff`.
   - Verified citations may be summarized in `external_research.md`.
7. Write external findings, if any, to:
   - `<PROJECT_ROOT>/docs/research/deep_search/<run_dir>/external_research.md`

## Hard Limits

- No inline arXiv or Semantic Scholar HTTP/API calls by this skill.
- Codex challenge is capped at one round.
- User choice is required before external paper search.
- Unverified citations cannot support prior updates.
