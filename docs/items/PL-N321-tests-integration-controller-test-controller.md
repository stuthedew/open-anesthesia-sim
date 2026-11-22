---
id: PL-N321
title: tests/integration/controller/test_controller_stored_states.py cites docs/MODEL.md § 'State vector', a section docs/MODEL.md does not have, and the documentation check misses it because the quotation is split across two lines
status: untriaged
added: 2026-11-22
---

**Problem.** tests/integration/controller/test_controller_stored_states.py cites docs/MODEL.md § 'State vector', a section docs/MODEL.md does not have, and the documentation check misses it because the quotation is split across two lines

**Found 2026-11-22** by the worker building `PL-DN13`, near the top of `tests/integration/controller/test_controller_stored_states.py`. `grep -n '^#\+ .*State vector' docs/MODEL.md` finds no such heading. The new code in `PL-DN13` does not repeat the citation.
