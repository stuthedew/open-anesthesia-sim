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
pr: 1003
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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.11 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Sixteen items, all apparatus and documentation, and a patch on both halves of § "Versioning decision"'s test: no capability boundary is crossed, and every number above it is spent, v0.6.0 through v0.9.0 being given to milestone sections. **Nothing in the simulator moved**: `src/` resolves to `37b0a4c` at v0.5.10 and here, and `tests/reference/` (`a184830`), `docs/MODEL.md` (`fd139ea`) and `README.md` (`9938368`) with it; `.github/` moves only to run `tools/possessive_section_check.py` under `uv` as well (`PL-MB3F`). **Five items put the in-flight machinery on `PL-MB2W`'s claim record**: `PL-N162` moves `show`, `flight`, `next` and the session-start digest onto `claims.holdings`, each hold printed with its kind and state, and `PL-FFR0` gives CI and `flight` one definition of a branch that claims nothing; `PL-J9S0` has CI refuse such a branch, and a claim ordering behind another live one; `PL-H14W` opens a claimed captures-only pull request as a draft, after v0.5.9's `#978` was merged six minutes in, and `PL-DDYD` replaces the arming catalog `CLAUDE.md` restated with `bin/docket arm`. **`PL-331V` makes the release train a claimed resource**, closing `PL-MFM4`'s blind spot for a session that has filed a release but not cut it. **Most of the rest are checks that passed on what they could not see**: `PL-Y1W0`'s `pr_body_check.py --compare` finds 27 of 681 squash bodies differing from their pull request's, and `PL-25JP` recovered the ten that landed empty; `PL-MB3F` names the source files `doc_check` cannot parse instead of skipping them; `PL-KNHX` and `PL-TP75` make `contrast_check` refuse a stale shortfall entry and count the errors its exit code counts; and `PL-4RK2` names a blocked generator head whose rank reaches nothing startable. `PL-SL16` states `PL-B11M`'s commit-attribution rule in `CLAUDE.md`. **Two are Gate 2 entries**, `PL-KNHX` and `PL-MFM4`, which leaves it at 48 of 186 cleared; eight are v0.6.0 deferrals, and `PL-NLXK`, the v0.5.10 cut, closes here because a cut cannot stamp itself.
