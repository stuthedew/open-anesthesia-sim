---
id: PL-MXLV
title: docs/ARCHITECTURE.md says contrast_check.py reads colours with ast because 'these tools run under a bare python3', which has not been true of it since PL-L17Q and which the same file contradicts at line 1158
status: untriaged
added: 2026-09-22
---

**Problem.** docs/ARCHITECTURE.md says contrast_check.py reads colours with ast because 'these tools run under a bare python3', which has not been true of it since PL-L17Q and which the same file contradicts at line 1158

The paragraph at `docs/ARCHITECTURE.md:730` reads: "It reads the color constants
with `ast` rather than importing them, because the interface imports PySide6 and
these tools run under a bare `python3`". Two claims, and the second is false of
this tool: `PL-L17Q` moved `contrast_check.py` onto the `uv run python` lines in
both the `Makefile` and `quality.yml`, because its input carries 3.12+ syntax a
3.11 parser cannot read. The same file states that correctly at line 1158, so
the document contradicts itself within one page.

The reason that survives is the *dependency* one, which
`tests/unit/test_tools_portability.py` states as "the promise is about what a
tool depends on, not about what it can read": a bare checkout or a hook has no
PySide6 to import, which is why the constants are read rather than imported -
whatever interpreter runs the tool.

**Done when** that sentence gives the dependency reason without the
interpreter claim, and nothing on the page says `contrast_check.py` runs at the
bare-`python3` floor.
