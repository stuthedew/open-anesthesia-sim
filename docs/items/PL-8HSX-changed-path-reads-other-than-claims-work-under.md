---
id: PL-8HSX
title: Changed-path reads other than claims.work_under_record leave core.quotePath on, so git prints a non-ASCII path in quoted octal and verify's protected-path audit compares that form: a new src/anesthesia_sim/core/café.py passes as 'none touched'
priority: P1
effort: M
status: ready
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-answer batch
added: 2026-09-25
payoff: a delegated branch that adds or edits a core, data or MODEL.md file under a name git would quote fails the protected-path audit instead of passing as none touched
verify: grep -q 'def test_a_non_ascii_protected_path_is_rejected' subprojects/docket/tests/test_verify.py
---

**Problem.** Changed-path reads other than claims.work_under_record leave core.quotePath on, so git prints a non-ASCII path in quoted octal and verify's protected-path audit compares that form: a new src/anesthesia_sim/core/café.py passes as 'none touched'

Found 2026-09-25 by PL-KR69's triage, git 2.43.0, in a scratch worktree off `origin/main`: a commit adding `src/anesthesia_sim/core/café.py` gives `verify.changed_paths` the one path `"src/anesthesia_sim/core/caf\303\251.py"`, quotes included, and `_within` matches it against no protected path. The working-tree half reads `git status --porcelain`, which quotes the same way. `-c core.quotePath=false` still quotes a path holding a tab, newline, `"` or `\`; only `-z` output is verbatim. PL-KR69's `vcs.changed_path_args` is the one place every changed-path read now builds its argv, so the fix lands there, but moving `-c` ahead of the subcommand changes `args[0]` in every test fake keyed on it.

**Reproduced 2026-09-25 against 46954a81**, after #1015 merged, git 2.43.0: a scratch repository commits `src/anesthesia_sim/core/café.py`, and `verify.changed_paths(root, "HEAD~1")` returns `('"src/anesthesia_sim/core/caf\\303\\251.py"',)`, where `_within(path, ("src/anesthesia_sim/core",))` is `False`. `vcs.changed_path_args` adds `--no-renames` only. So #1015 did not close this; it filed it. No tracked path is non-ASCII today, so the hole is open and not yet walked through.

**Why it matters.** It is PL-KR69's failure through another door: the protected-path audit is the one guard between a delegated worker and `src/anesthesia_sim/core`, `src/anesthesia_sim/data` and `docs/MODEL.md`, and it answers `PASS - none touched` for a change it could not read. A non-ASCII, tab, newline, `"` or `\` in a path is rarer than a rename, which is the only reason this is not worse than PL-KR69. P1 for the reason PL-KR69 was: a false PASS hides a change, where the P2 `verify` defects were false REJECTs that cost a session.

**Done when.** Every changed-path read the protected-path audit relies on (both halves of `verify.changed_paths`, the committed read and `git status`) hands `_within` the path as written. That means `-z` output, or `core.quotePath=false` for the non-ASCII case plus a refusal for the quoted remainder, built once in `vcs.changed_path_args` so `claims.work_under_record` stops spelling its own `-c`. A test commits a non-ASCII file under `src/anesthesia_sim/core/` and sees the audit reject it.

**Generator check.** It is an instance of PL-PVW2's fact, which of several spellings of one predicate is the answer. The predicate is which files a branch changed: `claims.work_under_record` disables quoting and the other readers do not. It is also a re-entry of PL-KR69, closed today, whose single argv builder carried the rename flag and not the quoting one. Now a member of PL-PVW2's `root-cause-of:`.
