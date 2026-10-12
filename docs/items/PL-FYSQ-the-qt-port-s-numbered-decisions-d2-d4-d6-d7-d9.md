---
id: PL-FYSQ
title: The Qt port's numbered decisions D2, D4, D6, D7, D9 and D10 are cited 15 times in app/ docstrings and one test, as (PL-25KS, decision Dn), but no file in the tree defines them: not PL-25KS's brief and not docs/pr-bodies/588.md
status: untriaged
added: 2026-10-12
---

**Problem.** The Qt port's numbered decisions D2, D4, D6, D7, D9 and D10 are cited 15 times in app/ docstrings and one test, as (PL-25KS, decision Dn), but no file in the tree defines them: not PL-25KS's brief and not docs/pr-bodies/588.md

**Found 2026-10-12** by a review pass over `#1442` (PL-7CRY, PL-Y4YX), which
kept three of them while moving or editing the sentences around them.
`git grep -nE "decision D[0-9]+" -- src tests` lists fourteen, and a fifteenth
breaks across a line in `app/stylesheets.py`'s module docstring: D2 four times,
D4 four, D7, D9 and D10 twice each and D6 once, in `dashboard_frame.py`,
`qt_widgets.py`, `run_view.py`, `simulation_view.py`, `stylesheets.py` and
`tests/unit/test_dashboard_frame.py`. `git log -G'decision D9'` finds them only
in the port commit `ae8fc7bc` (`#588`) and in `#1442`, so the numbered list
lived in a session's design reply and never reached the repository.

Each citation states its decision's content where it stands - "a slider
position is a printed value" for D4 - so nothing is lost but the handle; the
cost is a reader who goes looking for the list and finds nothing. Two
dispositions, either cheap: write the list once where `PL-25KS` would carry it,
or drop the numbers and keep the item id each citation already names.
