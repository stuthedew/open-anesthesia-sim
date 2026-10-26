---
id: PL-LSTW
title: tools/ignore_check.py is named for .gitignore but evaluates type: ignore directives, so a session looking for the gitignore check finds it and a session looking for the mypy one does not
priority: P3
effort: S
status: done
classes: infra
touches: tools/type_ignore_check.py, tests/unit/test_type_ignore_check.py, Makefile, .github/workflows/quality.yml, tests/unit/test_quality_step_order.py, docket.toml, subprojects/docket/src/docket/verify.py, subprojects/docket/README.md, subprojects/docket/tests/test_verify.py, tests/unit/test_workflow_paths_check.py, tests/unit/test_line_splits.py, tests/unit/test_concentration.py, .claude/hooks/push-check-guard.sh, tests/unit/test_push_check_guard.py, conftest.py, pyproject.toml, docs/apparatus.md, tools/config_home_check.py, tools/doc_check.py, tools/literal_home_check.py, tools/workflow_paths_check.py
added: 2026-09-15
closed: 2026-10-26
pr: 1856
verify: python3 tools/type_ignore_check.py --help >/dev/null && ! test -e tools/ignore_check.py
---

**Problem.** tools/ignore_check.py is named for .gitignore but evaluates type: ignore directives, so a session looking for the gitignore check finds it and a session looking for the mypy one does not

**Why it matters.** The name is the only index a session has. This repository
carries fifteen checks under `tools/`, and a session reaching for one reads the
filename rather than the module docstring - so `ignore_check.py` costs a wrong
open in both directions: a session looking for the `.gitignore` check finds it
and has to read 40 lines of docstring to learn it is about mypy, and a session
looking for the mypy-suppression check does not find it under any name it would
guess. Observed 2026-09-15 while working `PL-RFGY`: this session opened it
expecting a `.gitignore` check, which is exactly the wrong open the name
invites.

The cost is small per instance and permanent, and it grows rather than decays -
`PL-MXSL` puts a genuine ignore-related check into `doc_check.py`, so the
repository now has ignore-rule logic in a file *not* called `ignore_check.py`
and mypy logic in one that is.

**Done when.** No file under `tools/` is named for a thing it does not check.
The proposed rename is `tools/type_ignore_check.py`, which says what it
evaluates in the same shape as its neighbours (`import_boundary_check.py`,
`core_vocabulary_check.py`); the name is a proposal rather than a finding, and
any name that does not read as `.gitignore` satisfies the item. `Makefile`'s
invocation moves with it, and `git mv` keeps the history.

**Touches widened 2026-10-18, and set aside from a batch.** A grep for
`ignore_check` outside the item store and the release records finds the name
in twelve files, not two. They include `.github/workflows/quality.yml`,
`tests/unit/test_quality_step_order.py` (the step name it pins),
`docket.toml`, the docket subproject's `verify.py`, README and `test_verify.py`,
and the docstring of `tests/unit/test_concentration.py`, which is a product
test. `touches:` now names all twelve, so `bin/docket concurrent` can see the
overlap. The third-place workflow thread claimed it and yielded it unworked,
because `tests/unit/test_concentration.py` was changing on another open branch
at the time.

**Done 2026-10-26.** `tools/ignore_check.py` is now `tools/type_ignore_check.py`, and its test is `tests/unit/test_type_ignore_check.py`, both moved with `git mv`. Every live reference moved with them: 20 files, including the `make check` line, `quality.yml`'s step, the push guard's step list and its test, `docket.toml`'s test list, and the docstrings and comments that name it. `docs/apparatus.md`'s tree lists it in its alphabetical place. The item store, `ROADMAP.md`'s frozen item titles, the release notes and the published pull request bodies keep the old name, because they record what was true when they were written.
