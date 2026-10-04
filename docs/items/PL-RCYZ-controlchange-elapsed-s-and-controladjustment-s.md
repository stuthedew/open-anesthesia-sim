---
id: PL-RCYZ
title: ControlChange.elapsed_s, and ControlAdjustment's started_at_s and ended_at_s, are annotated float though every one is taken from a CaseInstant - SimulationState.elapsed_s - so the control record is the one holder of a case instant PL-CN5S left untyped (app/control_record.py and app/control_timeline.py were outside its touches)
status: untriaged
feature: parse-dont-validate
added: 2026-10-04
---

**Problem.** ControlChange.elapsed_s, and ControlAdjustment's started_at_s and ended_at_s, are annotated float though every one is taken from a CaseInstant - SimulationState.elapsed_s - so the control record is the one holder of a case instant PL-CN5S left untyped (app/control_record.py and app/control_timeline.py were outside its touches)
