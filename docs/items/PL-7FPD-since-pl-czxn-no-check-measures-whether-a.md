---
id: PL-7FPD
title: Since PL-CZXN no check measures whether a branch weakens a test of the apparatus or of app/'s Qt modules, or a simulator test on a branch that changes no function mutmut mutates: verify's mutation check mutates only core/ and four app/ modules, and the assertion check it replaced read every .py file
status: untriaged
added: 2026-10-24
---

**Problem.** Since PL-CZXN no check measures whether a branch weakens a test of the apparatus or of app/'s Qt modules, or a simulator test on a branch that changes no function mutmut mutates: verify's mutation check mutates only core/ and four app/ modules, and the assertion check it replaced read every .py file

**Found 2026-10-24 while building `PL-CZXN`.** Of the 445 first-parent merges on `main` from 2026-10-01 to 2026-10-24, 40 changed a function in a module mutmut mutates, and 138 changed a test file that mentions `anesthesia_sim` without changing such a function, mostly Qt and layout work under `app/` and its integration tests. On those 138, and on every apparatus branch, the mutation check passes with nothing to run. It names each changed simulator test file in a note, so the gap is said on the page rather than hidden, but nothing refuses a weakened test there. The project owner's decision on `PL-CZXN` chose this trade; this item records its cost so a later session can weigh closing it.

One route, not yet sized: for a changed simulator unit test file, mutate the functions its base version reaches, and refuse a mutant the base's tests kill and the branch's tests do not. Where the source is unchanged, a mutant has the same name on both sides, so the comparison is exact. The cost is the run time, since one test can reach most of `core/`.
