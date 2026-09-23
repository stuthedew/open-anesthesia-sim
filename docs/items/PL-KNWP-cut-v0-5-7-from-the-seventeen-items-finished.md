---
id: PL-KNWP
title: Cut v0.5.7 from the seventeen items finished since v0.5.6: a git call that fails stops reading as an empty answer, and a brief's prose is held to its own status, with nothing in the simulator moving
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-23
closed: 2026-09-23
payoff: the seventeen items finished since v0.5.6 ship under their own number and stop being re-offered in every session digest, and brief-state-agreement ships complete
verify: grep -q "^version = \"0.5.7\"" pyproject.toml
---

**Problem.** Cut v0.5.7 from the seventeen items finished since v0.5.6: a git call that fails stops reading as an empty answer, and a brief's prose is held to its own status, with nothing in the simulator moving

Seventeen items have closed since v0.5.6 and are re-offered in every session
digest, and `bin/docket release --dry-run` reports that they complete
`brief-state-agreement`. The project owner asked for the cut by number
(2026-09-23), which is also the dry run's mechanical guess. None is a
milestone, and every number above this one is spent - `bin/docket wave`
reserves 0.6.0, 0.7.0, 0.8.0 and 0.9.0 - so this is a patch on § "Versioning
decision"'s test rather than a capability boundary. Two are Gate 2 entries
(`PL-M6FY`, `PL-NGBM`), which stands at 41 of 185 cleared at this cut, and six
are v0.6.0 deferrals (`PL-9RFP`, `PL-B60Q`, `PL-19T3`, `PL-8YXJ`, `PL-J6HP`,
`PL-WNCT`).

Cut with `make release VERSION=0.5.7` rather than `bin/docket release` alone,
because `uv.lock` records the project's own version and the release mode says
the bare command leaves `make check` failing on `uv sync --locked`. The cut
recorded eleven `pr:` numbers before rendering the notes.

## What this release contains, by tree object

| Object | v0.5.6 | cut | |
| --- | --- | --- | --- |
| `src/` | `37b0a4c` | `37b0a4c` | identical - `core/`, `data/` and `app/` with it |
| `tests/reference/` | `a184830` | `a184830` | identical |
| `docs/MODEL.md` | `148686b` | `148686b` | identical |
| `README.md` | `9938368` | `9938368` | identical |
| `.github/` | `27c67f3` | `275baf5` | one comment in `pr-title.yml` (`PL-1PBV`) |

So nothing a learner can reach moves, read off tree identity alone. The
baseline section in `ROADMAP.md` is written around what the seventeen were for
rather than their class labels: a failed git call read as an empty answer
(`PL-9RFP`, `PL-19T3`, `PL-1PBV`), one invocation per command (`PL-NGBM`,
`PL-M6FY`, `PL-3T2Q`, and `PL-KH3Q`, the red `main` between two of them), a
brief read against its own status (`PL-8YXJ`, `PL-X4RX`, `PL-RWJD`), a gate's
facts read once (`PL-J6HP`, `PL-B60Q`), captures reaching `main` and work left
on a branch (`PL-WNCT`, `PL-R808`, `PL-SRBR`), and `PL-XYQW` and `PL-38HD`.

## v0.5.6's tag span

`#930` (`PL-NGBM`, `PL-M6FY`, `PL-3T2Q`) merged after v0.5.6's cut was taken
and before its tag - `git describe --contains c91b8d99` gives `v0.5.6~1` - so
v0.5.6's notes take the `### also inside this tag's span` pointer in this cut,
naming v0.5.7, as v0.5.6's own baseline section said they would.

## v0.5.7's own tag span

`#942`, this item's capture, merged by auto-merge before the cut was pushed -
the captures-only rule `PL-WNCT` introduced, on its first release - so the
branch was restarted from `main` and the cut commit carried across. `#944`
(`PL-BBT8`) merged after the cut was taken, touching only
`subprojects/docket/` and one item file. Both ship inside the v0.5.7 tag and
are described in the next release, whose cut writes v0.5.7's `### also inside
this tag's span` pointer for `#944`. `#942` closes no item, so it needs none.
