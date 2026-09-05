---
id: PL-8LXM
title: Delete chart_downsampling.py, its tests, the M4 paper and every citation of them
priority: P2
effort: M
status: blocked
blocked-by: PL-2FM6
classes: refactor, docs
feature: numerical-domain
touches: src/anesthesia_sim/app/chart_downsampling.py, tests/unit/test_chart_downsampling.py, docs/references, docs/MODEL.md, ROADMAP.md, docs/WORKING_NOTES.md, docs/items
added: 2026-09-05
verify: make check && ! test -e src/anesthesia_sim/app/chart_downsampling.py
---

**Problem.** With `PL-2FM6` landed, `app/chart_downsampling.py` (671 lines)
and `tests/unit/test_chart_downsampling.py` (15 KB) have no consumer. Kept
un-wired they still cost the lint, type-check and coverage gates on every run,
which is what `CLAUDE.md`'s "a check earns its place every run, or it is
retired" is against.

**Why it matters.** Dead code in the tree reads as live code. A session
opening `app/` finds a fully documented, fully tested downsampling module and
has no way to tell it is unreachable, so the next chart change is at risk of
being built against it. The same applies to the paper: `docs/references/` is
where a session looks to learn what the code is founded on, and an entry
nothing founds is a false signal about what the simulator does. The gates are
the smaller cost; the misleading signal is the real one.

**This is good work being removed, not bad work being fixed.** The module's
departure-from-Theorem-1 analysis is more careful than most published
implementations of M4. It is removed because the architecture deleted the
problem it solves, and the deletion should say so.

**What goes with it.** The scope is the sweep, not the file:

- `src/anesthesia_sim/app/chart_downsampling.py` and its test.
- `docs/references/jugel-2014-m4-visualization-oriented-time-series-aggregation.pdf`
  **and its entry in `docs/references/README.md`.** That directory holds papers
  the code cites; a paper no code cites is a question a reader has to answer
  (project owner, 2026-09-05). The citation is preserved in this item instead,
  in full, so the paper stays re-findable without staying on disk:

  > Jugel U, Jerzak Z, Hackenbroich G, Markl V. M4: A Visualization-Oriented
  > Time Series Data Aggregation. *Proceedings of the VLDB Endowment*.
  > 2014;7(10):797-808. ISSN 2150-8097.

- Every citation of the module: `docs/MODEL.md`, `ROADMAP.md`,
  `docs/WORKING_NOTES.md`, and about ten queue items including
  `PL-5CGK`, `PL-W3DD`, `PL-8GLL` and `PL-YDKJ`. `tools/doc_check.py` decides
  the dangling-citation question, so `make check` stays red until this is done
  — which is the check working, and is why the sweep is the item rather than a
  footnote to it.

**What would bring it back, stated as a precondition rather than a
capability.** A series that **cannot be re-derived from its inputs**. Nothing
in the simulator or on the roadmap produces one — planned items 13 to 19 (IV
PK, eBIS, nociception, renal/hepatic modifiers, CPB, ECMO, species profiles),
27 and 28 are all deterministic functions of the score, checked 2026-09-05.
The likelier future trigger is different and does **not** want M4: a model
component that stops being closed-form (the nonlinear concentration and
second-gas effects at planned items 6 and 7) needs *more keyframes* at a
spacing set by a solver's error control, not a dyadic ladder over millions of
raw samples.

The implementation and its analysis remain recoverable from this repository's
history; record the commit here at closure. `PL-49R8` is the rule that puts
that pointer where a session will meet it.

**Done when.** The module, its test, the PDF and its README entry are gone;
`make check` is green with no dangling citation; `PL-5CGK` is closed against
this item; and this item records the commit the implementation is recoverable
from.
