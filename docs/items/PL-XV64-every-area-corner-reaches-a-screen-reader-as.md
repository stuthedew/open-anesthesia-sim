---
id: PL-XV64
title: Every Area corner reaches a screen reader as 'Area corner' and every Area border as 'Area border', so a screen-reader user cannot tell which Area a corner or border acts on
priority: P3
effort: S
status: untriaged
classes: defect
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, tests/integration/test_keyboard_focus.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it: the Area menu each corner opens names its Area, so the release waits only on the owner test drive (filed 2026-11-28)
added: 2026-11-28
payoff: a screen-reader user who reaches an Area corner or border hears which Area it acts on
---

**Problem.** Every Area corner reaches a screen reader as 'Area corner' and every Area border as 'Area border', so a screen-reader user cannot tell which Area a corner or border acts on

**Why it matters.** The W3C's ARIA Authoring Practices Guide asks for "unique
names for elements with the same role unless the elements are actually
identical" (in its section "Composing Effective and User-friendly Accessible Names",
https://www.w3.org/WAI/ARIA/apg/practices/names-and-descriptions/, read
2026-11-28). With every kind of View on screen, 32 corners and 7 borders that
the keyboard reaches are each told to a screen reader by the same name. Each
corner's description says what the Area menu does, but not which Area it is
for. I suggest P3, because the Area menu a corner opens names its Area.

**Approach.** Name each corner with its Area's View title and its place, and
each border with the two Areas it divides, through
`dashboard_frame.control_name`, so the names start with "Area corner" and
"Area border" as now.

**Done when.** The two entries of `SHARED_PURPOSES` in
`tests/integration/test_keyboard_focus.py` are gone, and the test that reads
it still passes.

**How it was found.** Building `PL-YSFX`, 2026-11-28: its test that no two
reachable controls share a name found these two groups beside the run and plot
controls it fixed.

