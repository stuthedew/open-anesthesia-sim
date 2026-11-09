---
id: PL-DPY1
title: docs/MODEL.md says the main window cannot be closed while another window is open, then that closing it closes the others; a reader cannot tell which is the requirement for break-out windows
priority: P2
effort: S
status: untriaged
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-05
payoff: whoever builds break-out windows has one behaviour to build and test for keeping the per-substance values on screen
verify: ! grep -qF 'closed while any other window is open' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "What this list requires once the layout is the reader's" says that the main window cannot be closed while another window is open, and later that closing it closes the others. A reader cannot tell which is the requirement for break-out windows.

**Checked 2026-11-09:** § "What this list requires once the layout is the
reader's" still says the main window "cannot be closed while any other window
is open", and in the next sentence that "Closing the main window closes the
others" (lines 6658 to 6660). The passage specifies break-out windows, which
`ROADMAP.md` places outside v0.6.0.

**Why it matters.** Both sentences serve one safety requirement: the
per-substance tier stays on screen while any window shows a run. Either
mechanism meets it, but a contributor who builds break-out windows reads two
incompatible behaviours and cannot tell which one a test should hold.

**Done when.** The passage states the requirement once (the per-substance tier
is in view whenever any window of the application is open) and one mechanism
for it. **Recommended:** closing the main window closes the others. It never
refuses a reader's action, and it is how Blender treats its main window, whose
window system the layout adopts. Record the choice as a placeholder until
break-out windows are built.

**Generator check.** One-off: a finding from the `docs/MODEL.md`
structure-read sweep of 2026-11-05.

**Present at the Gate 3 freeze (checked 2026-11-09).** The passage this item
fixes was already in its file at `817a4d88`, the commit that froze Gate 3, so
under ROADMAP.md § "The gate is a snapshot, not a moving target" the item
joins v0.7.0's frozen list rather than being deferred by its capture date.
