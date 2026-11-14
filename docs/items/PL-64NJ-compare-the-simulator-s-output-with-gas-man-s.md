---
id: PL-64NJ
title: Compare the simulator's output with Gas Man's own engine, now that its source is public (rasman/gasmanonline, GPL-3.0)
status: untriaged
feature: gas-man-open-source
added: 2026-11-14
---

**Problem.** Compare the simulator's output with Gas Man's own engine, now that its source is public (rasman/gasmanonline, GPL-3.0)

**Why.** `docs/MODEL.md` § "Source hierarchy" calls Gas Man this project's
reference implementation, whose parameter set "defines Gas Man's behavior, so
this simulator can be compared with it". No test makes that comparison. The
independent-solution test cannot stand in for it, because the independent
solver solves our own equations. A comparison with Gas Man's engine would catch
a modelling difference, and would tell a learner who uses both tools why their
curves differ.

**What is now available.** Gas Man's desktop source and a scripting port were
published under GPL-3.0 at <https://github.com/rasman/gasmanonline>, read at
commit `d3a2dd3` on 2026-11-13. James Philip's letter in that repository asks
for Gas Man to become "a public open source application". The port's command
line runner, `gasman_api/run` (`gasman_run`), reads a scenario from CSV, JSON,
XML or Excel. It writes the circuit, alveolar, vessel-rich, muscle, fat and
venous tensions as CSV (`gasman_api/README.md`).

**Differences any gap must be explained by**, read from that commit:

- Gas Man solves each compartment exactly with the others held at their values
  from the start of the sub-step (`gasman_api/gasmanAPI/GasDoc.cpp:831-837`),
  over 6 s breath steps (`GasGlobal.h:19`) in single precision
  (`GasGlobal.h:93`). It halves the step only by the rule at
  `GasDoc.cpp:873-885`.
- Its venous tension is an instant flow-weighted mix (`GasDoc.cpp:891`), where
  ours is a 1.222 L pool.
- Its default circuit is 8 L (`gasman.ini` `[Volumes] CKT=8`), and ours departs
  from that deliberately.
- Its alveolar target carries an uptake-volume correction (`GasDoc.cpp:817-831`),
  which its `Disable Uptake` switch turns off. Ours holds alveolar volume fixed.
- Its MAC values differ from ours (`PL-LBVN`). MAC does not affect the
  tensions, only the MAC-multiple display.

**Constraints.**

- Never copy Gas Man's GPL-3.0 code into this Apache-2.0 tree. Build and run it
  outside the repository. The GNU GPL FAQ says "the output of a program is not,
  in general, covered by the copyright on the code of the program"
  (<https://www.gnu.org/licenses/gpl-faq.en.html#GPLOutput>, read 2026-11-13),
  so storing its output numbers as test values should be allowed.
- On 2026-11-13 a thread session's sandbox refused to build the downloaded
  code, so no Gas Man output exists yet. The run needs an environment where
  building it is allowed.

**Done when.** A reference test compares our six tensions with Gas Man's for
stated scenarios, at a tolerance taken from the differences above. `docs/MODEL.md`
says what the comparison shows and what it cannot show.

**Decided.** Filed on the project owner's agreement with the thread's
recommendation (project owner, 2026-11-14, ratified, over leaving the
comparison unfiled). The thread's full comparison is in the project's shared
folder, `v0.7.0/gasman-comparison/report.md` and `grading.md`.
