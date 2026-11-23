---
id: PL-XZKW
title: The vaporizer dial carries three names: the slider reads "Delivered sevoflurane", the control record "Delivered agent" and the run's readout "Vaporizer"
priority: P2
effort: S
status: done
classes: ux
feature: replay-findings
touches: src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/control_timeline.py, src/anesthesia_sim/app/dashboard_frame.py
added: 2026-11-23
closed: 2026-11-23
pr: 2287
filed-pr: 2287
tests: tests/unit/test_formatting.py::test_format_delivered_label_names_the_agent_being_delivered
---

**Problem.** One control now carries three names on screen. The slider is labelled "Delivered sevoflurane" (`format_delivered_label` in `app/formatting.py`). The record of control changes calls it "Delivered agent" (`CONTROL_INPUT_LABELS` in `app/control_timeline.py`). Since `PL-M4WT`, the run's own line reads "Vaporizer 1.80% (1.00 ×MAC)" (`DELIVERED_LINE_TEMPLATE` in `app/dashboard_frame.py`). A learner who moves the slider sees a value change under another name. Nielsen's fourth heuristic asks that one thing not go by two names (Nielsen J., "10 Usability Heuristics for User Interface Design", Nielsen Norman Group, 1994, reviewed 2024, https://www.nngroup.com/articles/ten-usability-heuristics/), and `PL-M4WT` cites it for the line's place.

**Why the readout says "Vaporizer".** `PL-M4WT` relabelled it so that a learner cannot read the setting as a modelled concentration, or as the inspired concentration at low fresh gas flow. "Delivered" on its own does not say delivered by what, or to where.

**The recorded reason for "Delivered agent".** `app/control_timeline.py` says the record avoids "vaporizer" because a vaporizer's dial is only one machine's way of setting the delivered concentration. That comment dates from `PL-DR1Z` (2026-09-04), before `docs/MODEL.md` described each agent's own vaporizer and began refusing an agent whose vaporizer cannot deliver a setting. The model's input is now the vaporizer dial, as `docs/MODEL.md` § "Units and symbols" says ("The vaporizer dial and MAC are given in percent of one atmosphere").

**Done when.** The slider, the record and the readout name the control the same way, with the agent where a label needs it, such as "Sevoflurane vaporizer" on the slider and "Vaporizer" in the record. The comment in `app/control_timeline.py` gives the current reason. The approved interface strings, `docs/INTERFACE.md` and the tests that pin the three labels are updated together. Found by `PL-M4WT`'s close-out, 2026-11-23, and by both blind review passes on its pull request.

**Done 2026-11-23**, in `PL-M4WT`'s pull request, because both blind review passes on it asked for the three labels to change together. The slider reads "Sevoflurane vaporizer" (`format_delivered_label`), the record of control changes logs "Vaporizer" (`CONTROL_INPUT_LABELS`), and the new-case notice reads "The desflurane vaporizer starts at that agent's own 1 MAC." (`NEW_CASE_CARRYOVER_TEMPLATE`), which pass 2 found the brief had missed. The slider's label is no longer than before for any agent ("Sevoflurane vaporizer" and "Delivered sevoflurane" are both 21 characters), so its card's width is unchanged. The comment in `app/control_timeline.py` gives the current reason. `docs/INTERFACE.md` says the control has one name, in the paragraph on the vaporizer line. The approved interface strings were regenerated. Files checked in the documentation sweep: `docs/INTERFACE.md`, `docs/MODEL.md`, `docs/VERIFICATION.md` and `README.md`, whose remaining uses of "delivered agent" name the model's quantity, not a label. Tests: `test_format_delivered_label_names_the_agent_being_delivered` in `tests/unit/test_formatting.py` pins the slider label, and the record lines in `tests/unit/test_control_timeline.py` and `tests/unit/test_run_presentation.py` pin "Vaporizer".

**Generator check.** The three names had one cause: the control's name was written out separately in three constants, so renaming one left the others on the old name. That cause is fixed here rather than filed. `VAPORIZER_LABEL` in `app/formatting.py` is now the one record of the name, and the slider label, the record's label, the run's line and the new-case notice all read it.

