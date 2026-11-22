---
id: PL-KNHK
title: Re-point the 34 mentions of docs/MODEL.md in five reference tests to the document and section that now state them; the edit is built and waits for a pull request that already needs the owner's read of tests/reference
status: done
feature: model-md-structure
touches: tests/reference
added: 2026-11-22
closed: 2026-11-22
pr: 2250
verify: ! grep -qF 'docs/MODEL.md` § "Arterial blood"' tests/reference/test_parameter_recovery.py
---

**Problem.** Re-point the 34 mentions of docs/MODEL.md in five reference tests to the document and section that now state them; the edit is built and waits for a pull request that already needs the owner's read of tests/reference

**Split from `PL-10BC`** (re-pointing the sectionless mentions of `docs/MODEL.md`) on 2026-11-22. Its worker re-pointed the mentions in five tests under `tests/reference/` too: `test_coupled_dynamics.py`, `test_late_washout_against_published_fits.py`, `test_parameter_recovery.py`, `test_published_wash_in_and_elimination.py` and `test_sevo_patient.py`, 80 lines added and 46 removed, in comments, docstrings and assertion messages only. Any edit to an existing line under `tests/reference/` waits for the project owner's read, so the commit was kept out of `PL-10BC`'s pull request. It is saved as a patch in the project's shared files, `v0.7.0/pl-knhk-reference-mentions.patch`, built on the sorted documents' headings.

**Why it matters.** A developer who follows one of these mentions to `docs/MODEL.md` finds a clinician's description that no longer holds the figure or the method the test names, because the split moved it to `docs/VERIFICATION.md`, `docs/PARAMETERS.md` or `docs/INTERFACE.md`.

**Done when.** Each mention of `docs/MODEL.md` in those five tests that means a statement now in another document names that document and its section, and each heading named exists in the document. The edit changes no test logic, value or tolerance.

**When to do it.** With the next pull request that already needs the owner's read of `tests/reference/`. `PL-MYK0` (five corrected statements in two of the same tests) is the likely one. Apply that patch to that branch with `git am`, and check each heading again against the documents as they then stand.

**Generator check.** Not a new defect: the remainder of `PL-10BC`, held back by the owner-read rule for reference tests.

**Done, 2026-11-22.** The saved patch applied cleanly to `main` at `22828fd0`, after `PL-MYK0` merged in #2243 without it. The five tests now name the document and section for each of the 34 mentions. The same commit fixes three older pointers in two of these files. In `test_parameter_recovery.py`, `docs/MODEL.md` § "Arterial blood" named no heading, and the statement it meant is under § "What the model represents". In `test_published_wash_in_and_elimination.py`, `docs/VERIFICATION.md` SS "Desflurane's residual" now uses the section mark and the heading's full title. Yasuda 1991's "Materials and Methods" lost its stray "SS" and is written as a paper's own locator, without the mark, as `tools/doc_check.py` asks for a section of an outside source. Each heading named by a `§` citation or a `section '...'` string in the five files was compared with the headings of `docs/MODEL.md`, `docs/VERIFICATION.md` and `docs/INTERFACE.md` as they stand at `22828fd0`. No test code changed: each file, parsed by Python before and after, gives the same tree once docstrings and `assert` failure messages are set aside. The owner was asked whether an edit with no code change needed his read under `PL-XSRG` (the published-data test hold), and answered "Agree with recs" on 2026-11-22 (project owner, 2026-11-22, ratified, over waiting for the next change to these tests). Files checked in the documentation sweep: the five test files, and the headings of `docs/MODEL.md`, `docs/VERIFICATION.md` and `docs/INTERFACE.md`.

**Blind review, 2026-11-22.** One general pass found three pointers that named too few places, and each was fixed in the same kind of edit. The desflurane-solubility failure message in `test_published_wash_in_and_elimination.py` named `docs/MODEL.md` § "Elimination at five minutes: does not agree", which does not make the vessel-rich claim; it now names `docs/VERIFICATION.md` § "Desflurane's residual, and why the parameter file was not changed", which does. The four late-tail pointers in `test_late_washout_against_published_fits.py` now also name `docs/INTERFACE.md` § "The washout tail inside the limit", which restates the crossing hours. The display-resolution message in `test_coupled_dynamics.py` now also names `docs/VERIFICATION.md` § "Independent-solution test", which quotes the step-dependent figures. The parsed programs still match the base.
