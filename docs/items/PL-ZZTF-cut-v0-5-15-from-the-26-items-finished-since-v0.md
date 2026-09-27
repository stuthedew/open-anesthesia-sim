---
id: PL-ZZTF
title: Cut v0.5.15 from the 26 items finished since v0.5.14
priority: P2
effort: S
status: ready
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
resource: release-train
added: 2026-09-27
payoff: the 26 items finished since v0.5.14 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.15\"" pyproject.toml
---

**Problem.** Cut v0.5.15 from the 26 items finished since v0.5.14

The project owner asked on 2026-09-27 for versions to be cut on the way to
v0.6.0, and the project's coordinator started this thread to cut the next one
once `PL-LPH9` had brought `ROADMAP.md` § "The cadence" in line with that
answer (`#1189`, merged 17:22 UTC).

**What was checked at filing.** `git ls-remote --tags origin` shows v0.5.14 as
the annotated tag `82d1749e` peeling to `863dede8`, the cut's own merge
(`#1156`), so the cut is not refused on an untagged predecessor. `bin/docket
flight` shows no release item claimed - its one row is `PL-NC62` on
`claude/scenario-branching-b15wcc`, `#1188` - and `bin/docket release 0.5.15
--dry-run` named 26 finished items. They match `main`'s own history: of the 32
pull requests merged after `#1156`, the nine with no bullet are captures,
design-round records and drops, and every id leading one of them without a
bullet is open or dropped.

**The version is a patch**, on both halves of `ROADMAP.md` § "Versioning
decision": the one change a learner can see is the window opening maximized
(`PL-Z4K6`), and every minor from v0.6.0 up is given to a milestone. No
equation, parameter or stored value moved, measured by tree object:
`src/anesthesia_sim/core/` goes from `d9e3ca9f` to `9a95dfd6` by one comment,
and `src/anesthesia_sim/data/` from `ab3499fd` to `b8477a15` by one source
note, with every stored value byte-identical. `docs/MODEL.md` moves +440 -56,
most of it `PL-KK1Q`'s measurement of the first 24 hours of washout against
Yasuda 1991's fitted mean curves, which is a statement about the model rather
than a change to it.

**Cut 2026-09-27, at 26 items**, with `make release VERSION=0.5.15`, from
`main` at `80a173db` (`#1189`). The ROADMAP.md row, its `current baseline`
mark and the baseline section are written by hand. `tools/pr_body_check.py`
found no squash commit that lost its body, and no closure among the 26 merged
inside v0.5.14's tag, so v0.5.14's notes owe no pointer. Re-reading the
notes' figures against the tree found `docs/MODEL.md` and `playback.py`
giving `PL-SQJ1`'s measured floor as 99.0% where its table has the 20x rung
at 98.9%; the notes give the table's figure, and `PL-B0JG` is filed to correct
the two passages. `PL-RZQ0` files the tag step, which only the owner can push
from this environment.
