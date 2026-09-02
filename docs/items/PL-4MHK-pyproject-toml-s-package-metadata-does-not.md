---
id: PL-4MHK
title: pyproject.toml's package metadata does not describe the project - a vague description and no classifiers
priority: P3
effort: S
status: blocked
classes: defect, docs
feature: project-introduction
touches: pyproject.toml
blocked-by: PL-N092
added: 2026-09-01
---

**Problem.** `[project] description` in `pyproject.toml` reads "Open-source
anesthesia simulation project". It names neither what is modeled
(volatile-agent uptake and distribution, three agents, one reference adult)
nor the educational-only limit that `README.md` and the running application
both state. `pyproject.toml` declares no `classifiers` at all either, so the
package makes no machine-readable statement of maturity, audience, or
subject.

**Why it matters.** These are displayed statements about a clinically
flavored tool, and they travel further than the file they live in: the
description is the package summary surfaced by `uv pip show`, by any wheel
built from this tree, and by PyPI if the project is ever published there.
"Anesthesia simulation project" read cold implies a broader and more clinical
scope than the model has. Presentation correctness is part of the
safety-critical standard, so the summary a package carries should match the
one `README.md` opens with rather than being a looser paraphrase of it.

The missing `classifiers` is the same gap in machine-readable form. The
project is early - v0.2.7, with the MVP three feature releases away per
`ROADMAP.md` - and nothing in the package metadata says so. A
`Development Status` classifier is the standard way to say it and costs one
line.

**Where.** `pyproject.toml`, the `[project]` table. The wording should agree
with `README.md`'s opening paragraph.

The GitHub repository "About" description is the same sentence in a different
box, and it is **still unset**: the project owner reviewed three rounds of
drafts on 2026-09-01, rejected all of them, and deferred the wording. Do not
write one here on the assumption the other exists, and do not treat the three
rejected directions as available - they are recorded under "Open thread: the
project's one-line self-description" in `docs/WORKING_NOTES.md`.

Sequencing: `PL-N092` (rewrite `README.md` as a human-readable introduction)
settles the same register question at length and with more room to get it
right. This item should follow it rather than lead it.

**Done when.** `description` names what is modeled and states the
educational-only limit; `classifiers` exists and carries at least a
`Development Status`, an `Intended Audience`, and a `Topic` entry, each an
exact string from <https://pypi.org/classifiers/>; and the wording agrees
with `README.md`'s opening. Where the GitHub "About" description has been set
by then, it agrees with that too. Consider whether `tools/doc_check.py` can
decide that agreement rather than leaving it to a reader; if it cannot, say
so here rather than adding a check that guesses.

**Notes.** Candidate classifier strings, verified against
<https://pypi.org/classifiers/> on 2026-09-01: `Development Status :: 3 -
Alpha`, `Intended Audience :: Healthcare Industry`, `Topic :: Scientific/
Engineering :: Medical Science Apps.` (the last is one string, wrapped here).
Whether `3 - Alpha` or `2 - Pre-Alpha` is the honest row is the project
owner's call.
