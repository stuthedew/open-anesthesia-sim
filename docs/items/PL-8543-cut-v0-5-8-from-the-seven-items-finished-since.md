---
id: PL-8543
title: Cut v0.5.8 from the seven items finished since v0.5.7: a verify: command outside the admitted shapes is refused when it is written, a dropped item's command stops being run, and a closed generator head or a misspelt front-matter key stops passing silently, with nothing in the simulator moving
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.5.9
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-23
closed: 2026-09-23
pr: 957
payoff: the seven items finished since v0.5.7 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.8\"" pyproject.toml
---

**Problem.** Cut v0.5.8 from the seven items finished since v0.5.7: a verify: command outside the admitted shapes is refused when it is written, a dropped item's command stops being run, and a closed generator head or a misspelt front-matter key stops passing silently, with nothing in the simulator moving

The project owner asked for the cut by number on 2026-09-23 (project owner,
2026-09-23, ratified, over leaving the six to ride a later release), answering
the session that offered it. That session filed this item and stopped before
starting it, for length: its spend was 175,487 against `CLAUDE.md`'s 150,000
budget.

`bin/docket release --dry-run` listed six at filing: `PL-1P5V`, `PL-BBT8`,
`PL-CT07`, `PL-DSPM`, `PL-KNWP` and `PL-QP9Z`. Anything that has merged
since, such as `PL-BX1C` (pull request #952, open at filing), ships in this cut
too, so re-run the dry run rather than trusting this list. Then run
`make release VERSION=0.5.8`, make the `ROADMAP.md` edits it names (the
version-table row, the current-baseline mark and the baseline section) and run
`make check`. The tag is the owner's to push, per
`.claude/skills/docket/modes/release.md`.

**Cut 2026-09-23.** Seven items rather than the six listed at filing:
`PL-BX1C` (`#952`) merged in between, as this brief said anything would, so the
title and payoff now say seven. Cut with `make release VERSION=0.5.8`, which
recorded seven `pr:` numbers before rendering the notes, stamped the seven
`milestone: v0.5.8`, wrote `docs/releases/v0.5.8.md`, bumped `pyproject.toml`
and relocked `uv.lock`. None is a milestone and every number above this one is
spent - `bin/docket wave` reserves 0.6.0 through 0.9.0 - so this is a patch on
§ "Versioning decision"'s test. One is a Gate 2 entry (`PL-BX1C`), which stands
at 42 of 185 cleared at this cut, and three are v0.6.0 deferrals (`PL-1P5V`,
`PL-BBT8`, `PL-DSPM`). No feature completes: the seven advance
`generator-identification`, `release-process`, `verify-command-meaning` and
`verify-false-reject`.

## What this release contains, by tree object

| Object | v0.5.7 | cut | |
| --- | --- | --- | --- |
| `src/` | `37b0a4c` | `37b0a4c` | identical - `core/`, `data/` and `app/` with it |
| `tests/reference/` | `a184830` | `a184830` | identical |
| `docs/MODEL.md` | `148686b` | `148686b` | identical |
| `README.md` | `9938368` | `9938368` | identical |
| `.github/` | `275baf5` | `275baf5` | identical |

So nothing a learner can reach moves. The baseline section in `ROADMAP.md`
groups the seven by what they were for: what a `verify:` command may be and
when it is run (`PL-1P5V`, `PL-BX1C`), generator machinery that reported what
was not so (`PL-BBT8`, `PL-DSPM`, `PL-CT07`), a start claim that auto-merge
erased (`PL-QP9Z`), and `PL-KNWP`, the v0.5.7 cut.

## v0.5.7's tag span

`#944` (`PL-BBT8`) merged after v0.5.7's cut was taken and before its tag -
`git describe --contains 43f255bc` gives `v0.5.7~1` - so v0.5.7's notes take
the `### also inside this tag's span` pointer in this cut, naming v0.5.8, as
`PL-KNWP` said they would. No other of the seven resolves inside a tag except
`#946`, the v0.5.7 cut, which is that tag's own commit and exempt by
construction.

## v0.5.8's own tag span

This item's capture (`#954`) merged before the work began, so the start claim
went up alone and no auto-merge was armed under it. Anything merging after the
cut is taken and before the v0.5.8 tag ships inside that tag, is described in
v0.5.9, and takes a pointer in v0.5.8's notes at that cut.
