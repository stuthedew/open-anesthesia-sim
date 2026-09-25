---
id: PL-VH5V
title: fixture_id_check matches PL-[A-Za-z0-9]+, so the prose 'Every PL-prefixed token' in .claude/ or a .py message is read as an id, while the placeholders PL-XXXX and PL-ZZZZ are accepted as valid
status: untriaged
feature: exact-gates
touches: tools/fixture_id_check.py, tests/unit/test_fixture_id_check.py
added: 2026-09-25
---

**Problem.** fixture_id_check matches PL-[A-Za-z0-9]+, so the prose 'Every PL-prefixed token' in .claude/ or a .py message is read as an id, while the placeholders PL-XXXX and PL-ZZZZ are accepted as valid

Reproduced both false refusals and both false passes. 42 `not-an-id` exemptions exist, 35 in tests - the exemption count is itself the cost of the loose pattern.

**Why it matters.** A loose pattern forces exemptions; exemptions hide real misses.

**Done when.** The pattern is the store's own id grammar (`store.ID_PATTERN`); a test holds `PL-prefixed` and `PL-XXXX`.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
