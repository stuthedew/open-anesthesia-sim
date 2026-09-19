---
id: PL-6P9Y
title: A milestone's Explicitly out of scope list is read as silence, so an id it names is unplaced where it could be reported out of scope
priority: P3
effort: S
status: done
classes: infra
feature: planning-cadence
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests/test_roadmap.py
added: 2026-09-01
closed: 2026-09-19
verify: uv run pytest subprojects/docket/tests/test_roadmap.py -q && grep -rq 'def test_an_out_of_scope_id_is_reported_excluded' subprojects/docket/tests
---

**Problem.** `PL-HDY6` made a milestone section place an id only from the two
structures that record membership - its frozen list's entries, and its
`Required scope`. Every other mention is now silence. That is the right answer
for a mention the reader cannot interpret, but one of them is not a mention at
all: `### Explicitly out of scope for vX.Y.Z` is a heading whose whole meaning
is exclusion, and the ids under it are as decidable as the ids under `Required
scope`.

Measured 2026-09-01, one id sits there: v0.4.0's out-of-scope list names
`PL-Z7LY` (horizontal panning of the chart window). `Scope.placement` answers
`unplaced` for it, so `docket next` ranks it between in-scope and out-of-scope
work and prints no marking, where the roadmap has actually made a decision
about it.

**Why it matters.** Small, and an improvement to correct behaviour rather than
a defect in it - which is why this is queue work rather than a v0.2.8 gate
entry under that release's scope test. The value is that the section's own
decision reaches the ranking: an id a milestone has explicitly ruled out
should not be offered ahead of work nobody has ruled on.

**Where.** `subprojects/docket/src/docket/roadmap.py` - `_scope_ids` and the
subsection tracking in `parse_milestones`, then `Scope`, which today has three
answers and would need the anchor's own exclusions to be one of them rather
than folded into `out-of-scope` (whose reason string says "appears in
`<milestone>`'s section, which the current step has not reached", and that is
not what an exclusion means).

**Done when.** An id under a milestone's `Explicitly out of scope` heading is
reported as excluded by that milestone rather than as unplaced, with a reason
string that says so, and a test covers `PL-Z7LY`.

**Triaged 2026-09-01.** P3, `infra`, `planning-cadence` alongside `PL-HDY6`
(place an id by where a milestone writes it), `PL-0RS6` and `PL-1TPM`, whose
reader this extends. Classed `infra` and **not** `defect`, deliberately: the
brief's own reading is that the current answer is correct rather than wrong -
`unplaced` is what silence should produce - and this makes a heading that is
not silence speak. Classing it `defect` would make it debt on the next gate for
behaviour nobody has called broken.

Not admitted to v0.2.8's frozen list. The three siblings are entries because
each fixed a reader producing a *wrong* placement; this one adds a placement
that does not exist yet, which `ROADMAP.md`'s "What the freeze closes" sends to
the queue.

P3 rather than the siblings' P2 because it moves exactly one id today
(`PL-Z7LY`, horizontal panning of the chart window, under v0.4.0's out-of-scope
heading at `ROADMAP.md:1201`), verified 2026-09-01, and that id belongs to a
milestone two steps out. The `verify:` command was run before being written
down: it deselects all 31 tests and exits 5 on the current tree.

---

**Done 2026-09-19, with `PL-HWW1`.** `Scope` has a fourth answer, `EXCLUDED`,
and `milestone_scope` fills it from the **anchor's own** `excluded_ids`. Three
surfaces say it: `placement_line` prints "explicitly out of scope for
<milestone>", `placement_mark` prints `[ruled out]` with its own legend clause,
and `recommend` writes "Explicitly out of scope for <milestone>: its section
names this id under that heading, so the roadmap has ruled on it."
`PLACEMENT_ORDER` sorts it below out-of-scope work rather than between the
bands, because an out-of-scope id is waiting for its step to come round and
this one has been decided.

**Folded into `PL-HWW1` rather than done on its own**, because that item was
already rewriting the reader that answers placement and the two would otherwise
have landed as a conflict in one function. The brief's own `Where` named the
design taken - a fourth answer rather than folding into `out-of-scope`, whose
reason string says "which the current step has not reached" and means something
else.

**The id it moves today is the one this brief predicted, at a different
anchor.** `PL-Z7LY` (horizontal panning of the chart window) is named under
v0.4.0's exclusion heading, as measured on 2026-09-01, *and* under v0.5.0's -
and v0.5.0 is the anchor, so `bin/docket show PL-Z7LY` now reports "explicitly
out of scope for v0.5.0 - the case you can branch" where it reported "placed by
no section" an hour ago. Another section's exclusions stay silent, deliberately:
one the project has passed says what was true then, and one it has not reached
is a decision that milestone's own scoping round may still revisit.
