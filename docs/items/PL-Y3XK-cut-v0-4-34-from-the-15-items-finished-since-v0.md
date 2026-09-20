---
id: PL-Y3XK
title: Cut v0.4.34 from the 15 items finished since v0.4.33: the release where the interface stopped answering in the host's colours, and the model's flow envelope stopped standing in for a machine's
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.4.35
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 770
payoff: clears the release the session-start digest re-raises in every session, and unblocks the next cut, which docket refuses while a release is untagged
verify: grep -q '^version = "0.4.34"' pyproject.toml
---

**Problem.** Cut v0.4.34 from the 15 items finished since v0.4.33: the release where the interface stopped answering in the host's colours, and the model's flow envelope stopped standing in for a machine's

The fifteen are three dark-appearance palette defects (`PL-0NVN` the three
selector popups, `PL-7W9N` the six legend checkboxes, `PL-RKRY` the bookmark
dialogs), the hover's compartment contention (`PL-0RZ0`), two
`anesthesia-machine` gate entries (`PL-8PS6` fresh gas flow range as a machine
property, `PL-439V` the Tec 6 as the second device class), five apparatus
items (`PL-FCM3`, `PL-6T44`, `PL-K4R5`, `PL-8G48`, `PL-CHQY`), three
housekeeping passes (`PL-028T`, `PL-V3QB`, `PL-WQF1`) and `PL-HP95`, the
v0.4.33 cut itself. All fifteen are merged on `origin/main`; `v0.4.33` is cut
and tagged (`ac35afb`), so nothing is outstanding from the previous release.

**`0.4.34` is the number, and the mechanical guess of `0.5.0` is refused by the
roadmap rather than by preference.** `ROADMAP.md` gives `0.5.0` to "the case
you can branch", whose gate still has `PL-D126` and `PL-WJNS` open with
`PL-WZVZ` blocked outside it, and whose `Required scope` is unbuilt - so
cutting `0.5.0` here would ship that milestone under its own name with most of
it missing. `0.6.0` through `0.9.0` are likewise spent on milestone sections.
The patch is also right on its own terms: no capability boundary is crossed.
Three palette fixes and a hover fix correct what an existing control renders
and answers; `PL-8PS6` adds a second refusal beside an existing one and the
shipped profile declares no range, so nothing displayed or refused changes
today; `PL-439V` is a written design decision.

**The one claim this cut owes a measurement is that nothing computational
moved**, because unlike the last four releases `src/anesthesia_sim/core/` and
`src/anesthesia_sim/data/` both do move here. Measured rather than asserted,
and the numbers go in the baseline section:

- `src/anesthesia_sim/data/` holds 42 numeric leaves at `v0.4.33` and 42 at
  `HEAD`, none differing in value and none added or removed; the only key
  added anywhere in the tree is `reference_circle_system.json`'s
  `deliverable_fresh_gas_flow_range`, whose value is `null`.
- The `core/` diff removes no numeric literal at all. The four it adds are
  three in prose and one range guard (`numeric_value < 0.0`).
- `tests/reference/` resolves to `fcb3eca` at both ends, so every
  published-reference expected value is byte-identical and still met.

**The cut may also clear `pr:` backfills.** `bin/docket record` bare writes
every one the base can supply; let it ride the release commit rather than
composing one for it.

**Procedure**, from the `docket` skill's release mode, in order:

1. `make release VERSION=0.4.34` - never `bin/docket release` alone, which
   leaves `uv.lock` stale and fails the next `uv sync --locked`.
2. `bin/docket record` for any `pr:` backfill the base can supply.
3. The edits `bin/docket release` prints as outstanding: a `ROADMAP.md`
   version-table row, the `current baseline` mark moved onto it, and a
   baseline section saying what the release was for.
4. `make check`, which is what proves those edits landed.
5. Commit, push, open the pull request; the tag is the project owner's to run
   after the merge.

**Retitled during the cut.** The working title said "the machine abstraction
gets its second device class". Reading `PL-439V` against the tree showed that
is wrong: it closed as **satisfied by `PL-FG9D`'s specification**, which
shipped in `v0.4.33`, so the Tec 6 entered `docs/machine-abstraction.md` one
release ago and nothing about it landed here. The title now names what this
release actually moves.
