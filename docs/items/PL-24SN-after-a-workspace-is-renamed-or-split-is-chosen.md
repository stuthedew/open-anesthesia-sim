---
id: PL-24SN
title: After a Workspace is renamed, or Split is chosen from an Area's chooser with the keyboard, the focus leaves the reader's place and lands on the page's scroll area
priority: P3
effort: S
status: ready
classes: defect, ux
feature: interface-design-review
touches: src/anesthesia_sim/app/workspace_tabs.py, src/anesthesia_sim/app/area_layout.py, tests/integration/test_layout_keyboard.py
deferred-from: v0.7.0 - captured after the freeze; keyboard focus only, and no displayed value is wrong
added: 2026-11-22
payoff: after a rename or a Split the focus stays where the reader is working
---

**Problem.** Two keyboard actions leave the focus somewhere the reader did
not put it. The independent review of `PL-B45W` found both on 2026-11-22.

1. After "+" adds a Workspace and the reader types its name, Tab or Return
   leaves the focus on the page's scroll area. On `main` before `PL-B45W` it
   went to a different scroll area. The name editor is built after Tab's
   order is set, and `WorkspaceTabs.focus_order` does not list it.
2. After the reader chooses Split from an Area's chooser with the keyboard,
   the focus goes to the page's scroll area. On `main` before `PL-B45W` it
   went to Start, where Space would start the run.

**Why it matters.** A keyboard user has to tab back to where they were. WCAG
2.2 Success Criterion 2.4.3, Focus Order, asks for an order that preserves
meaning and operability (as cited in `PL-B45W`). Losing the place after an
action is a common keyboard failure.

**What to do.** After a rename ends, give the focus to the renamed tab. After
a Split, give the focus to the new Area's chooser. Test both with real key
presses, as `tests/integration/test_layout_keyboard.py` does.

**Generator check.** Two instances of one cause: an action that removes or rebuilds the focused widget leaves Qt to pick the next focus. No other item records it.

**Done when.** A test renames a Workspace with the keyboard and finds the
focus on its tab, and a test splits an Area from its chooser and finds the
focus on the new Area's chooser.
