---
id: PL-2KC7
title: Cut v0.5.16 from the 5 items finished since v0.5.15
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
resource: release-train
added: 2026-09-27
payoff: the 5 items finished since v0.5.15 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.16\"" pyproject.toml
---

**Problem.** Cut v0.5.16 from the 5 items finished since v0.5.15

The project owner asked on 2026-09-27 for a version to be cut on the way to
v0.6.0 whenever a feature finishes, and the project's coordinator started this
thread once the `scenario-branching` chain's five Gate 2 items had all reached
`main`, the last of them `PL-7TXJ` (`#1194`, merged 19:45 UTC).

**What was checked at filing.** `git ls-remote --tags origin` shows v0.5.15 as
the annotated tag `61cb877b` peeling to `16cb66a4`, the cut's own merge
(`#1190`), so the cut is not refused on an untagged predecessor. `bin/docket
flight` shows no release item claimed: its rows are `PL-G8TR` (`#1198`),
`PL-LT77` and `PL-PNW6` (`#1197`) and `PL-W40L` (`#1199`). `bin/docket release
0.5.16 --dry-run` named 5 finished items, and they match `main`'s own history:
of the six pull requests merged after `#1190`, the two with no bullet are
`PL-8XQS`'s capture (`#1193`) and `PL-9DYK`'s recorded answer (`#1195`), both
still open, and the fifth bullet is `PL-NC62` (`#1188`), which merged inside
v0.5.15's tag during that cut's review and is described here, as v0.5.15's
baseline section says by name.
