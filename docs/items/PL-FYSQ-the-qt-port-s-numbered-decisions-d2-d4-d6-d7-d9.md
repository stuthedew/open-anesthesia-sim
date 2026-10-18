---
id: PL-FYSQ
title: The Qt port's numbered decisions D2, D4, D6, D7, D9 and D10 are cited 15 times in app/ docstrings and one test, as (PL-25KS, decision Dn), but no file in the tree defines them: not PL-25KS's brief and not docs/pr-bodies/588.md
priority: P3
effort: S
status: done
classes: docs
touches: docs/items/PL-25KS-port-the-dashboard-to-pyside6-the-readout-row.md
added: 2026-10-12
closed: 2026-10-18
pr: 1556
payoff: a reader following (PL-25KS, decision D4) from a docstring finds the decision and every other site it governs
verify: grep -qF 'D10' docs/items/PL-25KS*.md
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

**Why it matters.** A handle that resolves nowhere sends a reader to `PL-25KS`
and `#588` for a list neither holds, and the four citations of D2 lose what ties
them together: that one decision governs all four sites.

**Decided at the 2026-10-12 triage pass: write the list.** Each citation
already states its decision's content, so the list is assembled from the
fifteen citations rather than recalled, and it keeps the cross-site handle that
dropping the numbers would lose. It is one edit to one item file, where dropping
the numbers is fifteen edits across six files under `src/` and `tests/`.

**Done when.** `PL-25KS`'s brief carries a dated section listing D2, D4, D6,
D7, D9 and D10, each in the words its citations use, marked as assembled from
them on that date, and naming the sites that cite it.

**Generator check.** A one-off: a design reply's numbered list that never
reached the repository, cited by the commit built from it. No head's
`misread:` states it.
