---
id: PL-YYDT
title: The pull-request number in a commit subject is parsed four ways (vcs._SQUASH_NUMBER, doc_check, pr_body_check, vcs.PR_SUBJECT_RE), and the 99 'Merge pull request #N from' subjects on main give None to Landing.pull_request and N to FilingCommit
status: untriaged
feature: one-answer
touches: tools/pr_body_check.py, tools/doc_check.py, subprojects/docket/src/docket/vcs.py, tests/unit/test_pr_body_check.py
added: 2026-09-25
---

**Problem.** The pull-request number in a commit subject is parsed four ways (vcs._SQUASH_NUMBER, doc_check, pr_body_check, vcs.PR_SUBJECT_RE), and the 99 'Merge pull request #N from' subjects on main give None to Landing.pull_request and N to FilingCommit

Reproduced by importing both. doc_check's comment says it reads the number "the same way here rather than spelled a second time"; it is a second spelling. PL-HMZZ family.

**Why it matters.** Low today; the next caller copies whichever spelling it finds.

**Done when.** One parser, imported by all four.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
