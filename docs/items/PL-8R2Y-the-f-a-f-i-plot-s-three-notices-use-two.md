---
id: PL-8R2Y
title: The F_A/F_I plot's three notices use two grammatical forms: 'Not defined: the inspired concentration is too low to divide by.' while the other two read '..., so the ratio is not a wash-in fraction.', and NUREG-0700 guideline 2.7.1-2 asks system messages to use one construction
status: done
feature: interface-design-review
added: 2026-11-27
closed: 2026-11-27
pr: 2342
filed-pr: 2331
tests: tests/unit/test_dashboard_frame.py::test_the_wash_in_trace_draws_nothing_before_agent_reaches_the_circuit, tests/unit/test_dashboard_frame.py::test_the_wash_in_caption_names_no_cause_once_a_washout_empties_the_circuit
---

**Problem.** The F_A/F_I plot's three notices use two grammatical forms: 'Not defined: the inspired concentration is too low to divide by.' while the other two read '..., so the ratio is not a wash-in fraction.', and NUREG-0700 guideline 2.7.1-2 asks system messages to use one construction

**Where.** `src/anesthesia_sim/app/dashboard_frame.py` holds the three notices that take the place of the F_A/F_I plot's "Now:" reading: `WASH_IN_NOT_DEFINED_TEXT` ("Not defined: the inspired concentration is too low to divide by."), `WASH_IN_ELIMINATION_TEXT` ("Alveolar exceeds inspired, so the ratio is not a wash-in fraction.") and `WASH_IN_VENTILATION_STOPPED_TEXT` ("Alveolar ventilation was zero over the last simulated second, so the ratio is not a wash-in fraction."). The first opens with a verdict and a colon. The other two name the condition and then the verdict.

**Source.** NUREG-0700 Rev. 3 (O'Hara, Brookhaven National Laboratory for the U.S. Nuclear Regulatory Commission, July 2020; full text from https://www.osti.gov/servlets/purl/1644018, read 2026-11-27), guideline 2.7.1-2, p. 2-85: "System messages should use consistent grammatical construction." Guideline 1.3.3-4, p. 1-39, asks the same of labels.

**Found by** `PL-49D5`'s sourcing of its caption's wording on 2026-11-27, after the owner's rule that wording is decided from a cited source (`PL-HWZK`).

**Done when.** The three notices share one construction, and the approved interface strings record the new wording.

**Done 2026-11-27.** `WASH_IN_NOT_DEFINED_TEXT` in `app/dashboard_frame.py` now
reads "The inspired concentration is too low to divide by, so the ratio is not
defined." All three notices name the condition, then "so" and the verdict,
which is the form two of them already had. The other two are unchanged. The
comment above the three cites guideline 2.7.1-2. The approved interface
strings and the three tests in `tests/unit/test_dashboard_frame.py` that quote
the notice carry the new wording. `docs/INTERFACE.md` § "F_A/F_I as a
displayed ratio" describes the notice without quoting it, and needed no
change. The meaning is the same, so no clinical meaning changes.
