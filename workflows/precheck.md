# /deep-search precheck "<proposed exp>"

Purpose: search prior evidence for a proposed idea across closed axes, paper priors, and recent local outcomes before taking action.

## Required First Line

Before tool calls, output:

`[deep-search] precheck "<proposed exp>", mode=local-only — <short reason>`

Use `local-only` initially. Switch to `local+external` only after Gate A is triggered and the user chooses paper search angles.

## Steps

1. Classify the proposed experiment by axis.
   - Recognize at least: `gating`, `loss-reweighting`, `calibration`, `sequence-replacement`, `item-id-feature`, `time-feature`, `multi-cate`, `userpair`, `architecture-compressor`, `architecture-attention-bias`, and `regularization`.
   - Use explicit keywords from the proposal; do not infer a hidden axis without evidence.
2. Read closed-axis memory. Try BOTH locations (this project stores some feedback in the repo, others in user-global auto-memory):
   - Repo: `<PROJECT_ROOT>/memory/feedback_*axis_closed*.md` and similar `feedback_*.md` files if present.
   - User-global auto-memory: `<USER_AUTO_MEMORY>/feedback_*axis_closed*.md` and `feedback_*.md`.
   - For each axis match (either location), mark `CLOSED-AXIS-HIT` in the report with `file:line` citations.
   - If BOTH locations have no matching file, write `not present, skipped` and fall back to `decision_log.md` and `experiment_logs/` pattern evidence.
3. If `CLOSED-AXIS-HIT`, compare mechanism structure.
   - Read the `Why:` and `How to apply:` sections in the matching feedback file.
   - Decide whether the proposed mechanism is structurally similar to the closed mechanism or clearly distinct.
4. Pull paper priors.
   - Read `<PROJECT_ROOT>/docs/paper_priors.md` if present.
   - Read `<PROJECT_ROOT>/docs/paper_analysis.md` if present.
   - Mark whether the proposal has local paper-grounded `+EV`, `-EV`, or no local paper prior.
5. Check recent similar KILLs or failed axes.
   - Grep `<PROJECT_ROOT>/decision_log.md` for the axis and experiment tags.
   - Grep `<PROJECT_ROOT>/experiment_logs/*.md` if present.
   - Use `jobs-summary.csv` names only for lightweight job status context.
6. Recommend one decision.
   - `GO`: axis open, paper prior is positive or neutral, and no recent structurally similar KILL.
   - `NEEDS-JUSTIFICATION`: limited prior evidence; proceed with explicit rationale.
   - `REDUCED-PRIORITY`: N prior attempts on this axis closed at lower scores. Doesn't mean the axis is dead, but you should: (a) confirm your variant is structurally different from prior failures (see citations), OR (b) combine with another axis that compensates for the prior failure mode, OR (c) deprioritize unless other axes are exhausted.
7. Apply Gate A only if the proposed mechanism references a paper or mechanism absent from `paper_priors.md` and `paper_analysis.md`, and the user wants paper-grounded sanity checking.
8. Write output.
   - Directory: `<PROJECT_ROOT>/docs/research/deep_search/<YYYYMMDD-HHMM>_precheck/`.
   - Required file: `report.md` based on `templates/report.md`.
   - Optional file if `GO`: `experiment_meta_template.md` based on `templates/experiment_meta.md`.
   - Optional file if Gate A accepted: `external_research.md`.

## Acceptance Coverage

For `/deep-search precheck "ExpA add layer-norm gating"`, this workflow requires detecting the `gating` axis, checking `memory/feedback_gating_axis_closed.md` or noting its absence and falling back to local logs, flagging `CLOSED-AXIS-HIT` when present, citing ExpB and ExpC if local files contain those references, and returning `REDUCED-PRIORITY` when prior same-axis attempts closed at lower scores and the mechanism is structurally similar to the closed gating pattern.
