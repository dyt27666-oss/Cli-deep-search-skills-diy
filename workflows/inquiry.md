# /deep-search inquiry "<question>"

Purpose: answer a cross-experiment research question from local evidence first, then only ask for external search if local evidence is too thin.

## Required First Line

Before tool calls, output:

`[deep-search] inquiry "<question>", mode=local-only — <short reason>`

Use `local-only` initially. Switch to `local+external` only after Gate A is triggered and the user chooses paper search angles.

## Steps

1. Parse the question.
   - Extract experiment IDs matching `I-\d+`.
   - Extract axis names such as `gating`, `calibration`, `focal`, `sequence`, `item-id`, `time-feature`, `architecture`, `loss-reweighting`, `multi-cate`, `userpair`, and `regularization`.
   - Extract mechanism phrases, including Chinese terms such as `valid`, `LB`, `不预测`, `提升`, `下降`, `门控`, `校准`, `序列`, and `时间`.
2. Local retrieval, in this order, stopping once at least five strong hits are collected.
   - Grep `<PROJECT_ROOT>/decision_log.md` for IDs and keywords.
   - Grep `<PROJECT_ROOT>/eval_Logs/*.md` for IDs and keywords if present.
   - Grep `<PROJECT_ROOT>/memory/feedback_*.md` for axis names if present.
   - Grep `<PROJECT_ROOT>/docs/paper_priors.md` for keywords if present.
   - Grep `<PROJECT_ROOT>/outputs/taiji-output/training/jobs-summary.csv` by `name` or I-tag only; do not inspect heavy metric logs.
3. Decide Gate A.
   - If fewer than three local hits across `decision_log.md`, `eval_Logs/`, `memory/`, and `docs/paper_priors.md`, use Gate A to ask whether to search externally.
   - If three or more local hits exist, do not trigger external search; proceed with local synthesis.
4. Synthesize.
   - Write one paragraph answering the question.
   - Add bullets for each claim with `file:line` citations.
   - Explicitly distinguish evidence from inference.
5. Apply Gate C only if the inquiry reveals a previously undocumented mechanism that should become a prior candidate.
6. Write output.
   - Directory: `<PROJECT_ROOT>/docs/research/deep_search/<YYYYMMDD-HHMM>_inquiry/`.
   - Required file: `report.md` based on `templates/report.md`.
   - Optional file: `external_research.md` only if Gate A was accepted by the user.

## Acceptance Coverage

For `/deep-search inquiry "为什么 valid ↑ 不预测 LB ↑？"`, this workflow requires at least three local hits from `decision_log.md` and `eval_Logs/` if available, requires mentioning the documented `val ↑ / LB ↓` pattern (cite the running count from `docs/active_state.md` or `decision_log.md` at retrieval time — do not hardcode the count), and forbids external search when local evidence is sufficient.
