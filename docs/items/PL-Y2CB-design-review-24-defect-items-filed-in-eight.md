---
id: PL-Y2CB
title: Design review: 24 defect items filed in eight weeks name the Area layout module; find the design cause or record that there is none
priority: P2
effort: M
status: ready
classes: planning
feature: hotspot-review
touches: src/anesthesia_sim/app/area_layout.py
deferred-from: v0.7.0 - filed after the gate froze; a design review, which changes nothing a learner sees until a change it recommends is built
added: 2026-11-24
filed-pr: 2317
payoff: the interface files where most simulator defects land get a design change that prevents a group of them, instead of one fix per defect
---

**Problem.** The release cut's reading of where simulator defects land (`PL-36R0`) named `src/anesthesia_sim/app/area_layout.py` fifth on 2026-11-24. Of the items classed defect, safety or science and filed from 2026-09-29 to 11-23, 24 name it in `touches`. The file is 3,313 lines long. The file named beside it most often is `src/anesthesia_sim/app/simulation_view.py`, by 7 items, too few to share a review with the four files `PL-DZHD` takes.

**Why it matters.** Each of these defects was fixed on its own. A file that keeps collecting defects for different reasons usually has a design cause that no single item names. Kim, Zimmermann, Whitehead and Zeller, "Predicting Faults from Cached History", ICSE 2007, found that faults arrive in bursts in the same files. Gall, Hajek and Jazayeri, "Detection of Logical Coupling Based on Product Release History", found that files changed together reveal dependencies the code does not show. Xiao, Cai, Kazman, Mo and Feng, "Identifying and Quantifying Architectural Debt", ICSE 2016, doi:10.1145/2884781.2884825, found in seven projects that the five largest such design faults, each a group of files that change together, held 8% to 25% of the error-prone files and 20% to 61% of the maintenance effort. A declared file is an item's scope, not proof that the defect lay there, so this is a lead.

**What to do.**

1. List the items in the window whose `touches` name this file.
2. Group them by the fact each misread, from its `misread:` field where it has one (4 do), or else by the responsibility each touched, such as splitting sizes, joining Areas or dragging borders.
3. For each group of three or more, say whether one design change would have prevented most of it, such as one exact representation of a border's position in place of compared floating-point values.
4. Recommend each such change with what it costs and what it could break, or record that the defects are unrelated and the file is only large and busy.

**Done when.** The grouping and the recommendation are recorded here. Each recommended change is its own item, put to the owner where it is a major refactor, or this brief says why there is none. Closing this item covers this file in the release cut's reading until three more defects name it after it closed.

**Generator check.** None yet: this item looks for one.
