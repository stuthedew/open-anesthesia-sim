---
id: PL-DRRG
title: Cut v0.5.11 from the 16 items finished since v0.5.10
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
resource: release-train
added: 2026-09-25
closed: 2026-09-25
payoff: the 16 items finished since v0.5.10 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.11\"" pyproject.toml
---

**Problem.** Cut v0.5.11 from the 16 items finished since v0.5.10

The project owner asked for the cut on 2026-09-25 ("cut next version"), in a
session opened for it, answering the session-start digest's offer of 0.5.11.
`list_sessions` showed no other session cutting a release, and `git ls-remote
--tags origin` showed v0.5.10 tagged on its cut's own merge commit,
`6f43a628`, so the cut is not refused on an untagged predecessor. This is the
first release item filed with `resource: release-train` (`PL-331V`), so its
claim holds the train, and `bin/docket release 0.5.11 --dry-run` found no
rival holder and no other ref's cut.

**The pull request opens as a draft while the claim rides the branch**
(`PL-H14W`), and `bin/docket arm` answered `hold` until the closure.

**Cut 2026-09-25.** 16 items, as the dry run said at filing, and no other pull
request was open. Cut with `make release VERSION=0.5.11`, which recorded all
sixteen `pr:` numbers before rendering the notes, stamped the 16 `milestone:
v0.5.11`, wrote `docs/releases/v0.5.11.md`, bumped `pyproject.toml` and
relocked `uv.lock`. None is a milestone and every number above this one is
spent, so this is a patch on § "Versioning decision"'s test. No feature
completes. Two are Gate 2 entries (`PL-KNHX`, `PL-MFM4`), which stands at 48
of 186; eight are v0.6.0 deferrals. None merged inside v0.5.10's tag, which is
on its own cut's merge (`6f43a628`), so v0.5.10's notes take no pointer.
`src/`, `tests/reference/`, `docs/MODEL.md` and `README.md` are byte-identical
to v0.5.10; `.github/` moved by one `quality.yml` step (`PL-MB3F`).

**One bullet reworded by hand.** `PL-SL16`'s title quotes the harness
reminder's model-named trailer, and the notes render titles verbatim, so the
cut put a model name into a pushed file against `PL-B11M`. The bullet now says
"a model-named co-author"; the item's own title and census are `PL-CGBK`'s.

`PL-08D4` closes in the same commit: `git ls-remote --tags origin` shows
v0.5.10 as an annotated tag peeling to `6f43a628`, the merge of `#989`, so the
tag it asked for is in place. It ships in the next release, as this item does,
because both close after the notes were rendered.

Filed while cutting: `PL-HZWB` (tag v0.5.11, the owner's step) and `PL-CGBK`
(model names in `PL-SL16`'s title and census). `bin/docket claim` again read
the harness-seeded tracking ref as the remote's copy and did not push the
claim; that is `PL-WX87`, already filed with three sightings, so the claim was
pushed by hand and nothing new was filed.
