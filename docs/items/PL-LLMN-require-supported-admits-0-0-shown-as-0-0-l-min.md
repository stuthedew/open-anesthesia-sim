---
id: PL-LLMN
title: _require_supported admits -0.0 (shown as -0.0 L/min), True (as 1.0 L/min) and Decimal, and refuses a str with math.isfinite's own TypeError rather than the simulator's wording; none is reachable from the sliders (found reviewing #1350)
status: untriaged
added: 2026-10-04
---

**Problem.** _require_supported admits -0.0 (shown as -0.0 L/min), True (as 1.0 L/min) and Decimal, and refuses a str with math.isfinite's own TypeError rather than the simulator's wording; none is reachable from the sliders (found reviewing #1350)
