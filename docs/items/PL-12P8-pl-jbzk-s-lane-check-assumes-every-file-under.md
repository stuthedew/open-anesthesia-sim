---
id: PL-12P8
title: PL-JBZK's lane check assumes every file under tests/ is a test file, so a shared non-test helper is told to declare itself apparatus
status: untriaged
added: 2026-09-06
---

**Problem.** `tools/workflow_paths_check.py` decides a file's lane from
whether it imports `anesthesia_sim`, and its docstring rests the hard failure
on a measured premise: "There is no file in the tree the rule has to guess
about." That premise holds for *test* files and quietly assumes every file
under `tests/` is one. A shared non-test helper - a module holding a constant
or a fixture builder, imported by test files rather than collected as tests -
imports nothing from `src/` when what it holds is a literal, so the rule
classifies it as apparatus and the failure message tells the author to add it
to `workflow_paths`.

**Why it matters.** Following that instruction writes a false entry into the
one file that defines the lane boundary: simulator content declared as
workflow, so an item touching it and `docs/MODEL.md` becomes `crossing` and is
set aside from both lanes. The check would then pass, having made
`docket next` wrong - which is the "worse than no tool" case the check's own
docstring names, reached through its remedy rather than its rule.

**Observed 2026-09-06,** immediately, on the first such file: `PL-4GN8` added
`tests/reference/mass_balance_gate.py` holding one release-gate constant and
CI refused the branch. That item resolved it by removing the helper and
restating the constant per file, which is the repository's idiom and was the
better answer there - so nothing is currently failing, and the next author to
reach for a shared fixture meets the same message with no such escape.

**Where.** `tools/workflow_paths_check.py`, the file-collection step and the
failure message; `tests/unit/test_workflow_paths_check.py`.

**Done when.** A non-test module under `tests/` is either classified by
something other than its imports, or excluded from the check with the reason
recorded, or the failure message stops naming `workflow_paths` as the remedy
for a file that is not a test. Which of the three is the decision - the first
is the most useful and the most work, the third is nearly free and leaves the
judgment with the author.
