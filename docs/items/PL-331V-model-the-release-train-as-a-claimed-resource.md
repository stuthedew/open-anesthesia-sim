---
id: PL-331V
title: Model the release train as a claimed resource, so the release collision guard sees a session that has filed a release item but not cut
priority: P2
effort: M
status: done
classes: defect
feature: claim-record
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py, subprojects/docket/tests/test_cli.py, .claude/skills/docket/modes/release.md, subprojects/docket/README.md
blocked-by: PL-NST2, PL-0TD9
deferred-from: v0.6.0 - filed after the freeze by PL-MB2W's design round (2026-09-24), and not safety or science; generator work, which the pause on new mechanisms exists for
added: 2026-09-24
closed: 2026-09-24
payoff: part of the claim record that ends PL-MB2W's generator: one recorded fact decides who holds an item
verify: grep -qF 'resource: release-train' .claude/skills/docket/modes/release.md && grep -qE 'def test_\w*release_train' subprojects/docket/tests/test_release.py
---

**Problem.** Model the release train as a claimed resource, so the release collision guard sees a session that has filed a release item but not cut

**Part of `PL-MB2W`'s design** (who holds an item is recorded as a claim; design round of 2026-09-24, in `PL-MB2W` under "Design round, 2026-09-24"). Read that section's spec before starting: this brief names only this item's slice of it.

Add `resource: release-train`, stamped by release mode when it files the item. cmd_release refuses in three cases: another live holder, a cut hold that is not mine, or HEAD holding no train claim. Fix the 'no item id by design' lines at vcs.py:4066, cli.py:2570 and README.md:1535. Release mode claims the release item when it files it. Closes `PL-MFM4` (two release items filed for one release, each passing every guard).

**Why it matters.** `PL-MB2W` is a live generator: twenty items were each a new shape of work that some reader misread, because who holds an item is inferred from commit subjects, touched paths and ref age. This item is one slice of replacing that inference with a recorded claim, and the generator stops producing members only once the slices through `PL-DDYD` land.

**Done when.**

- A second session filing a release item while a live `release-train` claim is held elsewhere is refused.
- `PL-MFM4` is closed against this item.

**Build order.** After `PL-NST2`, `PL-0TD9`.

**The fault, reproduced 2026-09-24 on `b1d1b665`.** `release-train` appears nowhere in `cli.py`, `checks.py`, `claims.py`, `test_release.py` or release mode, so nothing stamps the resource and `cmd_release` consults no train claim.

## Design for this slice (2026-09-24, the session that claimed it)

Where the spec leaves a choice open, this is the choice, with the reason in one clause.

**The field.** `model.py` gains `RELEASE_TRAIN = "release-train"` and `RESOURCES = (RELEASE_TRAIN,)`; `Item.resource` (default empty), in `parse_item`'s `known` set, in `FIELD_ORDER` straight after `touches`, and in `_front_matter_values`. `checks._check_item` errors on a value outside `RESOURCES`, since a misspelt resource holds nothing and `holder` matches exactly. `cli.SET_FIELDS` gains `resource`, so an item filed without it can be stamped. `claims.py` already reads the raw field and needs no change.

**Filing is refused, not only cutting.** `bin/docket new --resource release-train "Cut v…"` (one title only; `--no-fetch` as `claim` has it) fetches, reads `claims.holdings`, and writes nothing (exit 3) when a live claim holds the train: on another branch ("another session is preparing a release"), or on HEAD's own branch ("this branch already holds it through PL-…; cut under that item"). A read that declined refuses (exit 1), per the floor. `--no-git` with `--resource` is a usage error (exit 2), because the resource exists for the check. This is the literal Done-when, and it leaves nothing to undo: no second release item is ever written.

**`claim` is not changed.** The window where two sessions both filed before either pushed a claim is closed at the cut instead: whichever orders second is refused there, before anything irreversible, and release mode's dry run straight after claiming surfaces it before the owner is asked for a version. A resource check inside `claim` would need `over` to name a claim on a different item, which the ordering does not define.

**Who is "mine" for the train** is decided by branch name (`vcs._head_name(hold.ref, remotes)` against HEAD's branch), as `arming` and `claiming` decide it, not by `Hold.mine`'s session token: the claim binds to the branch the cut lands through, and a handed-off session has a new token. One helper in `cli.py` answers `(rival, ours)` from one `Holdings`, where `rival` is `read.holder(RELEASE_TRAIN)` on another branch and `ours` is the first live train claim on HEAD's branch. `cmd_release`, `_cuts` and `new` all ask it, so they cannot disagree.

**`cmd_release`**, inside the branch after the landed check, reads `holdings` once after its fetch. Refusals, in this order, each a warning under `--dry-run` as the others are:
1. a cut on a ref HEAD does not contain (`cuts_in_flight`, unchanged), or a train `rival`, through `_parallel_cut_warning`. A rival is a `BranchCut` with no versions and `item` set, printed as "holds the release train for PL-… (claimed DATE), and has cut nothing yet", and it is not repeated for a ref already listed for its cut;
2. any read unreadable (`base`, `cuts.known`, or `read.known`), through `_unreadable_cut_warning`;
3. `ours` is None: HEAD's branch holds no claim on the train. The message gives the remedy: file with `new --resource`, commit the capture, `bin/docket claim <id>`, or stamp an existing item with `bin/docket set <id> --resource release-train`. A release item already closed on this branch has released its claim, and the message says so.

The third is last, so every existing refusal still refuses for its own reason.

**Cut holds stay on `vcs.cuts_in_flight`.** `Holdings.cuts` computes the same fact through the shared `_cut_versions`. Moving the cut half onto it would orphan `cuts_in_flight` and the 16 tests that pin it, with nothing a session sees changing. That move is `PL-FX5Q`'s kind of work.

**The digest.** `cli._cuts` adds a train rival to `CutsInFlight.branches` as the same `BranchCut`, so the digest names it instead of offering a release. `vcs.BranchCut` gains `item: str = ""`, and `render.format_digest` prints a train-only holder as "PL-… holds the release train, nothing cut yet". Once `PL-N162` lands, `_cuts` and `cmd_release` should read through its `_holdings(args)` so the digest reads the refs once.

**Prose.** The three "carries no item id by design" passages (the `CutsInFlight` docstring in `vcs.py`, the comment above `cmd_release`'s guard, and README § "Releases are mechanical") now say that a cut still carries none, and that the release item's train claim is the id the guard reads. The README's item format gains a `resource` paragraph. Release mode's "ship a release" opens with the filing: fetch, `new --resource release-train`, commit the capture alone, `claim`, then the dry run. Its list of refusals gains the train.

**Tests.** `test_cli.py`'s release fixtures cut from a `claude/` branch holding a claimed release item, so the success paths keep passing under refusal 3. `test_release.py` drives `new --resource` refused, a cut refused on a rival, a cut refused with no claim, and the digest line.
