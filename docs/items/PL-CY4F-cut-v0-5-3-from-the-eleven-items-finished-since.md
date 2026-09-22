---
id: PL-CY4F
title: Cut v0.5.3 from the eleven items finished since v0.5.2: the four gates that were reporting a result they had not established, with the simulator's stillness readable off one tree hash
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-22
closed: 2026-09-22
payoff: the eleven items finished since v0.5.2 ship under their own number and stop being re-offered in every session digest, and the release whose theme is gates reporting unearned success states its own no-computational-movement claim from a tree hash rather than from an argument
verify: grep -q "^version = \"0.5.3\"" pyproject.toml
---

**Problem.** Eleven items have closed since v0.5.2 and are re-offered in every
session digest. They complete one feature - `instruction-staleness-audit` - and
are apparatus and documentation work throughout; none is a milestone, so this
is a patch on § "Versioning decision"'s test rather than a capability boundary.

## What this release contains, by tree object

The whole of `src/` is byte-identical at v0.5.2 and at this cut, so the
no-computational-movement claim needs no argument at all this time:

| Object | v0.5.2 | cut | |
| --- | --- | --- | --- |
| `src/` | `422b27e1` | `422b27e1` | identical |
| `src/anesthesia_sim/core/` | `061714b0` | `061714b0` | identical |
| `src/anesthesia_sim/data/` | `ab3499fd` | `ab3499fd` | identical |
| `src/anesthesia_sim/app/` | `01bc2d90` | `01bc2d90` | identical |
| `tests/reference/` | `a1848300` | `a1848300` | identical |
| `.github/` | `6f63412a` | `da3c9510` | **moved** |

**No equation, parameter, constant, numerical method, solver step or displayed
clinical value moves.** v0.5.2 could not say that from a hash - its `core/`
tree had moved on a docstring, and the claim had to be established by parsing
both files at each revision and comparing ASTs. Here one object answers it, and
the contrast is worth recording: the proof v0.5.2 built is what a release has to
do when the hash does not answer, not what it does instead.

`.github/` is the one shipped tree that moves, and it moves for the release's
own reason: `PL-PBP5` gives `quality.yml` the three standard-library checks that
had no CI backstop.

## The theme, and why it is not a coincidence

All four defects in the release are one shape at a different altitude - a check,
a gauge or a record reporting a result it had never established. `PL-D0W8` (a
pipeline's exit status is the last command's, so a red tree commits as green),
`PL-J3WK` (the local gate passing `verify:` commands that can prove nothing),
`PL-PBP5` (CI passing a tree `make check` would refuse), `PL-44DG` (the resident
size gauge 7.2% low on payloads it never counted). The three documentation items
are the same failure in prose rather than in code: `PL-R5HK`'s hook count,
`PL-G7ST`'s provenance claim inside the item about provenance, and `PL-K4BN`'s
eight `pr:` numbers whose absence was training sessions to skim the advisory
block. The baseline section in `ROADMAP.md` is written around that rather than
around the class labels.

## Shipped as cut

`list_sessions` showed no sibling session holding a release when this cut was
taken - the one that raised v0.5.3 in its closing block is `ARCHIVED` and was
waiting on the project owner's answer, which arrived as this session's prompt -
and `bin/docket flight` reported no branch claiming an item. So this is not the
two-sessions-one-release case `PL-66FP` records.

The cut ships as taken, on `PL-V065`'s ratified precedent (project owner,
2026-09-21): anything merging between this cut and the tag sits inside the
`v0.5.3` tag without being named in its notes, and is cited under the next
release. This item closes there for the same structural reason `PL-JYTJ` closes
under v0.5.3 - a cut cannot stamp itself.

**Done when.** `pyproject.toml` reads 0.5.3, `docs/releases/v0.5.3.md` holds the
notes, `ROADMAP.md` carries the version-table row with the `current baseline`
mark moved onto it and a baseline section, `make check` is green, and the tag is
run by the project owner on the explicit merge-commit sha.
