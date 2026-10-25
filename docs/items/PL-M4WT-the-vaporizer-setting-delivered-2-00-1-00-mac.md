---
id: PL-M4WT
title: The vaporizer setting "Delivered 2.00% (1.00 ×MAC)" sits on the same heading row as "Modelled concentrations: Sevoflurane" and "Model outputs — not measurements.", so a model input reads as an eighth model output, and at low fresh gas flow it can be taken for the inspired concentration
priority: P2
effort: S
status: ready
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/unit/test_dashboard_frame.py, docs/MODEL.md
added: 2026-10-25
payoff: a learner cannot read the vaporizer setting as a modelled concentration or as the inspired concentration
verify: grep -q 'def test_the_delivered_line_is_labelled_as_the_vaporizer_setting' tests/unit/test_dashboard_frame.py
---

**Problem.** `_lay_out_readout_section` adds the substance heading, the interpretation disclaimer, a stretch, `_delivered_text` and `_one_mac_text` to one row (`app/run_view.py`). The line's text is `DELIVERED_LINE_TEMPLATE`, "Delivered {value} ({secondary})" (`app/dashboard_frame.py`). Nothing on it says that it is the dial setting.

**Why it matters.** The gap between the delivered and the inspired concentration at low flow is a core lesson. A setting placed under a "Model outputs" disclaimer can be read as what the patient receives. `docs/MODEL.md` asks the display to keep modelled values apart from other kinds of value. `PL-NWTM` ratified this placement as a placeholder on 2026-10-18. Whether a value is labelled correctly is still a correctness question, so the placement stays the owner's to decide.

**Done when.** The owner has decided where the delivered line sits. Wherever it sits, it is labelled as the vaporizer setting and is not under the "Model outputs" disclaimer. `tests/unit/test_dashboard_frame.py` has `test_the_delivered_line_is_labelled_as_the_vaporizer_setting`.

**Found by.** `PL-TBQS` reviewer replay on #1585, findings r04 F3 and r06 F1, plus `PL-ZWXD`'s fifth #1585 entry. Checked against main on 2026-10-25 by reading the heading row's construction.
