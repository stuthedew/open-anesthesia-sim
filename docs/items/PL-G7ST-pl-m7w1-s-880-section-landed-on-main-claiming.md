---
id: PL-G7ST
title: PL-M7W1's #880 section landed on main claiming the frozen 21:09 subject would land, but #880 was merged manually so the renamed title landed: the item about squash-subject provenance now carries a false provenance claim, and the near-miss it actually was narrows the hazard's scope
priority: P3
effort: S
status: done
classes: docs
feature: commit-provenance
touches: docs/items
added: 2026-09-21
closed: 2026-09-21
payoff: PL-M7W1 stops overstating how often the squash-subject freeze actually lands, and gains the auto-merge-only boundary that decides what direction 1 would have to cover
verify: grep -q 'a near miss, and a narrower hazard' docs/items/PL-M7W1-arming-auto-merge-freezes-the-squash-subject-at.md
---

**Problem.** PL-M7W1's #880 section landed on main claiming the frozen 21:09 subject would land, but #880 was merged manually so the renamed title landed: the item about squash-subject provenance now carries a false provenance claim, and the near-miss it actually was narrows the hazard's scope

**Problem.** `PL-M7W1`'s § "A second instance, three hours later, on #880",
landed on `origin/main` in `32c70c5d`, asserts that "the frozen squash subject
is the 21:09 original". The commit carrying that sentence is itself the
disproof: its subject on `origin/main` is the *renamed* title, without the
word "10" the 21:09 original had. The claim was written from the arm time
alone while the pull request was open, and never checked against what landed.

**Why it matters.** It is a false provenance claim inside the item about
provenance. A later session reading `PL-M7W1` to decide its three directions
would count #880 as an instance of the freeze, when it is an instance of the
freeze being *set up and then not happening*. That inflates the observed rate
of the defect the item is about, which is the input to whether direction 1 is
worth its machinery.

**And the correction carries a finding the item did not have.** The freeze
bites only when auto-merge itself performs the merge. A human merging by hand
composes the squash subject from the live title, so the arm-time capture is
irrelevant - and a hand merge is the ordinary case here, on #868 and #880
alike. That narrows § "Why it matters." in `PL-M7W1`, which reads as though any
armed pull request is exposed, and it is an argument about direction 1's cost
rather than against it.

**Done when** `PL-M7W1` no longer claims #880 froze a subject, says what did
happen and why, and records the auto-merge-only boundary. The behavioural half
stays: the session that armed and then renamed had written that item's
`**Decision needed.**` within the hour, which is what bears on direction 2.
