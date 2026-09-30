---
id: PL-8JY7
title: A declared `touches` path is never checked against the tree, so it goes stale silently
priority: P3
effort: S
status: done
classes: infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_vcs_silence.py, subprojects/docket/README.md, docs/items/PL-CNCF-controller-drawn-window-costs-6-2-ms-a-frame-at.md, docs/items/PL-MBP6-the-readme-has-no-image-of-the-interface-which.md, ROADMAP.md
added: 2026-08-30
closed: 2026-09-30
pr: 1234
verify: uv run pytest subprojects/docket/tests -k "touches and stale" && bin/docket check
---

**Problem.** `docket check` validates that a `verify:` command is present, that
a `blocked` item names its blocker and that a `done` item records a commit, but
it never asks whether the paths in `touches:` exist. Found while triaging
`PL-ZQ9C` (record an item's pull request, so provenance survives squash-merge),
which declared `subprojects/docket/src/docket/item.py`. This brief first called
that a file renamed to `model.py`, and it was not one: no commit in this
repository has ever held `item.py`, because docket arrived whole in `4bfa6041`
(2026-08-24) with `model.py` already its name. The declaration named a file
that never existed here, and nothing had ever read it.

**Why it matters.** `touches` is not documentation; it is the input to
`docket concurrent`, and the skill already says an absence of overlap proves
only that nobody foresaw a collision. A path that resolves nowhere is worse
than a missing one: it makes the item look analysed while contributing nothing
to the conflict graph, so two sessions can be told they may run together on
the strength of a filename that has not existed for weeks. It is also
decidable by reading the tree, which is where `CLAUDE.md` says the work
belongs.

**Live on 2026-09-30.** `PL-CNCF` (the chart read's 6.2 ms frame cost)
declares `src/anesthesia_sim/core/run_score.py`, which `bc21c320` (#512,
`PL-ZX12`) renamed to `run_definition.py`, and `PL-73ZN` (RunDefinition bounds
`opened_at_s` below but not above) declares `run_definition.py`. `bin/docket concurrent PL-CNCF`
names no file the two share: two items editing one module are reported as
independent.

**Decided (project owner, 2026-08-30): an advisory.** A `touches` path may
legitimately not exist yet — `PL-XH1D` (state how the project is developed)
names `CONTRIBUTING.md` and `PL-LWMS` (normalize commit messages with a
commit-msg hook) names `.mailmap`, both files their own work creates. So "the
path does not resolve" cannot be an error, and nothing decidable separates a
file-to-be-created from a rename left behind. The advisory says only what it
knows — these paths are not in the tree — and leaves the judgment to the
session reading it, which is the line `tools/doc_check.py` already draws.

It was to take the shape of the no-`touches` advisory `_groom` carried then,
which has since become an error in `_check_item` and fires only on an item
carrying a `verify:`. The two rejected options
are recorded so they are not re-proposed: an **error with an escape** (a
trailing `+` marking a path the work creates) puts syntax into a field whose
whole virtue is that it is a comma-separated list of paths; and **doing
nothing** loses a check that costs about twenty lines and then runs free
forever.

**Where.** Three modules, because `checks.py` reads no filesystem and no git
(`analyze`'s docstring says why). `vcs.gone_paths` reads which declared paths
the working tree lacks and a commit reachable from `HEAD` held, reusing
`vcs.in_tree`, which was written for this item; `cli._complete_report` hands
the answer to `analyze`, so `check`, `digest` and `next` count the same
advisories; and `checks._check_gone_touches` turns it into the advisory. Tests
in `subprojects/docket/tests/test_vcs.py` (the parse, against an injected
git), `test_checks.py` (the rule) and `test_cli.py` (the command against a real
repository, which is what proves git accepts the spelling). The advisory is
documented in `subprojects/docket/README.md`.

**Done when.** `docket check` lists, in one advisory line, every open item
whose `touches` names a path the tree does not hold and a commit reachable
from `HEAD` did, with the newest commit that changed each such path; the run
still exits zero; a path no commit has held, which is a file the work creates,
raises nothing; a closed item's `touches`, and an entry naming an item file
(already `_check_touched_items`' error), are not judged; a shallow clone
declines and says so; and tests cover a resolving path, a stale one, one never
held, and an item declaring no `touches` at all.

[superseded 2026-09-02: `PL-ZQ9C` is done and `PL-68XK` dropped; neither waits]
**Cheapest to land alongside `PL-68XK`** (check that every recorded commit
hash resolves) **or `PL-ZQ9C`** (record an item's pull request). All three edit
`subprojects/docket/src/docket/checks.py`, so `docket concurrent` will flag
them as contending — they want doing in one pass, not in parallel.

**Measured 2026-09-02, and it changes the design.** Every dangling `touches`
path in the store today is a file its own item is going to **create**, not a
stale reference:

| Item | Path | Created by |
| --- | --- | --- |
| `PL-LWMS` | `.mailmap` | its own "Done when" - collapse the owner to one identity |
| `PL-XH1D` | `CONTRIBUTING.md` | its own "Done when" - document the attribution rule |
| `PL-Y0RZ` | `tools/import_boundary_check.py` | the checker it exists to write |

So a check of the shape this brief describes - "a declared path that resolves
nowhere is stale" - would fire three times on the current store and be **wrong
all three times**. It would ship already crying wolf, which is the failure
`CLAUDE.md`'s retirement test now names, arriving before the check is even
built.

The distinction the check has to make is between a path that *was* real and a
path that is *not yet* real, and that is not decidable from the tree alone: both
look identical to `Path.exists()`. Two routes that are decidable:

- **Ask git, not the filesystem.** A path that no commit reachable from the
  default branch has ever held is forward-looking; one the history holds and the
  tree does not is stale. That is the `item.py` -> `model.py` rename this item
  was filed for, and it separates the two populations exactly. It costs a git
  walk, so it belongs beside the other git-derived reads that decline in a
  shallow checkout rather than answering wrongly.
- **Scope it to closed items.** A `done` item's `touches` should all resolve,
  because its work has landed. Cheaper, needs no git, and catches nothing until
  an item closes - which is late but never wrong.

Prefer the first. The second is the fallback if the walk proves too slow to run
on every `make check`.

**Do not implement the plain existence test.** It is the version this brief
originally described, and the measurement above is why it must not ship.

**Re-confirmed 2026-09-30: the problem stands, the history route holds, and
three things above were wrong.** Every `touches` entry in the store, sorted by
whether the working tree holds it and whether any commit reachable from `HEAD`
ever did:

| | In the tree | Held once, gone now | Never held |
| --- | ---: | ---: | ---: |
| Open items | 630 | 2 | 11 |
| Closed items | 4,668 | 103 | 6 |

All 11 never-held open paths are files their own work creates - `PL-VHHB`'s
`tools/ast_identity.py`, `PL-KJXS`'s pointer checker, `PL-4Z5Y`'s
`tests/reference/conftest.py`, the `src/anesthesia_sim/layout/` package three
items plan - so the plain existence test would still be wrong 11 times in 13.
The two held-and-gone paths are both real: `PL-CNCF`'s `run_score.py`, renamed
by `bc21c320`, and `PL-MBP6`'s `assets/branding`, removed by `dfd3e2c0` (#589).
The walk that finds them is one `git log` over the absent paths only, 72 ms on
this repository and none at all when every declared path is present.

- **Closed items are not judged, and the fallback is refuted.** 103 closed
  entries name a path later work moved, and 56 of them are two files the Qt
  port deleted: `chart_series.py`, declared by 18 closed items, and
  `test_simulation_view.py`, by 38. `.claude/rules/citation-drift.md` settles that a closed brief is a record
  rather than a live claim, and nothing reads a closed item's `touches` for
  concurrency, so firing there would change no decision 103 times. "Late but
  never wrong" was wrong.
- **`HEAD`, not the default branch.** A path the default branch created after
  this branch forked is in the default branch's history and not in this tree,
  so asking the default branch would report it gone from a branch that simply
  has not merged it yet. `HEAD` asks the history and the tree of one line,
  which is also what `since_filed` reads.
- **The history route does not catch the case this item was filed for.**
  `item.py` was never held, so it reads exactly as a file the work will create.
  That is the price of not crying wolf 11 times, and it is paid knowingly: a
  typo in `touches` stays the reader's to see, as a new file does.

Renames and deletions are reported alike, each with the newest commit that
changed the path, and `git show --stat -M <commit>` says where it went. Naming
the rename's target in the advisory was considered and left out: it needs a
second read and a parse of rename pairs to save a session one command, on an
advisory that fires only after a rename.

`PL-RWBV` (open items declaring nonexistent paths, filed 2026-09-14) asks for
this same check as the second half of its "Done when", with a different
discriminator - a path "named by the item's body as new". Whether a body names
a path *as new* is prose read for intent, which `CLAUDE.md` refuses to script,
and the mechanical form of it - the body names the path - would have passed
the one stale path left in the store, because `PL-CNCF`'s body names
`run_score.py` in the very paragraph noting that it is stale. `PL-RWBV`'s
remaining repair is `PL-CNCF`'s one entry, so it closes as a rider on this
branch.
