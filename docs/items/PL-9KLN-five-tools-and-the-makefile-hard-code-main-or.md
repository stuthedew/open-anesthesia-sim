---
id: PL-9KLN
title: Five tools and the Makefile hard-code main or origin/main as the default branch beside vcs.default_base (main_ci_status, tag_release, update_armed, pr_record_check, required_checks_check): read it against PL-PVW2's misread as a post-close instance
priority: P3
effort: M
status: done
classes: defect
feature: recorded-not-inferred
milestone: v0.5.21
touches: tools/main_ci_status.py, tools/tag_release.py, tools/update_armed.py, tools/pr_record_check.py, tools/required_checks_check.py, Makefile, tests/unit/test_main_ci_status.py, tests/unit/test_tag_release.py, tests/unit/test_update_armed.py, tests/unit/test_pr_record_check.py, tests/unit/test_required_checks_check.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_vcs_silence.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
closed: 2026-10-01
pr: 1271
payoff: which branch is the base is one answer in docket and in every CI tool, so a clone where main is only local, or a renamed default, cannot split them
verify: ! grep -qF 'BRANCH = "main"' tools/main_ci_status.py && ! grep -qF 'BRANCH = "main"' tools/tag_release.py && ! grep -qF 'default="main"' tools/update_armed.py
---

**Problem.** Five tools and the Makefile hard-code main or origin/main as the default branch beside vcs.default_base (main_ci_status, tag_release, update_armed, pr_record_check, required_checks_check): read it against PL-PVW2's misread as a post-close instance

**Recorded alternative, from the 2026-10-01 survey.** Read `vcs.default_base` or the one setting it reads. Shape B. Low confidence on the Makefile lines 216 and 361, which may need a literal for `make` itself.

**Why it matters.** `vcs.default_base` is the one answer to which ref a branch is compared against, preferring the remote's, and `PL-PVW2`'s step 1 moved the tools' own spellings of the default branch onto it. Five tools and two Makefile lines still carry a literal, so a default-branch change, or a clone where `main` is only the local branch, answers one way in docket and another in CI's tools.

**Reproduced 2026-10-01.** `tools/main_ci_status.py:131` and `tools/tag_release.py:52` hold `BRANCH = "main"`; `tools/update_armed.py:330` defaults `--base` to `main`, `tools/pr_record_check.py:89` to `origin/main`, `tools/required_checks_check.py:457` to `GITHUB_BASE_REF or "main"`; `Makefile:216` and `:361` pass `origin/main` to `bin/docket check --verify` and to `contrast_check.py`. Low confidence on the two Makefile lines, which may need a literal `make` can read: say which way they went.

**Done when.** Each tool reads `vcs.default_base` or the one setting it reads (`update_armed` and `pr_record_check` take the docket import shim the other tools already use), the `BRANCH = "main"` literals are gone, and the two Makefile lines are read against `vcs.default_base` and either dropped or kept with the reason beside them.

**Generator check.** An instance of `PL-PVW2`'s fact - which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it - filed after that head drained on 2026-09-26. Six such instances filed 2026-10-01 make `PL-KGYT`, this item's head.
