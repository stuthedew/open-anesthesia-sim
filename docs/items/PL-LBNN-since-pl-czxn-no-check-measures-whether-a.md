---
id: PL-LBNN
title: Since PL-CZXN no check measures whether a branch weakens a test of the apparatus: the owner's 2026-10-24 answer on PL-7FPD covers the simulator's tests of what the interface displays, and the assertion check PL-CZXN removed read the apparatus tests as well
status: untriaged
added: 2026-10-24
---

**Problem.** Since PL-CZXN no check measures whether a branch weakens a test of the apparatus: the owner's 2026-10-24 answer on PL-7FPD covers the simulator's tests of what the interface displays, and the assertion check PL-CZXN removed read the apparatus tests as well

Split from `PL-7FPD` while triaging it on 2026-10-24. `PL-7FPD`'s title names both halves of the gap. The owner's answer, relayed by the coordinator, brings back a check for the simulator's tests of what the interface displays, so `PL-7FPD`'s done-when now covers only the simulator half. This item keeps the apparatus half on record, so that it is not lost when `PL-7FPD` closes. A weakened apparatus test costs a session rather than a patient, which is why `.claude/rules/apparatus-standard.md` holds those tests to a lower bar. mutmut mutates only `src/`, so the mutation check cannot reach the apparatus as it stands.
