---
id: PL-KRZW
title: Decide what the interface does under a dark system appearance, now that every colour it declares is a light-theme value
priority: P2
effort: M
status: needs-decision
classes: defect, ux
feature: platform-palette
touches: src/anesthesia_sim/app/main.py, src/anesthesia_sim/app/theme.py, docs/MODEL.md
added: 2026-09-17
---

**Problem.** Decide what the interface does under a dark system appearance, now
that every colour it declares is a light-theme value.

`PL-DHBX` fixed the instance - three transport buttons taking their labels from
the host palette. The question it did not answer is the general one: this
interface hard-codes a light theme (`PANEL` `#FFFFFF`, `BACKGROUND` `#F4F7FA`,
`INK` `#243B53`) and never tells Qt so, while Qt's palette follows the system
appearance by default. The two disagree on every machine set to Dark, and the
interface currently wins only where a colour happens to be declared.

**Why it matters.** Two things ride on the answer, and they pull in different
directions.

The first is that the whole contrast apparatus is computed against those two
light surfaces. `tools/contrast_check.py`'s 24 requirements, `docs/MODEL.md` §
"Color contrast, and the standard this interface is held to", and the
dichromacy floors the six chart traces were re-picked against are all measured
on `PANEL` and `BACKGROUND`. If the interface ever rendered dark, every one of
those measurements would be against a surface not on screen - which is a
safety-apparatus failure rather than an aesthetic one. That argues for
declaring the light scheme and being done.

The second is that declaring it is not guaranteed to work.
`QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)` exists
since Qt 6.8, and Qt 6.11's own documentation says: "doing so is a hint to the
system, and overriding the color scheme is not supported on all platforms."
So it cannot be the mechanism a legibility guarantee rests on - which is why
`PL-DHBX` declared the button's colours instead. It can still be worth setting
as a belt-and-braces measure that also covers the chrome no stylesheet reaches:
scrollbars, splitter handles, tooltips, native dialogs.

**Decision needed.** Does the application declare a Light colour scheme to Qt,
leave the host appearance alone as it does today, or grow a second palette and
support dark appearance properly? The three are set out below with what each
costs; the recommendation is the first.

**The three options, as they stand.**

1. **Declare Light and keep declaring every colour.** The hint covers the
   chrome where the platform honours it; the declared colours cover everything
   that carries meaning whether or not it does. Costs a macOS reader in Dark
   appearance a light-appearing window.
2. **Declare nothing and keep declaring every colour.** Today's state after
   `PL-DHBX`. The chrome follows the host and the content does not, which is
   the mixed appearance in the `PL-DHBX` screenshots.
3. **Support dark appearance properly.** A second palette, every requirement
   re-measured against it, the six traces re-picked against dark surfaces under
   four vision models, and `docs/MODEL.md` restated for both. This is interface
   work at the scale of the `v0.5.x` interface-pass row, not a fix.

**Recommendation to put to the project owner: option 1**, with option 3 raised
as a roadmap line rather than an item. The apparatus reason is the strong one -
a contrast table measuring surfaces that are not on screen is worse than a
window that ignores the system appearance - and option 3 cannot be done
cheaply or half-way without producing exactly that.

**What this is not.** Not a question about the transport buttons, which are
fixed. Not blocked on the interface pass being scoped: the decision is
answerable now and options 1 and 2 are both one line or none.

**Done when** the project owner has chosen, the choice is recorded in
`docs/MODEL.md` § "Color contrast, and the standard this interface is held to"
with the reasoning, and - for option 1 - `app/main.py` declares the scheme and
a test holds it.
