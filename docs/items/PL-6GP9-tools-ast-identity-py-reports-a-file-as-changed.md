---
id: PL-6GP9
title: tools/ast_identity.py reports a file as 'changed' when only an attribute docstring (a bare string statement after an assignment) changed, because it strips only each body's first string statement, so the release cut of v0.6.7 read exit 1 for 19 src/ files whose code is identical once every bare string statement is removed; it is another reader of PL-8W1J's which-literals-are-docstrings fact (found cutting PL-LSN3)
priority: P2
effort: S
status: done
classes: defect
feature: one-source-of-truth
touches: tools/ast_identity.py, tools/fixture_id_check.py, subprojects/docket/src/docket/python.py, tests/unit/test_ast_identity.py, subprojects/docket/tests/test_python.py, docs/apparatus.md
added: 2026-10-25
closed: 2026-10-25
pr: 1810
payoff: a release cut's ast_identity verdict calls an attribute-docstring rewrite unchanged, so it no longer forces a trajectory comparison or a hand proof
verify: uv run pytest -q tests/unit/test_ast_identity.py subprojects/docket/tests/test_python.py -k 'attribute_docstring or without_docstrings'
reenters: PL-8W1J
---

**Problem.** tools/ast_identity.py reports a file as 'changed' when only an attribute docstring (a bare string statement after an assignment) changed, because it strips only each body's first string statement, so the release cut of v0.6.7 read exit 1 for 19 src/ files whose code is identical once every bare string statement is removed; it is another reader of PL-8W1J's which-literals-are-docstrings fact (found cutting PL-LSN3)

**What was done.** The removal of docstrings from a syntax tree now has one
home, `docket.python.without_docstrings`, which removes every string that
`docket.python.docstrings` returns. `tools/fixture_id_check.py` held that
function already, so it moved to `docket.python` and the check imports it.
`tools/ast_identity.py` now calls it too, instead of removing only the first
string of each body. `tools/fixture_id_check.py`'s copy was the only other
one: `glyph_check` and `doc_check` read `docstrings` itself and remove nothing.

Removing every string statement hides no executable change. A string that
stands as a statement on its own has no effect when the program runs, apart
from the first one's `__doc__`, which the tool already ignored.

Measured on the real history: `uv run python tools/ast_identity.py v0.6.6
v0.6.7 src` now ends "no code moved in 76 files" and exits 0. Before this
change it exited 1 and named 19 files.

**Generator check.** A reader of `PL-8W1J`'s fact, which strings are
docstrings, that `PL-8W1J`'s sweep did not reach. Recorded as `reenters:
PL-8W1J`. With the removal itself in `docket.python`, no tool spells it again.
