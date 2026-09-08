---
id: PL-ZX12
title: core/run_score.py never defines the musical sense of 'score', so a domain reader meets the term cold in the one module core/ is least able to explain itself in
status: untriaged
added: 2026-09-08
---

**Problem.** core/run_score.py never defines the musical sense of 'score', so a domain reader meets the term cold in the one module core/ is least able to explain itself in

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

**Done when.** The owner has said keep or rename; if rename, the sweep is done
and the release notes are left alone.
