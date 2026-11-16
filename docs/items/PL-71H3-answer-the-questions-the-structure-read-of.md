---
id: PL-71H3
title: Answer the questions the structure read of ROADMAP.md's v0.7.0 section left for its author: which choices the owner made, what the Goal table's figures date from, and the terms the section never defines
priority: P2
effort: M
status: done
classes: docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-07
closed: 2026-11-14
pr: 2161
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

**Answers, 2026-11-14.** Each answer names the record it came from. Where no record holds the answer, the answer says which records were searched.

1. **Ratified, not specified.** The owner's answer of 2026-11-10 ("agree with recs", ratified) is recorded in this brief. `ROADMAP.md` now reads "ratified in the scoping round (project owner, 2026-10-25, ratified ...)". What it was chosen over is not recorded: the brief of `PL-LF0P` (the scoping item) does not name an alternative, so the tag says so instead of inventing one.
2. **The 2012 printing of Philip's *Workbook for Gas Man*, read from the owner's copy.** `docs/references/README.md` § "Philip — *Workbook for Gas Man*" gives the title page (dated 2012-05-16, preface dated October 2010, 199 pages), and says the owner supplied it on 2026-09-15 as five section PDFs held in the private corpus. The brief of `PL-LF0P` and `ROADMAP.md` cite Figure 2-1 at printed p. 11 and Appendix E at printed p. 188. No record states the date on which the cited pages were read. The citation in `ROADMAP.md` could add the edition and the route, which is a line-edit change for `PL-YRY3`.
3. **The shares date from `PL-H5DV`'s measurement of 2026-09-23.** The table's fat shares (20% at 60 min, 30% at 180 min) match `PL-H5DV`'s sevoflurane row (reference adult, dial held at 1 MAC, 0.1 s steps, `AgentUptakeSystem.for_agent`). The table's tension figures and muscle shares first appear in commit `817a4d88` (the scoping commit, 2026-10-24 UTC), and no record gives the date they were measured. I did not rerun the model, so the table stays undated in `ROADMAP.md`. The two denominators are the same. "Stored agent" is `core/uptake_system.py` `total_stored_agent_l`, which sums the circuit, the alveoli and the patient's compartments, and the share bar divides by `stored_agent_l`, the snapshot's copy of that sum (`app/controller.py`).
4. **Sevoflurane 7.5 h, isoflurane 7.2 h, desflurane 4.7 h** (`PL-H5DV`'s table, measured 2026-09-23). Item 27's text already says "about five to seven and a half hours". The Goal paragraph could cite the three figures, as a line-edit change.
5. **The two numbers count different things, and no record reconciles them.** `PL-F2NX`'s sweep record says it read "every one of the 24 entries `bin/docket wave` listed as open": 13 that Gate 3 clears, 9 that v0.7.0 clears itself and 2 deferred. I found no record of the "about 81 open entries" figure, and counting the entries then open from the file at `817a4d88` was inconclusive. So the sentence in `ROADMAP.md` should say 24 entries were listed as open by `bin/docket wave`, and not that they were all the open entries on the frozen list. Left for `PL-YRY3`.
6. **Gate 2 gated v0.6.0, Gate 3 gates v0.7.0 and Gate 4 will gate v0.8.0.** A gate freezes when the release before it ships (`ROADMAP.md` § "The cadence"; the timeline rows 6, 8 and 10). Written into the frozen-list paragraph of `ROADMAP.md`.
7. **No.** `PL-0S0V` (entry 7) derives precision for the three run totals by quantity and unit. Its own record (`PL-2881`'s check of 2026-10-27) says `AgentAmount.COMPARTMENT` has no entry in any unit until `PL-2881` derives one, so entry 1 covers the per-compartment amount. "The three totals" are the delivered, exhausted and stored amounts of the accounting panel (`ROADMAP.md` entry 13). The Required scope numbers are not the build order. The order is in the items' `blocked-by` fields: `PL-RNYV` waits on `PL-2881` and `PL-KFTM`, `PL-S79P` waits on `PL-RNYV`, and `PL-B396` waits on `PL-KZ99`, `PL-0S0V`, `PL-2881` and `PL-93B3`. The same sweep found that entry 1 says the specification goes in `docs/INTERFACE.md`, while `PL-2881`'s title says `docs/MODEL.md`. This needs a line check and is not changed here.
8. **No item tracks either, and the visual pass comes after v0.7.0.** I searched `docs/items/` on 2026-11-14 for "carbon dioxide equivalent", "CO2e" and "flush". The only carbon dioxide hit is `PL-B396`, which lists it as a candidate unit, and the flush hits are in items about other topics. Planned item 4 is direct injection only. Both out-of-scope entries now say so. The third part is the owner's answer of 2026-11-10 (above): the row is renamed `v0.7.x — the interface pass` and moved below v0.7.0, and the other places that named it as `v0.6.x` (item 33's placement paragraph and the schematic's out-of-scope entry) are changed.
9. **"A holder" is right and "the one holder" is wrong.** `PL-RCYZ` and `PL-9DF9` both closed on 2026-10-24. In the code, `app/control_record.py` (`elapsed_s: CaseInstant`), `app/chart_time_base.py` (`fit_to_run`, `following_window`, `preview_window`) and `app/bookmarks.py` all hold a `CaseInstant`, so no record is the only one. The frozen-list entry for `PL-RCYZ` (`ROADMAP.md`, the line that says "the one holder") should say "a holder", as the `PL-9DF9` entry does. Left for `PL-YRY3`, because the entries are quoted briefs.
10. **Terms for `PL-YRY3` to define** (sourced where a record exists):
    - View: "a widget that is given what it draws. It does not assume its size, its neighbours, or that it is alone" (`docs/ARCHITECTURE.md`, the routing section).
    - Area: the region of a Workspace that holds a View, with a header that carries the View chooser (`docs/INTERFACE.md`, the area header sections). Confirm wording there.
    - Workspace: a saved arrangement of Areas (`docs/INTERFACE.md` and item 34 in `ROADMAP.md`). Confirm wording there.
    - View chooser: the menu in an Area's header that lists every kind of View (`docs/INTERFACE.md`, "Every area's header has a view chooser").
    - Compare mode: the display of more than one run, which draws one copy of a View per displayed run (`ROADMAP.md` entry 3 of the Required scope).
    - Readouts, Picture, snapshot, capture (the noun), debt item, generator head and its members: no one definition found. Take each from the code or the item that introduced it (`SimulationSnapshot` in `app/controller.py` for snapshot, Gas Man's Figure 2-1 for Picture), or point to `PL-H6T7`'s terms section.
    - Size marks (L), (M) and (S): effort of an item, large, medium and small (`ROADMAP.md`, the Size column paragraph).
    - A date such as "(`safety`, 2026-10-25)": a class of the item and the date it was recorded. No record states this, so confirm against `bin/docket` before writing it.

**Files checked, 2026-11-14.** `ROADMAP.md` (the v0.7.0 section, the timeline, the planned-milestone entry 33, the out-of-scope entries); `docs/references/README.md`; `docs/ARCHITECTURE.md`; `docs/INTERFACE.md` (the view chooser); `docs/items/` entries `PL-LF0P`, `PL-H5DV`, `PL-F2NX`, `PL-0S0V`, `PL-2881`, `PL-CN5S`, `PL-RCYZ`, `PL-9DF9`, `PL-H6T7`, `PL-RNYV`, `PL-S79P`, `PL-B396`; `src/anesthesia_sim/core/uptake_system.py`, `app/control_record.py`, `app/chart_time_base.py` and `app/controller.py` (read only). `docs/MODEL.md`, `docs/INTERFACE.md` and `src/` are unchanged.
