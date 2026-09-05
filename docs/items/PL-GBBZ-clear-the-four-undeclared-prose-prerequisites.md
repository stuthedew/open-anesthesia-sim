---
id: PL-GBBZ
title: Clear the four undeclared prose prerequisites the new advisory names
priority: P2
effort: S
status: needs-decision
classes: planning
feature: planning-cadence
touches: docs/items/PL-88GQ-state-every-displayed-decimal-count-as-a.md, docs/items/PL-SSBP-add-the-chart-time-base-selector-with-15-30-and.md, docs/items/PL-W8DQ-the-four-slider-active-tracks-use-accent-and.md, docs/items/PL-WZVZ-make-an-inter-machine-difference-attributable.md
added: 2026-09-05
---

**Problem.** `PL-ZBRB` made `docket check` notice a prerequisite stated in a
brief and never declared in `blocked-by`. It fires on four pairs in the store
as it lands, every one of them genuine:

| Item | Names as a prerequisite | The sentence, with the id elided |
| --- | --- | --- |
| `PL-88GQ` | `PL-X9KD` | "**Depends on.** … lands first" |
| `PL-SSBP` | `PL-011` | "The upper scales are blocked on …" |
| `PL-W8DQ` | `PL-GVXP` | "the choice depends on …" |
| `PL-WZVZ` | `PL-4DCG` | "**Depends on** … for the rows" |

The quoted sentences elide the blocker id on purpose. Written out, this brief
would trip the very advisory it exists to clear — an item *about* dependencies
reads like an item *with* them, which is one of the limits `PL-ZBRB`'s
docstring names and this is the first instance of it.

**Why it matters.** An advisory that fires on every run and is never cleared
trains a session to skim past it, and the cost of that is not these four items
but the next advisory, which is then read the same way (`PL-H7XN`, `PL-G049`).
`PL-ZBRB` was required to produce an advisory that *can* reach zero; this is
the pass that takes it there, and until it runs the check is carrying a
standing backlog of four.

**Why it is a separate item.** Declaring these edges is not a transcription.
Each one is a judgment about whether the sentence states a real prerequisite,
and the fix the advisory names — `blocked-by` plus `status: blocked` — takes
the item out of `docket next` entirely. Three of the four are product work
(`PL-SSBP` is a `teachable-case` item scoped to v0.4.0), so this reshapes the
ranking the current milestone is worked from. That is the project owner's call,
not a workflow session's.

**Where.** `docs/items/PL-88GQ-*.md`, `docs/items/PL-SSBP-*.md`,
`docs/items/PL-W8DQ-*.md`, `docs/items/PL-WZVZ-*.md` — front matter only.

**Watch for.** `_outranks_its_blocker` refuses a `blocked` item that ranks
above its own blocker, so setting `status: blocked` on one of these can
surface a second, real problem rather than closing cleanly. Raise the blocker
to meet what it holds up, as that check says; do not lower the blocked item.

**Decision needed.** Which of the four sentences state a real prerequisite,
and therefore which items gain `blocked-by` plus `status: blocked`. Declaring
an edge takes the item out of `docket next` entirely, and three of the four are
product work - `PL-SSBP` (add the chart time-base selector) is scoped to
v0.4.0 - so the answer reshapes what the current milestone is worked from.
Rewording the sentence is the alternative where it reads as a prerequisite but
is not. The advisory cannot reach zero until each pair is answered one way or
the other.

**Done when.** Each of the four either declares the edge — `blocked-by` and
`status: blocked` together — or has the sentence reworded because it was not
claiming a prerequisite, and `bin/docket check` raises no prose-dependency
advisory.
