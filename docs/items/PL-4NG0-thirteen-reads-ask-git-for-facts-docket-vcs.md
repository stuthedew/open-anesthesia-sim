---
id: PL-4NG0
title: Thirteen reads ask git for facts docket.vcs exports in their own spelling: the remote name origin in tag_release, branch_sweep, claiming, required_checks_check, main_ci_status, open_pull_requests, pr_body_check, left_behind_check and vcs's own behind-count; the shallow-clone test in left_behind_check and twice in pr_body_check; and GITHUB_TOKEN alone in update_armed, which reads no token where only GH_TOKEN is set
status: untriaged
feature: read-facts-through-docket
touches: tools/tag_release.py, tools/branch_sweep.py, subprojects/docket/src/docket/claiming.py, tools/required_checks_check.py, tools/main_ci_status.py, tools/open_pull_requests.py, tools/pr_body_check.py, tools/left_behind_check.py, subprojects/docket/src/docket/vcs.py, tools/update_armed.py
added: 2026-10-01
---

**Problem.** Thirteen reads ask git for facts docket.vcs exports in their own spelling: the remote name origin in tag_release, branch_sweep, claiming, required_checks_check, main_ci_status, open_pull_requests, pr_body_check, left_behind_check and vcs's own behind-count; the shallow-clone test in left_behind_check and twice in pr_body_check; and GITHUB_TOKEN alone in update_armed, which reads no token where only GH_TOKEN is set

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. The remote name, `vcs.REMOTE`: `tools/tag_release.py:51`, `tools/branch_sweep.py:79`, `subprojects/docket/src/docket/claiming.py:126` (`arming.py` reads this copy), `tools/required_checks_check.py:430`, `tools/main_ci_status.py:451`, `tools/open_pull_requests.py:130`, `tools/pr_body_check.py:330`, `tools/left_behind_check.py:169` and `subprojects/docket/src/docket/vcs.py:2153`; all agree. The shallow-clone test, `vcs.is_shallow`: `tools/left_behind_check.py:418`, `tools/pr_body_check.py:632` and `:687`; all agree. The token, `vcs.github_token`: `tools/update_armed.py:356` reads `GITHUB_TOKEN` alone, so where only `GH_TOKEN` is set it reads none.
