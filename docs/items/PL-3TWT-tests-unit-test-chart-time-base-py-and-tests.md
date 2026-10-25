---
id: PL-3TWT
title: tests/unit/test_chart_time_base.py and tests/integration/test_sevo_controller.py still say the interface is Flet, but it is Qt (found in the PL-FDMJ prose pass, 2026-10-25)
status: dropped
feature: stale-source-claims
added: 2026-10-25
closed: 2026-10-25
reason: duplicate of PL-21KP, which already covers the same present-tense Flet claims and missing test citations in these files; its two extra lines were folded into PL-21KP's brief
---

**Problem.** tests/unit/test_chart_time_base.py and tests/integration/test_sevo_controller.py still say the interface is Flet, but it is Qt (found in the PL-FDMJ prose pass, 2026-10-25)

**Also found, by the blind review of #1805 (2026-10-25).** The module
docstrings of `tests/unit/test_wash_in.py` and `tests/unit/test_formatting.py`
say they avoid building a Flet interface, and say the end-to-end path is tested
in `tests/unit/test_simulation_view.py`. That file does not exist. The
end-to-end tests are in `tests/integration/test_simulation_view.py`.
`tests/unit/test_dashboard_frame.py` line 8 names the same missing file as the
Flet suite. A reader checking the end-to-end coverage of a displayed value is
sent to a file that is not there, and may conclude the coverage is missing.
<!-- absent: tests/unit/test_simulation_view.py -->
