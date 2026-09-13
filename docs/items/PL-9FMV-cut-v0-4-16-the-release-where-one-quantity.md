---
id: PL-9FMV
title: "Cut v0.4.16: the release where one quantity stopped being stated two ways"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-13
closed: 2026-09-13
pr: 514
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.16"' pyproject.toml && test -f docs/releases/v0.4.16.md
---

**Problem.** Cut v0.4.16: the release where one quantity stopped being stated
two ways.

**Why it matters.** Thirteen finished items sat unnamed by any release. The
version table is what `bin/docket wave` reads to say where the plan stands, and
the baseline prose is the only record of what a range of work was *for* - so
until a release is cut, the range is legible only by reading thirteen item
files, which is the reconstruction the release exists to remove.

**What the range turned out to be.** Unusually, all thirteen entries are one
shape: two statements of one fact, drifted apart or free to drift. A clock
reading `5400.0 s` beside a chart axis reading `1h30m`. `FLOW_FRACTION_TOLERANCE`
defined at `1e-12` in two modules. A module docstring promising a
`SimulationConfigurationError` boundary that three exception types walked
through. A validation module named for wash-in that also covers elimination.
`docs/MODEL.md` naming sevoflurane four releases after three agents shipped.
`doc_check` reporting that every citation resolves while reading 39 of 324. A
debt gate counting five entries the project owner had already deferred to
v0.5.1. That shape is what the baseline section is written around, rather than
the usual grouping by class.

**Why a patch and not a minor.** `ROADMAP.md` § "Versioning decision" chooses
the number by the capability boundary a release crosses. This one crosses none:
`src/anesthesia_sim/data/` and `.github/` are byte-identical to `v0.4.15`, and
`src/anesthesia_sim/core/` changes only in docstrings, one moved constant whose
value is unchanged, and one rename - so no equation, parameter, unit, numerical
method or solver step moved. The simulator does nothing it could not do before;
it states what it does more clearly. v0.5.0 is not available in any case, being
behind Gate 1.

**Done when.** `pyproject.toml` and `uv.lock` are at 0.4.16,
`docs/releases/v0.4.16.md` exists, `ROADMAP.md` carries a v0.4.16 version-table
row with the `current baseline` mark moved onto it and a rewritten baseline
section, and `make check` passes.
