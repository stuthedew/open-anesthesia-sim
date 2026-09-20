---
id: PL-F1SZ
title: Cut v0.4.35 from the 16 items finished since v0.4.34: the release where a bookmark stops the run on the step that crosses it, and what a comparison against Gas Man is worth got written down by phase
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-20
closed: 2026-09-20
payoff: clears the release the session-start digest re-raises in every session, and unblocks the next cut, which docket refuses while a release is untagged
verify: grep -q '^version = "0.4.35"' pyproject.toml
---

**Problem.** Cut v0.4.35 from the 16 items finished since v0.4.34: the release where a bookmark stops the run on the step that crosses it, and what a comparison against Gas Man is worth got written down by phase

The sixteen are **one product item** - `PL-CTD7`, `P1`/`safety`, bookmark
crossing detected inside the advance loop - **two model-boundary statements**
in `docs/MODEL.md` (`PL-D126` and `PL-WJNS`, both `P1`/`science`), **the whole
of `gate-list-integrity`** (`PL-0VFF`, `PL-82B0`, `PL-880Z`, `PL-B8V1`,
`PL-HJZW`, `PL-KF0T`, with `PL-S6RS` the regroup that named the feature and
`PL-R0P3` and `PL-NLP4` beside it), two anesthesia-machine scope items
(`PL-77G2`, `PL-6WNZ`), `PL-YD6X`, and `PL-Y3XK`, the v0.4.34 cut itself.
`PL-TBMX` is dropped in the same commit rather than finished, so it is not in
the notes. All sixteen are merged on `origin/main` at `9335196`; `v0.4.34` is
cut and tagged on the remote (`bf5c1f2`, commit `8c83951`), so nothing is
outstanding from the previous release.

**`0.4.35` is the number, and unlike the last four cuts only one half of
§ "Versioning decision"'s test carries it.** Every number above it is spent -
`ROADMAP.md` gives `0.5.0` to "the case you can branch", whose `Required
scope` still has `PL-49R8`, `PL-B8MK`, `PL-Z3W6`, `PL-VKJW` and `PL-W7H9`
open, and `0.6.0` through `0.9.0` to milestone sections of their own. The
capability half is weaker than in `v0.4.34`, and the item says so rather than
asserting that nothing moved: `PL-CTD7` is the first release in which a
bookmark *does* anything. A threshold or time mark now halts the run on the
step that crosses it, at every playback multiplier, and leaves it paused. That
is a boundary a learner can feel. It is released as a patch because the
minor that would mark it is reserved for the milestone it is scope for, and
shipping `0.5.0` with five of its nineteen `Required scope` ids open would
name that milestone for work that is not in it.

**The claim this cut owes a measurement is that nothing computational moved,
and `tests/reference/` moves here for the first time since `v0.4.29`** - so
the published-reference argument cannot be made by tree identity alone and is
made by reading the diff:

- `src/anesthesia_sim/core/` resolves to `0c8e708` at both `v0.4.34` and
  `HEAD`, and `src/anesthesia_sim/data/` to `ab3499f` at both, so no equation,
  parameter, constant, numerical method or stored scientific value changed.
- `tests/reference/` resolves to `fcb3eca` at `v0.4.34` and `5b43d4b` here.
  The whole of that is **four added lines of prose inside the module docstring
  of `test_published_wash_in_and_elimination.py`**, `PL-D126`'s cross-reference
  to `docs/MODEL.md` § "Known limitations". No expected value, tolerance or
  case is added, removed or changed, so every published-reference gate still
  holds at the same numbers.
- `src/anesthesia_sim/app/` resolves to `3bbe8a2` at `v0.4.34` and `87baee9`
  here: four files, +731/-30, all of it `PL-CTD7`. The release as a whole is
  49 files, +3,624/-230.

**The cut may also clear `pr:` backfills.** `bin/docket record` bare writes
every one the base can supply; let it ride the release commit rather than
composing one for it.

**Procedure**, from the `docket` skill's release mode, in order:

1. `make release VERSION=0.4.35` - never `bin/docket release` alone, which
   leaves `uv.lock` stale and fails the next `uv sync --locked`.
2. `bin/docket record` for any `pr:` backfill the base can supply.
3. The edits `bin/docket release` prints as outstanding: a `ROADMAP.md`
   version-table row, the `current baseline` mark moved onto it, and a
   baseline section saying what the release was for.
4. `make check`, which is what proves those edits landed.
5. Commit, push, open the pull request; the tag is the project owner's to run
   after the merge.
