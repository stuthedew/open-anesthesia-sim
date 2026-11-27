---
id: PL-N321
title: tests/integration/controller/test_controller_stored_states.py cites docs/MODEL.md § 'State vector', a section docs/MODEL.md does not have, and the documentation check misses it because the quotation is split across two lines
priority: P2
effort: S
status: ready
classes: defect
feature: doc-consistency-checks
touches: tests/integration/controller/test_controller_stored_states.py, tools/doc_check.py
deferred-from: v0.7.0 - present at the freeze, not safety or science, and no user sees a wrong value from it; the gate is otherwise clear and the release waits on the owner test drive, so it is deferred rather than holding the release (triage 2026-11-23)
added: 2026-11-22
payoff: a section citation quoted across two lines is checked like any other, and the stored-states test cites a section that exists
reenters: PL-LPCB
---

**Problem.** tests/integration/controller/test_controller_stored_states.py cites docs/MODEL.md § 'State vector', a section docs/MODEL.md does not have, and the documentation check misses it because the quotation is split across two lines

**Found 2026-11-22** by the worker building `PL-DN13`, near the top of `tests/integration/controller/test_controller_stored_states.py`. `grep -n '^#\+ .*State vector' docs/MODEL.md` finds no such heading. The new code in `PL-DN13` does not repeat the citation.

**Why it matters.** A reader of the test follows the citation to `docs/MODEL.md` and finds no such section, and the document check says nothing, so the next stale citation split over two lines will not be caught either.

**Done when.** The test cites a section that exists, and a test of the document check shows a § citation quoted across two lines is held to the cited headings.

**Generator check.** An instance of `PL-LPCB`'s fact, which heading a § citation names, filed after that head closed: its fix reads a citation on one line only. Recorded with `reenters`.

**Reproduced 2026-11-23.** `docs/MODEL.md` has no heading containing "State vector".
