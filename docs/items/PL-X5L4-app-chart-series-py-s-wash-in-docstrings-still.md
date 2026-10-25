---
id: PL-X5L4
title: app/chart_series.py's wash-in docstrings still say 'sample' for a drawn column and reason from the 0.1 s step where the column spacing now governs
priority: P3
effort: S
status: done
classes: docs
feature: core-domain-language
touches: src/anesthesia_sim/app/chart_frame.py, src/anesthesia_sim/app/chart_time_base.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/wash_in.py
added: 2026-09-14
closed: 2026-10-24
pr: 1766
verify: ! grep -qE 'draws recorded samples|newest recorded sample|newest sample' src/anesthesia_sim/app/chart_frame.py src/anesthesia_sim/app/chart_time_base.py src/anesthesia_sim/app/controller.py
---

**Problem.** app/chart_series.py's wash-in docstrings still say 'sample' for a drawn column and reason from the 0.1 s step where the column spacing now governs

**Widened 2026-09-14, while merging `origin/main` into the sweep branch.** The
same word survives outside the wash-in docstrings, and the chart port
(`PL-G59B`) carried one instance into a new file: `app/chart_series.py:173`
and `:280` say a trace "draws recorded samples" where it draws the states of
a `DrawnWindow`; `app/chart_time_base.py:250` documents `newest_sample_s` as
"the newest recorded sample"; and `app/chart_frame.py:125` explains a
constant by what the chart did "while the chart selected recorded samples",
which is history and reads as such. The first three are the same rot as the
title; the fourth is fine and is listed so the next reader does not re-find
it. Measured on the merge of `aca9298` into `6dccd6d`.

**Re-pointed 2026-09-15, after the Qt port (#588) landed.** `app/chart_series.py`
no longer exists - the port renamed it to `app/chart_frame.py` - so the line
numbers in the paragraph above are stale and the `touches` above names where the
word actually is today: `app/chart_frame.py` (three instances, one of them the
`PL-2FM6` history sentence that is correct as history),
`app/chart_time_base.py` (the module docstring, `following_window`'s prose and
`newest_sample_s`'s parameter documentation) and `app/controller.py` (four,
including two that are correct history about what `app/wash_in.py` used to do).
<!-- absent: app/chart_series.py -->

**Why it matters.** "Sample" and "drawn column" are different quantities after
`PL-2FM6`, and the docstrings still use the first word for the second thing.
A reader reasoning from "the 0.1 s step" about code where the column spacing
governs will get the wrong answer about how much time a pixel is worth - which
is the chart's whole contract with the reader - and will get it while believing
the docstring. This is `CLAUDE.md`'s core-domain bar applied one layer out:
`app/` should read like what it draws, and a word that meant something precise
before a refactor is the hardest kind of stale, because it still parses.

The correct-as-history instances are the reason this is judgment rather than a
sed. Keep those, and say they are history where the sentence does not already.

**Done when.** No docstring under `app/` uses "sample" for a drawn column or
reasons from the simulation step where column spacing governs; the sentences
that describe what the chart used to do say so; and the `PL-2FM6` history line
in `chart_frame.py` is left alone.

**Closed 2026-10-24.** The `verify:` command named `recorded sample`, which also matched the `PL-2FM6` history comment in `chart_frame.py` that the Done-when says to leave alone ("while the chart selected recorded samples"). The command now names the stale phrases only, `newest sample` among them. The sweep also covered every other `app/` docstring that used "sample" for a drawn column or a state: `area_layout.py` and `simulation_view.py` (a chord joins two drawn columns), `dashboard_frame.py` (the snapshot holds the newest state) and `wash_in.py` (a quotient is classified). `fit_to_run` and `following_window` take the newest instant as `newest_instant_s` now, with `PL-9DF9`. The wash-in ceiling paragraph in `wash_in_stretches` says its 1.00235 figure was measured step by step, and that a drawn column can land on a later state that the measurement did not cover. The history sentences in `controller.py` and `run_series.py` stay, since each already says it is history.
