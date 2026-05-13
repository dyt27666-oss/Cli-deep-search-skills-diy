# Data Sources

This map defines where `/deep-search` looks for each kind of fact. If a file or directory is absent, report `not present, skipped` and continue.

## Job / Run Metadata

- `<PROJECT_ROOT>/outputs/<platform>/jobs-summary.csv`
  - Job id, `job_id`, name, description, status, update time, sync mode, and instance count.
  - Safe for direct Read/Grep.
- `<PROJECT_ROOT>/outputs/<platform>/all-checkpoints.csv`
  - Checkpoint inventory and lightweight training state.
  - Safe for direct Read/Grep.

## Metrics

- `<PROJECT_ROOT>/outputs/<platform>/all-metrics-long.csv`
  - Heavy file. Never direct Read/Grep.
  - Access only through `python3 <PROJECT_ROOT>/scripts/_deep_search_metric_query.py <job_id>`.

## Evaluation and LB Evidence

- `<PROJECT_ROOT>/outputs/<platform>/evaluation/`
  - Trimmed evaluation records.
  - Match by `mould_id`, job id, job name, or experiment tag substring.
- `<PROJECT_ROOT>/experiment_logs/*.md`
  - Human-readable evaluation notes and local-vs-LB patterns.
  - Use `file:line` citations.

## Experiment Metadata

- `<PROJECT_ROOT>/manifest.json`
  - Experiment names, tags, seeds, ablation fields, and tracked results where present.
- `<PROJECT_ROOT>/experiments/<experiment-id>/meta.md`
  - Per-experiment intent and hypothesis where present.
- `<PROJECT_ROOT>/decision_log.md`
  - Session decisions and prior experiment outcomes.
  - Prefer last 200 lines for postmortems, then targeted grep by experiment tag or axis.

## Priors and Memory

- `<PROJECT_ROOT>/docs/paper_priors.md`
  - Mechanism-level paper priors.
- `<PROJECT_ROOT>/docs/paper_analysis.md`
  - Broader paper analysis and supplemental research.
- `<PROJECT_ROOT>/docs/domain_hints.md`
  - Semantic, Episodic, and Working domain hints.
- `<PROJECT_ROOT>/memory/feedback_*.md` (repo memory if present)
- `<USER_AUTO_MEMORY>/feedback_*.md` (user-global auto-memory; some projects store closed-axis rules here, e.g. `feedback_gating_axis_closed.md`, `feedback_loss_axis_closed.md`)
  - Closed-axis rules and project feedback memories. **Always check both locations.**

## Outputs Produced by This Skill

- `<PROJECT_ROOT>/docs/research/deep_search/<YYYYMMDD-HHMM>_postmortem_<experiment-id>/report.md`
- `<PROJECT_ROOT>/docs/research/deep_search/<YYYYMMDD-HHMM>_inquiry/report.md`
- `<PROJECT_ROOT>/docs/research/deep_search/<YYYYMMDD-HHMM>_precheck/report.md`
- Optional: `prior_updates.diff`, `external_research.md`, `experiment_meta_template.md`.
