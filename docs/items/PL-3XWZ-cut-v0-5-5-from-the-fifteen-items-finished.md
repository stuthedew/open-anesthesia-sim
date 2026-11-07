---
id: PL-3XWZ
title: Cut v0.5.5 from the fifteen items finished since v0.5.4: one hover box stops holding two moments, and four checks stop passing on what they could not see, with nothing computational moving
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.5.6
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-22
closed: 2026-09-22
pr: 923
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

## Shipped as cut

`list_sessions` at the cut showed two sibling sessions running - `PL-0HPV`'s
and `PL-7TVT`'s, both on item work - and two idle, `PL-4W2L`'s and an earlier
`PL-0HPV` session, each of whose closing blocks asked the project owner whether
to cut v0.5.5. This is the session that answers them: neither held a cut,
`bin/docket flight` reported no ref carrying one, and `bin/docket release`
fetched and did not refuse. The mechanical half was pushed first, so a second
cut from any of them is now refused. This is therefore not `PL-66FP`'s
two-sessions-one-release case as far as anything could see.

**`app/` was read by syntax tree, not only by hash**, because it is the one
simulator tree that moved. With docstrings stripped: `chart_frame.py` changes
in `nearest_trace_point`, `nearest_wash_in_point`, their two replaced helpers
and one import (`PL-1K9G`), and in `_run_frame` and `assemble_chart_frame` by a
rename each (`PL-CZTR`, `PL-59WB`); `chart_time_base.fit_to_run` by its
parameter's name and error message (`PL-59WB`); `controller.py`,
`simulation_view.py` by alias reads rewritten to `fork.instant_s` or a local
renamed (`PL-CZTR`), `bookmarks.py` in docstrings and comments only; `qt_widgets.py`,
`dashboard_frame.py` and `theme.py` by `MarkRow`, `MarkListing.empty_line` and
three layout constants (`PL-FPY2`). Every `format_*` function in `app/` and
`_hover_value` are identical, and the numeric literals differ only by two `1`s
in `chart_frame.py` and `PL-FPY2`'s layout values.

`#920` (`PL-0HPV`) and `#921` (`PL-WFFX`) closed items after the cut was taken,
and `#919` merged between them closing nothing; `origin/main` was merged into
the branch before its pull request opened, so no CI result was discarded and
the local `make check` proved the tree CI tests.
`#922` (`PL-4W2L`) merged seven seconds after the pull request opened; it
merges cleanly, so the base was left where it was.

The cut ships as taken, on `PL-V065`'s ratified precedent (project owner,
2026-09-21): anything merging between this cut and the tag sits inside the
`v0.5.5` tag without being named in its notes, and takes the `### also inside
this tag's span` pointer `PL-P669` introduced. This item closes here and ships
under the next release - a cut cannot stamp itself.

**Done when.** `pyproject.toml` reads 0.5.5, `docs/releases/v0.5.5.md` holds
the notes, `ROADMAP.md` carries the version-table row with the `current
baseline` mark moved onto it and a baseline section, `make check` is green, and
the tag is run by the project owner on the merge commit.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.5 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Fifteen items, and a patch on both halves of § "Versioning decision"'s test: no capability boundary is crossed - the two changes a learner can see correct which instant an existing hover reports and how an existing panel lays out its rows - and every number above it is spent, v0.6.0 through v0.9.0 being given to milestone sections. **Nothing computational moved, read off tree identity for every tree but one**: `src/anesthesia_sim/core/` (`d9e3ca9`), `src/anesthesia_sim/data/` (`ab3499f`), `tests/reference/` (`a184830`) and `.github/` (`da3c951`) resolve to the same objects at v0.5.4 and here, so no equation, parameter, constant, numerical method, solver step or published-reference expected value changed. `app/` moves (`50d13b3` to `f3c6e26`, eight files, +304/-187), and compared by syntax tree with docstrings stripped its whole move is four items, with `_hover_value` and every `format_*` function in it identical. **`PL-1K9G` is `safety` at `P1`, and it changes what a hover reports on purpose.** Each trace answered at its drawn point nearest the pointer in two dimensions, so the pointer's height decided which instant it answered at: one box could label one run's compartments with instants 72 s apart on a 60-minute chart and 912 s apart on the 12-hour one, and a purely vertical 2 px movement moved the instant on 44.9% of pairs and the printed value on 35.1%. Now the pointer names the instant - each run answers at its drawn instant nearest the pointer in time, and a trace answers there only if its point is inside the 12 px radius - so one run's readings share an instant and a vertical movement moves neither; the cost, measured and stated, is that a steep trace answers over less area, down to 45-54% for the four fast compartments on the 12-hour axis. **`two-run-attribution` completes, 7 of 8** (`PL-GHMB` dropped), with `PL-FPY2` drawing each mark as a row of its own so a wrapped standing that names a run continues under its own mark rather than reading as the next one's. `PL-59WB` and `PL-CZTR` name an instant as an instant - `fit_to_run`'s input is the newest case instant rather than a run length, and a branch's fork instant is read only as `fork.instant_s` - with every value and every refusal's text unchanged. **The tooling half is one shape, a check passing on what it could not see**: `PL-5B88` (verify's suppression check could not see `@pytest.mark.skip` or `skipif`), `PL-Q8RQ` (`docket check` refuses a `verify:` narrowed with `pytest -k`, which an unrelated test's name can satisfy), `PL-YKSD` (a release tag is held to its own release's version file, since `v0.5.3`'s was pushed onto the commit before its own) and `PL-SZJ2` (`wave` reports a released milestone whose frozen list holds an entry no later gate places). **`PL-6Q9L` pauses new workflow mechanisms while any item carries `generator: live`** (project owner, 2026-09-22, ratified), on `PL-KVDK`'s first pass over the 161 non-product items filed 2026-09-20 to 09-22; `PL-G40Z` lets a no-behaviour repair ride the commit already being made; `PL-Q89J` adds `docket next --oldest`. **Seven of the fifteen are Gate 2 entries**, which stands at 29 of 185 cleared at this cut, and `PL-4KSZ`, the v0.5.4 cut, closes here because a cut cannot stamp itself.
