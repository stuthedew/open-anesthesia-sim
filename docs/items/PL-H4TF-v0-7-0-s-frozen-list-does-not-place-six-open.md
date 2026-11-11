---
id: PL-H4TF
title: v0.7.0's frozen list does not place six open science items from model-claims-held-by-tests (PL-19W8, PL-JP7P, PL-MCQ5, PL-5C1H, PL-H94Q, PL-TDX0): their deferred-from: answers the disposition error but not the gate's re-entry advisory, so the v0.7.0 cut must add them to the frozen list with the date and reason, or place them in Required scope
priority: P2
effort: S
status: done
classes: docs
feature: model-claims-held-by-tests
milestone: v0.6.17
touches: ROADMAP.md, docs/items
added: 2026-11-02
closed: 2026-11-07
pr: 2063
payoff: the v0.7.0 cut either clears the five science passes or records why it ships without them, and make check stops repeating the gate advisory
verify: grep -q 'PL-19W8' ROADMAP.md
---

**Problem.** `PL-B6YV` filed five passes under `model-claims-held-by-tests`
on 2026-11-02 and classed them `science`: `PL-19W8`, `PL-JP7P`, `PL-MCQ5`,
`PL-5C1H` and `PL-H94Q`. Each carries a `deferred-from: v0.7.0` line. That
line clears `bin/docket check`'s disposition error. It does not clear the
advisory that `tools/doc_check.py`'s gate re-entry rule prints. That rule says
a `safety` or `science` item re-enters the current gate whatever its
presence, and ROADMAP.md § "The gate is a snapshot, not a moving target"
says these two classes are not deferrable. So `make check` prints the
advisory on every run until the gate places them. `PL-TDX0`, filed later the
same day from `PL-TCD3`'s blind review, is a sixth in the same position.

**Why it matters.** The advisory repeats on every run while nothing acts on
it, which trains a reader to skip the advisories. And a v0.7.0 cut that does
not settle it ships with five open science items that its own rule places in
its gate.

**Done when.** At the v0.7.0 cut, or before it, each of the six items is in
v0.7.0's frozen list with the date and the reason it re-entered, or in its
Required scope. Or an item the cut finds is no longer needed is dropped with
its reason. `PL-19W8`'s count may drop the four passes behind it, which
would leave only `PL-19W8` to place. The gate re-entry advisory no longer
names any of them.

**Generator check.** Not a generator on what is known. It is one capture,
from one filing of five items. `bin/docket check` accepts `deferred-from:` on
a science item, and the gate re-entry advisory does not, and the advisory
says so in its own text. If a later filing meets the same disagreement, that
disagreement is the mechanism to record.

**Done 2026-11-07, by `PL-GW0P`'s re-check.** All six items joined v0.7.0's
frozen list on 2026-11-07, with the date and the reason, in the paragraph that
opens "38 captures joined this list". `PL-TDX0` joined undeferred. The other
five stay deferred, each with a `deferred-from:` that records the check that
no learner can see a wrong value now, which `PL-8C8W` made the rule. The gate
re-entry advisory no longer names any of them.
