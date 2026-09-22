---
id: PL-16HD
title: ROADMAP.md's v0.6.0 'Declined to Gate 2, because every one was captured after this list was frozen' subsection holds six entries and says 'All six' twice, but one paragraph says 'these seven were not yet filed', so a reader reconciling the count against the list finds one entry missing that was never there
priority: P3
effort: S
status: ready
classes: docs
feature: gate-list-integrity
touches: ROADMAP.md
added: 2026-09-22
payoff: a reader reconciling v0.6.0's post-freeze deferral list against its own prose stops looking for a seventh entry that never existed
verify: grep -qF 'these six were not yet filed' ROADMAP.md
---

**Problem.** ROADMAP.md's v0.6.0 'Declined to Gate 2, because every one was captured after this list was frozen' subsection holds six entries and says 'All six' twice, but one paragraph says 'these seven were not yet filed', so a reader reconciling the count against the list finds one entry missing that was never there

**Reproduced 2026-09-22 (`PL-14QR`, triage).** `grep -n 'these seven' ROADMAP.md` finds the
paragraph at line 5660. The list under the heading at line 5642 holds six
bullets (`PL-H0CF`, `PL-M7W1`, `PL-RFHH`, `PL-YZJD`, `PL-6SRZ`, `PL-Z891`), and
the subsection says "All six" at lines 5648 and 5662. Probable origin, inferred
rather than traced: `PL-PBP5`, which the paragraph beside it records as reverted
out of the pass. That would have taken the list from seven to six and left one
of the three counts behind.

**Why it matters.** The subsection records which post-freeze debt the gate
declined, and a reader checks it against the store. A count that disagrees with
its own list sends that reader looking for an entry that was never there. They
also cannot tell a miscount from a lost entry without reconstructing the pass
from history.

**Done when.** The paragraph's count agrees with the six-entry list.
