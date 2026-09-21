---
id: PL-C4W8
title: Sweep Gate 2's 168 clearable entries against the tree before any of them is worked: beat 3 of the cadence, unrun on a list frozen 2026-09-21 that the 2026-09-19 precedent says is 13-32 percent dead or overstated
status: untriaged
feature: gate-staleness-sweep
added: 2026-09-21
---

**Problem.** Sweep Gate 2's 168 clearable entries against the tree before any of them is worked: beat 3 of the cadence, unrun on a list frozen 2026-09-21 that the 2026-09-19 precedent says is 13-32 percent dead or overstated

## This pass answers two questions per entry, not one

**Decided (project owner, 2026-09-21, ratified)** - chosen over sweeping for
staleness alone and letting the placement question be settled entry by entry
later, and over deferring the affected entries to Gate 3.

**Question 1, the cadence's own: does this defect still reproduce against the
tree?** A `verify:` command tests for the presence of the fix and never for the
presence of the fault, so an entry solved another way fails forever and reads as
outstanding. Drop what no longer reproduces with its `reason`; correct the
briefs that overstate what is left. The one measured precedent put 13% of a
verified sweep dead or overstated and 32% of an unverified map, so expect
roughly 22 to 54 of the 168.

**Question 2, new: would v0.6.0 re-decide this?** If yes, the entry carries
`feature: interface-areas` and is cleared **by** the milestone rather than
before it. This is re-labelling and not renegotiation: `plan.py`'s rule is
"Cleared by the milestone itself: open debt carrying its feature", the gate
stays frozen, every entry stays written on the frozen list, and nothing is
deferred to Gate 3. The bucket holds exactly one member today (`PL-VN6M`), which
is the claim this question tests.

**The line to draw.** *Ownership, placement and sizing move; units, wording,
arithmetic and guards do not.* Where a control lives, what a surface is sized
against, and what a budget is a maximum over are all re-decided the moment a
surface becomes a View in an Area - v0.6.0's own Required-scope entry 9
(`PL-9LNF`) already records that the chart time base is owned by a dropdown
inside one plot's panel while governing both, and that the column budget is read
over two siblings that stop being siblings. Candidates named in the design round
and **not** yet verified: `PL-V67Q` (y-axis range control - where does the
control live), `PL-Z4K6` (readout columns at a given width), `PL-QYBW` (axis
scaling, which becomes per-View-instance state under entry 11), `PL-1K9G`
(hover column resolved in two dimensions), `PL-CNCF` and `PL-PGZF` (frame cost
at a column budget that becomes per-Area). Entries that stay in front of the
milestone on the same test: `PL-B396` (litres of vapour versus liquid mL),
`PL-SQJ1` (playback delivering 73-91% of the displayed rate), `PL-LLBV` (the
fork-instant guard refusing 35.5% of typable times), `PL-SPN6` (three
compartments raising one error). All of these are titles read in a design round,
which is the evidence standard this pass exists to replace - verify each against
the tree.

**Count before tightening anything.** `.claude/rules/expert-review.md` requires
naming what the suppressed side would have to be worth before a bar moves, and
this project has the worked example: raising the apparatus capture bar on a
self-generation rate was refuted when the count nobody ran came back 67%
still-real findings. Question 2 is a re-classification rather than a bar, but it
suppresses work from the pre-milestone window all the same, so it is answered
per entry against the tree and never per feature in bulk.

**The counter-precedent, which is why question 2 is counted and not assumed.**
This project made a near-identical argument once - that the Qt port would
redecide the visuals, so styling first was styling twice - and measurement
falsified it: the port changed `app/theme.py` by 10 insertions and 29 deletions
and redecided no palette entry, type size, padding or radius. The reason it may
cut differently here is that the port re-expressed widgets while carrying the
visual language across, where v0.6.0 changes ownership and containment. That is
a reason to check, not a reason to conclude.
