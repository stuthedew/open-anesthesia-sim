---
id: PL-QDH7
title: tools/ promises standard-library-only imports and nothing guards it, the way the parse floor now is
priority: P2
effort: S
status: ready
classes: defect, infra
feature: dev-tooling
touches: tests/unit/test_tools_portability.py
added: 2026-09-01
verify: uv run pytest tests/unit/test_tools_portability.py -k imports
---

**Problem.** `tools/doc_check.py`'s module docstring promises "standard
library only ... so this runs in a bare checkout exactly as it runs in CI",
and `tools/ruff.toml` repeats it. Nothing checks it. A tool added under
`tools/`, or an import added to this one, can reach a package that only exists
inside the project virtualenv, and `make check`'s `python3 tools/doc_check.py
check` then fails with `ModuleNotFoundError` in exactly the environments the
promise was made for.

**Why it matters.** This is the other half of the promise PL-921W guarded.
That item pinned the formatter so `tools/` cannot be rewritten into syntax bare
`python3` rejects, and widened the parse assertion to every file there.
The import half is the same promise, the same blast radius, and the same
"fixed where it fired, left where it also applies" shape PL-921W and PL-J295
both describe. `subprojects/docket/tests/test_portability.py` already guards
its own package with an `ALLOWED_IMPORTS` allowlist, so `tools/` is again the
second place a guard exists for the first.

**Where.** `tests/unit/test_tools_portability.py`, which PL-921W created and
which already reads `tools/` with `ast` for the parse check - the import walk
is the same traversal.

**Approach.** Prefer `sys.stdlib_module_names` over a hand-maintained
allowlist: it is a frozenset in the standard library since 3.10, so the test
needs no list to keep current, and it answers for the interpreter running the
test rather than for the one somebody remembered. Allow `docket` alongside it,
which `doc_check.py` imports deliberately from `subprojects/docket/src` for the
release-train grammar and which is itself standard-library-only. Deliberately
left out of PL-921W as scope beyond its "Done when", not as a judgment that it
is unnecessary.

**Done when.** A test fails if any file under `tools/` imports a module that is
neither in the standard library nor `docket`.

**Triaged and admitted to v0.2.8's frozen list, 2026-09-01.** P2,
`defect`/`infra`, `dev-tooling`, beside `PL-921W` in the "stops new debt being
introduced" group. Admitted under the scope test rather than the completion
rule: `PL-921W` is closed and shipped, and this is not what that entry needed
in order to be finished — it is the second half of the same promise, and the
lint gate is one of the pieces of machinery this release's goal names.

`verify:` was run before it was written down, and watched to fail: with no
matching test, `uv run pytest tests/unit/test_tools_portability.py -k imports`
deselects all three tests and exits 5, which is a failure. It passes once the
import test exists.
