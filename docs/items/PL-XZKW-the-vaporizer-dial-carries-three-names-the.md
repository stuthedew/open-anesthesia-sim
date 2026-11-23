---
id: PL-XZKW
title: The vaporizer dial carries three names: the slider reads "Delivered sevoflurane", the control record "Delivered agent" and the run's readout "Vaporizer"
status: untriaged
feature: replay-findings
added: 2026-11-23
filed-pr: 2287
---

**Problem.** One control now carries three names on screen. The slider is labelled "Delivered sevoflurane" (`format_delivered_label` in `app/formatting.py`). The record of control changes calls it "Delivered agent" (`CONTROL_INPUT_LABELS` in `app/control_timeline.py`). Since `PL-M4WT`, the run's own line reads "Vaporizer 1.80% (1.00 ×MAC)" (`DELIVERED_LINE_TEMPLATE` in `app/dashboard_frame.py`). A learner who moves the slider sees a value change under another name. Nielsen's fourth heuristic asks that one thing not go by two names (Nielsen J., "10 Usability Heuristics for User Interface Design", Nielsen Norman Group, 1994, reviewed 2024, https://www.nngroup.com/articles/ten-usability-heuristics/), and `PL-M4WT` cites it for the line's place.

**Why the readout says "Vaporizer".** `PL-M4WT` relabelled it so that a learner cannot read the setting as a modelled concentration, or as the inspired concentration at low fresh gas flow. "Delivered" on its own does not say delivered by what, or to where.

**The recorded reason for "Delivered agent".** `app/control_timeline.py` says the record avoids "vaporizer" because a vaporizer's dial is only one machine's way of setting the delivered concentration. That comment dates from `PL-DR1Z` (2026-09-04), before `docs/MODEL.md` described each agent's own vaporizer and began refusing an agent whose vaporizer cannot deliver a setting. The model's input is now the vaporizer dial, as `docs/MODEL.md` § "Units and symbols" says ("The vaporizer dial and MAC are given in percent of one atmosphere").

**Done when.** The slider, the record and the readout name the control the same way, with the agent where a label needs it, such as "Sevoflurane vaporizer" on the slider and "Vaporizer" in the record. The comment in `app/control_timeline.py` gives the current reason. The approved interface strings, `docs/INTERFACE.md` and the tests that pin the three labels are updated together. Found by `PL-M4WT`'s close-out, 2026-11-23. The replay-findings chain does it next, after `PL-M4WT`.
