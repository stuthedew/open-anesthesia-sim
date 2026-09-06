---
id: PL-4MHK
title: pyproject.toml's package metadata does not describe the project - a vague description and no classifiers
priority: P3
effort: S
status: done
classes: defect, docs
feature: project-introduction
touches: pyproject.toml, docs/WORKING_NOTES.md
blocked-by: PL-N092
added: 2026-09-01
closed: 2026-09-06
verify: python3 tools/doc_check.py check && grep -qF 'not a medical device: not for clinical prediction' pyproject.toml && grep -qF 'Topic :: Scientific/Engineering :: Medical Science Apps.' pyproject.toml
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

---

**Resolution, 2026-09-06.** `description` and `classifiers` are set; the
`readme` key this item was also expected to restore had already come back with
`PL-N092`'s README in `#391`, so nothing was owed on it here.

**The two questions this item left open, answered.**

*Which `Development Status` row is honest* — **`3 - Alpha`**. A case runs end
to end: v0.4.0 shipped the teachable case and v0.4.4 the exact propagator, which
is past the row meaning "not yet functional". It is not `4 - Beta` because the
MVP is still ahead (`ROADMAP.md` row 5, v0.5.0) and there is no packaged build.
This does not contradict the "PRE-RELEASE" banner the owner put on `README.md`
in `#394` and in the GitHub "About" field: alpha *is* a pre-release stage, and
`Development Status` classifies maturity rather than distribution. Flipping to
`2 - Pre-Alpha` is a one-line change if the owner reads it the other way.

*Whether `tools/doc_check.py` can decide the agreement* — **it cannot**, on
both halves, so no check was added.

- **Against the GitHub "About" field: impossible in principle.** That text is
  not in the tree. `doc_check.py` is standard-library only and must answer in a
  bare offline checkout, so reaching it would mean a network call from
  `make check`.
- **Against `README.md`: only by forcing the wording.** A substring test is the
  sole non-guessing form available, and it would require the summary to quote
  the README verbatim. It does not, deliberately - see below. Making it quote
  the README to satisfy a tool would be scripting the judgment, which
  `CLAUDE.md` forbids.

**The wording could not satisfy both sources, and that is now `PL-XF89`.**
`README.md:5` says "**inhaled**-anesthetic"; the "About" field says
"**volatile**-anaesthetic". The summary follows "volatile", because a package
`Summary` describes the artifact carrying it and 0.4.4 models three volatile
agents only - `README.md`'s own "What it does not simulate" leads with nitrous
oxide and any second gas. `PL-XF89` carries the three-way decision and the
US/British spelling split in the "About" field.

**Measured while closing this, and worth knowing before trusting the build.**
`uv build` 0.12.7 does **not** validate classifier strings: it built both
artifacts from a `Development Status :: 3 - Alpah` typo with no warning, so a
misspelling would ship in `PKG-INFO` and surface only at a PyPI upload this
project does not perform. It also does not refuse a `License ::` classifier
beside the SPDX `license` expression - it warns ("ambiguous and deprecated per
PEP 639") and builds. The five strings here were therefore checked by hand
against <https://pypi.org/classifiers/>, fetched 2026-09-06.

**No check was built for that either**, on `CLAUDE.md`'s retirement test: it
would need a vendored copy of a ~900-row list to run offline, to guard five
strings that change about once a release train, and would then pass on every
`make check` without ever changing a decision. The verified metadata as
shipped, from `PKG-INFO` in the built sdist:

```text
Summary: A deterministic simulator of volatile-anesthetic uptake and distribution, built for teaching. An educational tool, not a medical device: not for clinical prediction, dosing, or monitoring.
License-Expression: Apache-2.0
Classifier: Development Status :: 3 - Alpha
Classifier: Intended Audience :: Education
Classifier: Intended Audience :: Healthcare Industry
Classifier: Topic :: Education
Classifier: Topic :: Scientific/Engineering :: Medical Science Apps.
```

