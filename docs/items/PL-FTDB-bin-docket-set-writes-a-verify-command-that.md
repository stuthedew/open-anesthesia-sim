---
id: PL-FTDB
title: bin/docket set writes a verify: command that already passes, because it validates without running the verify it is writing, so a grep that matches its own frontmatter line (PL-CBDX, 2026-09-25) is accepted and fails the next make check
priority: P2
effort: S
status: done
classes: defect
feature: set-parity
milestone: v0.5.12
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-25
closed: 2026-09-26
pr: 1071
payoff: a verify: command that proves nothing is refused as it is written rather than a make check later, so docket verify never holds one that would accept a branch that did none of the work
verify: grep -q 'def test_set_refuses_a_verify_that_already_passes' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket set writes a verify: command that already passes, because it validates without running the verify it is writing, so a grep that matches its own frontmatter line (PL-CBDX, 2026-09-25) is accepted and fails the next make check

**Reproduced 2026-09-26 against 78b1a02b,** on a scratch copy of the store. `bin/docket set --verify "grep -qF 'self-match-probe' <the item's own file>"` exits 0 and writes the line, and the command then exits 0 with no work done, because the pattern is in the `verify:` line itself. `checks.py`'s replay reports exactly that as an error ("open but its `verify:` command already passes"), so `set` writes what the next `make check` refuses. `PL-CBDX`'s committed command is the anchored repair (`^\*\*Reviewed\.\*\*`).

**Why it matters.** `set` exists to refuse any write `docket check` would then fail, in the checker's words, and here it does not. The author finds out a `make check` later, and until then `docket verify` would accept a branch that did none of the work. A `grep` over the item's own file is an admitted shape, so `PL-1P5V`'s allowlist does not stop it.

**Done when.** `bin/docket set --verify` runs the command it is about to write on an open item, and refuses one that already exits 0 in the replay's words. A test in `subprojects/docket/tests/test_cli.py` holds it.

**Generator check.** An instance of the fact `PL-1P5V` and `PL-6TP8` both state, what a `verify:` command's exit status proves about its own item's work, filed 2026-09-25 after both heads closed (`PL-6TP8` on 2026-09-19, `PL-1P5V` on 2026-09-23). `PL-1P5V` fixed which shapes a command may take, and an admitted shape can still pass before the work. It is the first post-close instance of `PL-1P5V` on record. No other Generator check line names either head as one: `PL-R812`, the only line naming either, was filed 2026-09-22, before `PL-1P5V` closed, and `PL-5MYR`'s sweep of 2026-09-23 found none filed after. `PL-6TP8`'s seven post-close instances are `PL-1P5V`'s own members. That makes one of the three that would record `PL-1P5V` as a generator whose fix did not hold.

**Worked.** Reproduced on `e991944d` before the fix: the new test's first
`set` exited 0 and wrote the self-matching `grep`. `set` now writes the line,
runs the replay's own `already_passing` scoped to the one item through a new
`_replayed` helper, and keeps only the errors that run adds to `analyze`, so
the refusal is the replay's sentence and a blocked item gets the replay's
blocked wording. The command has to run with the line written, since a
self-matching `grep` passes on no other tree, so a refusal writes the file's
original bytes back, and so does an interruption during the run. What the
replay reads as no finding (a command not found, one killed at the limit,
one reading past the tree, a status the replay does not ask about) refuses
nothing, as it refuses nothing in `check`. Only `--verify` triggers the run,
as the brief says: a status-only write onto an item whose recorded command
already passes is still `check`'s to find.
