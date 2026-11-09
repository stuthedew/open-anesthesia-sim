---
id: PL-HP95
title: Cut v0.4.33 from the 9 items finished since v0.4.32: the release that puts the two bookmark collections in front of a learner
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.4.34
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 760
payoff: clears the release the session-start digest re-raises in every session, and unblocks the next cut, which docket refuses while a release is untagged
verify: grep -q '^version = "0.4.33"' pyproject.toml
---

**Problem.** Cut v0.4.33 from the 9 items finished since v0.4.32: the release that puts the two bookmark collections in front of a learner

The nine are `PL-LPLD` (the two bookmark collections), `PL-NM7X` (the
fresh-gas-flow default recorded as a teaching default), `PL-FG9D` (the
anesthesia-machine abstraction design), `PL-XJ37` (naming the fork control as
v0.5.0 scope), `PL-205P` (the `verify:` that read the remote and reddened
`main`), `PL-66Z5` and `PL-QNQJ` (the superseded branch refs and the paragraph
one of them carried), `PL-JFQ3` (promoting the nine blocked items whose
blockers had closed) and `PL-V3GD` (the `v0.4.32` cut itself). All nine are
merged on `origin/main`; `v0.4.32` is cut and tagged, so nothing is outstanding
from the previous release.

**`0.4.33` is the number, and the mechanical guess of `0.5.0` is refused by the
roadmap rather than by preference.** `ROADMAP.md` gives `0.5.0` to "the case
you can branch", whose gate still has `PL-WZVZ` and `PL-8PS6` open and whose
`Required scope` is unbuilt, so cutting `0.5.0` here would ship that milestone
under its own name with most of it missing. The patch is also right on its own
terms, on the `v0.4.25` precedent: the collections exist and are listed, but a
learner cannot yet run to a mark and stop, because the halt is `PL-CTD7` and is
not built. So no capability boundary is crossed, and every number above this
one is spent.

**The cut also clears one `pr:` backfill.** `PL-LPLD` is marked `done` on the
base and records no `pr`; `#758` is recoverable from its merge commit.
`bin/docket record` bare writes it and any other the base can supply; let it
ride the release commit rather than composing one for it.

**Procedure**, from the `docket` skill's release mode, in order:

1. `make release VERSION=0.4.33` - never `bin/docket release` alone, which
   leaves `uv.lock` stale and fails the next `uv sync --locked`.
2. `bin/docket record` for the `pr:` backfill above.
3. The edits `bin/docket release` prints as outstanding: a `ROADMAP.md`
   version-table row, the `current baseline` mark moved onto it, and a baseline
   section saying what the release was for.
4. `make check`, which is what proves those edits landed.
5. Commit, push, open the pull request; the tag is the project owner's to run
   after the merge.

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.33 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Nine items, and a patch on both halves of the versioning test: no capability boundary is crossed, and every number above it is spent. `PL-LPLD` builds the two bookmark collections the Gas Man reference simulator keeps under one dialog, as two kinds rather than one kind with a flavour field - `TimeBookmark`, an absolute instant, and `MacTarget`, a height held as a multiple of the running agent's 1 MAC on one named compartment (circuit, alveolar, mixed-venous, vessel-rich, muscle or fat, with the wash-in ratio refused as a quotient rather than a concentration) - and the scope floor's rising/falling/either field is **withdrawn rather than met** (project owner, 2026-09-20): a height is a height, and a run passing through it going up and again coming down has reached what was marked both times. `app/bookmarks.py` is toolkit-independent, the dashboard lists both under two headings behind an `Edit bookmarks` dialog, and a branch inherits its trunk's marks so a comparison cannot silently be taken at two different heights. **Nothing halts at one** - detection is `PL-CTD7`, unblocked here and not built - so a learner can name the moment they care about but not yet be taken to it, which is why this is a patch and is the same shape as `v0.4.25`. `src/anesthesia_sim/app/` resolves to `d00924e` at `v0.4.32` and `b1a6ec6` here: seven files, +1 238/-14, all of it `PL-LPLD`, with 745 lines of new test across four files. **Nothing computational moved** - `src/anesthesia_sim/core/` resolves to `89683c3` at both ends and `tests/reference/` to `fcb3eca`, so no equation, parameter, numerical method or solver step changed, and every published-reference expected value is byte-identical and still met. **One data file changed and no stored number did**, measured rather than asserted: `data/machines/reference_circle_system.json` is the only file under `src/anesthesia_sim/data/` to differ, its three numeric leaves and its key set are identical across the two trees, and the whole of the change is inside the `provenance_gap` string. That is `PL-NM7X`: 4.0 L/min stays, and the sentence calling it "a routine mid-range clinical flow" is **withdrawn rather than re-sourced** - an unsourced claim about practice, replaced by a teaching default chosen for a 90 s circuit time constant, where lowering it to 0.5 L/min would carry the same absent provenance and put the apparatus lag at 12 minutes, longer than the demonstration it exists to make. **It completes `replay-hermeticity`, 1 of 1:** `PL-205P` stops a `verify:` that reads the remote reddening `main`'s whole-store replay for a finding no commit caused and no pull request could show. `PL-FG9D` settles what a machine module is before there are two - `docs/machine-abstraction.md`, which declines internal circuit topology and refuses to fold it into an effective volume - and closing it unblocks the debt gate's last two entries, leaving the gate at **173 of 175 cleared**. `PL-XJ37` names the fork control as v0.5.0 scope, `PL-JFQ3` promotes the blocked items whose blockers had closed, `PL-66Z5` and `PL-QNQJ` clear the last superseded `claude/*` refs, and `PL-V3GD` is the v0.4.32 cut.
