---
id: PL-XV64
title: Every Area corner reaches a screen reader as 'Area corner', every Area border as 'Area border', and the plot controls of two Areas that show the same kind of View share their names, so a screen-reader user cannot tell which Area a control acts on
priority: P3
effort: S
status: untriaged
classes: defect
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/views.py, tests/integration/test_keyboard_focus.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it: the Area menu each corner opens names its Area, so the release waits only on the owner test drive (filed 2026-11-28)
added: 2026-11-28
payoff: a screen-reader user who reaches an Area corner or border hears which Area it acts on
---

**Problem.** Every Area corner reaches a screen reader as "Area corner" and
every Area border as "Area border", so a screen-reader user cannot tell which
Area a corner or border acts on.

A third case has the same cause. `PL-YSFX` names each plot's controls with its
View's title, such as "Time base, Concentrations". The Area menu's "Split left
and right" and "Split top and bottom" fill the new half with the same kind of
View (`AreaLayout.operations`), and each half keeps its own time base and axis
top. So after one split of the Concentrations Area, a screen reader hears two
"Time base, Concentrations" selectors, two "Axis top, Concentrations"
selectors and two pairs of arrow buttons, and cannot tell which plot the next
key press moves. A split Wash-in, Agent cost or Bookmarks Area repeats its
names in the same way. `PL-YSFX`'s test that no two controls share a name
cannot see it, because it builds each kind of View once.

**Why it matters.** The W3C's ARIA Authoring Practices Guide asks for "unique
names for elements with the same role unless the elements are actually
identical" (in its section "Composing Effective and User-friendly Accessible Names",
https://www.w3.org/WAI/ARIA/apg/practices/names-and-descriptions/, read
2026-11-28). With every kind of View on screen, 32 corners and 7 borders that
the keyboard reaches are each told to a screen reader by the same name. Each
corner's description says what the Area menu does, but not which Area it is
for. I suggest P3, because the Area menu a corner opens names its Area.

**Approach.** Give each Area one name for a screen reader: its View's title,
and, where two Areas show the same kind of View, which of them it is. Name
each corner with its Area's name and its place, each border with the two
Areas it divides, and each plot control with its Area's name instead of its
View's title, all through `dashboard_frame.control_name`, so the names still
start with the label shown. The names change when a View is swapped and when
an Area is split, joined or closed. How to tell two Areas of one kind apart in
words is this item's design work: research how screen-reader guidance and
simulation programs name repeated panes before choosing.

**Done when.** The two entries of `SHARED_PURPOSES` in
`tests/integration/test_keyboard_focus.py` are gone, and the test that reads
it still passes, with every kind of View on screen and again after the Area
menu splits an Area of each kind that draws against an axis.

**How it was found.** Building `PL-YSFX`, 2026-11-28: its test that no two
reachable controls share a name found the corners and borders beside the run
and plot controls it fixed. Both independent reviews of `PL-YSFX`'s change
found the split case, 2026-11-28.

