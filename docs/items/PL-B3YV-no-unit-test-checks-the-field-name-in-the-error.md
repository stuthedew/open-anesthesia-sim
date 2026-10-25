---
id: PL-B3YV
title: No unit test checks the field name in the error that record_external_agent_transfer raises for a refused transfer: mutating either require_nonnegative_finite name argument (to None, upper case or padded) survives tests/unit/test_agent_simulation_validation.py, so a refused delivered transfer could be reported as the exhausted one
status: untriaged
feature: tests-detect-wrong-values
added: 2026-10-25
---

**Problem.** No unit test checks the field name in the error that record_external_agent_transfer raises for a refused transfer: mutating either require_nonnegative_finite name argument (to None, upper case or padded) survives tests/unit/test_agent_simulation_validation.py, so a refused delivered transfer could be reported as the exhausted one
