# /deep-search dreamwalk "<scope hint>"

Purpose: open-ended, wide-net paper hunt that surfaces NEW mechanism families the team hasn't explored yet. Use when the project is plateauing on incremental +EV from already-explored axes and needs cross-axis breadth — NOT when there is a specific question (`inquiry`) or a proposed direction (`precheck`).

The mode is called **dreamwalk** (梦游) because it intentionally **wanders away** from the project's current focus. The point is to find mechanism families the team hasn't considered yet, not to validate an existing hypothesis.

## When to invoke dreamwalk vs inquiry vs precheck

| Subcommand | When |
|---|---|
| `dreamwalk` | "I'm out of ideas / stuck below a competition threshold / need fundamentally new mechanism families" |
| `inquiry` | "Why did X happen / what does the cross-experiment evidence say about Y" — focused Q&A |
| `precheck` | "Should I run experiment Z" — axis evidence for ONE proposed direction |

If the user is still iterating within known axes, use `precheck`. Only fall to `dreamwalk` when the team has explicitly hit a wall ("we need a new axis", "current axes are exhausted", "we need bigger jumps").

## Required First Line

```
[deep-search] dreamwalk "<scope hint>", mode=local+external — wide-net search outside currently-explored axes
```

`dreamwalk` is **always** `mode=local+external` because the goal is precisely to find things NOT in local evidence. There is no local-only dreamwalk.

## Steps

1. **Catalogue current state** (local, fast):
   - Read `docs/active_state.md` for current SOTA, in-flight jobs, and the project's "axis status" table (which axes are CLOSED / PROMOTED / UNTESTED)
   - Read `docs/paper_priors.md` for axes already covered by prior reading
   - Skim `decision_log.md` recent entries for axes recently killed
   - Pull the CLOSED-axis list and the PROMOTED-axis list — these become **exclusion criteria** for the external search

2. **Compose the Codex brief** with the following anti-narrowing structure:
   - State the project's hard constraints (data schema, task type, eval quota, latency)
   - List CLOSED axes explicitly with "DON'T propose papers in these"
   - List PROMOTED axes explicitly with "DON'T re-propose without strict 2026 novelty + clearly different mechanism"
   - Enumerate 6-10 example mechanism families the user has NOT explored ("contrastive learning for tabular rec without text", "meta-learning for distribution adaptation", "hyper-network or expert-routing", "knowledge distillation without text encoders", "adversarial robust training for shift", "new attention variants", "explicit field-pair learning beyond DCN family", "calibration variants beyond Platt", "self-supervised pretraining on pure IDs", etc.). The list should be **examples, not constraints** — explicitly tell Codex it can surprise us.
   - Target output: 8-12 papers across **at least 5 distinct mechanism families**. Spread the net.
   - Output format: per-paper Title / arXiv ID / Mechanism family (1 word) / Mechanism (1 line) / Reported lift / Fit (✅/⚠️/❌) / Implementation cost / Why novel relative to closed/explored axes
   - Demand: each paper must be verifiable via arXiv ID (≥2601 prefix or peer-reviewed 2026 conference); no padding with multimodal-only or text-only papers that violate our data schema

3. **Optional: parallel narrow-axis Codex** if user wants both breadth and depth. Dispatch a second Codex task that targets ONE specific mechanism family for 2026 evolution — useful when user names "the 2025 champion's axis X, find its 2026 successors". Run side-by-side with the wide dreamwalk.

   **MANDATORY brief additions for every Codex dreamwalk dispatch** (the 2026-05-14 stuck-task post-mortem made these load-bearing):

   - **Hard time budget = 25 minutes wall clock.** If exceeded, Codex MUST write whatever it has so far and exit. The brief must say verbatim: *"If you have not finished by minute 25, stop searching and write your current paper list to `papers.md` with a `## STATUS: PARTIAL_AT_25MIN` header. Do NOT keep going past 25 minutes regardless of completeness."*

   - **Incremental checkpoint writes.** The brief must instruct: *"After each paper you verify (arXiv abstract fetched, fit assessed), APPEND it to `papers.md` immediately. Do not batch all 8-12 papers to the end. If you crash or are killed mid-task, the partial file must contain the verified papers so far."* Use a `## Verified Papers` section that grows incrementally, plus a `## In-Progress` section with the paper currently being researched (so the resume step knows where to continue).

   - **Resume awareness.** The brief must instruct: *"BEFORE searching, READ `papers.md` if it exists. Skip any arXiv IDs already in the `## Verified Papers` section. If you find a `## In-Progress` entry, treat it as your starting point. Append rather than overwrite."*

   - **5-minute progress pings.** The brief must instruct: *"Every 5 minutes of wall-clock, append a one-line status to `progress.log` in the same dir: `[HH:MM] phase=<arxiv-search | abstract-fetch | composing> papers_verified=<N> currently=<arxiv_id or 'idle'>`. This is how the human (or Claude) detects stalls without reading the JSONL transcript."*

   - **Mandatory file write at exit.** The brief must end with: *"FINAL ACTION (non-negotiable, regardless of completion state): write `papers.md` to disk. If you skipped this in your final response, the run is considered failed."*

4. **Wait** for Codex output, but **arm a 30-minute kill timer on dispatch**. Codex dreamwalk tasks should complete in 10-25 min; if `papers.md` is still missing at minute 30 OR `progress.log`'s last entry is older than 7 minutes (= 1.5 ping cycles), the task is stuck and must be killed via `codex-companion.mjs cancel <job-id>`. Then re-dispatch — the new task picks up partial papers.md via the resume rule.

   **Use Monitor or a periodic poll** (10 min) on `progress.log` mtime + `papers.md` existence. Do NOT rely on the Codex bg launcher notification — past sessions confirmed it fires only when the launcher forwards the task, not when the underlying paper hunt completes.

5. **Triage the returned papers** against project constraints **before showing to user**:
   - Auto-reject: papers requiring text/image/multimodal data, papers requiring multi-task labels we don't have, papers requiring features we lack
   - Auto-flag for caution: papers requiring wholesale backbone replacement (large risk, slow to validate)
   - Auto-promote: drop-in modules ≤ 200 lines that fit the current backbone

6. **Cross-check against project history**: for each surviving paper, grep `decision_log.md` + `experiments/*/meta.md` for any prior mention of the same mechanism — if it was discussed but skipped (e.g. blocked on a now-resolved prerequisite), call this out explicitly. The team may have already deferred this exact direction.

7. **Synthesize**: rank survivors by **expected EV × P(success) ÷ implementation cost**. Use the user's stated eval-quota threshold (if known — e.g. "minimum +0.0005 expected lift") as a floor cut.

8. **Chip the user** on which 1-2 directions to develop into a precheck or experiment.

## Output

### Directory naming

`docs/research/deep_search/<YYYY-MM-DD>_dreamwalk_<TAG>/`

The `<TAG>` is **mandatory** and follows a strict schema (see below). One dreamwalk run = one TAG. Future runs that hit the same TAG should resume into the existing dir (per the resume rule), not create parallel dirs.

### Mandatory TAG schema

Format: `[<AXIS-STATE>-<SCOPE-WORD>]` — uppercase, hyphen-separated, ≤ 30 chars.

`<AXIS-STATE>` documents WHY this dreamwalk fires (the project state that triggered it):
- `POST-PROMOTE-PLATEAU` — last few experiments PROMOTED but +EV diminishing
- `POST-KILL-PIVOT` — last 2+ KILL on same axis, looking for new axis
- `PRE-SUBMISSION-DOUBLECHECK` — final pre-Round-N check for missing mechanism families
- `RECOVERY-AFTER-STUCK` — earlier dreamwalk stuck/incomplete, this is the retry

`<SCOPE-WORD>` is the breadth modifier:
- `WIDE` — 5+ mechanism families, "show me everything"
- `NARROW-<axis>` — single named axis evolution (e.g. `NARROW-ATTENTION`, `NARROW-CALIBRATION`)
- `DEPTH-<axis>` — pile up evidence on one axis already-considered

Example tags: `[POST-PROMOTE-PLATEAU-WIDE]`, `[POST-KILL-PIVOT-NARROW-CALIBRATION]`, `[RECOVERY-AFTER-STUCK-WIDE]`.

### papers.md header (Codex MUST write this verbatim at file creation, before any paper)

```markdown
# Dreamwalk: [<TAG>] — <YYYY-MM-DD>

## Tag
`[<TAG>]`

## Scope hint
<the verbatim "scope hint" argument the user passed; full sentence>

## Trigger
- <one-line: what made this dreamwalk fire — competition cutoff gap, recent KILL pattern, plateau, etc>
- <one-line: any user-cited number/threshold relevant to the search>

## Project snapshot at run time
- SOTA exp: <id + LB + 1-line mechanism>
- In flight: <list of in-flight job ids if any>
- Daily eval quota: <N>, threshold +<expected lift minimum>
- Backbone constraint: <whether backbone replacement is on/off the table>

## STATUS: RUNNING

## Verified Papers
<incremental append-only — each verified paper goes here>

## In-Progress
<current arXiv ID being researched, blank when idle>
```

Required files in the dir:
- `dreamwalk_brief.md` — the Codex brief verbatim (for reproducibility)
- `papers.md` — Codex writes this incrementally per the header schema above + `## STATUS` value (one of: `RUNNING`, `PARTIAL_AT_25MIN`, `COMPLETE`, `STUCK_ABORTED`)
- `progress.log` — Codex appends a one-line ping every 5 min: `[HH:MM] phase=<x> papers_verified=<N> currently=<arxiv_id or 'idle'>`. Used by Claude to detect stalls.
- `recommendation.md` — top 2-3 candidates with priority ranking + rationale (written by Claude after dreamwalk completes, NOT by Codex)

### Why TAG matters (rationale)

Without a tag, future sessions can only find dreamwalks by date and a generic "wide" / "narrow" descriptor. With a tag, you can:
- Grep `[POST-PROMOTE-PLATEAU-*]` across all dreamwalks to compare what mechanism families surfaced at each plateau in project history
- Filter "have we already dreamwalked the calibration axis under PIVOT?" before re-dispatching
- Build a long-term knowledge graph of dreamwalk-state-vs-paper-recommendation that informs prior updates

Untagged dreamwalks become indistinguishable archaeology after 2-3 weeks. Every dreamwalk must carry its provenance.

Optional: `external_research.md` if WebFetch verification of any specific arXiv ID was needed (the Codex companion already does this internally; only re-fetch when a paper looks borderline).

## Constraints

- **No assumption smuggling**: do NOT pre-filter the Codex brief by what you (Claude) think is plausible. The point of dreamwalk is to surface things you wouldn't have proposed. Codex should see the raw constraint list and decide.
- **No padding**: if Codex finds only 4-5 verifiable 2026 papers, return only those. Do not fill with 2024-25 papers to hit "8-12". Quality > quantity.
- **Honest verdicts**: do not soften "❌ doesn't fit" to "⚠️ might work" just because the paper sounds interesting. The user needs to see clear go/no-go signals.
- **Cross-axis priority**: when 2+ surviving papers are in the same mechanism family, only keep the best one — the goal is mechanism diversity, not paper count.

## Failure modes to watch

| Mode | Symptom | Mitigation |
|---|---|---|
| Codex returns 0-2 papers, all already explored | Codex narrowed too early | Re-dispatch with explicit "you are missing families: X, Y, Z; try arxiv search for [terms]" |
| All papers fail the data-schema check | Multimodal bias in 2026 corpus | Add "we have ONLY anonymized integer IDs + dense floats" to brief; re-dispatch |
| All papers require backbone replacement | High-impact papers tend to be backbone-changing | Mark them all "🔴 high risk" and explicitly chip user on architectural risk tolerance |
| Papers fit but expected lift is below user's quota threshold | Sub-threshold candidates | Honest report; explicitly tell user "no candidate above your +0.0005 threshold" rather than pad |
| **Codex bg task runs > 30 min without writing `papers.md`** | `papers.md` missing or 0 bytes; `progress.log` last entry > 7 min stale; `codex-companion.mjs status --all` shows `elapsed > 30m` | **(Post-2026-05-14 stuck-tasks lesson)** Cancel the job via `codex-companion.mjs cancel <task-id>`. Read `papers.md` partial content if any. Re-dispatch with the **same** target paths — resume rule + checkpoint writes preserve what was verified. Common root cause = Codex stuck in arXiv PDF parsing on a paywalled or malformed PDF. |
| **Multiple zombie tasks accumulate in broker** | `codex-companion.mjs status --all` shows N running but no actual file growth | Cancel all zombies before re-dispatching. Past sessions found tasks "running" for hours after their work actually completed but the broker wasn't notified. |

## Relation to other workflows

- `dreamwalk` is a **discovery** step. Its output should never be implemented directly. Always followed by `precheck` on the top 1-2 candidates before submitting an experiment.
- After an experiment chosen from `dreamwalk` candidates lands, the `postmortem` should reference back to the dreamwalk run dir for reproducibility ("idea came from `docs/research/deep_search/<run_dir>/recommendation.md` candidate #N").

## Example invocation (real, from 2026-05-14 session)

```
/deep-search dreamwalk "post-PROMOTE plateau on industrial PCVR competition; LB 0.825 needs to reach 0.829 for Top 50 cutoff; already explored cross-branch / calibration / cate-OOF / optimizer-β2 / seq-time-Fourier / IF-DFM-Lite-recency; need NEW mechanism families"
```

Result: see `docs/research/deep_search/2026-05-14_dreamwalk_post_promote/` — Codex returned papers across regularization, behavior-conditioning, hyper-network, contrastive, distillation, and adversarial-shift families; top 2 chosen for follow-up precheck.
