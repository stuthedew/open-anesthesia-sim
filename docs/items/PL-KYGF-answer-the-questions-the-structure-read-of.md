---
id: PL-KYGF
title: Answer the questions the structure read of ROADMAP.md's v0.6.0 section left for its author: what 'the gate decision' was, which entry decides an Area refused a size, and the definition of done's baseline
priority: P3
effort: M
status: done
classes: docs
feature: roadmap-structure
touches: ROADMAP.md
added: 2026-11-08
closed: 2026-11-16
pr: 2168
payoff: The v0.6.0 record that a session reads to change the layout system answers its own open questions.
verify: grep -qF 'restoreGeometry' ROADMAP.md
---

**Problem.** Answer the questions the structure read of ROADMAP.md's v0.6.0 section left for its author: what 'the gate decision' was, which entry decides an Area refused a size, and the definition of done's baseline

**Source.** The copy editor's structure read of `ROADMAP.md` (chapter reads 27 to 34, the v0.6.0 section), quoted whole in `PL-B6V1`. Slice 6 (`PL-B6V1`) applied the moves and answered from the tree each query the tree answers, and its record lists those answers. These need the author: the record does not hold the answer, so a session would be guessing. `PL-71H3` holds the same kind of question for the v0.7.0 section.

**The questions.**

1. The opening paragraph says "The placement, the split and the gate decision were all recommendations put to the owner and agreed." The placement is the early slot and the split is item 34's halving at break-out. What was "the gate decision"?
2. Required scope entry 5 gives the View contract a clause for "what the container does when an Area cannot honour a size", and entry 8 decides "what a split or a border drag does when the minimum cannot be met". Which entry decides that behaviour? The other should keep a pointer.
3. Entry 1 says the tree gives up some joins, which are refused. Entry 14 says the border-chain query recovers "the one behaviour that the tree gives up compared with Blender's graph". Is that one behaviour or two?
4. The definition of done checks "No learner-visible regression against v0.5.0" and then "Everything a learner could do with two runs on 2026-09-16". v0.5.0 shipped on 2026-09-21. Which baseline applies?
5. Does the definition of done's "A Workspace that names none of those Views still leaves them reachable" cover a Workspace the learner saved, as well as the shipped ones? Are the "two surfaces" of the View contract bullet the "two Views that already exist"?
6. Entry 5 cites "the four clauses that the 2026-09-16 audit added". Which item records that audit?
7. Entry 2 says the 2026-09-16 measurement "is stronger than the form that item recorded". Stronger in what way?
8. Entry 20's Area header paragraph says "Planned-milestone item 33's own argument for the move names the header, but no entry specifies it", while entry 20 specifies the header. What is "the move"? And what does entry 20 decide about the View chooser, the one surface whose paragraph lists no decisions?
9. Is remembering which screen a window was on planned for later, or ruled out? The out-of-scope list now puts it with the windows planned for later.
10. The floating-Areas entry said "So the exclusion is stated with its condition", a sentence about the text that slice 6 cut; planned-milestone item 34 keeps the history before it. Which condition did it mean, beyond "wanted later" and `docs/MODEL.md`'s occlusion rule?

**Why it matters.** v0.6.0's section is the record a session reads to change the layout system. A question it leaves open is answered again by guesswork in every session that needs it.

**Done when.** Each question is answered in this brief, and the answer that belongs in `ROADMAP.md` is written there by the line edit (`PL-YRY3`) or by its own commit.

**Sorted 2026-11-09: whose each question is.** Questions 1 to 8 and 10 are a session's, because a record or the tree answers them. Question 1 is in `PL-NMTF`'s record of the scoping round. Questions 2, 3 and 5 are answered by the code and `docs/interface-provenance.md`. Question 4 is answered by v0.6.0's cut item, `PL-9CS6`, which records what the release was checked against. Questions 6, 7 and 10 are answered by a search of the store and of `PL-B6V1`'s and planned item 34's history. Question 8 is answered by the section itself. Question 9 is the owner's, because it decides whether a feature stays on the roadmap.

**Decision needed.**

Question 9: when break-out into separate windows is built, should the simulator remember which screen each window was on, or is that ruled out? v0.6.0's out-of-scope list gives the danger: a position restored onto a changed set of monitors can put a window where the learner cannot see it. **Recommended:** planned for later with break-out, on one condition. A saved position is restored only onto a screen that is still connected; otherwise the window opens on the main screen. The danger is then a condition on the feature rather than a reason to rule it out, as with floating Areas. Nothing changes for a learner until break-out is scheduled.

**Answered 2026-11-09:** "Do whatever blender does" (project owner, 2026-11-09). So remembering each window's screen is planned with break-out, and it follows Blender. Blender's source (`blender/blender` `main`, read on 2026-11-09) does the following:

1. It saves every window's position and size in the file (`posx`, `posy`, `sizex` and `sizey` on `wmWindow`). It restores them for every window in the window list (`wm_window_ghostwindows_ensure` in `source/blender/windowmanager/intern/wm_window.cc`).
2. It does not check that the monitor a window was on still exists. Its comment says "in practice the window manager will likely move to the correct monitor". On Windows, its platform layer moves and shrinks a new window so that it fits the work area of the nearest monitor (`adjustWindowRectForClosestMonitor` in `intern/ghost/intern/GHOST_WindowWin32.cc`). The macOS and Linux platform layers were not read.
3. A detached single-editor window keeps its size and position in a separate store of recent settings, not in the file (`WM_window_open_temp`). It is placed at that saved position only where the platform supports placement across several monitors. Otherwise it opens centred on the pointer.

The Qt equivalent of point 2 is `QWidget::restoreGeometry`: "If the restored geometry is off-screen, it will be modified to be inside the available screen geometry" (Qt 6 documentation, read on 2026-11-09). This answer replaces the recommendation above, whose check that the screen is still connected Blender does not make. The work for this question is to move "Remembering which screen a window was on" in ROADMAP.md from v0.6.0's out-of-scope list to break-out's plan, record Blender's behaviour above as the design, and note the hazard as the toolkit's correction rather than a check of the project's own.

**Generator check.** One-off: questions from the `ROADMAP.md` structure-read sweep, which a move-only slice left for the author. No mechanism keeps producing them.

**Checked 2026-11-09 against the tree at the freeze (`PL-GW0P`).** The passages these questions are about were present when Gate 3 froze at `817a4d88`: for example "the placement, the split and the gate decision were" all ratified, and "Remembering which screen" in the out-of-scope list. At `needs-decision` the item counts as debt, so it joins v0.7.0's frozen list.

**Answers, 2026-11-16.** Each answer names the record it comes from.

1. **"The gate decision"** was whether v0.6.0 froze a debt gate of its own on
   the day it was scoped. `PL-NMTF`'s "Answered 2026-09-16" section, question
   2, records the answer: no. Gate 2 stayed where the timeline put it, frozen
   when v0.5.0 shipped, and became v0.6.0's gate. That day it was recorded as
   an exception to the rule that a gate freezes when its milestone is
   scoped. `PL-KKRP` replaced that rule on 2026-10-03: a list now freezes on
   the later of the day its milestone is scoped and the day the milestone
   before it ships, so no exception remains (`ROADMAP.md` § "The cadence").
2. **Entry 8 decides it.** `PL-K285` is entry 8's item, and the code cites it
   for the behaviour: `src/anesthesia_sim/layout/sizing.py` ("`PL-K285`
   decided the rules"), `src/anesthesia_sim/app/area_layout.py`, and the
   module docstring of `src/anesthesia_sim/app/view_contract.py` ("A View is
   never drawn below the size it needs", `PL-K285`). `docs/interface-provenance.md`
   § "An Area has a minimum size, and says so when it cannot be given it"
   cites `PL-K285` as well. Entry 5's clause is the fourth question that
   `PL-BNYF`'s audit added to `PL-TH35`, and the contract states the rule
   while citing `PL-K285`. Entry 5 now ends that clause with "Entry 8 decides
   that last behaviour."
3. **Two things.** `PL-3J2P`'s brief, § "What it costs, stated exactly" and the
   paragraph after it, and `docs/interface-provenance.md` give both. A
   splitter tree cannot hold a layout that only a join reaches, such as the
   five-area pinwheel, so that join is refused (entry 1). And where four
   Areas meet, a tree keeps only one of the two crossing borders as one
   handle. The chain query (`LayoutModel.borders()`) recovers that second
   one, which is the behaviour entry 14 means. "Differing exactly once across
   thirty-two" is the one four-way meeting point, in Blender's Shading
   Workspace. Entry 14 now says the tree gives up two things and the query
   recovers one.
4. **v0.5.0.** v0.5.0 shipped on 2026-09-21 (its tag, and `PL-4B1G`, its cut
   item, closed that day). 2026-09-16 is the day v0.6.0 was scoped, when
   v0.5.0's compare mode was 13 of 20 Required-scope items done (`PL-NMTF`'s
   2026-09-17 quote). The bullet already says the check is "against v0.5.0's
   own definition of done". `PL-9CS6` and the done-check it cites
   (`/mnt/project-files/v0.6.0/dod-check.md`, row 9) checked it that way:
   "Every v0.5.0 capability is still tested". The trajectory comparison ran
   against the v0.5.42 tag. The bullet now says "in v0.5.0".
5. **Yes, it covers a Workspace the learner saved.** The guarantee holds by
   construction: the chooser in every Area lists every registered View,
   whatever the Workspace names (`src/anesthesia_sim/app/view_registry.py`'s
   module docstring, `PL-50PZ`). `tests/integration/test_view_chooser.py`
   checks it over the shipped Workspaces and one that is not shipped. **The
   two surfaces are not the two Views.** They are two Areas showing the same
   View for one run: `test_two_areas_of_the_chart_draw_one_frame_sampled_for_the_wider`
   in `tests/integration/test_view_contract.py`, which the done-check's row 8
   calls "two copies of one surface". Both bullets are reworded to say so.
6. **`PL-BNYF`**, the 2026-09-16 audit of the queue against the layout model.
   `PL-TH35`'s section "Area-model audit (PL-BNYF)" records the four clauses.
   Entry 5 now names it.
7. **Stronger in two ways.** The sentence was written in `9982a04f` (#629,
   2026-09-16), where it closed a longer measurement that slice 6 moved to
   `PL-C842`'s brief. `PL-C842` had recorded that the saved state carries
   sizes, a child count and a few flags but not which View is in which pane,
   and that a three-pane state restores into a two-pane splitter. The
   re-measurement added that the same three panes in reverse order save the
   same bytes, and that a two-pane state also restores into a three-pane
   splitter, because `restoreState()` fails only on a bad magic number or a
   newer format. So the state cannot even detect a reordering, and a
   mismatch in either direction passes. The comparison is this session's
   reading of the two records, which no record states in those words. Entry
   2 now says what is stronger.
8. **"The move" is item 33's move to after item 34.** The sentence's first
   form, in `7f970bbe` (#1395, 2026-10-10), read "Named by item 33's own move
   argument; specified by no entry", and item 33's paragraph "It runs after
   item 34 rather than before it" (`PL-PHKP`, 2026-09-16) names the area
   header among the surfaces item 34 brings. So it meant that no entry other
   than entry 20 specified the header, which is why entry 20 took it. The
   sentence now says so. **The chooser:** `PL-RBXL`'s answers of 2026-10-11
   decide a flat menu button showing the current View's title, not a combo
   box, because combo boxes here are settings and choosing a View changes no
   run. Its menu lists every registered View in registry order, with the
   current one checked, and it is as wide as its title. Entry 20's chooser
   paragraph now gives the first two.
9. Answered by the owner, above. See the next paragraph for what was written.
10. **Only the occlusion rule.** The sentence's first form, in `9982a04f`,
    ended with a colon: "the exclusion is stated with its condition: floating
    arrives under `docs/MODEL.md`'s occlusion rule, which binds it without
    being re-argued for it." So "its condition" was the occlusion rule and
    nothing beyond it. The entry still states that condition. Its pointer
    named `docs/MODEL.md`, but the rule moved to `docs/INTERFACE.md` with
    `PL-CTXZ` (§ "Minimum displayed outputs" → "What this list requires once
    the layout is the reader's"). The pointer now names `docs/INTERFACE.md`.

**Done 2026-11-16.** Questions 1 to 8 and 10 are answered above, and the
answers that belong in `ROADMAP.md` are written there: the gate decision in
v0.6.0's opening paragraph, and the sentences in Required scope entries 2, 5,
14 and 20, in two Definition of done bullets, and in the floating-Areas entry.
For question 9, "Remembering which screen a window was on" left v0.6.0's
out-of-scope list. Planned-milestone item 34 now holds a paragraph after
"Break-out unscheduled, 2026-09-26" that records Blender's behaviour as the
design, under the owner's answer. The break-out entry in v0.6.0's out-of-scope
list points to it.

Before writing the paragraph, this session read Blender's source again
(`blender/blender` `main`, 2026-11-16) and the Qt 6 page for `QWidget`. It
confirmed points 1 to 3 of "Answered 2026-11-09", with two corrections to
that reading. First, `wm_window_ghostwindow_ensure` passes a saved position to
a new window only where the platform reports that it can place windows
(`WM_CAPABILITY_WINDOW_POSITION`), and otherwise opens it at position 0, 0.
Second, the comment "in practice the window manager will likely move to the
correct monitor" is about the start position used when there is no startup
file, not about a saved position on a missing monitor. Blender still makes no
check that a saved monitor exists. `adjustWindowRectForClosestMonitor` in
`GHOST_WindowWin32.cc` clamps a new window's size and position to the work
area of the nearest monitor, as recorded. Qt's documentation says of
`restoreGeometry`: "If the restored geometry is off-screen, it will be modified
to be inside the available screen geometry."

Files checked in the docs sweep: `ROADMAP.md` (v0.6.0's section, planned-milestone
items 33 and 34, § "The cadence"), `docs/interface-provenance.md`,
`docs/INTERFACE.md` § "Minimum displayed outputs", the briefs of `PL-NMTF`,
`PL-9CS6`, `PL-B6V1`, `PL-TH35`, `PL-3J2P`, `PL-C842` and `PL-RBXL`, and
`src/anesthesia_sim/app/view_contract.py`, `view_registry.py` and
`layout/sizing.py`.
