---
id: PL-L94N
title: subprojects/docket/README.md's release paragraph says a P0 or P1 apparatus filing outside the generator tier breaks PL-04KR's prediction, but since PL-00TR a class-pinned simulator item that reaches only instruction files is left out too
priority: P3
effort: S
status: ready
classes: docs
feature: convergence-visibility
touches: subprojects/docket/README.md
deferred-from: v0.6.0 - a sentence in the docket's own README, which changes nothing a learner sees
added: 2026-10-18
payoff: The README's account of the release alarm matches what inflow counts
verify: grep -q 'class-pinned' subprojects/docket/README.md && grep -q 'recurrence_chains' subprojects/docket/README.md
---

**Problem.** subprojects/docket/README.md's release paragraph says a P0 or P1 apparatus filing outside the generator tier breaks PL-04KR's prediction, but since PL-00TR a class-pinned simulator item that reaches only instruction files is left out too

**Why it matters.** The README is the docket's specification. Its paragraph on what
`docket release` prints about inflow lists the filings that break the `P1` prediction as
those outside the generator tier. Since `PL-00TR`, `inflow._pinned_by_class`
also leaves out a `safety_classes` item whose only apparatus paths are
instruction files. A reader of the README alone would expect such an item to
be reported.

**Why it was not fixed in `PL-00TR`.** On 2026-10-18 the README was held by
another workflow thread's open pull request (#1588), and the coordinator asked
this thread to leave it alone. This is a follow-up to `PL-00TR`, not a second
filing of it, so the recurrence `docket new` recorded on `PL-00TR` is withdrawn.

**Two more sentences from the same pull request (#1594), added 2026-10-18.**
`PL-RX3H` made the recurrence count follow a closed anchor: `plan.recurrence_chains`
adds the filings recorded on each closed item that an open item re-files. The
README's `recurrences` paragraph still describes the count as the captures
`docket new` matched to one item. `PL-K23D` made `record N --merge` name each
released-notes bullet it declined to restate, by file and line. The README's
paragraph on how `record` restates released bullets does not say so. Both are
the same file and the same hold, so they ride this item rather than two more.

**Done when.** The README sentence names both exclusions: the generator tier,
and a class-pinned item that reaches only instruction files. The `recurrences`
paragraph says the count follows closed anchors, and the restating paragraph
says a bullet carried on from the margin is left alone and named.

**Generator check.** Bookkeeping: a document sentence left behind by a code
change, which `PL-G424` states. It is a known shape, filed so the sentence
does not go stale unnoticed.
