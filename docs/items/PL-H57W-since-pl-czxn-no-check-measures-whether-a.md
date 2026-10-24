---
id: PL-H57W
title: Since PL-CZXN no check measures whether a branch that changes no core function weakens a core unit test, because PL-7FPD's route compares only the display modules' mutants; the same comparison over core's mutants took 538 to 968 s for one changed test file
status: untriaged
added: 2026-10-24
---

**Problem.** Since PL-CZXN no check measures whether a branch that changes no core function weakens a core unit test, because PL-7FPD's route compares only the display modules' mutants; the same comparison over core's mutants took 538 to 968 s for one changed test file

Split from `PL-7FPD` while triaging it on 2026-10-24. `PL-7FPD`'s problem covers any simulator test changed on a branch that changes no mutated function. The owner's answer, relayed by the coordinator, brings back a check for tests of what the interface displays, and `PL-7FPD`'s recommended route compares only the mutants of the `app/` display modules, because that cut one measured run from 1,837 mutants to 202. A core unit test loosened on a branch that changes no core function, such as a wider tolerance on a concentration, therefore stays unmeasured. That is the safety-critical standard's concern as much as a display test is. `PL-7FPD`'s brief holds the three measured runs: 538 s for every mutant `tests/unit/test_formatting.py` reaches, 968 s for every mutant two changed dashboard tests reach, and 113 s for the `app/` mutants of the same two tests, on four shared cores.
