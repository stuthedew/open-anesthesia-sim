---
id: PL-NC0D
title: The branch selector's width is a constant, FORK_POINT_SELECTOR_WIDTH = 230 px, measured on Inter at 12 and 13 px; the readout panels reserve their width from their own font at runtime (PL-3355), which would hold on a machine drawing another face
priority: P2
effort: S
status: done
classes: defect, ux
feature: presentation-safety
touches: src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
closed: 2026-10-19
payoff: On a desktop with a wider or larger default font, a mark's entry in the branch selector still reads as a mark instead of being cut before the words that say so.
verify: grep -q 'def test_the_branch_selector_fits_its_widest_entry_in_a_wider_face' tests/integration/test_simulation_view.py
---

**Problem.** The branch selector's width is a constant, FORK_POINT_SELECTOR_WIDTH = 230 px, measured on Inter at 12 and 13 px; the readout panels reserve their width from their own font at runtime (PL-3355), which would hold on a machine drawing another face

**Reproduced 2026-10-17** (triage), by setting the application font and
measuring the widest mark entry ("<widest h><widest m><widest s>, on your
mark", built as `test_the_branch_selector_draws_its_widest_entry_whole`
builds it) against the selector's edit field, 196 px of the 230: Inter fits
at 12, 13 and 14 px (162, 175, 188 px) and is cut at 15 and 16 px (203, 216);
DejaVu Sans fits at 12 and 13 px (171, 185) and is cut from 14 px (199, 213,
228). Script: `scratchpad/ui-a/test_repro_nc0d.py`. The app sets no font of
its own, so the selector draws in the platform's default face and size.

**Why it matters.** A desktop whose default face is DejaVu Sans at 14 px, or
any face at a larger accessibility text size, is an ordinary configuration,
so this is reachable - and the part cut is the "on your mark" that tells a
mark's entry from a recorded control change, the distinction the constant's
own comment says the width exists to keep. The clock reading leads the
entry and survives, so no instant is misstated; that is why it is
`defect`/`ux` at `P2` rather than `safety`. The existing test passes here
only because it measures in the container's Inter at 12 px.

**Done when.** The branch selector reserves its fixed width at construction
from its own font's metrics over the widest entry it can hold, frame,
padding and arrow included, as `MetricPanel` does for the readouts
(`PL-3355`), and `theme.FORK_POINT_SELECTOR_WIDTH` is retired. A test,
`test_the_branch_selector_fits_its_widest_entry_in_a_wider_face` in
`tests/integration/test_simulation_view.py`, builds the panel under a wider
application font (DejaVu Sans at 16 px, which cuts the 230 px constant) and
asserts the widest mark entry fits the edit field.

**Regression check 2026-10-19.** `ForkPanel` fixes the selector's width from `dashboard_frame.widest_fork_point_label`, measured in the selector's own font, plus the frame, padding and arrow the style draws around the text field. `theme.FORK_POINT_SELECTOR_WIDTH` is gone. `test_the_branch_selector_fits_its_widest_entry_in_a_wider_face` fails on the code before this change (the `src/` of b1240300, the head of #1675) with `assert 228 <= 196` under DejaVu Sans at 16 px.
