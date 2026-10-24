---
id: PL-88MK
title: dashed_pen leaves Qt's default square cap on 2-3 px pens, so each dash paints one pen width longer and each gap one shorter; three dashed compartment traces look near-solid, and dash is the only channel separating compartments for colour-vision-deficient readers
status: untriaged
feature: replay-findings
added: 2026-10-24
---

**Problem.** dashed_pen leaves Qt's default square cap on 2-3 px pens, so each dash paints one pen width longer and each gap one shorter; three dashed compartment traces look near-solid, and dash is the only channel separating compartments for colour-vision-deficient readers

**Evidence.** Raised on `#578` by the panel's display reviewer and both generalist runs, and marked correct by the blind checker at that merge, which cited Qt's `QPen::setDashPattern` documentation: the cap extends every dash. `pg.mkPen` switches to a round cap only above 4 px. Nobody rendered it, because the container has no display. On `origin/main` on 2026-10-24, `dashed_pen` in `app/qt_chart.py` still builds the pen with `pg.mkPen` and sets a dash pattern, with no cap style.

**Why it matters.** The reviewers computed alveolar [10, 4] at 3 px painting as 13 on and 1 off, and mixed venous and muscle at 2 px as 6/1 and 4/1. The dash pattern is the only channel that separates some compartment pairs whose colours are nearly identical to a reader with a colour-vision deficiency, so that reader can take a value off the wrong trace. The swatch test compares only `dashPattern()` numbers.

**Done when.** A rendered check (an offscreen grab, as the run-the-app skill allows) shows whether the painted dashes match `COMPARTMENT_TRACES`. If they do not, `dashed_pen` sets `Qt.PenCapStyle.FlatCap` and a test checks painted run lengths.
