# /deep-search postmortem <job_id>

Purpose: inspect one experiment run outcome, connect it to local experiment history and priors, and produce a concise research report plus optional user-reviewed prior diff.

## Required First Line

Before tool calls, output:

`[deep-search] postmortem <job_id>, mode=local-only — <short reason>`

Use `local-only` initially. Switch to `local+external` only after Gate A is triggered and the user chooses paper search angles.

## Steps

1. Read `<PROJECT_ROOT>/outputs/<platform>/jobs-summary.csv`.
   - Find the row whose `job_id` equals the argument.
   - If no row exists, abort with: `job_id not in scrape; refresh your job/run metadata export first`.
   - Cite the row with `file:line` in the report.
2. Determine terminal state.
   - Terminal statuses are `SUCCEED`, `FAILED`, `KILLED`, `CANCELED`, `FINISHED`, `COMPLETED`.
   - If status is not terminal, mark the analysis as `pre-mortem (curve-only)` and avoid final outcome claims.
3. Pull token-safe metrics with Bash:
   - `python3 <PROJECT_ROOT>/scripts/_deep_search_metric_query.py <job_id>`
   - Check exit code: `0` = data found; `1` = metrics file missing (rerun the CLI scrape first); `2` = bad usage. On non-zero, write `metrics not available, skipped` in the report and continue.
   - Include the table in `Evidence` or summarize the rows if the output is long.
4. Pull evaluation result for this job.
   - Read files under `<PROJECT_ROOT>/outputs/<platform>/evaluation/` if present.
   - Match by `mould_id`, exact job id, or `name`/job tag substring.
   - If not present, write `not present, skipped`.
5. Find experiment metadata.
   - Search `<PROJECT_ROOT>/manifest.json` for a matching `name` substring.
   - Search `<PROJECT_ROOT>/experiments/<experiment-id>/meta.md` for the experiment tag if the directory exists.
   - Grep the experiment tag in `<PROJECT_ROOT>/decision_log.md` directly: `grep -n "ExpX" decision_log.md | tail -50` — cheaper and more precise than reading last-200-lines blindly.
   - Read `<PROJECT_ROOT>/experiment_logs/<experiment-id>.md` if present.
6. Find structurally similar past experiments without semantic overclaiming.
   - Match on explicit tags, experiment names, and `ablation_removes` in manifest-like records.
   - Compare obvious val-vs-LB patterns if local evaluation logs mention them.
   - If evidence supports the documented `valid ↑ / LB ↓` repeated pattern, call it out with citations; do not claim automatic semantic detection.
7. Cross-check priors.
   - Read `<PROJECT_ROOT>/docs/paper_priors.md` if present.
   - Read `<PROJECT_ROOT>/docs/domain_hints.md` if present, especially Semantic priors.
   - Search `<PROJECT_ROOT>/memory/feedback_*.md` if present, especially closed-axis rules.
8. Apply Gate A using `<PROJECT_ROOT>/.claude/skills/deep-search/gates/gate_a_external_search.md`.
   - Trigger for PROMOTE with LB at least `+0.003` over current SOTA, surprise KILL not covered by `docs/paper_priors.md`, or contradiction of a Semantic prior.
   - If ON, run the chip protocol and write optional `external_research.md`.
9. Apply Gate C using `<PROJECT_ROOT>/.claude/skills/deep-search/gates/gate_c_major_finding.md`.
   - Trigger for prior promotion/demotion proposals, undocumented KILL mechanism, or PROMOTE with LB lift at least `+0.003`.
   - If ON, write optional `prior_updates.diff`; never edit priors directly unless the user explicitly chooses it.
10. Write report output.
    - Directory: `<PROJECT_ROOT>/docs/research/deep_search/<YYYYMMDD-HHMM>_postmortem_<experiment-id>/`.
    - Required file: `report.md` based on `templates/report.md`.
    - Optional files: `prior_updates.diff`, `external_research.md`.
11. Final message is five lines plus paths:
    - Verdict.
    - Best local evidence.
    - Gate A status.
    - Gate C status.
    - Absolute output paths.

## Platform Eval Quota — Verify Before Assuming

Before assuming a failed eval burns daily quota, **check empirically once on your platform**. Most experiment-platforms charge quota on successful run only (FAILED evals do not count). If your platform behaves this way:

- After `status=failed`, scrape event log immediately, diagnose root cause from `logs/<task_id>.txt`, retry **same-day without quota concern**.
- This applies to **infrastructure / packaging failures** (missing module, OOM, upload mismatch). It is NOT permission to brute-force a mechanism that's actually broken — fix the root cause first, then retry.
- A failed eval still occupies its compute slot for the duration of `running` state. Don't queue parallel retries before the failed one releases.

If your platform DOES charge quota on failed evals: be far more conservative; treat the first attempt as the only attempt and do a dry-run / lint of upload contents first.

## Default Infer File Set — Beware Hidden Whitelists

Most platform CLI tools have a hardcoded default whitelist for "what gets uploaded as inference code" (typically: `dataset.py, dense_transform.py, eda.py, infer.py, model.py` or similar). **If your inference path imports anything outside this set** (custom utility modules, feature-artifact loaders, etc.), the eval will fail with `ModuleNotFoundError: No module named '<module>'` on the first inference step.

Mitigation:
- Stage a clean directory containing ALL needed files, then use the CLI's "include all" mode (often `--include-all-files` or `--submit-name <name>` mode resolving a curated package dir).
- Before live `eval create`, scan your `infer.py` and `dataset.py` for `from <local_module> import` lines and ensure each is in the upload set.

## Acceptance Coverage

For `/deep-search postmortem 98238` when terminal, this workflow requires reading `jobs-summary.csv`, invoking `_deep_search_metric_query.py 98238`, producing `report.md`, and triggering Gate C chips if LB exceeds current SOTA by at least `+0.003`.
