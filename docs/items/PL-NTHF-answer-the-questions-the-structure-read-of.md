---
id: PL-NTHF
title: Answer the questions the structure read of ROADMAP.md's Development pathway and Planned milestones left for their author: Phase 0's decision record, contradictions between catalogue entries, and figures with no date or unit
priority: P3
effort: L
status: done
classes: docs
feature: roadmap-structure
milestone: v0.6.17
touches: ROADMAP.md docs/items/PL-YRY3-line-edit-roadmap-md-section-by-section-with.md
added: 2026-11-08
closed: 2026-11-10
pr: 2086
payoff: The pathway and the planned-milestone catalogue stop contradicting each other, and each figure in them carries its date and unit.
verify: grep -qE '^\*\*Answers' docs/items/PL-NTHF-*.md
---

**Problem.** Answer the questions the structure read of ROADMAP.md's Development pathway and Planned milestones left for their author: Phase 0's decision record, contradictions between catalogue entries, and figures with no date or unit

**Source.** The copy editor's structure read of `ROADMAP.md` (chapter reads 45 to 48, § "Development pathway" and § "Planned milestones"), quoted whole in `PL-M3MV`. Slice 7 (`PL-M3MV`) applied the moves and answered from the tree each query the tree answers; its brief's "What this slice did" lists those. These need the author, because no record holds the answer. Row numbers below are the chapter reads' rows, which `PL-M3MV` quotes.

**The questions.**

1. Who replaced Phase 0 with the debt gate on 2026-08-25, and which item records that decision? No item does, so the record stays in § "Phase 0, which the debt gate replaced". If no item ever recorded it, one should, and the record can then move there.
2. § "Phase 0, which the debt gate replaced" says the queue "holds 48 now". On what date was that count taken?
3. The same section says "The queue holds almost no defects", while its table gives "8 defect-classed items open" on 2026-08-25. Does the first sentence describe the queue when Phase 0 was written?
4. Phase 2 says the display-constants work came first. It landed in `v0.4.11`, after `v0.4.0` had shipped item 25 and the recording half of item 8. First within what?
5. The rule now in `PL-5XG1` says that where the timeline has taken a phase's first half, the phase does not name the release. Phases 2 and 3 name `v0.4.0`, `v0.4.11` and `v0.5.0`. Does the rule cover only work not yet shipped?
6. The known risk asks whether the rework argument still applies to the milestones that the timeline places before the generalization. Which milestones are they, and what does `PL-5XG1`'s count count?
7. § "Planned milestones" says an item stays unspecified until it is promoted. The old text added "(no goal, required scope, or definition of done)", yet unpromoted items state goals and required properties. Is the rule or the entries out of date?
8. The catalogue calls version numbers "after v0.2.3" provisional, while it cites shipped releases to `v0.6.0` and schedules items in `v0.7.0`. After which version are numbers provisional now?
9. Item 24 says six chart traces "cannot be more than 1.48 apart", and item 33 points to it. What quantity is 1.48: a contrast ratio, or a luminance ratio?
10. Item 1's naming decision binds "this milestone and `PL-WZVZ`". After the 2026-09-20 split, is "this milestone" item 1 (the interlocks) or item 40 (the data-file framework)? The survey, design and naming notes stay in item 1 until this is answered.
11. Item 30 derives body composition by default and says it "moves fat uptake", yet weight scales the compartments directly and not through body composition. How does body composition act on the model? Is height an input? It appears only in the declined route.
12. Item 30 says the supported-range refusal applies to an out-of-range body-composition edit, while its covariate paragraph says the response (blocking, logging or both) is open. Which holds?
13. Item 30 says `PL-B9PY` covers two-run rendering, still to come. Item 33 says `PL-B9PY` is the panel decomposition that landed in `v0.4.25`. Which item covers two-run rendering?
14. Item 33's prerequisites and out-of-scope paragraph speak of Flet rendering and the CanvasKit fetch, but the interface moved to Qt in `v0.4.26`. Does the CanvasKit prerequisite still apply, and what does each prerequisite require to land?
15. Item 34 says two of Area, View and Workspace are adopted from Blender. Which one is the project's own term?
16. Item 31 gives no phase or release. Where does it sit?
17. Item 32's "the rest of what a first-time visitor meets" names no list. What is left in item 32?
18. Item 34 says ten of twenty-one Blender views can access the screen. Which Blender version, and on what date?
19. Item 39 opens with "temperature and water content", and its fix covers "temperature, pressure and water content together". Which is the scope?
20. Item 40 says "Internal circuit topology was declined, and item 39 reverses that". Item 39 is about each compartment's gas-phase conditions and never mentions circuit topology. Is the item number wrong, or does item 39 cover topology?
21. The introduction says "None of items 1-43 mix scientific-core and UI/tooling concerns". Item 37 owes a parameter file and a display, and item 43 covers the simulator, its documents and the apparatus. Does the sentence still hold?
22. Item 43 says `PL-K88Z`'s inventory sizes the work "before the row is scoped". Is the row scoped now?

**Why it matters.** § "Development pathway" and § "Planned milestones" are what the owner reads to decide what comes next. Contradictions between entries, and figures with no date or unit, make each entry need checking before it can be relied on.

**Done when.** Each question is answered in `ROADMAP.md`, or in the item that records the decision, and the answer is recorded here.

**Sorted 2026-11-09: whose each question is.** Every question is a session's, because the tree, git history or an item record answers it, or because it is wording:

- Questions 1 to 3: `git log -S` on `ROADMAP.md` finds who wrote each sentence, and when. Where no item records the decision, say so and file one.
- Questions 4 to 8, 10, 15, 19 to 21: wording, or a fact the roadmap or the named item already records (`PL-5XG1` for questions 5 and 6, `docs/interface-provenance.md` for question 15, item 1's account of item 39 for question 20).
- Question 9: `src/anesthesia_sim/app/theme.py` records the 1.48 spacing.
- Questions 13, 14, 17, 18, 22: the item store, the version table and `docs/interface-provenance.md`. `PL-7J96` was dropped and `PL-2QMK` closed, which also feeds `PL-1BVB`.
- Question 16: item 31 has no phase or release, so it is unscheduled intent. Placing it would be a new decision, and nobody has asked for one.
- Questions 11 and 12 concern how item 30 will work. They are recorded as open for item 30's own scoping round, and they are not a question of the roadmap's wording now.

**Generator check.** One-off: questions from the `ROADMAP.md` structure-read sweep, which a move-only slice left for the author. No mechanism keeps producing them.

**Answers 2026-11-10.** Each question is answered in `ROADMAP.md` unless the answer says otherwise.

1. The session that scoped v0.3.0 under `PL-003` retired Phase 0 on 2026-08-25, in commit `53cbecaa`, whose message gives the reasons. `PL-003`'s brief does not mention Phase 0, and no record says whether the owner asked for it. § "Phase 0, which the debt gate replaced" now says so. No new item is filed: the commit is the record, and a decision taken 76 days ago with nothing open behind it needs no item to rank.
2. The count of 48 is from 2026-08-25, the day of that commit, whose message gives "24 open items to 48". The section now dates it.
3. Yes. "The queue holds almost no defects" was in Phase 0's own text (`9c2c68ee`, 2026-08-25). The section now says it describes the queue when Phase 0 was written.
4. The display constants were consolidated in v0.4.11 (`PL-2CS8`), after v0.4.0. Phase 2 now gives the release instead of saying the phase opened with it.
5. The rule applies to work that the timeline has placed and not yet shipped. A shipped release is history, and naming it is the dated history that the same rule asks for. No change to `ROADMAP.md`, because the rule now lives in `PL-5XG1`'s brief.
6. § "The known risk" already says the owner accepted the risk for every release the timeline names. The count the question asked about is no longer in `ROADMAP.md`. It is in `PL-5XG1`'s brief, part 2. No change.
7. The entries are right and the rule was worded too widely. § "Planned milestones" now says an item has no goal, required scope or definition of done until it is promoted, and that an entry may still record its intent and the properties it must have.
8. A row's version number is provisional until its milestone is scoped. The catalogue now says that in place of "after v0.2.3".
9. 1.48 is a contrast ratio: the most that the closest of six traces can differ when each is capped at luminance 0.30 by the 3:1 minimum (`app/theme.py`, and `docs/MODEL.md`, which derives it from 21^(1/5)). Item 24 now says "a contrast ratio of more than 1.48:1".
10. The naming decision binds every surface that names a machine, whichever item builds it. `docs/machine-abstraction.md` § "Question 5" states it for the running interface and the machine's own panel, and item 40's machine-selection surface (`PL-4TWW`) names a machine as much as item 1's interlocks do. Item 1 now says that. The survey, design and naming notes stay in item 1.
11. Open for item 30's scoping. Item 30 now lists it under "Two open questions".
12. Open for item 30's scoping, listed beside question 11.
13. `PL-B9PY` decomposed the run view so two runs could be drawn at once, in v0.4.25, and item 11 shipped comparison on it in v0.5.0. Item 30's paragraph now says both have shipped, so its teaching payoff arrives as soon as it ships.
14. Settled by `PL-1BVB` (#2083). Item 33 says both prerequisites are met, and its figure-export sentence no longer names Flet.
15. View is the project's own term. Blender calls that thing an Editor. Item 34 now names Area and Workspace as Blender's and points at § "The third word is deliberately not Blender's".
16. Item 31 has no phase or release, because it is unscheduled intent. Placing it would be a new decision, and nobody has asked for one. No change.
17. No list of the remaining pieces was ever written: the original text said only that the owner "expects a number of similar human-facing pieces". Item 32 now says the list is made when the item is scoped.
18. Blender 5.3's source at commit `931bb2e7`, read for `PL-FTP5` and recorded on 2026-09-15 (`docs/interface-provenance.md`, "10 of 21 iterate over every area on the screen"). Item 34 now gives the version and date.
19. The scope is temperature, pressure and water content, as item 39's own fix paragraph says. Its opening sentence now names all three.
20. The number is right. `docs/machine-abstraction.md` assigns representing the inlet's position to item 39, because a multi-limb circuit changes the model boundary, and it names item 39 as one of two conditions that reverse the decline. Item 39 now says so.
21. It did not hold. Items 37 and 43 each span the core and the interface or tooling. The catalogue now says so.
22. The `v0.6.x — one source of truth` row is a patch track, so it takes no scope of its own. Item 43 now says the inventory sized the work for that row.
