---
id: PL-979Z
title: CaseInstant and the three flow types are built from another checked quantity silently - CaseInstant(StepCount(600)) is an instant of 600 s, CaseInstant(FreshGasFlow(5.0)) one of 5 s and FreshGasFlow(CaseInstant(5.0)) a flow of 5 L/min - because require_a_number admits every int and float subclass and only the stored-value checks (require_case_instant, _require_built) name a swapped quantity; refuse another checked quantity at the constructor, as Fraction refuses a Percent (found reviewing PL-7N8P)
status: untriaged
feature: parse-dont-validate
added: 2026-10-05
---

**Problem.** CaseInstant and the three flow types are built from another checked quantity silently - CaseInstant(StepCount(600)) is an instant of 600 s, CaseInstant(FreshGasFlow(5.0)) one of 5 s and FreshGasFlow(CaseInstant(5.0)) a flow of 5 L/min - because require_a_number admits every int and float subclass and only the stored-value checks (require_case_instant, _require_built) name a swapped quantity; refuse another checked quantity at the constructor, as Fraction refuses a Percent (found reviewing PL-7N8P)
