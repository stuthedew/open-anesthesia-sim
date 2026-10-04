---
id: PL-7N8P
title: require_supported_case_instant admits True (as 1.0 s) and Decimal, and lets OverflowError escape for an int past the float range (CaseInstant(10**400)) rather than refusing in the simulator's words - the shape PL-LLMN records for the flows' _require_supported, so decide the two together; none is reachable from the interface (found reviewing #1354)
status: untriaged
added: 2026-10-04
---

**Problem.** require_supported_case_instant admits True (as 1.0 s) and Decimal, and lets OverflowError escape for an int past the float range (CaseInstant(10**400)) rather than refusing in the simulator's words - the shape PL-LLMN records for the flows' _require_supported, so decide the two together; none is reachable from the interface (found reviewing #1354)

**The docstrings follow the decision.** `CaseInstant`'s and
`require_supported_case_instant`'s Raises sections name only
`SimulationConfigurationError`, while a `str` raises `math.isfinite`'s own
`TypeError` and an `int` past the float range raises `OverflowError` (measured
2026-10-04 in #1354's second review pass). Whichever way this is decided, the
two docstrings are brought into line with it. `StepCount` already refuses
`bool` (`PL-CN5S`'s outcome says why), so refusing it here too would make the
two types of that slice agree.
