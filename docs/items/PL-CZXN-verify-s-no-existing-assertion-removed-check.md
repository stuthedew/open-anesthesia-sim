---
id: PL-CZXN
title: verify's 'no existing assertion removed' check REJECTs intended test rewrites: about 15 of the 17 verify --self REJECTs in main's commit messages since 2026-10-01 were waived, so decide whether diff mutation on the changed lines replaces it
priority: P2
effort: M
status: done
classes: defect
feature: defect-review-2026-10
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/config.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md, tools/diff_mutation.py, tools/fact_home_check.py, tests/unit/test_diff_mutation.py, tests/unit/test_doc_check.py, docket.toml, docs/mutation-testing.md, docs/apparatus.md, .claude/skills/docket/modes/close-out.md, .claude/skills/docket/modes/triage.md, .claude/skills/docket/modes/capture.md, docs/items/PL-29RM-in-a-truncated-clone-vcs-written-since-reads-a.md, docs/items/PL-3GKR-promote-the-stale-slug-filename-advisory-to-an.md, docs/items/PL-4YDJ-git-path-reads-outside-changed-path-args-take.md, docs/items/PL-BGMK-two-open-items-whose-touches-and-verify-command.md, docs/items/PL-G60V-layoutmodel-join-s-availability-depends-on.md, docs/items/PL-JTCQ-three-git-path-readers-take-git-s-c-quoted.md, docs/items/PL-K23D-bin-docket-record-merge-leaves-a-notes-bullet.md, docs/items/PL-P6LL-docket-frontmatter-keys-reads-keys-out-of-23-of.md, docs/items/PL-PLV0-verify-s-falsifies-advisory-says-the-line-had.md, docs/items/PL-XFWG-the-accounting-panel-s-unaccounted-and-absolute.md
added: 2026-10-19
closed: 2026-10-24
pr: 1728
payoff: a REJECT from verify --self means something again, while a branch whose tests no longer catch a change to its own lines still fails
verify: ! grep -qF 'no existing assertion removed' subprojects/docket/src/docket/verify.py
reenters: PL-4W2L
recurrences: 2026-10-24 PL-7FPD
---

**Problem.** verify's 'no existing assertion removed' check REJECTs intended test rewrites: about 15 of the 17 verify --self REJECTs in main's commit messages since 2026-10-01 were waived, so decide whether diff mutation on the changed lines replaces it

**How it was measured.** A defect review on 2026-10-19 read `docs/items` with `docket.store.read_items` and placed each item with `Item.lane(workflow_paths)`. A defect is an item whose `classes` include `defect` or `safety`. An organic defect is one filed before any head's `root-cause-of:` named it and carrying no `reenters:`. The scripts lived in the session's scratchpad and are gone, so this paragraph is the method.

**Evidence.** `git log origin/main --since=2026-10-01` bodies name `verify --self` 228 times. They record about 17 `REJECT`s, and about 15 of those come from the one check "no existing assertion removed", each explained away as an intended rewrite. Examples: #1650, #1606, #1585, #1583, #1572, #1537, #1475, #1453 and #1451. The check's heads, `PL-G21K` and `PL-4W2L` (detecting weakened tests from diff text), recorded 12 members and 3 re-entries. A hard `REJECT` that is routinely waived teaches sessions to read past `REJECT`, which `CLAUDE.md` § "Prefer deterministic tooling over repeated model work" counts as a defect in the check. The protection still matters, because a weakened simulator test is a safety risk.

**Decided** (project owner, 2026-10-19, ratified, over demoting the check to an advisory and over keeping it): replace it with `tools/diff_mutation.py`, added 2026-10-17, run on the branch's changed lines. That measures directly whether the tests still fail when the changed code is altered.

**Done when.** `verify --self` no longer runs the assertion-removed check, and a branch whose tests stop catching a mutation of its changed lines fails instead, with tests for both.

**Why it matters.** A hard `REJECT` that sessions waive about 15 times in 17 teaches them to read past `REJECT`. A session that has learned that will also read past the one that catches a weakened simulator test, which is the case the check exists for.

**Checked 2026-10-20:** `subprojects/docket/src/docket/verify.py` still names the check 4 times, and `main`'s commit bodies since 2026-10-01 mention it 20 times.

**Generator check.** An instance of `PL-4W2L`'s fact, "whether a branch's diff weakens its tests", filed after that head closed on 2026-09-23. Recorded as `reenters: PL-4W2L`.

**Built 2026-10-24.** `docket verify` no longer reads assertions from the diff. The check `no existing assertion removed`, every reader it used, and its waiver `falsifies:` are gone: the field is no longer parsed, `docket set --falsifies` is gone, and the ten item files that carried the line no longer do. In their place, `verify` runs one integrity check per run, beside `make check`, in `--self` and in a delegated review alike: `the unit tests catch a mutation of each changed line`. It runs `docket.toml`'s new `mutation_command`, which here is `tools/diff_mutation.py --verdict --base <base>`. The tool prints a JSON verdict, and `verify` refuses while it names a mutant of a changed line that the simulator's unit tests did not catch, or one it could not decide. Nothing in the check reads the diff's text, so the class `PL-MR8Z`, `PL-W6ZD` and `PL-GXLX` belonged to has no reader left to misread.

- **What counts.** A mutant counts only where a line it changes is one the branch changed. `mutated_rows` places each uncaught mutant on its line by fitting `mutmut show`'s diff to the file, and a mutant no single offset fits is undecided, which refuses. A survivor on a line the branch did not change is named in a note and not counted. A timeout counts as caught, as PIT and Stryker count one. `# pragma: no mutate` on a changed line is how an equivalent mutant is cleared, and the check prints every such line.
- **"Stop catching" read as "do not catch".** A mutant of a changed line exists only on the branch, so there is no base run of it to compare with. The workable reading of the done-when is that the branch's tests must catch a fault in each line the branch wrote.
- **When it cannot answer, it refuses.** A command that exits non-zero, runs past `MUTATION_TIMEOUT_S` (two hours), or prints anything but the verdict gives a `FAIL` that says it has no answer. Where `mutation_command` is unset, the check is a `NOTE` saying nothing measured the tests.

**Measured 2026-10-24, on four cores.** A branch that changes no function mutmut mutates costs a few seconds: 405 of the 445 merges on `main` since 2026-10-01 are that kind. A branch that does pays about five minutes before its first mutant: 300 s for 3 mutants (`#1574`), 324 s for 9 (`#1650`), 471 s for 186 (`#1537`), and 2,190 s for 340 (`#1676`, the largest batch). Another session's test suite shared the cores during the last two runs, so those two are upper bounds. Of the 40 merges that changed a mutated function, 37 changed 200 mutants or fewer, counted from the mutant lists the runs generated. On the four measured merges, the check would have passed `#1574` and refused the other three: `#1537` on one mutant (`>` to `>=` at `FLOW_FRACTION_TOLERANCE` in `_require_fractions_sum_to_one`), `#1650` on seven (four survivors in `saved_time_base` and three in `saved_time_base_value`, which no unit test reaches), and `#1676` on three (the compartment name in `BreathingCircuit.set_agent_amount`'s refusal, which was that batch's own deliverable). Each is a unit-test gap a test can close. The old check refused `#1537` and `#1650` too, but on rewrites the work was meant to make, which no test could clear.

**What it does not cover, said so the trade is visible.** mutmut mutates only `core/` and four `app/` modules, so a test of the apparatus, or of the Qt half of `app/`, is no longer measured by any check: the old check covered both. A branch that changes a simulator test without changing a mutated function is passed with a note naming the test file, because a mutant changes the code and not the test. `PL-7FPD` holds that gap, and `PL-88HC` the run time.

**`PL-4W2L`'s cluster.** Its fact, "whether a branch's diff weakens its tests", has two halves. The assertion half now has no reader of diff text at all, so that half is finished: there is nothing left for a misread to re-enter. The suppression half still reads markers from the diff, as `PL-G21K` resolved, and is not this item's.
