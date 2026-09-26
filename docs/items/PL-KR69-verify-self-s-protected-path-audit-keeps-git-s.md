---
id: PL-KR69
title: verify --self's protected-path audit keeps git's rename detection, so git mv of a src/anesthesia_sim/core/ file to a path outside core prints 'PASS no protected path modified - none touched', while arm's --no-renames diff lists the core file
priority: P1
effort: M
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/arming.py, subprojects/docket/src/docket/claims.py, tools/doc_check.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs.py, docs/items/PL-WNQT-bin-docket-stranded-reports-a-one-path-commit.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by its own triage on 2026-09-25, which the Stream A thread working it ran
added: 2026-09-25
closed: 2026-09-25
pr: 1015
payoff: a core or data file moved out of its protected directory fails verify's protected-path audit instead of passing as none touched, and every read of what a change touched agrees about renames
verify: grep -q 'def test_moving_a_protected_file_out_is_rejected' subprojects/docket/tests/test_verify.py && grep -q 'def changed_path_args' subprojects/docket/src/docket/vcs.py
---

**Problem.** verify --self's protected-path audit keeps git's rename detection, so git mv of a src/anesthesia_sim/core/ file to a path outside core prints 'PASS no protected path modified - none touched', while arm's --no-renames diff lists the core file

Reproduced twice, independently (by the audit and again by PL-P0FP's session in a scratch clone): `git mv src/anesthesia_sim/core/alveolar.py tools/moved_core.py`, commit, `bin/docket verify --self PL-YSMV` prints `PASS no protected path modified - none touched`. `verify.changed_paths` (`verify.py:1498`) and `files_in_flight` (`vcs.py:3042`) keep rename detection; `arming.py:199` and `claims.py:867` pass `--no-renames`. PL-J16N is the same mechanism in `_modified_by` only.

**Reproduced again at triage, 2026-09-25**, git 2.43.0, in a scratch worktree off `origin/main` at `055d5f98`: `git mv src/anesthesia_sim/core/alveolar.py tools/moved_core.py`, committed. `git diff --name-only origin/main...HEAD` and `git show --name-only --format= HEAD` each print only `tools/moved_core.py`; with `--no-renames` the diff prints both paths. `bin/docket verify --self --base origin/main PL-YSMV` prints `PASS  no protected path modified - none touched`. Both of `changed_paths`' reads are blind: the branch diff, and the `git show` its commits form uses when the item's id leads a commit.

**Why it matters.** The protected-path audit guards safety-critical simulator code; a rename carries a core file out of it unseen. Recommended P1.

P1 as recommended, classed `defect` rather than `safety`: no clinical value is computed here, but the answer is a false PASS on the one guard over the code that computes them. The earlier `verify` defects ranked P2 were false REJECTs, which cost a session rather than hiding a change.

**Which reads the helper takes, settled at triage.** The rule it states: a read that lists the paths a change touched names both sides of a rename, because the old path was deleted and a guard that sees only the new one misses the deletion. A read asking which file is new (`--diff-filter=A`) or where a file came from (`-M`, `--follow`) keeps git's pairing, because there the pairing is the answer. So besides the four named above it takes:

- in `vcs.py`, `_landing_split`, `_superseded`, `change_landed` and `since_filed`, which already pass the flag, and `_cut_versions`, `filed_with_work`'s `git show`, `_carried_work`, `_changed_items`, `closed_by`, `ref_walk` and `working_paths`, which do not;
- `claims._history`, which already does;
- `tools/doc_check.py`'s `_changed_paths`, where a rename's old name is the one stale prose still cites.

Left as they are: `verify._file_steps` and `vcs._walk_following_renames` pair renames on purpose; `vcs.cut_window`, `filed_with_work`'s `git log`, `tools/generator_check.py` and `tools/doc_check.py`'s notes history ask which file is new; `vcs._commits_by_landing` matches each commit's paths against `_landing_split`'s, which holds only the paths a change puts content at, so a rename's deleted side would match neither set and leave the commit unclassified (found at the build, when the walk was first moved onto the helper); and `vcs._unmerged_commits`' walk is PL-J16N's, whose brief weighs what `--no-renames` there would do to `_superseded`.

**Done when.** Every changed-path read in the apparatus passes `--no-renames` (one helper); a regression test moves a core file out and the audit fails.
The helper is `vcs.changed_path_args`. `test_moving_a_protected_file_out_is_rejected` in `subprojects/docket/tests/test_verify.py` drives both of `changed_paths`' forms against real git, and `test_files_in_flight_lists_both_names_of_a_rename` in `subprojects/docket/tests/test_cli.py` drives the other named read.

**Generator check.** An instance of PL-PVW2's fact - which spelling of a repeated predicate is the answer - for the question "which paths did this change". PL-PVW2 is untriaged and outside this project's list of heads, so this item is that one question's share of it; PL-J16N is the same question at `_unmerged_commits`' walk.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
