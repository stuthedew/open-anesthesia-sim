---
id: PL-WW0Q
title: bin/docket arm holds a change to arming.py for a read but arms one to what its answer is read through - vcs.changed_path_args and default_base, claims.holdings, cli.cmd_arm and the test_arm_ tests - so the gate can still be loosened unread from beside it
priority: P2
effort: M
status: done
classes: defect
feature: review-hold
milestone: v0.5.29
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, docs/maintainer.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-25
closed: 2026-10-18
pr: 1587
payoff: a pull request that could loosen arm's answer through a pinned test waits on the owner's read, at about one read in ninety docket commits
verify: grep -q 'def test_arm_holds_a_change_to_an_existing_test_arm_test' subprojects/docket/tests/test_cli.py
reenters: PL-K6B2
recurrences: 2026-10-05 PL-552M withdrawn 2026-10-05 PL-552M
---

**Problem.** bin/docket arm holds a change to arming.py for a read but arms one to what its answer is read through - vcs.changed_path_args and default_base, claims.holdings, cli.cmd_arm and the test_arm_ tests - so the gate can still be loosened unread from beside it

**Found** building `PL-K6B2`, whose brief excepts `arming.py` alone, as `PL-SQTR`'s recommendation 2 worded it. Everything else under `subprojects/docket/` arms on green, the tests that pin `arm`'s answers included, so a change to `vcs.changed_path_args` that reads fewer paths, with its test edited to match, would merge unread and make every later answer `arm`. The existing guards are `verify --self`'s "no existing assertion removed" and a session's reluctance to weaken a test, neither of which a hold is.

**Reproduced 2026-09-26 against 78b1a02b.** `arming.arm` reads the changed paths through `vcs.changed_path_args` and the holds through `claims.holdings`, and holds a tooling path only where `GATE in paths` (`arming.py`'s hold rule, today `path == GATE`). A pull request changing `vcs.py`, `claims.py`, `cli.py` or a `test_arm_` test arms on green like any other docket change.

**Why it matters.** The hold exists so the gate cannot loosen itself, and `PL-SQTR`'s recommendation 2 drew that line at `arming.py` alone. A regression in the path read that passes its own edited test merges unread, and every later `arm` answer reads through it, simulator pull requests included. That read broke twice this week (`PL-KR69`, `PL-8HSX`), and `PL-PVW2` is moving "which files a branch changed" into `vcs.changed_path_args`, so change there is rising.

**Decision needed.** Whether the hold reaches past `arming.py` to what its answer is read through, and how. This reopens `PL-SQTR`'s recommendation 2 (project owner, 2026-09-25, ratified) on a cost its case did not carry. Counted 2026-09-26 over the 55 commits on `main` since 2026-09-19 that today's rule would arm:

- (a) Hold `vcs.py`, `claims.py`, `cli.py` and `test_cli.py` as the gate. It closes the hole at file level and would have held 40 of the 55 (73%), which gives back most of `PL-K6B2`'s payoff.
- (b) Hold `vcs.py` and `claims.py` only: 13 of the 55 (24%). It leaves `cli.cmd_arm` open, and holds every step of `PL-PVW2`'s consolidation for a read.
- (c) Pin each path class the read has broken on (a rename across the boundary, a non-ASCII path, a deletion) in `test_arm_` tests through real git, and hold a diff that changes or deletes an existing `test_arm_` test. None of the 55 did. A loosening then has to edit a pinned answer, and that edit waits on a read; a class no test pins still arms.
- (d) Leave it, and say in `docs/maintainer.md` that the hold covers the classifier, not its inputs.

**Recommendation: (c).** It holds at the one place every loosening of a pinned answer has to pass, and costs almost no reads, which are what the owner's review is spent on. Every option but (d) is a new rule in an existing check, so the owner's yes lifts the generator pause for it, as their yes to `PL-SQTR` did for `PL-K6B2` (`PL-6Q9L`).

**Refreshed 2026-10-12, in the first batched design round, against
`origin/main` at 919ad967.** `PL-PVW2` drained on 2026-09-26 and `PL-KR69` and
`PL-8HSX` are closed, so the rising change the paragraph above expected has
landed; the hole is unchanged - `arming.py`'s hold rule still tests
`path == GATE`, and everything it reads through arms on green. Over the 90
commits on `origin/main` since 2026-09-26 that touch `subprojects/docket/`:
(a) would have held 65 (72%); (b) 24 (27%); (c) at most the 4 that added or
changed a `def test_arm_` line, of which 3 also changed `arming.py` and were
held anyway, so about 1 in 90; `arming.py` itself held 11. Two answers the
owner gave since bear on the choice: on 2026-10-12 workflow pull requests
merge on green without his word (`PL-KPM2`), which (a) and (b) would partly
undo, and the same day he kept `arming.py` on the read list ("Agree", 11:09Z,
recorded by `PL-VKHD` in `#1438`), which is the gate itself. **The
recommendation stands: (c)**, the one option that closes the loosening route
at a cost his 2026-10-12 rule can bear. It goes to him rather than being
decided here because it reopens `PL-SQTR`'s recommendation 2, a ratified
decision, which `CLAUDE.md` § "Working with the project owner" says to put
back to him on ordinary evidence. [superseded 2026-10-12: `#1439` merged before the answer came, so no open
item carries `generator: live` and the build needs no lift] His yes lifts the
pause on new workflow mechanisms for it (`PL-6Q9L`); on 2026-10-12 `PL-8QMD`
is the one open item carrying `generator: live`, and its pull request `#1439`
is open.

**Done when.** `arm` holds for a read a pull request that changes or deletes
an existing `test_arm_` test in `subprojects/docket/tests/test_cli.py`; each
path class the read has broken on - a rename across the boundary, a non-ASCII
path, a deletion - is pinned there in a `test_arm_` test through real git; a
test holds the hold itself; and `docs/maintainer.md` says what the hold
covers: `arming.py` and the tests that pin its answers, not its inputs.

**Generator check.** Re-entry of `PL-K6B2` (closed 2026-09-25), whose Worked paragraph names this gap and whose `recurrences:` already records this capture. The fact misread is which code decides `arm`'s answer: `arming.py` alone, or everything it reads through. That is `PL-SQTR` recommendation 2's wording, and no head's `misread:` states it.

**Answered** (project owner, 2026-10-12, ratified, over (a) holding `vcs.py`,
`claims.py`, `cli.py` and `test_cli.py` as the gate, (b) holding `vcs.py` and
`claims.py` alone, and (d) leaving it): (c). "Agree with recs", in this
thread at 12:51Z. It reopens and replaces `PL-SQTR`'s recommendation 2 for
this one route: the gate's read now reaches the pinned answers in `test_arm_`
tests as well as `arming.py`. His yes was to lift the pause on new workflow
mechanisms for it (`PL-6Q9L`); by the time it came `#1439` had merged and no
open item carries `generator: live`, so the build needs no lift.

**Worked, 2026-10-18, re-confirmed against `3d3515a5`.** The hole still held:
`arming.py`'s hold rule tested `path == GATE` alone. Built as answer (c).
`arming.PINS` is `subprojects/docket/tests/test_cli.py`, found from the
module's location as `PL-QFCR` finds the gate. When a change reaches it, `arm`
parses both sides and holds for the owner's read when an existing pinned
definition changes or goes. A definition is pinned when its name starts with
`test_arm_`, `_arm` or `ARM_`, or when it is a test that uses `_arm` or
`arming`. That last part widens the owner's "test_arm_ tests" to the arm
tests that do not carry the prefix, such as
`test_a_change_outside_the_owners_read_list_arms_on_green` and
`test_the_owners_read_list_is_spelt_as_the_owner_spelt_it`, which pin answers
just as much. A function's docstring and the file's formatting are left out of
the comparison, so rewording loosens nothing and holds nothing. A new test
arms. A side that will not parse leaves the answer `unknown`.

`test_arm_holds_a_change_to_an_existing_test_arm_test` holds the hold itself:
an edit, a deletion and a changed helper hold, while a new test, a reworded
docstring and an unpinned test arm. `test_arm_holds_a_simulator_path_whatever_shape_its_change_takes`
pins the three path classes through real git: a move from `src/` into the
store, a path outside ASCII, and a deletion. `docs/maintainer.md` now says the
hold covers `arming.py` and the tests that pin its answers, not its inputs.
One residual stays open by design: a change to a shared helper such as `_put`
or `_commit_file` arms, since most of `test_cli.py` uses them.
