---
id: PL-5ZLQ
title: Cut v0.5.12 from the 131 items finished since v0.5.11
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
resource: release-train
added: 2026-09-26
payoff: the 131 items finished since v0.5.11 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.12\"" pyproject.toml
---

**Problem.** Cut v0.5.12 from the 131 items finished since v0.5.11

The project owner raised the cut on 2026-09-26 ("We should probably cut a new
version soon with all these fixes?") in the Projects trial's "Fix generators"
project, and its coordinator started the "Next release" thread for it. The
session-start digest was offering 0.5.12, and `bin/docket release 0.5.12
--dry-run` named 130 finished items, 131 once `PL-9RSP`'s `#1112` merged
minutes later, completing seven features:
context-budget-reading, count-input-addressing, gate-status-guard,
rendered-claim-accuracy, set-parity, timeline-arrangement and
verify-false-reject. It carries all nine generator heads the trial's topic
named (`PL-B8HZ`, `PL-HMZZ`, `PL-QHCW`, `PL-MB2W`, `PL-Q4DF`, `PL-XBV4`,
`PL-PVW2`, `PL-GPJ7`, `PL-979D`), each `done`; `bin/docket generators` lists
`PL-MT3R` alone as still generating.

**What was checked at filing.** `git ls-remote --tags origin` shows v0.5.11 as
an annotated tag peeling to `fe2046f7`, the cut's own merge (`#1003`), so the
cut is not refused on an untagged predecessor. `list_sessions` shows no other
session cutting a release, and `bin/docket flight` shows no release item
claimed. `git diff v0.5.11..origin/main` leaves `src/`, `tests/reference/` and
`README.md` untouched; `docs/MODEL.md` differs only by the § marks `PL-YSMV`
and `PL-GPJ7`/`PL-QQCD` put on its cross-references, so no equation,
parameter, method or displayed value moved. None of the branches then in
flight (`PL-3PH2`, `PL-MT3R`, `PL-S8LZ`'s `#1110`, and `PL-9RSP`'s `#1112`,
since merged) edits an item file the cut stamps.

**Timing, put to the owner on 2026-09-26: cut now, or after `PL-MT3R` (the
remote-copy head) lands.** Recommendation: cut now, and work proceeds on it
until the owner answers. `PL-MT3R` is at `needs-decision`, so waiting holds the
131 behind a design answer and three merges in a row (its build, `PL-C3MN` and
`PL-21KN`). Neither member's defect reaches a cut on a branch only this session
pushes to, and cutting while claim and arm are being rewritten is the riskier
order. What waiting would buy is a v0.5.12 with no generator head live; 0.5.13
can carry that instead.
