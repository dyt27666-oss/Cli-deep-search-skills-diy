# Gate A — External Paper Search

Purpose: decide whether local evidence is insufficient or surprising enough to justify external paper retrieval.

## Trigger Conditions

Trigger Gate A when any condition is true:

- `postmortem`: the result is a PROMOTE with LB lift at least `+0.003` over current SOTA.
- `postmortem`: the result is a surprise KILL whose mechanism is not covered by `<PROJECT_ROOT>/docs/paper_priors.md`.
- `postmortem`: the result contradicts a Semantic prior in `<PROJECT_ROOT>/docs/domain_hints.md`.
- `inquiry`: local evidence has fewer than three hits across `decision_log.md`, `experiment_logs/`, `memory/`, and `docs/paper_priors.md`.
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

## Pre-Gate-A: Read Project Constraints (MANDATORY)

**Before drafting search angles, the skill MUST read the project's hard-constraint sources** so the search isn't framed against constraints that prohibit the result.

**Constraint sources to read** (skip if a source doesn't exist in the project):
1. **Official rules / data card** (e.g., `<PROJECT_ROOT>/docs/competition_original.md`, `docs/data_card.md`, `README.md` data sections, or upstream challenge website doc)
   - Data shape: anonymized integers? raw text/image/URL? feature types? max-sequence-length? privacy filters?
   - Modeling rules: ensemble allowed? max parameters? inference latency cap? frozen pretrained models OK?
2. **Project's baseline doc** (e.g., `<PROJECT_ROOT>/docs/baseline_*.md`, `manifest.json` top entries)
   - Current SOTA score, gap to target, fork base
3. **Closed-axis registry** (`<PROJECT_ROOT>/docs/active_state.md` + `<USER_AUTO_MEMORY>/feedback_*axis_closed*.md`)
4. **Data EDA summary** (e.g., `<PROJECT_ROOT>/docs/data_eda_summary.md`, `data_understanding_*.md`)

**For each constraint found, paste it VERBATIM (not summarized) into the Codex search prompt.** Summarization loses fidelity — the exact wording often matters for whether a paper's method applies.

**Anti-pattern (what NOT to do)**:
- Drafting an angle like "cold-item CTR architecture, ≥2025, industrial papers" when the project data is anonymized-int-only. Codex will happily return text-based papers (MOON / MIM / etc.) that physically can't be applied to your data.

**Correct pattern**:
- Read data card → discover "no raw text/image/URL" → re-frame angle as "dense item representation derived from anonymized integer features (NO text), ≥2025". Codex returns angle-specific papers that actually fit.

**If constraints are unclear**: surface a chip to the user asking which constraint to prioritize, BEFORE drafting angles.

## Protocol

1. **Pre-Gate-A**: read constraint sources above; extract verbatim constraint clauses; if any clause directly prohibits the search target (e.g., "no text" while the question implies text-based solutions), narrow the question with the user via chips before continuing.
2. **Year floor**: per Year Freshness Rule above, compute and announce the year floor.
3. Draft two or three candidate search angles.
   - Format each angle as `<keyword>; ≥<year_floor>; <venue filter>; expected evidence type`.
   - **Every angle MUST already incorporate the Pre-Gate-A constraints**. Example: if data is anonymized-int-only, angle becomes `dense item representation from anonymized integer features (NO text), ≥2025` not just `cold-item architecture, ≥2025`.
   - Keep angles tied to the local mechanism, not broad architecture fishing.
4. Invoke `/codex:rescue` for one challenge round only:
   - Prompt: `Challenge these search angles for /deep-search Gate A. 1 round only. Reply: ACCEPT / ADD <angle> / DROP <angle> / REFRAME <angle to angle>.`
   - **Include the project constraints (verbatim) at the top of the challenge prompt** so Codex challenges against the real constraint set, not generic.
5. Resolve Codex's challenge.
   - Accept useful `ADD`, `DROP`, or `REFRAME` feedback with a one-line rationale.
   - If Codex disagrees with the initial list, restate the final list and why.
   - Do not continue into a multi-round debate.
6. Ask the user with AskUserQuestion chips.
   - `question`: `Gate A — 准备外部搜查，选角度（可多选）`
   - `header`: `Search angle`
   - `multiSelect: true`
   - Every option label MUST include the year floor tag (e.g., `≥2025`) AND the binding constraint tag (e.g., `anonymized-only`).
   - Put the best option first and append `(Recommended)` to that option label.
   - Put `都不搜，仅靠本地` last.
7. If the user overrides the year floor (states a different cutoff), GOTO step 2 and recompute; re-issue chips with the new floor.
8. If the user chooses external angles, invoke `/codex:rescue`:
   - Prompt: `Project constraints: <verbatim constraint clauses from Pre-Gate-A>. Deep search arXiv + Semantic Scholar for: <angles>. Year filter: ≥<year_floor> only (today is <YYYY-MM-DD>, anything pre-<year_floor> is stale for this topic). Return for each: paper title, authors, year, venue, arxiv URL, DOI, 2-sentence finding, relevance to <project context>'s pipeline UNDER the listed constraints (REJECT papers whose method violates a stated constraint). Max 5 papers per angle. Reject any paper without permanent URL (no arxiv / no DOI).`
9. Verify every returned citation.
   - WebFetch each arXiv URL.
   - Parse or inspect the fetched page title and confirm it matches the returned paper title.
   - Reject any paper whose published year < year_floor — explicit additional check (Codex may slip).
   - **Reject any paper whose method requires inputs NOT in the project's data card** (e.g., text-based methods on anonymized-int datasets) — re-check against Pre-Gate-A constraints.
   - Bad citations are tagged `[unverified: <reason>]` or `[constraint-violation: <which-constraint>]` and excluded from `prior_updates.diff`.
   - Verified + constraint-compatible citations may be summarized in `external_research.md`.
10. Write external findings, if any, to:
    - `<PROJECT_ROOT>/docs/research/deep_search/<run_dir>/external_research.md`

## Hard Limits

- No inline arXiv or Semantic Scholar HTTP/API calls by this skill.
- **Pre-Gate-A constraint reading is MANDATORY** — never draft an angle without first reading the project's data card / rules doc / baseline doc.
- **Constraint clauses are pasted VERBATIM** into the Codex prompt, not summarized. Summarization loses fidelity that determines applicability.
- Year floor must be set BEFORE drafting angles. Skill must not draft an angle without a year filter.
- Codex deep-search prompt must include the year floor verbatim + the current date for grounding.
- Step-8 post-verification rejects any paper with `year < year_floor`. Codex may slip; the skill is the final checker.
- Codex challenge is capped at one round.
- User choice is required before external paper search.
- Unverified citations cannot support prior updates.
