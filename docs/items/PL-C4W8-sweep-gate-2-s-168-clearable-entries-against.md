---
id: PL-C4W8
title: Sweep Gate 2's 168 clearable entries against the tree before any of them is worked: beat 3 of the cadence, unrun on a list frozen 2026-09-21 that the 2026-09-19 precedent says is 13-32 percent dead or overstated
priority: P2
effort: M
status: ready
classes: housekeeping, infra
feature: gate-staleness-sweep
touches: docs/items, docs/WORKING_NOTES.md
added: 2026-09-21
payoff: the 154 swept entries can be worked on evidence rather than on a brief that may describe a tree from two weeks ago, and the three dead ones stop being ranked and offered
verify: python3 tools/doc_check.py check && ! grep -qF 'still unswept are the' docs/items/PL-C4W8-sweep-gate-2-s-168-clearable-entries-against.md
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

## Run 2026-09-21: question 1 answered, question 2 recorded and not written

**Coverage: 154 of the 168 clearable entries.** The 14 still unswept are the
W1 batch - `PL-087W`, `PL-2DTK`, `PL-3LLZ`, `PL-4V6B`, `PL-4W2L`, `PL-6YYR`,
`PL-73P0`, `PL-7RTN`, `PL-7TVT`, `PL-99YZ`, `PL-9LXK`, `PL-B78T`, `PL-BGMK`,
`PL-BYMX`, all workflow lane. The session ran past its context budget before
that batch returned; nothing about them is known either way and they must be
swept before the gate is worked.

**Question 1 outcome: 3 dead, 7 overstated, 144 still reproducing.** About 6%,
against the 13-32% the precedent predicted and the 22-54 entries this brief
expected. The reason is in `docs/WORKING_NOTES.md`: both product-lane drops
trace to one event, the 2026-09-15 Qt port, and Gate 2's entries were filed
almost entirely after it. A staleness rate measures how much upheaval a window
contained rather than anything constant about the store.

Dropped: `PL-3JP0`, `PL-Z9K5`, `PL-SY1J`. Corrected and still open on a
narrower question: `PL-SQJ1`, `PL-Y4YX`, `PL-JQY1`, `PL-RWBV`, `PL-TKFD`,
`PL-LBW5`, `PL-MSFB`.

**Question 2 is blocked on `PL-YVP7`, and this is the finding of the pass.**
The verdicts exist and were reached per entry against the tree; none has been
written to any entry, because the instrument the decision names would damage
what it is written over. `plan.py`'s `gate()` puts an entry inside the
milestone only when `item.feature` equals the milestone's feature, `feature:`
holds one string, and 147 of the 170 clearable entries already carry one.

**The verdicts, for whoever writes them once `PL-YVP7` is answered:**

- `PL-CNCF` and `PL-PGZF` - **re-decided.** Both turn on
  `simulation_view.py`'s `plot_width_px=max(self._concentration_chart
  .plot_width_px(), self._wash_in_chart.plot_width_px())`, which is the
  milestone's own named mechanism: a column budget read across sibling plots
  that stop being siblings. Checked directly rather than taken from a report.
  Both carry `feature: chart-readout`.
- `PL-WZVZ` - **re-decided on the mechanism, and to be left alone regardless.**
  Its blockers `PL-TH35` and `PL-R1WQ` are v0.6.0 Required scope. But it is
  `safety`-classed, inherited from Gate 1, carries `feature:
  anesthesia-machine`, and `ROADMAP.md`'s gate section writes out by name
  where it sits and why. Re-labelling it would contradict recorded prose as
  well as destroying a feature membership.
- **Everything else swept: not re-decided.** Including three of the six
  candidates the design round named - `PL-V67Q`, `PL-QYBW` and `PL-Z4K6`.
  `PL-Z4K6` is the instructive one: `ROADMAP.md` already reasons that two of
  its three levers wait on planned-milestone item 33 in `v0.7.x`, a different
  and later milestone, and only `WINDOW_SCREEN_FRACTION` is answerable now.
  `PL-1K9G` is hover-selection arithmetic, not placement.

That is 2 confirmed members plus 1 contested, against the 6 candidates the
design round listed - which is the counter-precedent holding. Titles read in a
design round are not evidence, and this is the measurement that says so.

**Why it matters.** A `verify:` command tests for the presence of the fix and
never for the presence of the fault, so an entry whose problem was solved
another way fails forever and reads as outstanding - it is ranked, offered by
`bin/docket next`, and counted into the gate. Without this pass a session
spends a sitting rediscovering that there is nothing to fix, and the gate's own
count overstates what is left. The three entries dropped here were each being
offered as work.

**Done when.** All 168 clearable entries have been read against the tree, not
just the 154 done here: the W1 batch above is swept, whatever it finds is
dropped with a `reason` or corrected in place, and the coverage paragraph no
longer names any entry as unswept. Question 2's verdicts stay recorded rather
than written until `PL-YVP7` settles how they are recorded; that is `PL-YVP7`'s
to close, not this item's.
