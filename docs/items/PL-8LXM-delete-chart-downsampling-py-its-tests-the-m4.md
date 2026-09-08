---
id: PL-8LXM
title: Delete chart_downsampling.py, its tests, the M4 paper and every citation of them
priority: P2
effort: M
status: done
classes: refactor, docs
feature: numerical-domain
milestone: v0.4.12
touches: src/anesthesia_sim/app/chart_downsampling.py, tests/unit/test_chart_downsampling.py, docs/references, docs/MODEL.md, ROADMAP.md, docs/WORKING_NOTES.md, docs/items
added: 2026-09-05
closed: 2026-09-08
pr: 488
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

**Closed 2026-09-08.** `app/chart_downsampling.py`, its test, the PDF and its
`docs/references/README.md` entry are gone; `make check` is green with no
dangling citation, which is the check that made the sweep the item rather
than a footnote to it.

**The implementation is recoverable from `d433940`**, the last commit that
carried the module, and the citation it was founded on is preserved above in
full so the paper stays re-findable without staying on disk.

**Where the sweep went beyond the file.** `docs/MODEL.md`'s chart section
stated the drawn set as M4 over recorded samples and now states the two rules
that place an evaluated column; `docs/ARCHITECTURE.md`'s package map, its
render-path paragraph and its PEP 695 example; `docs/WORKING_NOTES.md`'s
rendering-bound note; `ROADMAP.md`'s v0.5.0 Required scope and one stale
module reference; and the tooltip docstring in `app/simulation_view.py`,
which told a reader that a drawn point was "an M4 representative of a bucket
rather than a sample" - the one remaining place the interface described its
own trace in the retired algorithm's terms.

**Two things the sweep turned up that the brief did not name.** The PEP 695
example three open tooling items rest on (`PL-L17Q`, `PL-Y0RZ`, `PL-JRV5`)
was this module's `def first_index_at_or_after[SampleT](`; each is annotated
with the surviving example, `app/chart_series.py`'s `type PlottedSeries`
statement, so the constraint they argue from is still checkable. And
`PL-QXSB`'s "it would make decimation optional" paragraph argued from
machinery that no longer exists; it is rewritten as the claim the measurement
actually supports, about how many columns are affordable.

**Closed items citing the module are left as written.** A brief is the
reasoning at the time it was written, and rewriting a closed one to match a
tree it predates would falsify the record rather than repair it.
