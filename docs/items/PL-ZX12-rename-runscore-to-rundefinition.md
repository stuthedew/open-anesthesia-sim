---
id: PL-ZX12
title: Rename RunScore to RunDefinition: 'score' is a metaphor a domain reader has to be taught, in the package that should read like the domain
priority: P2
effort: S
status: done
closed: 2026-09-13
classes: refactor, docs
feature: core-domain-language
touches: src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_run_definition.py, tests/unit/test_simulation_view.py, tests/integration/test_controller.py, tests/integration/test_chart_patching.py, tests/integration/test_sevo_controller.py, tests/reference/test_canonical_evaluation.py, docs/ARCHITECTURE.md, docs/MODEL.md, docs/WORKING_NOTES.md, ROADMAP.md, docs/items/PL-49R8-a-path-scoped-rule-that-stops-a-session-re.md
added: 2026-09-08
verify: test -f src/anesthesia_sim/core/run_definition.py && ! grep -rqE 'RunScore|ScoreSegment|run_score' src/ tests/
---

**Problem.** `core/run_score.py` holds a run as its *score*, and never says what
that word means. The term is not from anesthesia, and it is carrying the whole
idea of the module.

The term is introduced in italics - "the settings in force at each moment -
the *score*" - in the shape of a definition, and then never defined. Nowhere
in `core/`, `docs/MODEL.md` or `PL-T691` does any line say which sense of the
word is meant. `docs/MODEL.md` § "The run is that record, and every state is
derived from it" describes the whole mechanism without using the word at all,
so a reader who wonders cannot resolve it by reading further.

**Why it matters here specifically.** `.claude/rules/core-domain.md` asks that
`core/` read like the domain. "Score" is not an anesthesia term, so it is
carrying a metaphor from outside the domain into the one package held to that
bar - which is defensible, and is exactly the case that owes the reader a
sentence. The project owner asked what the word meant while reading this
module (2026-09-08), which is the evidence.

**Half of this is already done (`PL-2FM6`, 2026-09-08).** The module docstring
now states the musical sense: the written instruction set a performance is
produced from rather than a recording of one, alongside the note that
`Keyframe` is the same vocabulary borrowed from animation, and that the names
to reject are the ones suggesting a stored trajectory.

**What is left is a decision, and it is the project owner's.** They asked
whether the module should be `run_core` instead. The recommendation is **no**,
for a reason specific to this tree rather than to taste: `core/` is already
the package name that carries `CLAUDE.md`'s Flet-independence boundary, so
`core/run_core.py` makes the word mean two different things in one path and
reads as "the central part of a run", which is vaguer than what this is. The
literal alternative, `control_timeline`, is worse still: it is already taken
in the app layer, where `snapshot().control_timeline` is the record of *user
acts* rather than of equation settings, and the two are deliberately different
records (`controller.score_segments`' docstring says so).

So the options are keep `score` with the definition now in place, or pick a
third name. If a rename is wanted, the cost is mechanical but wide: the module,
its test, `RunScore`, `ScoreSegment`, `controller.score_segments`,
`run_score.py`'s citations in `docs/MODEL.md` and `ROADMAP.md`, and the word
"score" throughout the v0.4.8 release notes, which are history and should not
be rewritten.

**Decided 2026-09-08: rename it** (project owner). The recommendation above was
to keep `score` now that the definition exists; the owner's answer is that a
term needing a definition in `core/` is the problem rather than the missing
definition, and that stands. The definition already landed and is kept: it
explains the name the history will still carry.

**The name: `RunDefinition`, in `core/run_definition.py`.** Plain English,
no metaphor to learn, and no collision anywhere in the tree - which is the
whole of what is being bought here. `ScoreSegment` becomes `RunSegment` and
`SimulationController.score_segments` becomes `run_segments`. The alternative
worth naming is `RunTimeline`, which has the merit of being `PL-T691`'s own
phrase ("the run is its control-input timeline"), and the demerit that the app
layer's `snapshot().control_timeline` is a *different* record - the acts a user
made, not the settings the equations were assembled from - so two timelines
would sit one call apart meaning different things.

**Sequencing, which is not free (found 2026-09-08).** This lands **after
`PL-8LXM` and before `PL-49R8`**, and both halves of that are load-bearing:

- *After `PL-2FM6` and `PL-8LXM`.* Both are rewriting `core/run_score.py`,
  `app/controller.py`, `app/chart_series.py` and `app/simulation_view.py` right
  now, and `PL-8LXM`'s citation sweep already opens `docs/MODEL.md`,
  `ROADMAP.md` and `docs/WORKING_NOTES.md` - the same documents this sweep
  touches. Renaming first means renaming code about to be deleted; renaming
  straight after means the docs are opened once rather than twice.
- *Before `PL-49R8`.* That item specifies its rule file as
  `.claude/rules/run-is-its-score.md` and its `verify:` command greps that
  exact path. Written before this rename, the rule is born carrying the term
  being retired, in the one file whose whole job is telling a future session
  how this architecture works. `PL-49R8`'s filename and `verify:` move with
  this item.

**Size.** 60 occurrences across six `.py` files and 10 across
`docs/ARCHITECTURE.md`, `docs/MODEL.md` and `ROADMAP.md`. `docs/releases/`
carries it once, in `v0.4.5.md`'s "score architecture", and release notes are
history: left alone deliberately, which is why the docstring definition stays
in whatever the module ends up called.

**Done when.** The module, its classes and `score_segments` are renamed;
`docs/ARCHITECTURE.md`, `docs/MODEL.md` and `ROADMAP.md` follow; the
docstring's explanation of the retired term is kept for the history that still
uses it; `docs/releases/` is untouched; and no `RunScore`, `ScoreSegment` or
`run_score` remains under `src/` or `tests/`.

**`PL-8LXM` closed 2026-09-08, so this is unblocked and deferred rather than
blocked** (project owner, same day): the M4 cleanup was the scope that was
approved, and the rename is its own piece of work. The sequencing note above
still holds for whoever takes it - it lands before `PL-49R8`, which now waits
on this item rather than on `PL-2FM6`.
