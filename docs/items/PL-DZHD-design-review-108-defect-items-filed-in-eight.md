---
id: PL-DZHD
title: Design review: 108 defect items filed in eight weeks name the interface's controller, dashboard frame, simulation view or run view, and 37 name two of them; find the design cause or record that there is none
priority: P2
effort: M
status: ready
classes: planning
feature: hotspot-review
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py
deferred-from: v0.7.0 - filed after the gate froze; a design review, which changes nothing a learner sees until a change it recommends is built
added: 2026-11-24
filed-pr: 2317
payoff: the interface files where most simulator defects land get a design change that prevents a group of them, instead of one fix per defect
---

**Problem.** The release cut's reading of where simulator defects land (`PL-36R0`) named these four interface files first on 2026-11-24. Of the items classed defect, safety or science and filed from 2026-09-29 to 11-23, 108 name at least one of them in `touches`, and 37 name two or more:

1. `src/anesthesia_sim/app/controller.py`, 48 items, 4,429 lines.
2. `src/anesthesia_sim/app/dashboard_frame.py`, 48 items, 4,698 lines.
3. `src/anesthesia_sim/app/simulation_view.py`, 39 items, 2,908 lines.
4. `src/anesthesia_sim/app/run_view.py`, 35 items, 2,135 lines.

The pairs named together most often are `controller.py` with `run_view.py` (21 items) and `dashboard_frame.py` with `controller.py` (19).

**Why it matters.** Each of these defects was fixed on its own. A file that keeps collecting defects for different reasons usually has a design cause that no single item names. Kim, Zimmermann, Whitehead and Zeller, "Predicting Faults from Cached History", ICSE 2007, found that faults arrive in bursts in the same files. Gall, Hajek and Jazayeri, "Detection of Logical Coupling Based on Product Release History", found that files changed together reveal dependencies the code does not show. Xiao, Cai, Kazman, Mo and Feng, "Identifying and Quantifying Architectural Debt", ICSE 2016, doi:10.1145/2884781.2884825, found in seven projects that the five largest such design faults, each a group of files that change together, held 8% to 25% of the error-prone files and 20% to 61% of the maintenance effort. A declared file is an item's scope, not proof that the defect lay there, so this is a lead.

**What to do.**

1. List the items in the window whose `touches` name these files.
2. Group them by the fact each misread, from its `misread:` field where it has one (8 do), or else by the responsibility each touched, such as run state, preview, layout or formatting.
3. For each group of three or more, say whether one design change would have prevented most of it: one owner for a shared state, a narrower interface between the controller and a view, or a file split by responsibility.
4. Recommend each such change with what it costs and what it could break, or record that the defects are unrelated and the files are only large and busy.

**Done when.** The grouping and the recommendation are recorded here. Each recommended change is its own item, put to the owner where it is a major refactor, or this brief says why there is none. Closing this item covers these four files in the release cut's reading until three more defects name a file after it closed.

**Generator check.** None yet: this item looks for one.
