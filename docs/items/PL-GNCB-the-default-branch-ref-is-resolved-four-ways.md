---
id: PL-GNCB
title: The default-branch ref is resolved four ways (vcs.default_base, pr_body_check.default_branch_ref, pr_title_check --base, left_behind_check's symref), so a clone whose default is master gets origin/master from one and None from another
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, tools/pr_body_check.py, tools/pr_title_check.py, tools/left_behind_check.py
added: 2026-09-25
---

**Problem.** The default-branch ref is resolved four ways (vcs.default_base, pr_body_check.default_branch_ref, pr_title_check --base, left_behind_check's symref), so a clone whose default is master gets origin/master from one and None from another

Reproduced with a master-only clone. PL-GVC0 covers the prefix only.

**Why it matters.** Low today.

**Done when.** One resolver, imported by all four.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
