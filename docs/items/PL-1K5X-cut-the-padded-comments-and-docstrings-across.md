---
id: PL-1K5X
title: Cut the padded comments and docstrings across src/
priority: P2
effort: M
status: done
classes: docs
feature: prose-quality
milestone: v0.6.7
touches: src/anesthesia_sim/core, src/anesthesia_sim/data, src/anesthesia_sim/app, src/anesthesia_sim/layout, src/anesthesia_sim/app_metadata.py, docs/items/PL-21KP-present-tense-flet-claims-survive-the-qt-port.md
added: 2026-09-05
closed: 2026-10-25
pr: 1798
verify: ! grep -qF 'Mass-balance accounting: verify that a simulation run neither creates nor' src/anesthesia_sim/core/agent_simulation_validation.py && ! grep -qF 'Exception hierarchy for what the layout package refuses.' src/anesthesia_sim/layout/exceptions.py && ! grep -qF 'in place give way before the Areas that it did. An Area that gives way shrinks' src/anesthesia_sim/app/area_layout.py
not-delegable: readability is judged by a person, and no command separates a trimmed comment from a padded one. A length ceiling would be met by deleting the provenance note this item exists to keep, which is the one outcome it forbids. `touches` reaches `src/anesthesia_sim/core` and `src/anesthesia_sim/data` besides, which delegation may never modify
---

**Problem.** The comments and docstrings in `src/` are, in the project owner's
reading (2026-09-05), far too verbose and poorly written. One of two halves
split out of `PL-XXBD` (rewrite the code comments across `src/` and `tests/`),
which was `L` and therefore unstartable from the queue.

**Measured 2026-09-05, with the tokenizer:** roughly 4,600 of `src/`'s ~9,700
lines are comment or docstring prose - about half the tree. It is concentrated
in `src/anesthesia_sim/app` (~3,800 lines of prose in ~7,300), with
`src/anesthesia_sim/core` carrying ~790 in ~2,300 and `src/anesthesia_sim/data`
effectively none. That is where the two standards below divide, and it is worth
knowing before starting: most of the volume is UI prose, and most of the care
is owed to a tenth of it.

**Why it matters.** The standard is **human readability**, and that is the
whole of it: a person opening the file should reach the point faster and
understand more. Wordiness is the defect and cutting it is the fix. [superseded 2026-10-17: the defect is compressed wording; see the re-aim note below] This is
deliberately *not* the standard `PL-JK0M` applies to the agent-facing
instruction files, where cutting a rule for being wordy is the forbidden
outcome.

**The safety-critical qualifier, which lands almost entirely in `core/`.** In a
calculation path, padding around the reasoning is what hides it, so trimming
serves the reviewer. What a comment must never lose is the *why* - a provenance
note, a unit, a cited equation, or the reason a value is what it is. Shorten
the prose, keep the fact.

**Where.** `src/`. Counts are measured 2026-09-05 and rounded because they move every release; re-measure before starting rather than trusting them - they are here for ordering, not as a claim.

**Done when.** Every comment and docstring under `src/` has been read and,
where it was padded, cut: nothing restating the line below it, no docstring
paragraph repeating its own first sentence, no clause that adds nothing. Every
*why* is still on the page - each provenance note, unit, cited equation and
reason-a-value-is-what-it-is, in the same file it was in. `make check` passes.

**Re-aimed 2026-10-17 by `PL-8ZTQ`.** A blind sample of 91 passages found that
the main defect is compressed wording, not padding. Readers stumbled on
dropped small words, ordinary words used in private senses, sentences carrying
several claims, and unclear references. Padding blocked reading in none of
them. So the work is to rewrite each awkward sentence as
`.claude/rules/plain-writing.md` says, and to cut only text that repeats
itself. Where this brief says to cut prose, read it that way. The rewritten
text may come out longer.

Start with the code the rules name as the instance to read first, such as
`src/anesthesia_sim/core/tissue.py`, because sessions copy it.

**Done 2026-10-25.** Every docstring and `#` comment under `src/` was
rewritten as `.claude/rules/plain-writing.md` says, file group by file group.
One agent rewrote each group, and a second compared it with the original and
repaired any fact that was lost, changed or blurred. A script then checked
each file against `main`: the code with docstrings removed must be identical,
directive comments must match, and every code span, item id, pull request
number, URL, number and section reference must survive. `make check`'s
checks pass, and so does the full test suite. Where `main` changed a
passage after the rewrite began (`PL-F9TC`'s `MacPercent` in `app/`), the
passage keeps `main`'s text.

The rewrite changed no fact, so the stale facts its agents found were filed
instead, under the `stale-source-claims` feature: `PL-756M` (code spans naming
symbols that do not exist), `PL-DP7B` (two `core/` docstrings describing older
code) and `PL-0Z35` (five `app/` comments). Two more Flet claims were added to
`PL-21KP`, which already covers them.
