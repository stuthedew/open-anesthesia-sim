---
id: PL-WW0Q
title: bin/docket arm holds a change to arming.py for a read but arms one to what its answer is read through - vcs.changed_path_args and default_base, claims.holdings, cli.cmd_arm and the test_arm_ tests - so the gate can still be loosened unread from beside it
priority: P2
effort: M
status: needs-decision
classes: defect
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-25
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
back to him on ordinary evidence. His yes lifts the pause on new workflow
mechanisms for it (`PL-6Q9L`); on 2026-10-12 `PL-8QMD` is the one open item
carrying `generator: live`, and its pull request `#1439` is open.

**Done when.** `arm` holds for a read a pull request that could loosen its answer by the route the decision picks, a test in `subprojects/docket/tests/test_cli.py` holds it, and `docs/maintainer.md` says what the hold covers.

**Generator check.** Re-entry of `PL-K6B2` (closed 2026-09-25), whose Worked paragraph names this gap and whose `recurrences:` already records this capture. The fact misread is which code decides `arm`'s answer: `arming.py` alone, or everything it reads through. That is `PL-SQTR` recommendation 2's wording, and no head's `misread:` states it.
