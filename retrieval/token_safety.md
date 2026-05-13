# Token Safety

These rules are hard constraints for `/deep-search`.

## Never Directly Read or Grep

- `<PROJECT_ROOT>/outputs/taiji-output/training/all-metrics-long.csv`
- `<PROJECT_ROOT>/outputs/taiji-output/training/logs/<jobId>/*.txt`
- `<PROJECT_ROOT>/outputs/taiji-output/training/code/<jobId>/files/*` unless the user explicitly asks for a specific file.

## Always Use Safe Sources

- Job summary: `<PROJECT_ROOT>/outputs/taiji-output/training/jobs-summary.csv`.
- Checkpoints: `<PROJECT_ROOT>/outputs/taiji-output/training/all-checkpoints.csv`.
- Evaluations: `<PROJECT_ROOT>/outputs/taiji-output/evaluation/evaluations/`.
- Per-job metrics: `python3 <PROJECT_ROOT>/scripts/_deep_search_metric_query.py <jobInternalId>`.
- Per-job log errors: `taac2026 logs <jobId>` only if error snippets are needed; this extracts Errors/Tracebacks rather than dumping full logs.

## Retrieval Discipline

- Stop local inquiry retrieval once at least five strong hits are collected.
- Prefer `rg -n` for targeted text search in small docs.
- Cite local evidence using `file:line` notation.
- Distinguish observed evidence from inferred mechanism in reports.
