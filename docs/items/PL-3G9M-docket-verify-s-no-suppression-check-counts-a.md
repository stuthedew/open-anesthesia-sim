---
id: PL-3G9M
title: docket verify's no-suppression check counts a call of a function named pytest_ignore_collect as an added suppression, so a test that calls a conftest's hook refuses the close-out audit: three of PL-GQCQ's four refused lines were such calls, and only a definition of the hook or a collect_ignore assignment drops a file from collection
priority: P2
effort: S
status: ready
classes: defect
feature: verify-false-reject
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_verify.py, subprojects/docket/README.md
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-10-25
payoff: a test that calls a conftest's collection hook no longer holds its pull request for the owner's read, since verify counts only a definition of the hook
verify: grep -q 'def test_a_call_of_the_collection_hook_is_not_a_suppression' subprojects/docket/tests/test_verify.py
reenters: PL-G21K
---

**Problem.** docket verify's no-suppression check counts a call of a function named pytest_ignore_collect as an added suppression, so a test that calls a conftest's hook refuses the close-out audit: three of PL-GQCQ's four refused lines were such calls, and only a definition of the hook or a collect_ignore assignment drops a file from collection

**Evidence.** On 2026-10-25, `bin/docket verify --self PL-GQCQ` refused "no suppression added" on four lines. One is the hook's definition in the root `conftest.py`. The other three are calls in `tests/unit/test_bytecode_guard.py`, such as `ROOT_HOOKS.pytest_ignore_collect(tmp_path / path, config) is None`, which test that hook. A call of the function drops nothing from any collection. The README's own description of the marker says it reads "the hook a `conftest.py` drops a file from collection with", which is a definition.

**The fix.** Count the `pytest_ignore_collect` marker only where a statement defines a function of that name, and keep reading `collect_ignore` and `collect_ignore_glob` as assignments. Replay the narrowing over `main` as the earlier narrowings were.

**Reproduced 2026-10-25.** `is_suppression_line("tests/x.py", line)` returns `True` both for `def pytest_ignore_collect(collection_path, config):` and for `    assert ROOT_HOOKS.pytest_ignore_collect(tmp_path / path, config) is None, path`, which is a call.

**Why it matters.** `bin/docket verify --self` gives no waiver for "no suppression added", so the false reject cannot be cleared from inside the branch. It held `#1797` for the owner's read even though its diff disabled no test. Any later change that tests a conftest hook by calling it will be held the same way. A check that refuses correct work also teaches readers to skim the block where a real suppression appears.

**Done when.** The check counts `pytest_ignore_collect` only in a statement that defines a function of that name. A call of the hook is not counted. A test pins both cases, and the README's description of the marker says the same.

**Generator check.** The fact misread is whether an added statement disables a test, the fact `PL-G21K` heads ("Whether a branch's diff weakens its tests"). That head drained on 2026-09-22 by reading code rather than prose. This item re-enters it with a case its fix did not cover: a statement whose code names a marker without being one. One member in a month does not make the head live again, so the item is fixed here and records `reenters: PL-G21K`, and the fix reads the statement's shape, a definition, rather than a sharper token.
