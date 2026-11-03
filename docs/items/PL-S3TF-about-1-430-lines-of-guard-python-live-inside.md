---
id: PL-S3TF
title: About 1,430 lines of guard Python live inside python3 -c strings in .claude/hooks/*.sh, where ruff, mypy and tools/fact_home_check.py never read them; direct-merge-guard.sh builds a second GitHub API client there, and three guards import json unused
status: untriaged
feature: guard-review-2026-11
added: 2026-11-03
---

**Problem.** About 1,430 lines of guard Python live inside python3 -c strings in .claude/hooks/*.sh, where ruff, mypy and tools/fact_home_check.py never read them; direct-merge-guard.sh builds a second GitHub API client there, and three guards import json unused
