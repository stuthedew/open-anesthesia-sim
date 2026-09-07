---
id: PL-GBBZ
title: Clear the four undeclared prose prerequisites the new advisory names
priority: P2
effort: S
status: done
classes: planning
feature: planning-cadence
touches: docs/items/PL-88GQ-state-every-displayed-decimal-count-as-a.md, docs/items/PL-SSBP-add-the-chart-time-base-selector-with-15-30-and.md, docs/items/PL-W8DQ-the-four-slider-active-tracks-use-accent-and.md, docs/items/PL-WZVZ-make-an-inter-machine-difference-attributable.md
added: 2026-09-05
closed: 2026-09-07
pr: 434
verify: bin/docket show PL-WZVZ >/dev/null && grep -q '^blocked-by: PL-FG9D, PL-4DCG$' docs/items/PL-WZVZ-make-an-inter-machine-difference-attributable.md
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

**Done 2026-09-07, and the decision the brief asked for had been overtaken by
events: three of the four pairs cleared themselves between 2026-09-05 and
today, and the one left carried no ranking consequence to decide.**
`bin/docket check` fired on one pair, not four. The check skips a closed item
and a closed blocker by design - `_check_prose_dependencies` takes only
`item.is_open` and `blocker.is_open`, because "most in-body mentions name work
that has since closed, which is history rather than a defect" - so a pair
leaves the advisory when either end closes, whether or not anybody edited the
sentence. That is what happened to three of them:

| Pair | Why it no longer fires | Was the sentence answered? |
| --- | --- | --- |
| `PL-88GQ` -> `PL-X9KD` | both closed (item 2026-09-06, blocker 2026-09-06) | No. `PL-88GQ` was done *inside* `PL-X9KD`, which is the two being worked together as both briefs said to. The prerequisite was satisfied rather than declared. |
| `PL-SSBP` -> `PL-011` | item closed 2026-09-05; blocker `dropped` 2026-09-05 | Yes, and before this item was written. The brief already says the sentence is "recorded here as history" and that the cost "was decimation's rather than the history buffer's", so it was never claiming a prerequisite. |
| `PL-W8DQ` -> `PL-GVXP` | blocker closed 2026-09-07; item still open (`ready`) | Yes. The brief now reads "**Depends on.** Nothing" and "no longer conditional", and the surviving mention is "sequenced after `PL-GVXP`" - `after` is deliberately not a cue. It would stay silent even if `PL-GVXP` reopened. |
| `PL-WZVZ` -> `PL-4DCG` | still fired: both open, edge undeclared | This item's actual work. |

**The one real pair, and why declaring it needed no decision.** `PL-WZVZ`
(make an inter-machine difference attributable) states a genuine prerequisite
on `PL-4DCG` (survey the anesthesia machines in current clinical use): the
comparison table's rows "come straight from PL-4DCG's survey document, which
is the single source for them", and its **Done when** requires that "no
per-machine value appears anywhere that is not traceable to PL-4DCG's survey
document". So the edge is declared rather than the sentence reworded.

The brief expected this to reshape the current milestone's ranking, which is
why it was filed `needs-decision`. It does not, on two independent grounds.
`PL-WZVZ` already carried `status: blocked` on `PL-FG9D`, so it was already
out of `bin/docket next` - the declaration adds no exclusion. And `PL-FG9D` is
itself `blocked-by: PL-4DCG`, so `PL-WZVZ` could not have become unblocked
ahead of `PL-4DCG` anyway: the edge was already there transitively and this
writes down what the ranking was already doing. Front matter only; no
`status` change was needed.

**`_outranks_its_blocker` did not fire**, which the **Watch for** section
flagged as the likely second problem: `PL-WZVZ` is `P3` and `PL-4DCG` is `P2`,
so the blocked item does not rank above its blocker and no band had to move.

**What this leaves for the check.** The prose-dependency advisory is at zero
and the store's only remaining grooming advisory is `PL-1JDD` (make the source
tier machine-readable), unrelated. Three of the four pairs having left by
closure rather than by an answer is the expected shape rather than a gap -
rewriting a closed item's brief would be rewriting a record - but it does mean
the standing backlog this item was filed against was smaller than four by the
time anyone reached it.
