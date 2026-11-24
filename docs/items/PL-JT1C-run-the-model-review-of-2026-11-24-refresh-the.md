---
id: PL-JT1C
title: Run the model review of 2026-11-24: refresh the session ledger and CI history, read each trial session's arm, compute each arm's required sample size from the first closed outcome windows, and run the blind-review pass check
status: untriaged
feature: model-review
touches: docs/model-review.md, docs/session-ledger.tsv, docs/ci-runs.tsv, tools/ci_runs.py, tests/unit/test_ci_runs.py
added: 2026-11-24
---

**Problem.** Run the model review of 2026-11-24: refresh the session ledger and CI history, read each trial session's arm, compute each arm's required sample size from the first closed outcome windows, and run the blind-review pass check

**Why it matters.** The project owner asked for this month's run on
2026-11-24 (project owner, 2026-11-24): the main question is the effort trial,
`high` against `xhigh`, assigned by `PL-HYRM` and analysed under `PL-63CB`
§ "Effort monitoring". It is the first run at which trial items have closed
30-day windows. A scheduled run earlier that day could not finish because it
had no `claude-code-remote` tools, and committed nothing.

**What the run does.** It follows `.claude/skills/model-review/SKILL.md` in
full: it refreshes `docs/ci-runs.tsv` and `docs/session-ledger.tsv`, reads each
cloud session's arm from the first "Effort trial:" line of its session-start
digest, leaves out threads, sessions with no arm and moved sessions and counts
each group, computes each arm's required sample size from the observed rates,
reports by model and by split period, runs the blind-review pass check, and
writes the run's entry into `docs/model-review.md`.
