---
id: PL-W40L
title: The repository-root conftest.py isolates git for the docket and hook tests but sits on the product side of workflow_paths by omission, so an item touching it and the tests it serves is crossing
status: untriaged
feature: parallel-sessions
touches: docket.toml
added: 2026-09-27
---

**Problem.** The repository-root conftest.py isolates git for the docket and hook tests but sits on the product side of workflow_paths by omission, so an item touching it and the tests it serves is crossing

**Evidence, 2026-09-27.** `conftest.py` at the repository root sets
`GIT_CONFIG_GLOBAL` and `GIT_CONFIG_SYSTEM` to `/dev/null` so that the tests
which build scratch repositories with real git - `subprojects/docket/tests/`
and the `.claude/hooks/` tests under `tests/unit/` - read none of the
developer's git configuration (`PL-YRYR`). Both of those are apparatus.
`docket.toml`'s `workflow_paths` does not list it, so it is on the product side
by omission, and `PL-YRYR` itself - `conftest.py`,
`subprojects/docket/tests/test_git_isolation.py`, `test_cli.py`,
`test_verify.py` and `subprojects/docket/README.md` - was `crossing` and
offered to neither lane.

It sits outside `tests/`, so `tools/workflow_paths_check.py` never reads it,
and `PL-12P8` has since made a support module's side the list's declaration
wherever its imports cannot decide it. This file's declaration is the default
nobody chose.

**Recommendation:** list `"conftest.py"` in `workflow_paths`, with one line in
the comment block beside `PL-12P8`'s paragraph saying why: its purpose is the
tests that run git, and a git setting changes nothing the simulator's tests
do. Filed rather than fixed on `PL-12P8`'s branch because it applies to every
pytest run, product included, so the current placement is a defensible choice
rather than a slip.
