# Gate C — Major Finding Chips

Purpose: surface major knowledge changes to the user in plain language and record only user-approved prior diffs.

## Trigger Conditions

Trigger Gate C when any condition is true:

- Proposed prior promotion from Working to Episodic or Episodic to Semantic.
- Proposed prior demotion or review flag for a Semantic prior.
- A KILL has a mechanism not previously documented locally.
- A PROMOTE has LB lift at least `+0.003` over current SOTA.

If none applies, write `Gate C: OFF — no user-facing prior decision needed` in the report.

## Protocol

1. Write a plain-language summary.
   - Maximum three sentences.
   - Avoid jargon where possible.
   - State what changes for the next experiment.
2. Ask the user with AskUserQuestion chips.
   - `question`: `<plain-language conclusion> 要不要把这条写进 prior？`
   - `multiSelect`: `false` (required so the `preview` field is supported by AskUserQuestion).
   - Include context-specific options.
   - Default options may include:
     - `写进 [[domain-hints-semantic]]`
     - `写进 [[memory]] feedback_*`
     - `暂不写，下次实验复现再说 (Recommended)`
   - Use the `preview` field on at least one option to show proposed diff lines.
3. On user pick, write `<PROJECT_ROOT>/docs/research/deep_search/<run_dir>/prior_updates.diff`.
   - Do not directly edit Semantic priors unless the user explicitly chooses an edit path.
   - Never auto-commit.
   - If the user chooses to defer, write a short deferred note in `report.md` instead of a prior diff.

## Diff Rules

- Verified external citations may support a diff; unverified citations cannot.
- Local claims need `file:line` citations in the report.
- Keep proposed prior text short enough for human review.
