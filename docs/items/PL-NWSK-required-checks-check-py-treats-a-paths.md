---
id: PL-NWSK
title: required_checks_check.py treats a paths-filtered pull_request job as reporting, but GitHub leaves such a check pending forever on a pull request the filter excludes, so the reconciliation would read agreement while merges hang
priority: P2
effort: S
status: ready
classes: defect
touches: tools/required_checks_check.py, tests/unit/test_required_checks_check.py
added: 2026-09-19
payoff: stops a path-filtered CI job reading as agreement while pull requests wait forever on a required check that can never arrive
verify: grep -q 'def test_a_paths_filtered_pull_request_job_is_undecidable' tests/unit/test_required_checks_check.py
---

**Problem.** required_checks_check.py treats a paths-filtered pull_request job as reporting, but GitHub leaves such a check pending forever on a pull request the filter excludes, so the reconciliation would read agreement while merges hang

**Why it matters.** `tools/required_checks_check.py` (`PL-XZD0`) reconciles the
jobs that report a status check on `pull_request` against the required list, in
both directions, and it is written to refuse rather than guess wherever it
cannot name a check - a matrix job, a reusable workflow call, an unreadable
`on:` block, an unreachable API. A workflow-level `paths:` or `paths-ignore:`
filter is a fifth case it does not know about, and it is the one that fails
*silently in the direction the check exists to prevent*.

GitHub does not report a skipped-by-path workflow's checks at all. A required
status check naming such a job therefore stays **pending forever** on any pull
request the filter excludes - the identical symptom `PL-KPP1` (`#377`) cost a
manual merge and a wrong diagnosis for. The documented workaround is a second
workflow declaring a job of the same name under the inverse filter, which
exists precisely because the check never arrives on its own.

The reconciliation would read this as agreement: the job is in the tree, its
name is in the required list, both sets match. So the check would be green
while merges hang, which is `CLAUDE.md`'s first compounding-friction test - a
check passing while the guarantee it stands for is void. That it is a *known*
boundary of a guard rather than an unknown one is what makes it worth an item:
the next session reading `required_checks_check.py`'s docstring will find four
refusals listed and reasonably conclude the fifth was considered.

**No workflow here carries such a filter today**, which is why it is captured
rather than fixed: there is nothing to reproduce against, and the fix owes a
regression test, so `CLAUDE.md`'s fix-now door is shut on it (test 1).

**Where.** `tools/required_checks_check.py`, in `_triggers` - which currently
reads only the event names under `on:` and discards everything nested beneath
them.

**Done when.** A `pull_request` or `pull_request_target` trigger carrying
`paths:` or `paths-ignore:` raises `Undecidable` with the other four refusals,
naming the filter and why a required check on a path-filtered job hangs; a test
asserts it; and the docstring's refusal list carries it.
