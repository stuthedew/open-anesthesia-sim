---
id: PL-6YWK
title: PL-4L6Z's verify: runs the whole reference suite, so it is killed at docket check's 120s limit and nothing is claimed about the item on any run
priority: P2
effort: S
status: ready
classes: defect, infra
feature: queue-hygiene
touches: docs/items
added: 2026-09-13
verify: uv run pytest subprojects/docket/tests/test_verify.py -q && grep -qE '^verify: .*tests/reference/test_[a-z0-9_]+\.py' docs/items/PL-4L6Z-*.md
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

**Done when.** `PL-4L6Z`'s `verify:` names the single reference test file its
work adds rather than the whole directory, completes inside `LANDED_TIMEOUT`,
and fails today for the reason the paired shape intends - the suite half
passing, the `grep` half finding no such test.

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
