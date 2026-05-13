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

## Year Freshness Rule (apply BEFORE drafting angles)

Recency requirements vary by topic. The skill MUST set an explicit year floor before drafting angles, and surface that floor in every Codex prompt and every user-facing chip option.

**Compute `current_year` fresh — DO NOT hardcode**:
- Read system clock: `date +%Y` via Bash, OR rely on the project context's date if Bash isn't being called.
- The session-context date is the source of truth. If conversation suggests a different year (e.g., the user mentions "2026"), trust the user.

**Default year floor by topic type**:

| Topic type | Default floor | Rationale |
|---|---|---|
| Industrial CTR / recommendation architecture | `current_year - 1` | LLM-era pace; 2-yr-old industrial paper often already superseded |
| LLM / multimodal item encoders | `current_year - 1` | Same |
| ML methodology (DRO / IPS / domain adaptation) | `current_year - 2` | Slower but still moving |
| Theory / foundational / classical mechanisms | `current_year - 5` | Stable; older work is fine |
| Specific named architecture follow-ups (e.g., HSTU successors) | `current_year - 1` | Industrial fast-iterate |

**If the topic doesn't fit any row**: default to `current_year - 2`. Announce the choice explicitly in the report and in the Codex prompt.

**Surface to user**:
- Every Gate A AskUserQuestion option label MUST include the year floor as an explicit tag, e.g. `"LLM/text-encoder as item backbone; ≥2025; …"`.
- Every Codex deep-search prompt MUST repeat the year floor in plain language (not just in the angle string), with the rationale: `"Year filter: ≥2025 only (today is YYYY-MM-DD, anything pre-2025 is stale for this topic)."`
- If the user overrides the floor (e.g., "use ≥2024 instead"), re-issue Gate A chips with the new floor; do NOT silently accept.

**Examples (assume `current_year = 2026`)**:
- Industrial CTR text-encoder paper: `≥2025`
- Domain-adaptation methodology: `≥2024`
- Information-bottleneck theory: `≥2021`

## Protocol

1. **Year floor**: per Year Freshness Rule above, compute and announce the year floor.
2. Draft two or three candidate search angles.
   - Format each angle as `<keyword>; ≥<year_floor>; <venue filter>; expected evidence type`.
   - Keep angles tied to the local mechanism, not broad architecture fishing.
3. Invoke `/codex:rescue` for one challenge round only:
   - Prompt: `Challenge these search angles for /deep-search Gate A. 1 round only. Reply: ACCEPT / ADD <angle> / DROP <angle> / REFRAME <angle to angle>.`
4. Resolve Codex's challenge.
   - Accept useful `ADD`, `DROP`, or `REFRAME` feedback with a one-line rationale.
   - If Codex disagrees with the initial list, restate the final list and why.
   - Do not continue into a multi-round debate.
5. Ask the user with AskUserQuestion chips.
   - `question`: `Gate A — 准备外部搜查，选角度（可多选）`
   - `header`: `Search angle`
   - `multiSelect: true`
   - Every option label MUST include the year floor tag (e.g., `≥2025`).
   - Put the best option first and append `(Recommended)` to that option label.
   - Put `都不搜，仅靠本地` last.
6. If the user overrides the year floor (states a different cutoff), GOTO step 1 and recompute; re-issue chips with the new floor.
7. If the user chooses external angles, invoke `/codex:rescue`:
   - Prompt: `Deep search arXiv + Semantic Scholar for: <angles>. Year filter: ≥<year_floor> only (today is <YYYY-MM-DD>, anything pre-<year_floor> is stale for this topic). Return for each: paper title, authors, year, venue, arxiv URL, DOI, 2-sentence finding, relevance to <project context>'s pipeline. Max 5 papers per angle. Reject any paper without permanent URL (no arxiv / no DOI).`
8. Verify every returned citation.
   - WebFetch each arXiv URL.
   - Parse or inspect the fetched page title and confirm it matches the returned paper title.
   - Reject any paper whose published year < year_floor — explicit additional check (Codex may slip).
   - Bad citations are tagged `[unverified: <reason>]` and excluded from `prior_updates.diff`.
   - Verified citations may be summarized in `external_research.md`.
9. Write external findings, if any, to:
   - `<PROJECT_ROOT>/docs/research/deep_search/<run_dir>/external_research.md`

## Hard Limits

- No inline arXiv or Semantic Scholar HTTP/API calls by this skill.
- Year floor must be set BEFORE drafting angles. Skill must not draft an angle without a year filter.
- Codex deep-search prompt must include the year floor verbatim + the current date for grounding.
- Step-8 post-verification rejects any paper with `year < year_floor`. Codex may slip; the skill is the final checker.
- Codex challenge is capped at one round.
- User choice is required before external paper search.
- Unverified citations cannot support prior updates.
