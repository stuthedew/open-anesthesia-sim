---
id: PL-YYDT
title: The pull-request number in a commit subject is parsed four ways (vcs._SQUASH_NUMBER, doc_check, pr_body_check, vcs.PR_SUBJECT_RE), and the 99 'Merge pull request #N from' subjects on main give None to Landing.pull_request and N to FilingCommit
priority: P3
effort: S
status: done
classes: refactor
feature: one-answer
milestone: v0.5.12
touches: tools/pr_body_check.py, tools/doc_check.py, subprojects/docket/src/docket/vcs.py, tests/unit/test_pr_body_check.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-answer batch
added: 2026-09-25
closed: 2026-09-26
pr: 1074
payoff: the next tool that needs a commit's pull-request number imports one parser that names the subject shape, instead of copying a squash-only spelling that cannot see the 99 merge-commit pull requests on main
verify: grep -q 'def test_pull_request_number_reads_both_subject_shapes' subprojects/docket/tests/test_vcs.py
---

**Problem.** The pull-request number in a commit subject is parsed four ways (vcs._SQUASH_NUMBER, doc_check, pr_body_check, vcs.PR_SUBJECT_RE), and the 99 'Merge pull request #N from' subjects on main give None to Landing.pull_request and N to FilingCommit

Reproduced by importing both. doc_check's comment says it reads the number "the same way here rather than spelled a second time"; it is a second spelling. PL-HMZZ family.

**Re-confirmed 2026-09-25 against 46954a81**, importing all four on `Merge pull request #71 from owner/branch`. `vcs.Landing(...).pull_request`, `doc_check.SQUASH_PR_RE` and `pr_body_check.SQUASH_SUBJECT_RE` give nothing, and `vcs.FilingCommit(...).pull_request` (through `PR_SUBJECT_RE`) gives `71`. `origin/main` holds 99 such subjects. No caller gives a false answer from it today. `pr_body_check`'s squash-only anchor is deliberate, since a merge commit has no body to recover. `Landing` falls back to the commit hash in `left_behind_check`, and `doc_check`'s tag-span read says in its docstring that the early pull requests are invisible to it. So this is a consolidation rather than a repair, and the one parser has to carry which subject shape it matched.

**Why it matters.** Low today; the next caller copies whichever spelling it finds.

**Generator check.** It is an instance of PL-PVW2's fact, which spelling of a repeated predicate is the answer. The predicate is the pull-request number a subject names. It is **not** PL-HMZZ's, despite "PL-HMZZ family" above. PL-HMZZ's fact is which pull request carried an item's work, and its inference (`_merges_naming`, `_number_closing`) already reads both shapes through `PR_SUBJECT_RE`. The squash-only parsers that disagree here are callers PL-HMZZ's recorded `pr:` would not retire.

**Done when.** One parser, imported by all four.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Fixed 2026-09-26.** `vcs.subject_pull_request` is the one parser. It returns the number with the shape that named it (`SubjectPullRequest.squash`), so `Landing`, `FilingCommit` and `merged_pull_requests` read both shapes, and `tools/doc_check.py`'s tag span and `tools/pr_body_check.py`'s squash walk keep the squash shape alone by filtering on the flag rather than by a pattern of their own. `vcs._SQUASH_NUMBER`, `doc_check.SQUASH_PR_RE` and `pr_body_check.SQUASH_SUBJECT_RE` are gone. One behaviour moved: `Landing.pull_request` now names the pull request for a `Merge pull request #N from` landing, where it gave None and `left_behind_check` fell back to the commit hash.
