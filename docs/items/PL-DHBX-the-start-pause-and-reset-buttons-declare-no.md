---
id: PL-DHBX
title: The Start, Pause and Reset buttons declare no colour, so their labels are illegible under macOS Dark appearance
priority: P2
effort: S
status: done
classes: defect, ux
feature: platform-palette
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/run_view.py, tools/contrast_check.py, tests/integration/test_qt_widgets.py, tests/integration/test_simulation_view.py
added: 2026-09-17
closed: 2026-09-17
verify: uv run pytest tests/integration/test_simulation_view.py -q && grep -q 'def test_every_transport_button_declares_its_own_foreground' tests/integration/test_simulation_view.py
---

**Problem.** The Start, Pause and Reset buttons declare no colour, so their
labels are illegible under macOS Dark appearance.

Reported by the project owner on 2026-09-17 against `0.4.26+gd67e06df`, with
the screenshot: the three transport labels were absent while every control
beside them - the agent selector, the playback selector, the status word - drew
correctly. Their second message isolated it: *"It only occurs in mac 'dark'
appearance mode. When I switch to light, the text returns."*

**The mechanism, measured rather than inferred.** `RunView` built the three as
bare `QPushButton`s and set no stylesheet on them, so their label colour came
from Qt's palette `ButtonText` role. That role follows the **host appearance**:
Qt 6.11's `QStyleHints.colorScheme` documentation states the palette "follows
the system's default color scheme (also known as appearance), and changes when
the system color scheme changes". Under macOS Dark it is near-white - while
every surface this interface draws stays the light theme's `PANEL` `#FFFFFF`
and `BACKGROUND` `#F4F7FA`, which are hard-coded. White label, white surface.

Confirmed in this container by driving the palette directly rather than by
reading the source: with `ButtonText` set to `#FFFFFF` and `Button` to
`#323232`, a bare button rendered its box at `#454545` - the palette's value -
and the same button carrying `transport_button_stylesheet` rendered it at
`#FFFFFF`. A tree walk of the whole dashboard found the three buttons were the
**only** text-bearing controls left undeclared; every label goes through
`styled_label`, and both selectors through `selector_stylesheet`, which exists
for this exact reason and says so.

**Why it matters.** This is the simulator's entire run-control surface, and it
was unreadable for any reader whose machine is in Dark appearance - which is
the default on a Mac after dusk under the system setting. Nothing in the
repository could have caught it: `tools/contrast_check.py` measures declared
pairs, and an undeclared control declares nothing to measure, so the report
read `24 of 24 ... 0 known shortfalls` while three controls were invisible.
That gap is `PL-4L49`.

It also sat inside a scope note that had just been written. `PL-NGF7`
(2026-09-16) scoped disabled states out of the contrast check and named "the
start, pause and reset buttons" as plain controls covered by WCAG 2.2 SC
1.4.3's exemption for text in an *inactive* component. The exemption is real
and the decision stands - but these buttons were undeclared in **both** states,
and only the disabled half is exempt. The enabled half is squarely inside SC
1.4.3.

**Done when** the three transport buttons declare their own foreground and
background, the pair is measured by `tools/contrast_check.py`, and a test holds
both the colours and `RunView`'s application of them.

---

**Done, 2026-09-17.** `transport_button_stylesheet` in
`src/anesthesia_sim/app/qt_widgets.py` declares `PANEL` fill, `INK` label and a
`MUTED` 1px edge, and `RunView` applies it to all three buttons. Both pairs
were already in `REQUIREMENTS` - `INK` on `PANEL` for the label, `MUTED` on
`BACKGROUND` for the edge against the row behind it - so the change extends
those two entries to name the new sites rather than adding a colour;
`contrast_check` reports `24 of 24 ... 0 errors` with the buttons inside it.

**Scoped to `:enabled`, deliberately.** The disabled state is left whole to the
platform - box and label together - which keeps `PL-NGF7` intact rather than
reopening a decision made the day before. Declaring the fill without the label
would have been worse than declaring neither: a white box under a foreground
still following the dark scheme. Whether the disabled half should be declared
too is not answered here; it is the narrower half of `PL-KRZW`.

**Two tests, each run both ways.**
`test_a_usable_transport_button_draws_the_theme_rather_than_the_host_palette`
renders a styled and a bare button under a stand-in dark palette and holds the
styled one to `PANEL`; the bare one is rendered beside it so the test cannot
pass vacuously if the platform plugin ignores the palette. No pixel lands
exactly on `INK` - the glyphs are antialiased - so the label is identified by
which declared colour its darkest pixel is nearest.
`test_every_transport_button_declares_its_own_foreground` holds `RunView` to
applying it, which is the half a test of the helper alone would not catch:
with the helper present and the `run_view.py` call removed, it fails.

**What this could not verify, and who can.** macOS is not reachable from the
container and the `offscreen` platform plugin ignores `setColorScheme`
entirely, so the mechanism was proven through the palette rather than on the
machine that showed it. The fix does not depend on the platform - a stylesheet
`color:` overrides the palette everywhere Qt runs - but the confirmation is the
project owner's to give, in Dark appearance.

**Considered and rejected: declaring the colour scheme instead.**
`QGuiApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)` in
`app/main.py` is one line and would have fixed the whole class - scrollbars and
splitter handles included. Qt 6.11's own documentation rules it out as the
*guarantee*: "doing so is a hint to the system, and overriding the color scheme
is not supported on all platforms." A legibility guarantee for the run controls
cannot rest on a hint the toolkit says may be ignored. It remains worth
deciding on its own merits, which is `PL-KRZW`.
