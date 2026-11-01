---
id: PL-TPXR
title: app/control_timeline.py's module docstring says its one unit conversion is from a fraction to the percent the delivered dial is displayed in, but since PL-NJPB format_control_value also converts the recorded percent to a fraction before format_percent, so the docstring misstates where the delivered value's units change (found closing PL-KSLX)
status: untriaged
feature: stale-source-claims
added: 2026-11-01
---

**Problem.** app/control_timeline.py's module docstring says its one unit conversion is from a fraction to the percent the delivered dial is displayed in, but since PL-NJPB format_control_value also converts the recorded percent to a fraction before format_percent, so the docstring misstates where the delivered value's units change (found closing PL-KSLX)
