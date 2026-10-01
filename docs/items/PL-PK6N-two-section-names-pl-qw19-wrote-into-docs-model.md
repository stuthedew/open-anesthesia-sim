---
id: PL-PK6N
title: Two section names PL-QW19 wrote into docs/MODEL.md and docs/machine-abstraction.md lack the section mark, so make doc-check has advised on them every run since 2026-09-27
status: untriaged
added: 2026-10-01
---

**Problem.** Two section names PL-QW19 wrote into docs/MODEL.md and docs/machine-abstraction.md lack the section mark, so make doc-check has advised on them every run since 2026-09-27

`make doc-check` prints, under "Advisories (judgment needed)":

- `docs/MODEL.md`: "What real workstations hold" names a section without the
  mark, so a rename of it would pass unreported; write § "What real
  workstations hold"
- `docs/machine-abstraction.md`: "The run owns its opening conditions" names a
  section without the mark, so a rename of it would pass unreported; write
  § "The run owns its opening conditions"

Both strings arrived in `PL-QW19` (let a machine profile omit its startup fresh
gas flow, `#1211`, 2026-09-27), per `git log -S` on each file. The cost of
leaving them is the one the advisory names - a later rename of either section
leaves a reference nothing reports - and the second cost is the advisory itself:
two lines firing on every run that nobody acts on train a session to skim the
block where a real one appears.

**Found.** 2026-10-01, in `PL-4C41`'s close-out docs sweep, which changed
neither file. Not fixed there: both files are outside that item's `touches`.

**Done when.** Each reference reads § "..." where it names the section (or
the sentence is reworded so it no longer names one, if the advisory has misread
it), and `make doc-check` prints neither advisory.
