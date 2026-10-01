---
id: PL-HWNG
title: tests/unit/test_run_definition.py's _two_change_run sets sevoflurane's dial to 2.0%, where AgentUptakeSystem.for_agent already opens it at 1 MAC, so its first record_change may record nothing and every test built on it may be exercising one change rather than the two its name promises (reported while building PL-NJPB; the 2.0% matches the opening dial, but whether record_change skips an unchanged setting was not checked)
status: untriaged
added: 2026-10-01
---

**Problem.** tests/unit/test_run_definition.py's _two_change_run sets sevoflurane's dial to 2.0%, where AgentUptakeSystem.for_agent already opens it at 1 MAC, so its first record_change may record nothing and every test built on it may be exercising one change rather than the two its name promises (reported while building PL-NJPB; the 2.0% matches the opening dial, but whether record_change skips an unchanged setting was not checked)
