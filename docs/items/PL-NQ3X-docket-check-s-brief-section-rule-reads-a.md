---
id: PL-NQ3X
title: docket check's brief-section rule reads a fenced copy of the capture template above the real sections and reports 'brief has nothing under Why it matters', under --verify too
status: untriaged
feature: exact-gates
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-25
---

**Problem.** docket check's brief-section rule reads a fenced copy of the capture template above the real sections and reports 'brief has nothing under Why it matters', under --verify too

Reproduced: a brief quoting the template in a fence, then carrying real sections, fails. Close to PL-6G8T.

**Why it matters.** A false refusal on a correct brief.

**Done when.** Fenced blocks are blanked before the section scan; a test holds the reproduction.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
