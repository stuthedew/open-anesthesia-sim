---
id: PL-88MK
title: dashed_pen leaves Qt's default square cap on 2-3 px pens, so each dash paints one pen width longer and each gap one shorter; three dashed compartment traces look near-solid, and dash is the only channel separating compartments for colour-vision-deficient readers
priority: P1
effort: S
status: ready
classes: defect, safety
feature: replay-findings
touches: src/anesthesia_sim/app/qt_chart.py, tests/integration/test_qt_chart.py
added: 2026-10-24
payoff: each dashed compartment trace paints the dash pattern it is meant to, so a reader with a colour-vision deficiency can still tell the traces apart
verify: grep -q 'FlatCap' src/anesthesia_sim/app/qt_chart.py && grep -q 'def test_each_dashed_pen_paints_its_dash_pattern' tests/integration/test_qt_chart.py
---

**Problem.** dashed_pen leaves Qt's default square cap on 2-3 px pens, so each dash paints one pen width longer and each gap one shorter; three dashed compartment traces look near-solid, and dash is the only channel separating compartments for colour-vision-deficient readers

**Evidence.** Raised on `#578` by the panel's display reviewer and both generalist runs, and marked correct by the blind checker at that merge, which cited Qt's `QPen::setDashPattern` documentation: the cap extends every dash. `pg.mkPen` switches to a round cap only above 4 px. Nobody rendered it, because the container has no display. On `origin/main` on 2026-10-24, `dashed_pen` in `app/qt_chart.py` still builds the pen with `pg.mkPen` and sets a dash pattern, with no cap style.

**Why it matters.** The reviewers computed alveolar [10, 4] at 3 px painting as 13 on and 1 off, and mixed venous and muscle at 2 px as 6/1 and 4/1. The dash pattern is the only channel that separates some compartment pairs whose colours are nearly identical to a reader with a colour-vision deficiency, so that reader can take a value off the wrong trace. The swatch test compares only `dashPattern()` numbers.

**Done when.** `dashed_pen` sets `Qt.PenCapStyle.FlatCap` whenever it sets a dash pattern, and `tests/integration/test_qt_chart.py` has `test_each_dashed_pen_paints_its_dash_pattern`, which paints each pen in `COMPARTMENT_TRACES` and the control mark offscreen and checks the painted run lengths against the pattern times the pen width.

**Reproduced 2026-10-24 on `main` at `91a98348`.** `pen.capStyle()` on a `dashed_pen` pen is `SquareCap`, and `pg.mkPen` sets no cap. Each pen was painted as a horizontal line on a 600 by 20 px white `QImage` with antialiasing off, and the row through the line's centre was scanned. The painted on/off runs, in px, were: alveolar (3 px, intended 10/4) 13/1; mixed venous (2 px, 4/3) 6/1; vessel-rich (2 px, 6/6) 8/4; muscle (2 px, 2/3) 4/1; fat (2 px, 12/4/2/4) 14/2/4/2; the control mark from the theme (1.5 px, 3/5) 5/3. With `FlatCap` set, every trace painted its intended pattern exactly. The control mark goes through `dashed_pen` too, so it has the same fault. No test calls `dashed_pen` by name; the dash assertions in `tests/integration/test_qt_chart.py` compare only `dashPattern()` numbers.
