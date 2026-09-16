---
id: PL-Y04W
title: Build break-out: an Area taken into its own top-level window, the window lifetime that keeps the main window unclosable while break-outs exist, and the test that every window the application can be left showing carries the invariant display tier
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: L
blocked-by: v0.7.0
classes: safety, anticipated, feature
touches: src/anesthesia_sim/app/, src/anesthesia_sim/layout/, docs/MODEL.md, tests/integration
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
