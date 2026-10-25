---
id: PL-6GP9
title: tools/ast_identity.py reports a file as 'changed' when only an attribute docstring (a bare string statement after an assignment) changed, because it strips only each body's first string statement, so the release cut of v0.6.7 read exit 1 for 19 src/ files whose code is identical once every bare string statement is removed; it is another reader of PL-8W1J's which-literals-are-docstrings fact (found cutting PL-LSN3)
status: untriaged
feature: one-source-of-truth
added: 2026-10-25
---

**Problem.** tools/ast_identity.py reports a file as 'changed' when only an attribute docstring (a bare string statement after an assignment) changed, because it strips only each body's first string statement, so the release cut of v0.6.7 read exit 1 for 19 src/ files whose code is identical once every bare string statement is removed; it is another reader of PL-8W1J's which-literals-are-docstrings fact (found cutting PL-LSN3)

**Next steps, written 2026-10-25 by a thread that stopped for length before starting it.** `tools/ast_identity.py`'s `without_docstrings` (line 68) strips only the first string statement of each body. The home of "which strings are docstrings" is `docket.python.docstrings` in `subprojects/docket/src/docket/python.py`, which `PL-8W1J` made the one reading: every string that is a statement of its own, attribute docstrings included. Make `without_docstrings` read that function instead of deciding again. `tools/fixture_id_check.py` has its own `without_docstrings` (line 297), so check whether it is a third copy of the same fact.
