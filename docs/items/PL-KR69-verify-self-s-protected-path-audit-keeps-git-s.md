---
id: PL-KR69
title: verify --self's protected-path audit keeps git's rename detection, so git mv of a src/anesthesia_sim/core/ file to a path outside core prints 'PASS no protected path modified - none touched', while arm's --no-renames diff lists the core file
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py
added: 2026-09-25
---

**Problem.** verify --self's protected-path audit keeps git's rename detection, so git mv of a src/anesthesia_sim/core/ file to a path outside core prints 'PASS no protected path modified - none touched', while arm's --no-renames diff lists the core file

Reproduced twice, independently (by the audit and again by PL-P0FP's session in a scratch clone): `git mv src/anesthesia_sim/core/alveolar.py tools/moved_core.py`, commit, `bin/docket verify --self PL-YSMV` prints `PASS no protected path modified - none touched`. `verify.changed_paths` (`verify.py:1498`) and `files_in_flight` (`vcs.py:3042`) keep rename detection; `arming.py:199` and `claims.py:867` pass `--no-renames`. PL-J16N is the same mechanism in `_modified_by` only.

**Why it matters.** The protected-path audit guards safety-critical simulator code; a rename carries a core file out of it unseen. Recommended P1.

**Done when.** Every changed-path read in the apparatus passes `--no-renames` (one helper); a regression test moves a core file out and the audit fails.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
