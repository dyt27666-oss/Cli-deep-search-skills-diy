# Token Safety

These rules are hard constraints for `/deep-search`.

## Never Directly Read or Grep

- `<PROJECT_ROOT>/outputs/<platform>/all-metrics-long.csv`
- `<PROJECT_ROOT>/outputs/<platform>/logs/<job-id>/*.txt`
- `<PROJECT_ROOT>/outputs/<platform>/code/<job-id>/files/*` unless the user explicitly asks for a specific file.

## Always Use Safe Sources

- Job summary: `<PROJECT_ROOT>/outputs/<platform>/jobs-summary.csv`.
- Checkpoints: `<PROJECT_ROOT>/outputs/<platform>/all-checkpoints.csv`.
- Evaluations: `<PROJECT_ROOT>/outputs/<platform>/evaluation/`.
- Per-job metrics: `python3 <PROJECT_ROOT>/scripts/_deep_search_metric_query.py <job_id>`.
- Per-job log errors: your platform CLI or log-export tool only if error snippets are needed; extract Errors/Tracebacks rather than dumping full logs.

## Retrieval Discipline

- Stop local inquiry retrieval once at least five strong hits are collected.
- Prefer `rg -n` for targeted text search in small docs.
- Cite local evidence using `file:line` notation.
- Distinguish observed evidence from inferred mechanism in reports.
