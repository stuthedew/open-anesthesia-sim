---
id: PL-9FMV
title: "Cut v0.4.16: the release where one quantity stopped being stated two ways"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.17
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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.16 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> All thirteen entries are the same shape: two statements of one fact, drifted apart or free to drift. **Nothing computational moved** - `src/anesthesia_sim/data/` and `.github/` are byte-identical to `v0.4.15`, and `src/anesthesia_sim/core/` changes in docstrings, one moved constant and one rename, so no equation, parameter, unit, numerical method or solver step is touched. **What a reader sees is the clock.** `PL-SSBP` gave the chart a time base spanning a case, so an axis tick read `1h30m` while the clock and every recorded control stamp beside it read `5400.0 s`, and locating a control mark meant dividing by 3600 by hand; `PL-Y5WR`'s 24-hour envelope then made the clock's top reading `86400.0 s`, seven characters of tenths on a quantity a reader thinks about in hours. The clock, the stamps and the axis now share one compound form - `45s`, `1m30s`, `1h23m45.6s`, `24h` - built in one function, dropping a zero component and keeping a tenth only where there is one, so a stamp still resolves the `0.1 s` step the simulation advances by (`PL-Q4M4`, `PL-CZFY`). The old docstring's argument for two forms, that "a compound duration form would round the stamp away", was checkable and false; `format_elapsed` now also raises rather than printing `-1.0 s`. **Two error boundaries were false where they were stated:** `core/parameters.py` promised in its own docstring that every raise reaching a caller is a `SimulationConfigurationError` while a missing, unreadable or truncated data file escaped as `OSError`, `UnicodeDecodeError` or `JSONDecodeError` - three types where the audit named two, because the file is opened as text (`PL-B32L`) - and `_apply_setting` caught a narrower class than the timer paths beside it, so an unexpected raise escaped into Flet's dispatch (`PL-YK2V`). `FLOW_FRACTION_TOLERANCE` stood at `1e-12` in two modules guarding the two perfusion-sum checks independently; one definition now, identical value, so no threshold moved (`PL-TCW5`). **The provenance line stopped answering when it could not:** `APP_VERSION` falls back to `unknown`, which is a version-shaped string, and the header subtitle is the interface's only link between a displayed number and the model behind it, so a build that cannot identify itself now says "Version unavailable (this build is not traceable)" (`PL-KCWD`). **Three names had outlived what they name** - `RunScore` is `RunDefinition`, in the package that should read like the domain (`PL-ZX12`); the wash-in validation module and its `docs/MODEL.md` section cover elimination too (`PL-B9VL`); and `docs/MODEL.md` named sevoflurane in its headings, Purpose and symbol table four releases after three agents shipped (`PL-KGNF`). **And the citation tying `core/` to the specification is enforced rather than asserted.** `PL-VZL0` cites `docs/MODEL.md` from every `core/` function implementing a governing equation, precisely so a section rename cannot silently orphan it - and `tools/doc_check.py` read the comma form and not the section-mark form this repository writes, leaving 285 of the tree's 324 document-section citations unchecked while the run reported that they all resolve. Recognising the form surfaced eighteen errors: eleven were one false positive, a citation wrapped across two lines of a blockquote, and seven were genuinely stale pointers in closed items (`PL-V13T`). Five gate entries deferred to the Qt port by owner decision are `blocked` rather than counted as debt the gate could clear (`PL-D143`). Thirteen items, one of which is the v0.4.15 cut itself.
