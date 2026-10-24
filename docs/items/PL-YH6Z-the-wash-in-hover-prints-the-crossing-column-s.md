---
id: PL-YH6Z
title: The wash-in hover prints the crossing column's F_A/F_I above 1 under the label 'Wash-in F_A/F_I', a value app/wash_in.py classes as elimination and refuses to show as wash-in
priority: P1
effort: S
status: ready
classes: defect, safety
feature: replay-findings
touches: src/anesthesia_sim/app/chart_frame.py, tests/unit/test_chart_frame.py
added: 2026-10-24
payoff: the wash-in hover never prints an F_A/F_I above 1 as a wash-in fraction, so a learner is not taught a wash-in past completion
verify: grep -q 'def test_the_wash_in_hover_withholds_the_ratio_at_an_elimination_terminus' tests/unit/test_chart_frame.py
---

**Problem.** The wash-in hover prints the crossing column's F_A/F_I above 1 under the label 'Wash-in F_A/F_I', a value app/wash_in.py classes as elimination and refuses to show as wash-in

**Evidence.** All three panel reviewers and both generalist runs raised this on `#578`, and the blind checker reproduced it at that merge: a default sevoflurane run with the vaporizer shut at 600 s hovers its terminus dot as "Wash-in F_A/F_I ... 1.03", while `read_wash_in` returns elimination for the same state. On `origin/main` on 2026-10-24, `format_wash_in_hover` in `app/chart_frame.py` still prints `format_wash_in_ratio(stretch.ratios[index])` with no wash-in test visible in the function. It was not re-run on `main`.

**Why it matters.** `docs/MODEL.md` § "F_A/F_I as a displayed ratio" and rule 2 of `app/wash_in.py` say a quotient above 1 is not a wash-in fraction. The crossing column is drawn only so the line meets the reference, and the hover turns it into a printed number that teaches a wash-in past completion, at the dot a reader is most likely to point at.

**Done when.** `format_wash_in_hover`, and `format_compared_wash_in_hover` where it has the same fault, print no F_A/F_I number for a column that `read_wash_in` classes as elimination, and `tests/unit/test_chart_frame.py` has `test_the_wash_in_hover_withholds_the_ratio_at_an_elimination_terminus`, which hovers the terminus column of the scenario above.

**Reproduced 2026-10-24 on `main` at `91a98348`.** Default sevoflurane at 2.0%, 0.1 s steps, vaporizer to 0 at 600 s, run on for 1200 s, chart assembled at 900 px. The terminus of the stretch with `ends_above_equilibrium` set, at 630.0 s, hovers as "Modelled sevoflurane · 10m30s / Wash-in F_A/F_I (alveolar / modelled circuit) / 1.01", while `read_wash_in` returns `WashInReading(domain=ELIMINATION, plotted_ratio=None)` for the same column. The printed number depends on the column width: 1.00 (ratio 1.00002) after 300 s at 900 px, 1.02 after 3000 s at 900 px, and 1.03 after 300 s at 100 px, which is the reported value. `nearest_wash_in_point`, the real pointer path, returns the same readout. `format_wash_in_hover` is at lines 1226 to 1255 of `app/chart_frame.py` and prints the ratio at line 1253. `format_compared_wash_in_hover`, at line 1399, probably has the same fault and was not tested. `tests/unit/test_chart_frame.py` lines 450 to 472 already build this scenario.

**Route decided 2026-10-24 at triage: withhold the number.** The brief offered two routes, withholding the number or labelling the column as the reference crossing. Withholding follows rule 2 of `app/wash_in.py` and `docs/MODEL.md` § "F_A/F_I as a displayed ratio", which already refuse to show a quotient above 1 as a wash-in fraction, so it adds no new display rule. A label for the crossing column would be new wording on screen. Either is correct; this is a placeholder choice under the 2026-10-18 rule on look and wording, and a session building it may revisit it.
