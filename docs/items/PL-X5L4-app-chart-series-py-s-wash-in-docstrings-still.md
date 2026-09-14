---
id: PL-X5L4
title: app/chart_series.py's wash-in docstrings still say 'sample' for a drawn column and reason from the 0.1 s step where the column spacing now governs
status: untriaged
added: 2026-09-14
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
