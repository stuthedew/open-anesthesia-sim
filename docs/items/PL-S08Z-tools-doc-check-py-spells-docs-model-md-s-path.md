---
id: PL-S08Z
title: tools/doc_check.py spells docs/MODEL.md's path a third time, as MODEL = Path("docs/MODEL.md"), beside product_paths.MODEL_DOC, which PL-5S71 made the home; fact_home_check misses it because the name differs
priority: P2
effort: M
status: done
classes: defect
feature: one-source-of-truth
touches: subprojects/docket/src/docket/arming.py, tools/product_paths.py, tools/doc_check.py, tools/import_boundary_check.py, tools/new_prose.py, tools/restated_constants.py, tools/workflow_paths_check.py, tools/fact_home_check.py, tests/unit/test_fact_home_check.py, docs/apparatus.md
added: 2026-10-25
closed: 2026-10-25
pr: 1802
payoff: a second spelling of where a file or tree lives fails make check, so moving docs/MODEL.md, src/ or tests/ cannot leave one tool reading the old place
verify: uv run pytest -q tests/unit/test_fact_home_check.py -k 'repository_path or names_no_path' && python3 tools/fact_home_check.py
reenters: PL-MM3Q
---

**Problem.** tools/doc_check.py spells docs/MODEL.md's path a third time, as MODEL = Path("docs/MODEL.md"), beside product_paths.MODEL_DOC, which PL-5S71 made the home; fact_home_check misses it because the name differs

**Why it matters.** `CLAUDE.md` makes one source of truth for a shared fact
the project's core design principle. A path spelled in two tools agrees only
until one of them is edited. If `docs/MODEL.md` moved, `doc_check` would go on
reading the old path while every other tool read the new one. The same sweep
found two more paths spelled twice under different names: the test tree, as
`restated_constants.SUITE = "tests"` and `workflow_paths_check.TESTS_DIR =
Path("tests")` beside `docket.arming.TESTS`, and the source tree, as
`import_boundary_check.SOURCE_ROOT = "src"` and `new_prose.SOURCE = "src/"`.
`fact_home_check` rule 2 compares names, and values only where the value is a
call given arguments, so a path bound under a second name passed it.

**Done when.** Each of the three paths has one binding, in `docket.arming`
(which `docket` and every tool can import) and re-exported through
`tools/product_paths.py`, and every other reader imports it.
`fact_home_check` rule 2 also refuses a module-level value that names a path
in the tree, as a string or as a constructor's one argument, bound under two
names in two files. `tests/unit/test_fact_home_check.py` covers the finding and
the two shapes it must not read: a string naming no path, such as the branch
prefix `"claude/"`, and a method's argument, such as `rstrip("/")`.

**Generator check.** The same fact `PL-MM3Q` read for calls, one value bound
under two names, reached through a value it did not compare. `PL-MM3Q` closed
today, so this is recorded as `reenters: PL-MM3Q`. The rule now compares
repository paths too, and every path left spelled twice is drained. A path
inside a tuple or an f-string is still not read, and
`docket.arming.READ_PATHS` names `src/anesthesia_sim/data/` that way.
