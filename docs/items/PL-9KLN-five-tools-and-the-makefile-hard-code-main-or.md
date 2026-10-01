---
id: PL-9KLN
title: Five tools and the Makefile hard-code main or origin/main as the default branch beside vcs.default_base (main_ci_status, tag_release, update_armed, pr_record_check, required_checks_check): read it against PL-PVW2's misread as a post-close instance
status: untriaged
feature: recorded-not-inferred
added: 2026-10-01
---

**Problem.** Five tools and the Makefile hard-code main or origin/main as the default branch beside vcs.default_base (main_ci_status, tag_release, update_armed, pr_record_check, required_checks_check): read it against PL-PVW2's misread as a post-close instance

**Recorded alternative, from the 2026-10-01 survey.** Read `vcs.default_base` or the one setting it reads. Shape B. Low confidence on the Makefile lines 216 and 361, which may need a literal for `make` itself.
