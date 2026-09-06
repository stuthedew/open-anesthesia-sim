---
id: PL-GQWP
title: The new README publishes the playback-rate ladder, the chart time-base range and the agent list, and nothing holds any of the three to the code
priority: P2
effort: S
status: ready
classes: docs, test
feature: project-introduction
touches: README.md, tests/unit/test_playback.py, src/anesthesia_sim/app/playback.py, src/anesthesia_sim/app/chart_time_base.py, tools/doc_check.py
added: 2026-09-06
verify: uv run pytest tests/unit/test_playback.py && grep -q 'README.md' tests/unit/test_playback.py
---

**Problem.** `README.md` § "What it simulates" states three capability facts
whose authority is a Python constant, and nothing compares the two:

- the playback ladder, written `1x, 5x, 20x, 60x or 300x real time`, which is
  `SUPPORTED_PLAYBACK_RATES` in `src/anesthesia_sim/app/playback.py`;
- the chart time base, written "from fifteen minutes to twelve hours", which is
  `SELECTABLE_TIME_BASES` filtered by `SELECTABLE_TIME_BASE_FLOOR_S` in
  `src/anesthesia_sim/app/chart_time_base.py`;
- the agents, written "sevoflurane, isoflurane or desflurane", which is the set
  of files in `src/anesthesia_sim/data/agents/`.

**Why it matters.** This is the failure `PL-NBWP` already fixed once, for a
different document. `test_the_control_grid_at_each_rate_is_the_one_two_documents_publish`
in `tests/unit/test_playback.py` holds the rate ladder to *two* documents -
`app/playback.py`'s own docstring and `docs/MODEL.md` § "Supported simulation
step" - and the README is neither of them, because the README did not exist
when that test was written. So adding a rung today updates the code, the
docstring and `docs/MODEL.md`, and leaves the front page asserting the old
ladder with every check green.

It is a presentation-correctness question rather than a tidiness one. A reader
deciding whether the simulator can show them a fat compartment filling is
reading the top rate; a reader deciding whether a case fits one view is reading
the time-base range. Neither is a model-coupled statement - which is exactly why
`PL-RM83`'s boundary rule allows them on the front page, and why the front page
is now the only place they are stated with nothing behind them.

**Where.** `README.md` § "What it simulates"; the three constants above;
`tools/doc_check.py`, which already holds `README.md` in `DOC_GLOBS` and already
resolves its cited paths and `make` targets, so the document is in the checker's
hands and only this class of claim is unchecked.

**Approach, and the judgment in it.** The decidable half is small and the
scriptable form is not obvious, because prose is prose: "from fifteen minutes to
twelve hours" cannot be parsed out of an arbitrary sentence. Two candidates:

1. *Extend the playback test to a third document.* Cheapest, and it reaches only
   the rate ladder: `PUBLISHED_CONTROL_GRID_S` is already the shared table, and
   the test would assert every offered multiplier appears in the README's
   sentence. Narrow, exact, no new mechanism.
2. *A marked-value convention for the README, as `docs/MODEL.md` already has.*
   `check_prose_provenance` in `tools/doc_check.py` holds `docs/MODEL.md`'s
   prose numbers to the data files through an HTML-comment marker, and the same
   shape would work here against a constant rather than a JSON key. Wider reach,
   and a new marker vocabulary to maintain for three facts.

Option 1 first regardless; whether option 2 is worth its upkeep for three
sentences is the decision, and `CLAUDE.md`'s "the gate is whether it will
genuinely run again" is the test to answer it against.

**Done when.** Adding a playback rung, moving the time-base floor or ceiling, or
shipping a fourth agent fails a check while `README.md` still states the old
one - or the project has recorded, with the reason, that it will not.

**Notes.** Found 2026-09-06 while writing the README under `PL-N092`, which is
what created all three claims. Not fixed there: the README was the item, and a
check is its own change with its own decision in it.
