---
id: PL-6GP9
title: tools/ast_identity.py reports a file as 'changed' when only an attribute docstring (a bare string statement after an assignment) changed, because it strips only each body's first string statement, so the release cut of v0.6.7 read exit 1 for 19 src/ files whose code is identical once every bare string statement is removed; it is another reader of PL-8W1J's which-literals-are-docstrings fact (found cutting PL-LSN3)
status: untriaged
feature: one-source-of-truth
added: 2026-10-25
---

**Problem.** tools/ast_identity.py reports a file as 'changed' when only an attribute docstring (a bare string statement after an assignment) changed, because it strips only each body's first string statement, so the release cut of v0.6.7 read exit 1 for 19 src/ files whose code is identical once every bare string statement is removed; it is another reader of PL-8W1J's which-literals-are-docstrings fact (found cutting PL-LSN3)
