---
id: PL-9FLD
title: ROADMAP.md's v0.5.17 row and baseline section say the washout fix took about two and a half minutes off every CI run, where #1221 measured 90 s on fast runners and 79 s on slow ones
priority: P3
effort: S
status: done
classes: docs
feature: release-process
touches: ROADMAP.md, docs/items
added: 2026-09-28
closed: 2026-09-28
pr: 1223
payoff: ROADMAP.md states the washout fix's measured CI saving rather than the estimate its item was filed with
verify: grep -q "79 s on slow ones" ROADMAP.md
---

**Problem.** ROADMAP.md's v0.5.17 row and baseline section say the washout fix took about two and a half minutes off every CI run, where #1221 measured 90 s on fast runners and 79 s on slow ones

Found by `PL-HHCD`'s session, which wrote both sentences, when `#1221`
landed while `#1219` was armed. The v0.5.17 row's headline says the 24-hour
washout tests "stopped adding about two and a half minutes to every CI run",
and the baseline section's `PL-F08Y` bullet says "the recomputation had added
about two and a half minutes to every CI checks run". Both took the figure
from `PL-F08Y`'s title, which was the estimate it was filed with.
`#1221` measured the CI pytest step over every successful `quality.yml` run
from 2026-09-26 to 2026-09-27: the fix took 90 s off it on fast runners and
79 s on slow ones, and the washout file still costs about 25 s and 91 s
against a run without it, the slow-runner tail `PL-4Z5Y` carries.

**Why it matters.** `ROADMAP.md`'s current-baseline row is what a session
reads for what a release did, and this one says the washout cost is gone
while `PL-4Z5Y`, still open for the owner's decision, measures 25 to 91 s of
it left. A session weighing `PL-4Z5Y` against it would be weighing the
estimate.

**Done when.** The headline says what changed, the washout tests stopped
recomputing the same curves in every test worker, with no figure; the row's
`PL-F08Y` clause and the baseline bullet give `#1221`'s measurement. Nothing
else in the release's prose cites a CI time. The v0.5.17 tag keeps the old
sentence, as a tag does.
