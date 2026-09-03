---
id: PL-THVN
title: PL-011's history sizing assumes six flat floats per sample, which PL-W3DD's per-substance mapping invalidates inside the same milestone
status: untriaged
added: 2026-09-03
---

**Problem.** `PL-011` (bound the controller's concentration history) sizes the
retention problem from the record's current shape:

> a slotted dataclass of seven floats is on the order of a few hundred bytes

and then, more precisely, "a `SimulationHistorySample` measures 88 B as an
object plus its floats (~256 B worst case, ~88 B if the floats are shared), so
the cap bounds retention at roughly 2.3-6.6 GB."

`PL-W3DD`, in the same milestone, re-keys `SimulationHistorySample` by substance
rather than by six flat named compartment floats. A per-substance mapping is not
a slotted dataclass of seven floats: it carries a dict or a nested structure per
sample, and per-sample cost rises by considerably more than the two measurements
above allow for. Both numbers — the "few hundred bytes" that sets `PL-011`'s
priority as "lower than it looks", and the 2.3-6.6 GB the chosen cap is said to
bound — stop describing the record they are about.

**Why it matters.** The cap is a bound on memory, and its value was chosen
against a per-sample cost. If that cost changes by a factor of several within
the same release, the cap either stops bounding what it claims to bound or is
more conservative than it needs to be, and in both cases the brief's stated
justification is wrong. This is an ordering dependency neither item records:
`PL-011` is `ready` and `PL-W3DD` is `ready`, and nothing tells a session
picking `PL-011` that the number it is about to write into the brief has a
short life.

**Where.** `docs/items/PL-011-*.md`, the sizing paragraphs (lines 19-20 and
30-32 at capture); `docs/items/PL-W3DD-*.md`; the record itself at
`src/anesthesia_sim/app/controller.py:17-27`.

**Approach.** Cheapest fix is sequencing plus a note: land `PL-W3DD` first, and
have `PL-011` measure the cap against the shape that ships. If `PL-011` goes
first, its brief should state the measurement as provisional and name `PL-W3DD`
as the item that invalidates it, so the re-measurement is owed rather than
forgotten. Either way `bin/docket concurrent` should stop offering the two as
independent — neither declares the other in `touches`.

**Done when.** The two items record their dependency, and whichever lands second
carries a per-sample size measured against the shipped record shape.

**Found.** Session auditing which open items the v0.4.1 `core/` pass would
invalidate, 2026-09-03. Not a v0.4.1 interaction — an intra-v0.4.0 one found on
the way past.
