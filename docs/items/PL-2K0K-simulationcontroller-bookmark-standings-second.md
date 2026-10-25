---
id: PL-2K0K
title: SimulationController.bookmark_standings' second and third docstring paragraphs and SimulationView._refresh_bookmarks' docstring use private senses a newcomer cannot parse: 'What the run did is joined by the steps it opened on and stands on, asked now', 'the runs answer one mark differently', 'standings nobody answered', 'load-bearing' (found by PL-YHR3's prose review, out of its scope)
priority: P3
effort: S
status: done
classes: docs
feature: prose-quality
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py
added: 2026-10-19
closed: 2026-10-24
pr: 1766
payoff: a newcomer can follow why each bookmark standing is read from every run, so the reasoning behind what the bookmark panel tells a learner can be checked
verify: ! grep -qF 'What the run did is joined by the steps it opened on and stands on' src/anesthesia_sim/app/controller.py && ! grep -qF 'so the runs answer one mark' src/anesthesia_sim/app/simulation_view.py
---

**Problem.** SimulationController.bookmark_standings' second and third docstring paragraphs and SimulationView._refresh_bookmarks' docstring use private senses a newcomer cannot parse: 'What the run did is joined by the steps it opened on and stands on, asked now', 'the runs answer one mark differently', 'standings nobody answered', 'load-bearing' (found by PL-YHR3's prose review, out of its scope)

**Why it matters.** These docstrings explain why a bookmark's standing is
computed from every run and from the steps a run opened on. A reader who
cannot parse them cannot check that reasoning, and the bookmark panel is a
surface that tells a learner whether a run reached a target. The phrases are
the private senses that `.claude/rules/plain-writing.md` point 3 names.

**Checked 2026-10-19.** On `main` at `1e5cb9bd`, `bookmark_standings` in
`src/anesthesia_sim/app/controller.py` still opens its third paragraph with
"What the run did is joined by the steps it opened on and stands on, asked
now", and `_refresh_bookmarks` in `src/anesthesia_sim/app/simulation_view.py`
still says "the runs answer one mark differently". "load-bearing" is in the
comment below `_refresh_bookmarks`'s docstring.

**Done when.** Both docstrings say the same facts in plain English: what a
standing is computed from, why a mark inside the step a branch opened on reads
as crossed, and why every run's standings are passed. No fact, id or citation
is dropped, and no code changes.
