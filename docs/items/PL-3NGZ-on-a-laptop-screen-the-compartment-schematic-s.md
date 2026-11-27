---
id: PL-3NGZ
title: On a laptop screen the compartment schematic's labels can be in view while the lines that qualify them have scrolled away: the run's name while two runs are compared, the line saying what the shares are of while a container is above the scale, and the tension's unit
priority: P1
effort: M
status: ready
classes: defect, safety
feature: presentation-safety
touches: src/anesthesia_sim/app/qt_schematic.py, docs/INTERFACE.md, tests/integration/test_compartment_schematic_view.py
added: 2026-11-27
filed-pr: 2326
payoff: a learner comparing two runs on a laptop never sees a run's tensions, amounts or shares without its name, the tension's unit or what the shares are of
reenters: PL-P83G
---

**Problem.** On a laptop screen the compartment schematic's labels can be in view while the lines that qualify them have scrolled away: the run's name while two runs are compared, the line saying what the shares are of while a container is above the scale, and the tension's unit

**Why it matters.** A label read without its qualifier can be misread. While
two runs are compared, a learner can see one run's tensions, amounts and
shares with neither run's name on screen, and the two runs can differ a lot:
in one scroll position a reviewer saw "Circuit 44%" and "Fat 4%" for the
first run while the second run read circuit 79% and fat under 1%. While a
container is above the scale, the line that says the shares are of all the
agent at this instant can be below the Area's edge. The tension's unit, % of
1 atm, is printed only in the scale caption, which scrolls on this screen.

**What was measured** (the review of `PL-8PL4`, 2026-11-27, Maintenance
Workspace at 1366 by 768, offscreen platform font):

1. With a branch open, the schematic's Area is about 110 px tall and scrolls.
   For each run there are about 24 scroll positions, of 636, at which its
   labels and bars are wholly in view and no run name is. The bars were in
   view without their compartment names at 142 positions; the single bar on
   `main` before `PL-8PL4` was in view without its key at 97. With one run
   neither happens.
2. With one run and the circuit above the scale (sevoflurane at 8%), two of
   three measurements found the share caption below the Area's edge, and one
   found it in view. `docs/INTERFACE.md` says it can scroll.
3. `PL-8PL4` put the share caption directly under the containers, so with
   one run and nothing above the scale it is in view at every screen size
   the lesson test checks.

[superseded 2026-11-27: the triage pass placed this item on v0.7.0's frozen list, so it is fixed now rather than in `PL-9WDN`; see **Placed 2026-11-27** below] **Direction.** Each qualifier belongs where it cannot scroll away from the
values it qualifies: inside the canvas beside the labels, or in a line that
stays at the top of the Area while the content scrolls. That is a layout
decision for item 33's interface pass (`PL-9WDN`), which writes the design
language first.

**Done when** no scroll position at 1366 by 768 shows a run's labels without
its name while runs are compared, or a share without what it is a share of,
and a test scrolls through every position to check it.

**Placed 2026-11-27 (triage).** Classed `safety`, because `CLAUDE.md`'s safety-critical standard counts a value shown without its run, its unit or what it is a share of as a presentation failure. The hazard is live on `main` at `f653c1eb`, where `PL-8PL4` merged as #2326 with the measurements above taken on its branch. A `safety` entry with a live hazard re-enters the current gate and cannot be deferred (`ROADMAP.md` § "Deferring to the next gate"), so this item joins v0.7.0's frozen list and is fixed before the release rather than in `PL-9WDN`'s interface pass. Where each qualifier sits is a placement choice. The building session picks one of the two the direction names, records it as a placeholder, and `PL-9WDN`'s design language may restyle it later.

**Generator check.** A re-entry of `PL-P83G` at sibling sites. Both are a qualifier drawn in a different widget from the values it qualifies, inside an Area that scrolls, so the two can separate. `PL-P83G` fixed the share bar's segment names. The run's name, the share caption and the tension's unit are the same mechanism, and this item was filed by the same pull request (#2326). Two items are not a generator.
