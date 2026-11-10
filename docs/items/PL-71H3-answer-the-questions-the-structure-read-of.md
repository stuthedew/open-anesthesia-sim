---
id: PL-71H3
title: Answer the questions the structure read of ROADMAP.md's v0.7.0 section left for its author: which choices the owner made, what the Goal table's figures date from, and the terms the section never defines
priority: P2
effort: M
status: ready
classes: docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
payoff: The v0.7.0 section a session builds and cuts from records the kind of each owner choice, dates its figures and defines its terms.
verify: grep -qF 'v0.7.x — the interface pass' ROADMAP.md
recurrences: 2026-11-08 PL-NTHF
---

**Problem.** Answer the questions the structure read of ROADMAP.md's v0.7.0 section left for its author: which choices the owner made, what the Goal table's figures date from, and the terms the section never defines

**Source.** The copy editor's structure read of `ROADMAP.md` (chapter reads 35 to 41, the v0.7.0 section), quoted whole in `PL-YNFS`. Slice 5 (`PL-YNFS`) applied the moves and answered from the tree each query the tree answers. These need the author: the record does not hold the answer, so a session would be guessing.

**The questions.**

1. Did the project owner ratify or specify the choice that the schematic and the agent cost readout are each a View of their own? The section says only "The project owner confirmed this in the scoping round", while its two other choices carry the `(project owner, 2026-10-25, ratified, over ...)` tag.
2. Which edition and year of the Gas Man Workbook does the section cite by printed page, and how was it read (route, date)? The Mapleson citation beside it gives its route.
3. What do the Goal table's figures date from, and for which version of the shipped defaults? The table gives no date. Do its "share of stored agent" and the share bar's "share of all the agent the run holds" use the same denominator, that is, does "stored" include the circuit, the alveoli and the blood?
4. How many hours does fat take to overtake muscle for each agent? The Goal says `PL-H5DV` worked them out and gives no figure.
5. The staleness sweep says "Each of the 24 entries open at the time was checked", while the frozen list held about 81 open entries that day. How do the two numbers relate?
6. Which gate number goes with which release? The section names Gate 2, Gate 3 and Gate 4 and never pairs a number with a release.
7. Does `PL-0S0V` (Required scope entry 7) cover the per-compartment amount's precision that `PL-2881` (entry 1) derives? Which are "the three totals" that entry 1 names? Do the Required scope numbers give the build order?
8. Is carbon dioxide equivalent tracked by an item, as its out-of-scope entry says it "waits for a decision of its own"? Is the circuit flush planned anywhere? Does the visual pass (planned-milestone item 33) come before or after v0.7.0?
9. Two frozen-list entries call different records "the one holder" and "a holder" of a case instant `PL-CN5S` left untyped (the control record, `PL-RCYZ`, and the chart time base). Which is right?
10. Terms the section uses and never defines, for the line edit (`PL-YRY3`) to define once where each first appears or to point at a definition: View, Area, Workspace, View chooser, compare mode, readouts, Picture, snapshot, capture (as a noun), debt item, generator head and its members, the size marks (L), (M) and (S), and what a date such as "(`safety`, 2026-10-25)" records. `PL-H6T7` already holds apparatus, lane and generator.

**Why it matters.** v0.7.0 is the next release, and its section is what a session reads to build and cut it. A choice whose kind is unrecorded cannot be reopened on the right bar, and a figure with no date cannot be checked against the model as it now stands.

**Done when.** Each question is answered in this brief, and the answer that belongs in `ROADMAP.md` is written there by the line edit (`PL-YRY3`) or by its own commit.

**Sorted 2026-11-09: whose each question is.** Most are a session's, because the tree or a record answers them:

- Question 2: `docs/references/README.md` § "Philip — *Workbook for Gas Man*" records the edition.
- Questions 3 and 4: `PL-H5DV`'s and `PL-LF0P`'s records, or a rerun of the model at the shipped defaults, dated.
- Question 5: the record of the staleness sweep, `PL-F2NX`.
- Question 6: the timeline pairs them. Gate 2 gated v0.6.0, Gate 3 gates v0.7.0, and Gate 4 gates v0.8.0.
- Question 7: the briefs of `PL-0S0V` and `PL-2881`.
- Question 8, first two parts: on 2026-11-09 no item tracks carbon dioxide equivalent or the circuit flush, and planned item 4 covers injection only. Each out-of-scope entry should say so.
- Question 9: the code that holds the case instant.
- Question 10: wording. It goes in `PL-H6T7`'s terms section or the line edit (`PL-YRY3`).

Question 1 and the third part of question 8 are the owner's. The first is a fact about his own act that no record holds. The second is the order in which features come in.

**Decision needed.**

1. Question 1: did you ratify or specify, in the v0.7.0 scoping round on 2026-10-25, that the schematic and the agent cost readout are each a View of their own? **Recommended:** record it as ratified, like the two tagged choices beside it, since the scoping session put all three to you as recommendations. Nothing a learner sees changes; it sets the bar for reopening the choice later.

2. Question 8: does the visual pass (planned item 33: palette, type scale, spacing) come before or after v0.7.0? The timeline names its row `v0.6.x`, which puts it before, but v0.7.0's Required scope is all closed and the cut waits only on your test drive. **Recommended:** after v0.7.0, renamed `v0.7.x`. The pass then styles the schematic and agent cost Views once, which is the same reason it already runs after item 34. A learner sees the current look through v0.7.0.

**Answered 2026-11-10:** "agree with recs" (project owner, 2026-11-10, ratified). Both answers are the recommendations above.

1. Question 1: the choice that the schematic and the agent cost readout are each a View of their own was ratified on 2026-10-25, over specified. `ROADMAP.md` should tag it `(project owner, 2026-10-25, ratified)` and name what it was chosen over, as it does for the two choices beside it.
2. Question 8, third part: the visual pass comes after v0.7.0, over keeping it before. Its timeline row is renamed `v0.7.x — the interface pass` and moves below v0.7.0. The reason is the one that already put it after item 34: the pass styles each surface once, after the surface exists, and v0.7.0 adds the schematic and the agent cost View. The statement in question 8 that the cut "waits only on your test drive" no longer holds: on 2026-11-10 v0.7.0's debt gate still had 56 entries open.

**Generator check.** One-off: questions from the `ROADMAP.md` structure-read sweep, which a move-only slice left for the author. No mechanism keeps producing them.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** The passages these questions are about were present when Gate 3 froze at `817a4d88`, in their earlier wording: for example "as the project owner confirmed in the same" scoping round, and the Workbook citations. At `needs-decision` the item counts as debt, so it joins v0.7.0's frozen list.
