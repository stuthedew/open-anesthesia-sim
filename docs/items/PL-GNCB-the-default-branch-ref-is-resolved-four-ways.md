---
id: PL-GNCB
title: The default-branch ref is resolved four ways (vcs.default_base, pr_body_check.default_branch_ref, pr_title_check --base, left_behind_check's symref), so a clone whose default is master gets origin/master from one and None from another
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, tools/pr_body_check.py, tools/pr_title_check.py, tools/left_behind_check.py, tests/unit/test_pr_body_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-answer batch
added: 2026-09-25
closed: 2026-09-26
payoff: a clone whose default branch is not main gets the same base from every tool as from docket, instead of a silent skip from some and a wrong comparison from others
verify: grep -q 'def test_default_branch_ref_follows_docket_on_a_master_only_clone' tests/unit/test_pr_body_check.py
---

**Problem.** The default-branch ref is resolved four ways (vcs.default_base, pr_body_check.default_branch_ref, pr_title_check --base, left_behind_check's symref), so a clone whose default is master gets origin/master from one and None from another

Reproduced with a master-only clone. PL-GVC0 covers the prefix only.

**Re-confirmed 2026-09-25 against 46954a81** in a scratch clone of a master-only origin. `vcs.default_base` gives `origin/master` (its `DEFAULT_BRANCHES` tries four names). `pr_body_check.default_branch_ref` gives `None` (it tries `origin/main` and `main`). `pr_title_check`'s `--base` defaults to `origin/main`, which does not resolve there. `ls-remote --symref origin HEAD`, which `left_behind_check` reads, names `refs/heads/master`.

**Why it matters.** Low today: this repository's default is `main`, and CI passes `PR_BASE`. A clone that differs gets a confident wrong base from one tool, or a silent skip, while `docket` answers correctly.

**Generator check.** It is an instance of PL-PVW2's fact, which spelling of a repeated predicate is the answer. The predicate is the default branch's ref, and `vcs.default_base` already holds the most complete spelling for the tools to import.

**Done when.** One resolver, imported by all four.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

**Fixed 2026-09-26.** `pr_body_check.default_branch_ref` and `pr_title_check`'s `--base` default now ask `vcs.default_base`, so a `master`-only clone gets `origin/master` from all three. `left_behind_check` keeps its `ls-remote --symref origin HEAD` read, and its docstring now says why: it is the one reader comparing the remote's tips, and it takes the default branch from the same answer as those tips, so the two cannot come from different moments. That read already named `master` on the master-only clone this item was reproduced on, so it was never one of the disagreeing answers.
