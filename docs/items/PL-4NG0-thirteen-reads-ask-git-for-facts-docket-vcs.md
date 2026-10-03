---
id: PL-4NG0
title: Thirteen reads ask git for facts docket.vcs exports in their own spelling: the remote name origin in tag_release, branch_sweep, claiming, required_checks_check, main_ci_status, open_pull_requests, pr_body_check, left_behind_check and vcs's own behind-count; the shallow-clone test in left_behind_check and twice in pr_body_check; and GITHUB_TOKEN alone in update_armed, which reads no token where only GH_TOKEN is set
priority: P3
effort: M
status: ready
classes: defect
feature: read-facts-through-docket
touches: tools/tag_release.py, tools/branch_sweep.py, subprojects/docket/src/docket/claiming.py, tools/required_checks_check.py, tools/main_ci_status.py, tools/open_pull_requests.py, tools/pr_body_check.py, tools/left_behind_check.py, subprojects/docket/src/docket/vcs.py, tools/update_armed.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/release.py, tests/unit/test_update_armed.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: the remote name, the shallow-clone test and the token are each read in one place, so another remote name or a GH_TOKEN-only shell gets one answer from every tool
verify: ! grep -qF 'REMOTE = "origin"' tools/tag_release.py && ! grep -qF 'REMOTE = "origin"' tools/branch_sweep.py && ! grep -qF 'os.environ.get("GITHUB_TOKEN") or None' tools/update_armed.py
---

**Problem.** Thirteen reads ask git for facts docket.vcs exports in their own spelling: the remote name origin in tag_release, branch_sweep, claiming, required_checks_check, main_ci_status, open_pull_requests, pr_body_check, left_behind_check and vcs's own behind-count; the shallow-clone test in left_behind_check and twice in pr_body_check; and GITHUB_TOKEN alone in update_armed, which reads no token where only GH_TOKEN is set

**Sites**, from `PL-KGYT`'s sweep (its `**Swept 2026-10-01.**` line), each read against the source that day. Where a line says *agree*, the two spellings answer alike on every input today, and the risk is the next change to the fact reaching one of them only. The remote name, `vcs.REMOTE`: `tools/tag_release.py:51`, `tools/branch_sweep.py:79`, `subprojects/docket/src/docket/claiming.py:126` (`arming.py` reads this copy), `tools/required_checks_check.py:430`, `tools/main_ci_status.py:451`, `tools/open_pull_requests.py:130`, `tools/pr_body_check.py:330`, `tools/left_behind_check.py:169` and `subprojects/docket/src/docket/vcs.py:2153`; all agree. The shallow-clone test, `vcs.is_shallow`: `tools/left_behind_check.py:418`, `tools/pr_body_check.py:632` and `:687`; all agree. The token, `vcs.github_token`: `tools/update_armed.py:356` reads `GITHUB_TOKEN` alone, so where only `GH_TOKEN` is set it reads none.

**Re-confirmed at start, 2026-10-03, and three more found.** All thirteen still read as the sweep found them; `vcs.py`'s behind-count is `behind_remote`. A search of every string literal under `tools/`, `subprojects/docket/src/` and `.claude/hooks/` that is not a docstring found three more reads of the remote name the sweep did not list, and this item takes them, since its payoff needs them: `vcs.DEFAULT_BRANCHES` spells `origin/main` and `origin/master` while `vcs.default_branch` strips the prefix by `REMOTE`, so the two must agree for the default branch's bare name to come out; `left_behind_check.orphaned_branches` strips `origin/` from each branch `vcs.orphaned` reports; and `release.tag_confirmation` defaults its `remote` to `"origin"`, which `docket release` prints as the line that shows whether the remote holds a tag. All three agree today. `arming.py` reads `REMOTE` from `docket.vcs` once `claiming.py` does, because mypy's strict mode refuses a name read through a module that only imported it. A message reporting one of these reads failing names the remote through `REMOTE`, as `claiming.py`'s and `vcs.py`'s already did. Left as they are: `.claude/hooks/stop_hook_patch.py`'s `remote.origin.fetch`, which names the remote the harness cloned, a fact of the harness rather than of docket, in a hook that imports no docket; and advice elsewhere to run `git fetch origin`, which is prose rather than a read. The shallow-clone test and the token have no other readers.

**Why it matters.** Each site answers from its own spelling of a fact docket exports, so the next change to that fact reaches the export and not the copy, and the two then answer differently with nothing to say so - the mechanism `PL-KGYT` closed as spent.

**Done when.** Each site under **Sites**, and each of the three found at start, reads the export instead of its own spelling, and where a site answered differently from the export, a test pins that input.

**Generator check.** A member of `PL-KGYT` (done 2026-10-01), filed by that head's closing sweep and named in its `root-cause-of:`; its fix, the write-time rule in `.claude/rules/apparatus-standard.md` (`PL-HC8P`), covers new readers and these predate it, so this is neither a post-close instance nor a new generator.
