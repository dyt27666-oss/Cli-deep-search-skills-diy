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

4. **Wait** for Codex output. Dreamwalk Codex tasks typically take 10-25 minutes due to multi-axis arxiv searching. **Do not poll** — let bg notification arrive.

5. **Triage the returned papers** against project constraints **before showing to user**:
   - Auto-reject: papers requiring text/image/multimodal data, papers requiring multi-task labels we don't have, papers requiring features we lack
   - Auto-flag for caution: papers requiring wholesale backbone replacement (large risk, slow to validate)
   - Auto-promote: drop-in modules ≤ 200 lines that fit the current backbone

6. **Cross-check against project history**: for each surviving paper, grep `decision_log.md` + `experiments/*/meta.md` for any prior mention of the same mechanism — if it was discussed but skipped (e.g. blocked on a now-resolved prerequisite), call this out explicitly. The team may have already deferred this exact direction.

7. **Synthesize**: rank survivors by **expected EV × P(success) ÷ implementation cost**. Use the user's stated eval-quota threshold (if known — e.g. "minimum +0.0005 expected lift") as a floor cut.

8. **Chip the user** on which 1-2 directions to develop into a precheck or experiment.

## Output

Directory: `docs/research/deep_search/<YYYYMMDD-HHMM>_dreamwalk/`

Required files:
- `dreamwalk_brief.md` — the Codex brief verbatim (for reproducibility)
- `paper_candidates.md` — Codex's raw paper list + your triage table
- `recommendation.md` — top 2-3 candidates with priority ranking + rationale

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

## Relation to other workflows

- `dreamwalk` is a **discovery** step. Its output should never be implemented directly. Always followed by `precheck` on the top 1-2 candidates before submitting an experiment.
- After an experiment chosen from `dreamwalk` candidates lands, the `postmortem` should reference back to the dreamwalk run dir for reproducibility ("idea came from `docs/research/deep_search/<run_dir>/recommendation.md` candidate #N").

## Example invocation (real, from 2026-05-14 session)

```
/deep-search dreamwalk "post-PROMOTE plateau on industrial PCVR competition; LB 0.825 needs to reach 0.829 for Top 50 cutoff; already explored cross-branch / calibration / cate-OOF / optimizer-β2 / seq-time-Fourier / IF-DFM-Lite-recency; need NEW mechanism families"
```

Result: see `docs/research/deep_search/2026-05-14_dreamwalk_post_promote/` — Codex returned papers across regularization, behavior-conditioning, hyper-network, contrastive, distillation, and adversarial-shift families; top 2 chosen for follow-up precheck.
