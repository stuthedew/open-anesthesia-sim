---
id: PL-3G9M
title: docket verify's no-suppression check counts a call of a function named pytest_ignore_collect as an added suppression, so a test that calls a conftest's hook refuses the close-out audit: three of PL-GQCQ's four refused lines were such calls, and only a definition of the hook or a collect_ignore assignment drops a file from collection
status: untriaged
feature: verify-false-reject
added: 2026-10-25
---

**Problem.** docket verify's no-suppression check counts a call of a function named pytest_ignore_collect as an added suppression, so a test that calls a conftest's hook refuses the close-out audit: three of PL-GQCQ's four refused lines were such calls, and only a definition of the hook or a collect_ignore assignment drops a file from collection

**Evidence.** On 2026-10-25, `bin/docket verify --self PL-GQCQ` refused "no suppression added" on four lines. One is the hook's definition in the root `conftest.py`. The other three are calls in `tests/unit/test_bytecode_guard.py`, such as `ROOT_HOOKS.pytest_ignore_collect(tmp_path / path, config) is None`, which test that hook. A call of the function drops nothing from any collection. The README's own description of the marker says it reads "the hook a `conftest.py` drops a file from collection with", which is a definition.

**The fix.** Count the `pytest_ignore_collect` marker only where a statement defines a function of that name, and keep reading `collect_ignore` and `collect_ignore_glob` as assignments. Replay the narrowing over `main` as the earlier narrowings were.
