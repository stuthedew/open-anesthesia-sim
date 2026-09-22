---
id: PL-3XWZ
title: Cut v0.5.5 from the fifteen items finished since v0.5.4: one hover box stops holding two moments, and four checks stop passing on what they could not see, with nothing computational moving
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-22
payoff: the fifteen items finished since v0.5.4 ship under their own number and stop being re-offered in every session digest, and the release that fixes which instant a hover labels a value with states what a learner now sees and proves by measurement that no computed value moved with it
verify: grep -q "^version = \"0.5.5\"" pyproject.toml
---

**Problem.** Cut v0.5.5 from the fifteen items finished since v0.5.4: one hover box stops holding two moments, and four checks stop passing on what they could not see, with nothing computational moving

Fifteen items have closed since v0.5.4 and are re-offered in every session
digest. They complete one feature - `two-run-attribution`, 7 of 8 with
`PL-GHMB` dropped, which `PL-FPY2` finishes - and seven of them are Gate 2
entries (`PL-1K9G`, `PL-59WB`, `PL-5B88`, `PL-CZTR`, `PL-FPY2`, `PL-Q8RQ`,
`PL-SZJ2`), which stands at 29 of 185 cleared at this cut. None is a milestone,
and every number above this one is spent - `bin/docket wave` reserves 0.6.0,
0.7.0, 0.8.0 and 0.9.0 - so this is a patch on § "Versioning decision"'s test
rather than a capability boundary.

## What this release contains, by tree object

| Object | v0.5.4 | cut | |
| --- | --- | --- | --- |
| `src/anesthesia_sim/core/` | `d9e3ca9` | `d9e3ca9` | identical |
| `src/anesthesia_sim/data/` | `ab3499f` | `ab3499f` | identical |
| `tests/reference/` | `a184830` | `a184830` | identical |
| `.github/` | `da3c951` | `da3c951` | identical |
| `src/anesthesia_sim/app/` | `50d13b3` | `f3c6e26` | **moved** - eight files, +304/-187 |

So no equation, parameter, constant, numerical method or solver step moves, and
that is read off tree identity rather than a diff. `app/`'s whole move is four
items: `PL-1K9G` (`chart_frame.py`: which drawn instant a hover reports),
`PL-FPY2` (`qt_widgets.py`, `dashboard_frame.py`, `theme.py`: each mark drawn
as a row of its own), `PL-59WB` (`chart_time_base.py`: a parameter renamed,
its value unchanged and pinned by a test) and `PL-CZTR` (`controller.py`,
`bookmarks.py`, `simulation_view.py`: an alias deleted, every refusal rendering
the text it did before).

**One thing a learner reads does move, and by design**: which drawn instant a
hover reports at a given pointer position (`PL-1K9G`). The values the model
produces at every instant are unchanged; what changed is which of them one box
presents together. `docs/MODEL.md` moves in § "Reasonably foreseeable misuse,
and the hazards the presentation carries", § "The chart's time base", § "The
hover and the run it belongs to", § "Where more than one trace answers" and §
"When it answers".

## The theme

The simulator half is one hover box that stopped holding two moments -
`PL-1K9G`, `safety` at `P1` - and three items keeping an attribution or an
instant honest (`PL-FPY2`, `PL-59WB`, `PL-CZTR`). The tooling half is one
shape, a check passing on what it could not see: `PL-5B88`, `PL-Q8RQ`,
`PL-YKSD`, `PL-SZJ2`. The rest is how sessions work and two queue passes -
`PL-6Q9L`, `PL-G40Z`, `PL-KVDK`, `PL-Q89J`, `PL-14QR`, `PL-Y4YG` - and
`PL-4KSZ`, the v0.5.4 cut. The baseline section in `ROADMAP.md` is written
around that rather than around the class labels.

**Done when.** `pyproject.toml` reads 0.5.5, `docs/releases/v0.5.5.md` holds
the notes, `ROADMAP.md` carries the version-table row with the `current
baseline` mark moved onto it and a baseline section, `make check` is green, and
the tag is run by the project owner on the merge commit.
