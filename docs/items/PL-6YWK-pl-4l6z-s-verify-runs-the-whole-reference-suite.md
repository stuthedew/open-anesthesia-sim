---
id: PL-6YWK
title: PL-4L6Z's verify: runs the whole reference suite, so it is killed at docket check's 120s limit and nothing is claimed about the item on any run
priority: P2
effort: S
status: done
classes: defect, infra
feature: verify-replay-cost
milestone: v0.4.28
touches: docs/items
added: 2026-09-13
closed: 2026-09-19
pr: 699
verify: grep -q '^verify: grep' docs/items/PL-4L6Z-verify-the-model-by-making-it-compute-a.md
---

**Problem.** PL-4L6Z's verify: runs the whole reference suite, so it is killed at docket check's 120s limit and nothing is claimed about the item on any run

**Why it matters, and why the limit is not what moves.** `LANDED_TIMEOUT` is
120 s and its comment says what it is holding: "long enough for a project's own
suite, short enough that one wedged command cannot hang `make check`". Raising
it for one item spends that guarantee on the item least able to justify it.
`PL-4L6Z`'s command is `uv run pytest tests/reference/ && grep -rq '...'
tests/reference/`, and the first half runs the whole reference suite.

What the kill costs is the item's specification. A command that is killed
neither passes nor fails, so `bin/docket check --verify` can say nothing about
`PL-4L6Z` on any run: it cannot be reported as already passing, which is the
advisory that catches a command proving nothing, and it cannot be reported as
selecting nothing. The one open item this project holds up as its verification
centrepiece is the one item its own check has no reading of, and that has been
true on every run since the command was written.

**Done when.** `PL-4L6Z`'s `verify:` is the discriminating `grep` alone, with
no prerequisite clause ahead of it, so it completes well inside
`LANDED_TIMEOUT` and fails today because the test it names does not exist yet.

The "single reference test file" this originally asked for is superseded:
`PL-6TP8`'s ratified shape makes the command a `grep`, and `grep -rq` over
`tests/reference/` exits 1 - the code an ordinary failure gives - where a named
file the work has not yet created would exit 2 on a missing path. The directory
is the right argument once the `pytest` half is gone.

**`PL-RCQM` was dropped into this item on 2026-09-17** (project owner), having
been filed a day earlier from the other direction - the session-start digest's
red-`main` line rather than the sweep's cost. Two measurements it took are not
repeated above and are worth having before the command is rewritten:

- `bin/docket check --verify` cost **233.8 s for 164 commands** on run #2104, so
  the 120 s this one item burns and learns nothing from is about half again the
  mean command.
- The slowest command that *did* complete was `PL-P1P6` at **97.2 s**, against
  the 120 s limit. **The budget has no headroom left**, which is the evidence
  that closes the alternative remedy: raising `LANDED_TIMEOUT` would have to
  clear 97.2 s for everything else too, so narrowing `PL-4L6Z`'s command is the
  only route that does not spend the guarantee the limit exists to hold.

`PL-RCQM`'s brief also settles a misattribution worth not repeating: run #2104's
log names `PL-4L6Z` immediately before its non-zero exit, and that is the *not
checked* line, which claims nothing and fails nothing. The error on that run was
`PL-D1RT`'s command already passing. Fixing this item does not take `main`
green, and nothing here ever did.

**Re-pointed by `PL-6TP8`, 2026-09-19.** What the limit kills is the
prerequisite clause, `uv run pytest tests/reference/`; the discriminating
`grep -rq` behind it runs in under a second. The form of the repair is
`PL-6TP8`'s shape half: if the field drops prerequisite clauses, `PL-4L6Z`'s
command becomes the `grep` alone; if it keeps them, the clause narrows to the
one reference file the work adds, as briefed. Either way the command completes
inside the limit and fails today for the right reason.

**Decided 2026-09-19, later the same day.** The shape half was ratified: the
repair is the `grep` alone, so `PL-4L6Z`'s command becomes `grep -rq 'def
test_a_tissue_volume_recovered_from_its_washin_matches_the_stored_value'
tests/reference/`. This item's own `verify:` still pins a single-file pytest
target, which that shape does not produce, so rewrite it first when starting
this - run and watched failing, as the skill asks.

**Done 2026-09-19.** `PL-4L6Z`'s command is now `grep -rq 'def
test_a_tissue_volume_recovered_from_its_washin_matches_the_stored_value'
tests/reference/`, measured at **2 ms, exit 1** on this checkout, against the
120 s kill it replaced. That returns the whole-store replay's headroom: the
budget's previous slowest completing command was `PL-P1P6` at 97.2 s, and this
item was the only one of the 176 killed outright.

This item's own `verify:` was rewritten in the same commit, for the same
reason: it carried a `uv run pytest subprojects/docket/tests/test_verify.py -q`
prerequisite and then pinned a single-file target that `PL-6TP8`'s shape does
not produce. It is now `grep -q '^verify: grep'` against `PL-4L6Z`'s file - the
same shape `PL-8T83` already used for `PL-M26Q` - run and watched failing at
exit 1 before the work.
