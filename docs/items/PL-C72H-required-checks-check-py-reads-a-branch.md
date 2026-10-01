---
id: PL-C72H
title: required_checks_check.py reads a branch-filtered pull_request trigger as reporting, but GitHub's workflow-syntax page says a run skipped by a branch filter leaves its checks Pending too, so a branches-ignore naming the protected branch, or a branches list leaving it out, would read as agreement while merges hang
priority: P3
effort: S
status: ready
classes: defect
feature: required-check-trigger-reading
touches: tools/required_checks_check.py, tests/unit/test_required_checks_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: a workflow its own branch filter skips on main's pull requests reads as missing, so a merge-blocking Pending check is caught before the merge
verify: grep -q 'def test_a_branch_filter_excluding_the_protected_branch_does_not_report' tests/unit/test_required_checks_check.py
---

**Problem.** required_checks_check.py reads a branch-filtered pull_request trigger as reporting, but GitHub's workflow-syntax page says a run skipped by a branch filter leaves its checks Pending too, so a branches-ignore naming the protected branch, or a branches list leaving it out, would read as agreement while merges hang

**Why it matters.** A required check whose workflow a branch filter skips stays Pending and blocks the merge, per the GitHub page the title cites, while the tool reads that workflow as reporting and passes, so the hang is found at merge time with the check green. Latent: only `quality.yml`'s `push` trigger carries a `branches` filter, and no `pull_request` trigger does (read 2026-10-01).

**Done when.** A `pull_request` trigger whose `branches` or `branches-ignore` excludes the protected branch reads as not reporting, a test pins each filter, and the GitHub sentence the title rests on is checked against the page and cited in the docstring.

**Reproduced 2026-10-01.** `_triggers` returns `{'pull_request'}` for a `pull_request` trigger carrying `branches-ignore: [main]`: the filter is not read. The GitHub page itself was not re-read in this pass.

**Generator check.** The same fact as `PL-848V`, in the same function; see that item.
