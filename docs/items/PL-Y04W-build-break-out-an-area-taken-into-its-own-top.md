---
id: PL-Y04W
title: Build break-out: an Area taken into its own top-level window, the window lifetime that keeps the main window unclosable while break-outs exist, and the test that every window the application can be left showing carries the invariant display tier
priority: P2
effort: L
status: dropped
classes: safety, anticipated, feature
feature: interface-areas
touches: src/anesthesia_sim/app/, src/anesthesia_sim/layout/, docs/MODEL.md, tests/integration
blocked-by: v0.7.0
added: 2026-09-16
closed: 2026-09-26
reason: Break-out came off the timeline on 2026-09-26 (project owner: wanted eventually, not soon; PL-V1Y7), so no release builds it, and blocked-by: v0.7.0 would have released it once the schematic, v0.7.0 since that day, was scoped. An eventual feature is intent in ROADMAP.md planned-milestone item 34, which cites this brief for its Qt transient-parent measurement; the rule it would enforce stays in docs/MODEL.md § Minimum displayed outputs, and its hazard is not live, since nothing creates a second top-level window. Priority moves to P1 on the drop because the P2 band only waits while an anticipated safety item is blocked, as with PL-TBMX.
---

**Problem.** Build break-out: an Area taken into its own top-level window, the window lifetime that keeps the main window unclosable while break-outs exist, and the test that every window the application can be left showing carries the invariant display tier

**Why it matters.** This is planned-milestone item 34's second half and the
whole of the v0.7.0 row. `PL-W54S`'s answer, recorded in `docs/MODEL.md` on
2026-09-16, is what it has to enforce: every top-level window carries the
invariant display tier and the name of the run it shows, and the per-substance
tier lives once in a main window that cannot be closed while any other is open.

**The obvious Qt construction does the opposite of what that needs**, measured
on PySide6 6.11.2 / Qt 6.11.2 on 2026-09-16. A secondary window built as
`QWidget(main, Qt.Window)` is top-level but has `main`'s window as its
*transient parent*, and Qt counts only *primary* windows - top-level, no
transient parent, `Qt.WA_QuitOnClose` - when deciding the last window has
closed. So closing the main window emits `lastWindowClosed` and quits the
application while the break-out window is still visible. A parentless secondary
window does not have that property but then has no relation to the main window
at all. Neither is the rule; the rule is the main window vetoing its own close
while break-outs exist, and it has to be built rather than inherited.

**Done when.** A reader can take an Area into its own top-level window, itself
a full window with its own Areas; every such window carries the invariant tier
and names its run; the main window refuses to close while any other is open and
closing it closes them; and a test drives break-out and asserts that every
window the application can be left showing carries the invariant set, including
after the last non-broken-out window is closed.

*Scope.* `ROADMAP.md` timeline row 9, v0.7.0 - the second screen. Not yet
scoped; this item is what that scoping round will build from.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-B6V1`).** `ROADMAP.md`'s § "Completed: v0.6.0 - the layout is the reader's" -> "Debt gate: the frozen list" recorded this item's deferral to Gate 3 in the paragraph below, written at the freeze. "This section" is that frozen-list section, and "its own group above" is a group of deferred entries retired on 2026-10-12 (`PL-8QMD`). Its v0.7.0 is the break-out row as the timeline then stood; v0.7.0 has been the schematic since.

> **`PL-Y04W` is deferred to Gate 3 on § "The cadence" beat 3's terms, and the three conditions are met here rather than assumed.** It is the break-out build item. It covers an Area taken into its own top-level window, and the window lifetime that keeps the main window unclosable while break-outs exist. It also covers the test that every window the application can be left showing carries the invariant display tier. "The timeline" gives break-out to row 9, v0.7.0. The item comes to this gate because it is `safety`-classed, not because it is ordinary debt. So requiring it before v0.6.0 begins would require v0.7.0's own build item to close first, and no order satisfies that. The three conditions are met as follows. This section says that the entry is deferred, and why. The deferral names **Gate 3**, which freezes when v0.6.0 ships and clears before v0.7.0's implementation begins. v0.7.0 is the release that builds it. The entry stays written on this list, in its own group above, rather than being removed. **Its hazard is not live, read against the tree rather than asserted**. Nothing under `src/anesthesia_sim/` creates a second top-level window. `inert_splitter` at `src/anesthesia_sim/app/qt_widgets.py` has its handles disabled, so no Area can be taken out of one. So no window today could be left showing without the invariant display tier. Its `anticipated` class already records that. v0.6.0's Goal section calls it a violation pre-loaded rather than present.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-B6V1`).** The next paragraph, which records this item's drop and stays in `ROADMAP.md`, followed it with these sentences about the paragraph above.

> The paragraph above is left as the freeze wrote it. Its v0.7.0 is the break-out row as it then stood, and v0.7.0 has been the schematic since. The group of its own that it names was retired on 2026-10-12 with the other deferral groups. The entry now stays on the list with the others (`PL-8QMD`).

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-M3MV`).** `ROADMAP.md`'s § "Planned milestones" carried this paragraph under item 34, "Blender's window management as the model for the interface". In it, "this item" means item 34, "here" means that entry, "this file" means `ROADMAP.md`, and "above" and "below" point within `ROADMAP.md` as it then stood. Item 34 keeps the decision, and v0.6.0's Required scope entries 1 and 7 hold what keeps break-out possible.

> *Break-out unscheduled, 2026-09-26* (project owner, 2026-09-26: "This is something I don't want to rule out doing eventually. Not something that needs done soon."). Break-out remains this item's second half and is still wanted, but it has no row on § "The timeline". Its row, "the second screen", came off the timeline. As a consequence, the schematic (item 27) moved back to v0.7.0, and multi-substance (items 6 and 7) moved to v0.8.0 (`PL-V1Y7`). Break-out is placed when the owner asks for it, as any catalogue entry is. **What keeps it possible stays in v0.6.0, unchanged.** First, the saved layout root carries a set of windows from version 1 (Required scope entry 1, `PL-HJPY`). A root that gained a set of windows later would need a schema migration against every Workspace a learner has saved. Second, the unconditional region is built in the per-window shape settled above (entry 7, `PL-W54S`). Break-out's build item, `PL-Y04W`, was dropped the same day, because an eventual feature is recorded here as intent, rather than as an item in the queue. The item's brief keeps the measurement that the build will need first. That measurement was taken on PySide6 6.11.2 / Qt 6.11.2 on 2026-09-16. A secondary window built as `QWidget(main, Qt.Window)` has `main` as its transient parent. Qt counts only primary windows when it decides that the last window has closed. So closing the main window quits the application while the broken-out window is still visible. The rule the build must satisfy is `docs/MODEL.md` § "Minimum displayed outputs" -> "What this list requires once the layout is the reader's".
