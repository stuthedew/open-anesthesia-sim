---
id: PL-S3TF
title: About 1,430 lines of guard Python live inside python3 -c strings in .claude/hooks/*.sh, where ruff, mypy and tools/fact_home_check.py never read them; direct-merge-guard.sh builds a second GitHub API client there, and three guards import json unused
priority: P2
effort: L
status: ready
classes: refactor
feature: guard-review-2026-11
touches: .claude/hooks/floor-interpreter-guard.sh, .claude/hooks/gate-status-guard.sh, .claude/hooks/push-check-guard.sh, .claude/hooks/docket-branch-guard.sh, .claude/hooks/direct-merge-guard.sh, .claude/hooks/pr-body-email-guard.sh
deferred-from: v0.7.0 - captured after the freeze; a guard-hook defect in the workflow lane, not safety or science, and no learner sees it
added: 2026-11-03
payoff: guard code is linted, type-checked and held to one source of truth like every other Python file, so defects like a second GitHub client stop accumulating unseen
verify: ! grep -qF "python3 -c '" .claude/hooks/floor-interpreter-guard.sh .claude/hooks/gate-status-guard.sh .claude/hooks/push-check-guard.sh .claude/hooks/docket-branch-guard.sh .claude/hooks/direct-merge-guard.sh .claude/hooks/pr-body-email-guard.sh
---

**Problem.** About 1,430 lines of guard Python live inside python3 -c strings in .claude/hooks/*.sh, where ruff, mypy and tools/fact_home_check.py never read them; direct-merge-guard.sh builds a second GitHub API client there, and three guards import json unused

**Why it matters.** Guard code inside a shell string is outside every check
the repository runs on Python: no lint, no type check, no one-source-of-truth
check. That is how `direct-merge-guard.sh` came to build a second GitHub API
client, and how three guards import `json` unused. It also forces the payload
through an environment variable, which `PL-B5K1` shows fails past 128 KiB.

**Done when.** Each guard's Python lives in a module under `.claude/hooks/`
that ruff, mypy and `tools/fact_home_check.py` read, each `.sh` only starts
it, and `direct-merge-guard` uses the repository's one GitHub client.

**Generator check.** The shape behind `PL-B5K1` and part of `PL-9KSJ`, but not
itself a misread fact. It shares every guard file with the `PL-9KSJ` cluster,
so it is sequenced with that work.
