---
id: PL-KHXB
title: The banner shown when a run reaches the 24-hour supported run length, and the core's refusal message, tell the learner that beyond it the model's omitted metabolism and its fat perfusion dominate the trace, for every agent, though docs/MODEL.md says nothing breaks at hour 25 and only sevoflurane is metabolized enough to matter
priority: P1
effort: S
status: ready
classes: science, ux
feature: supported-run-length-text
touches: src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/core/supported_ranges.py, tests/unit/test_dashboard_frame.py, tests/unit/test_supported_ranges.py
added: 2026-10-25
payoff: the one sentence that explains the 24-hour stop is true for every agent, instead of teaching that metabolism dominates desflurane's kinetics after a day
verify: ! grep -qF 'fat perfusion dominate' src/anesthesia_sim/app/dashboard_frame.py && ! grep -qF 'fat perfusion dominate' src/anesthesia_sim/core/supported_ranges.py && grep -q 'def test_the_supported_limit_notice_says_the_model_is_not_validated_past_the_span' tests/unit/test_dashboard_frame.py
recurrences: 2026-10-25 PL-0889
---

**Problem.** `SUPPORTED_LIMIT_NOTICE_TEMPLATE` (`app/dashboard_frame.py`)
says "Beyond it this model's omitted metabolism and its fat perfusion dominate
the trace". `require_supported_run_length` raises the same sentence
(`core/supported_ranges.py`). The project's own text says the
opposite. The cap is "a declared envelope, not a discovered cliff", and
"nothing breaks at hour 25" (`core/supported_ranges.py`). The error
grows "progressively" (`docs/MODEL.md` § "Supported run length"). Sevoflurane is the binding
agent, and isoflurane and desflurane are barely metabolized. "Its fat
perfusion" also reads as physiology, when the recorded limitation is the
model's fat flow.

**Why it matters.** This is the one sentence that explains the stop. A
learner who reaches the limit with desflurane is told that metabolism
dominates its kinetics after a day, which is wrong pharmacology. The wording
should say the model is not validated past this span because it omits
metabolism and its fat flow differs from measurement.

**Done when.** `SUPPORTED_LIMIT_NOTICE_TEMPLATE` and the message `require_supported_run_length` raises no longer say that metabolism and fat perfusion dominate the trace. They say the model is not validated past this span because it omits metabolism and its fat flow differs from measurement. `tests/unit/test_dashboard_frame.py` has `test_the_supported_limit_notice_says_the_model_is_not_validated_past_the_span`.

**Found by.** `PL-TBQS` reviewer replay on #421, findings r01 F2, r03 F2,
r04 F3 and r06 F2. Checked against main on 2026-10-25 by reading both
strings.
