---
id: PL-756M
title: Three code spans in src/ name symbols that do not exist: plotted_wash_in_ratio in app/wash_in.py (the function is read_wash_in), wash_in_readings in app/run_series.py's DrawnWindow.compartment_fractions docstring and its error message (the function is wash_in_quotients), and ControlChange.value in app/control_timeline.py (found rewriting src/ prose for PL-1K5X)
priority: P3
effort: S
status: done
classes: docs
feature: stale-source-claims
touches: src/anesthesia_sim/app/wash_in.py, src/anesthesia_sim/app/run_series.py, src/anesthesia_sim/app/control_timeline.py
added: 2026-10-25
closed: 2026-10-25
pr: 1817
payoff: every function an interface docstring or error message names can be found in the code
verify: ! grep -qF 'plotted_wash_in_ratio' src/anesthesia_sim/app/wash_in.py && ! grep -qF 'wash_in_readings' src/anesthesia_sim/app/run_series.py && ! grep -qF 'ControlChange.value' src/anesthesia_sim/app/control_timeline.py
---

**Problem.** Three code spans in src/ name symbols that do not exist: plotted_wash_in_ratio in app/wash_in.py (the function is read_wash_in), wash_in_readings in app/run_series.py's DrawnWindow.compartment_fractions docstring and its error message (the function is wash_in_quotients), and ControlChange.value in app/control_timeline.py (found rewriting src/ prose for PL-1K5X)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds `plotted_wash_in_ratio` at `app/wash_in.py` line 137, `wash_in_readings` at `app/run_series.py` lines 233 and 249, and `ControlChange.value` at `app/control_timeline.py` line 269. `ControlChange` in `app/control_record.py` has `previous_value` and `new_value` and no `value` field.

**Why it matters.** A reader who follows a named function to find where a wash-in fraction is formed finds nothing. One of the three names is in an error message, which is the text that is meant to send a developer to the right code.

**Done when.** The three code spans and the error message name symbols that exist (`read_wash_in`, `wash_in_quotients`, and the `ControlChange` field meant). No behaviour changes.
