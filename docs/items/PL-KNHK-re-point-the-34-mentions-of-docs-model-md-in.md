---
id: PL-KNHK
title: Re-point the 34 mentions of docs/MODEL.md in five reference tests to the document and section that now state them; the edit is built and waits for a pull request that already needs the owner's read of tests/reference
status: untriaged
feature: model-md-structure
touches: tests/reference
added: 2026-11-22
---

**Problem.** Re-point the 34 mentions of docs/MODEL.md in five reference tests to the document and section that now state them; the edit is built and waits for a pull request that already needs the owner's read of tests/reference

**Split from `PL-10BC`** (re-pointing the sectionless mentions of `docs/MODEL.md`) on 2026-11-22. Its worker re-pointed the mentions in five tests under `tests/reference/` too: `test_coupled_dynamics.py`, `test_late_washout_against_published_fits.py`, `test_parameter_recovery.py`, `test_published_wash_in_and_elimination.py` and `test_sevo_patient.py`, 80 lines added and 46 removed, in comments, docstrings and assertion messages only. Any edit to an existing line under `tests/reference/` waits for the project owner's read, so the commit was kept out of `PL-10BC`'s pull request. It is saved as a patch in the project's shared files, `v0.7.0/pl-knhk-reference-mentions.patch`, built on the sorted documents' headings.

**Why it matters.** A developer who follows one of these mentions to `docs/MODEL.md` finds a clinician's description that no longer holds the figure or the method the test names, because the split moved it to `docs/VERIFICATION.md`, `docs/PARAMETERS.md` or `docs/INTERFACE.md`.

**Done when.** Each mention of `docs/MODEL.md` in those five tests that means a statement now in another document names that document and its section, and each heading named exists in the document. The edit changes no test logic, value or tolerance.

**When to do it.** With the next pull request that already needs the owner's read of `tests/reference/`. `PL-MYK0` (five corrected statements in two of the same tests) is the likely one. Apply that patch to that branch with `git am`, and check each heading again against the documents as they then stand.

**Generator check.** Not a new defect: the remainder of `PL-10BC`, held back by the owner-read rule for reference tests.
