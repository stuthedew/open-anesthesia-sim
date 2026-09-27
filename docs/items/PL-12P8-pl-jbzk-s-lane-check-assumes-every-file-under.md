---
id: PL-12P8
title: PL-JBZK's lane check assumes every file under tests/ is a test file, so a shared non-test helper is told to declare itself apparatus
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
milestone: v0.5.16
touches: tools/workflow_paths_check.py, tests/unit/test_workflow_paths_check.py, docket.toml, docs/ARCHITECTURE.md
added: 2026-09-06
closed: 2026-09-27
pr: 1196
verify: grep -q 'def test_the_conftest_that_renders_the_qt_tests_lands_in_the_product_lane' tests/unit/test_workflow_paths_check.py
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

**Decision needed.** Which of the three the brief names: classify a non-test
module under `tests/` by something other than its imports; exclude it from the
check with the reason recorded; or leave the rule and stop the failure message
naming `workflow_paths` as the remedy for a file that is not a test. The first
is the most useful and the most work, the third is nearly free and leaves the
judgment with the author.

**A second instance, 2026-09-14 (`PL-G59B`).** `tests/conftest.py` - one
line, `os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")`, which exists so
the *product's* Qt chart can render under pytest - imports no `anesthesia_sim`
and was told to declare itself apparatus. It is listed in `workflow_paths` to
keep `make check` green, which is the wrong lane for it and is exactly this
item's defect.

**Decided, 2026-09-27, by the session working it** (a choice between three
routes the brief itself offered, with one tool's behaviour as its blast
radius, so the session's under `.claude/rules/instruction-writing.md` rule
14). The second route, sharpened: a support module is excluded from the half
of the rule its imports cannot decide, and held to the half they can.

- *Why not the first* - classifying a support module some other way. By
  importer, the live instance has no answer: `tests/conftest.py` is loaded for
  every test beneath it, product and apparatus alike. By location - every
  support module is the simulator's - an apparatus fixture builder under
  `tests/unit/` would be told to leave the list, this defect in the mirror.
- *Why not the third* - changing only the message. The check would still fail
  on `tests/conftest.py` with no correct remedy left to print, so the one
  live instance could not be fixed at all.
- *What was built.* A test file is what pytest collects (`test_*.py`,
  `*_test.py`, pinned to this run's `python_files`); anything else under
  `tests/` is a support module. One importing `anesthesia_sim` is still refused
  a `workflow_paths` entry - built on the simulator, it is the simulator's.
  One importing none of it is left where the list puts it, and the clean
  report counts those, so what the check did not decide is printed rather
  than rounded off. `tests/conftest.py` left the list, which puts an item
  touching it and the Qt test it serves in the product lane.

**Reproduced 2026-09-27, before the fix:** with the conftest entry removed the
check printed `tests/conftest.py imports no anesthesia_sim, so it is
apparatus ... Add "tests/conftest.py" to workflow_paths`; with it present, an
item touching `tests/conftest.py` and `tests/integration/test_qt_chart.py`
read `crossing`.
