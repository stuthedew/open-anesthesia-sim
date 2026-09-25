---
id: PL-5SNG
title: .claude/hooks/floor-interpreter-guard.sh names one 3.11 collision (app_metadata.py) and six uv-run tools, where app/bookmarks.py:451 is a second collision and seven ast tools run under uv, and neither its comments nor its deny message say doc_check and possessive_section_check also parse source and decline at the floor
status: untriaged
added: 2026-09-24
---

**Problem.** .claude/hooks/floor-interpreter-guard.sh names one 3.11 collision (app_metadata.py) and six uv-run tools, where app/bookmarks.py:451 is a second collision and seven ast tools run under uv, and neither its comments nor its deny message say doc_check and possessive_section_check also parse source and decline at the floor

**Found 2026-09-24, closing `PL-MB3F`.** Read against the tree at that close:

- Line 15 says "The collision is one line", naming `app_metadata.py:92`
  (PEP 758). `app/bookmarks.py:451` (PEP 695, `def _looked_up[Mark: ...]`)
  has also failed under 3.11 since 2026-09-20.
- Line 40 says `make check` runs "six of them under `uv run python`". It runs
  seven ast-parsing tools there, and since `PL-MB3F` also `doc_check.py` and
  `possessive_section_check.py`.
- The deny message (lines 137-141) lists six tools, missing
  `fixture_id_check.py`, and names only `app_metadata.py`.
- `tests/unit/test_floor_interpreter_guard.py:86-88` allows
  `python3 tools/doc_check.py check` on the ground that "`make check` and the
  CI floor section run these bare on purpose". Only the CI floor section does
  now. The allowance itself is still right: bare `doc_check` names what it
  cannot parse rather than failing.

Wording only. What the hook refuses is unchanged.
