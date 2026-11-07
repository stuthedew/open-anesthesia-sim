---
id: PL-NLXK
title: Cut v0.5.10 from the 8 items finished since v0.5.9: who holds an item becomes a Claim trailer that bin/docket claim and yield write and one claims.holdings reader reads, every generator head names the fact its members misread, and a blocked generator's own blockers rank in its tier, with nothing in src/ moving
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
milestone: v0.5.11
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-24
closed: 2026-09-24
pr: 989
payoff: the 8 items finished since v0.5.9 ship under their own number and stop being re-offered in every session digest
verify: grep -q "^version = \"0.5.10\"" pyproject.toml
---

**Problem.** Cut v0.5.10 from the 8 items finished since v0.5.9: who holds an item becomes a Claim trailer that bin/docket claim and yield write and one claims.holdings reader reads, every generator head names the fact its members misread, and a blocked generator's own blockers rank in its tier, with nothing in src/ moving

The project owner asked for the cut on 2026-09-24 ("cut new version"), in a
session opened for it, answering the session-start digest's offer of 0.5.10.
`list_sessions` showed no other session cutting a release, no branch on
`origin` carried `docs/releases/v0.5.10.md`, and `git ls-remote --tags origin`
showed v0.5.9 tagged on its cut's own merge commit, `6c8307e0`, so the cut is
not refused on an untagged predecessor.

`bin/docket release --dry-run` listed 8 at filing - `PL-038`, `PL-0TD9`,
`PL-3FYK`, `PL-5MYR`, `PL-NST2`, `PL-QFWF`, `PL-R498` and `PL-SW2K` -
completing no feature. `src/`, `docs/MODEL.md` and `README.md` are
byte-identical to v0.5.9, and `bin/docket wave` reserves 0.6.0 through 0.9.0,
so this is a patch on `ROADMAP.md` § "Versioning decision"'s test. Anything
that merges before the cut ships in it too, so re-run the dry run rather than
trusting this count. Then run `make release VERSION=0.5.10`, make the
`ROADMAP.md` edits it names (the version-table row, the current-baseline mark
and the baseline section) and run `make check`. The tag is the owner's to
push, per `.claude/skills/docket/modes/release.md`.

**The pull request opens as a draft while the claim rides the branch.**
`PL-H14W` is v0.5.9's `#978`, merged by hand six minutes in while that cut was
uncommitted, because a claimed captures-only pull request opens as an ordinary
mergeable one titled for the work. A draft cannot be merged, so it is marked
ready only once the cut is pushed and green. That applies one of the remedies
`PL-H14W` lists to weigh, to this branch only, and decides nothing there.

**Cut 2026-09-24.** 8 items, as the dry run said at filing, and no other pull
request was open. Cut with `make release VERSION=0.5.10`, which recorded the
five `pr:` numbers still missing (`PL-038`, `PL-0TD9`, `PL-5MYR`, `PL-NST2`
and `PL-SW2K`) before rendering the notes, stamped the 8 `milestone: v0.5.10`,
wrote `docs/releases/v0.5.10.md`, bumped `pyproject.toml` and relocked
`uv.lock`. None is a milestone and every number above this one is spent, so
this is a patch on § "Versioning decision"'s test. No feature completes. None
of the 8 is a Gate 2 entry, which stands at 46 of 185 as it did at v0.5.9, and
five are v0.6.0 deferrals. No v0.5.10 item merged inside v0.5.9's tag, which is
on its own cut's merge (`6c8307e0`), so v0.5.9's notes take no pointer.
`src/`, `tests/reference/`, `docs/MODEL.md`, `README.md` and `.github/` are
byte-identical to v0.5.9.

`PL-LRP2` closes in the same commit: `git ls-remote --tags origin` shows v0.5.9
tagged on `6c8307e0`, the cut's own merge, so the tag it asked for is in place.
It ships in the next release, as this item does, because both close after the
notes were rendered.

Filed while cutting: `PL-08D4` (tag v0.5.10, the owner's step) and `PL-WX87`
(`claim` read this branch's stale local tracking ref as the remote's copy, so
its push-at-once never fired here and the session pushed the claim by hand).

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.5.10 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Eight items, all apparatus and documentation, and a patch on both halves of § "Versioning decision"'s test: no capability boundary is crossed, and every number above it is spent, v0.6.0 through v0.9.0 being given to milestone sections. **Nothing in the simulator moved, and this cut says so by tree identity alone**: `src/` resolves to `37b0a4c` at v0.5.9 and here, so `core/` (`d9e3ca9`), `data/` (`ab3499f`) and `app/` (`f3c6e26`) are byte-identical, and `tests/reference/` (`a184830`), `docs/MODEL.md` (`fd139ea`), `README.md` (`9938368`) and `.github/` (`275baf5`) with them. **Four items build `PL-MB2W`'s claim record**: `PL-3FYK` reads a `Claim:` trailer on the holder's own branch under a seven-day lease in one reader, `claims.holdings`, releasing it at `blocked` as well as `done` and `dropped` (project owner, 2026-09-24, ratified, over holding the claim until the item is `done` or `dropped`); `PL-NST2` completes that reader with the landed prefix, status dispositions, the item's `resource:` and cut holds; `PL-0TD9` writes the record with `bin/docket claim` and `bin/docket yield`, which replace start mode's empty-commit recipe; and `PL-SW2K` moves the cutover marker to the writer (project owner, 2026-09-24, ratified, over accepting the window until `PL-0TD9` lands), so a branch started between the two merges is read by the old rules rather than as claiming nothing. `show`, `flight` and `next` move onto the record with `PL-N162`. **Two are the generator machinery**: `PL-5MYR` gives every head a `misread:` line naming the one fact its members misread (project owner, 2026-09-23), which `bin/docket check` requires and `bin/docket generators` prints beside the pairs of heads that share a member, and `PL-QFWF` ranks a blocked live head's direct blockers in the generator tier, where `PL-3FYK` had fallen to an ordinary P2 the moment the design round blocked `PL-MB2W` on it. `PL-038` measures that a mid-session `CLAUDE.md` edit invalidates no prompt cache, and the bullet now says so. **None is a Gate 2 entry**, which stands at 46 of 185 cleared at this cut as at the last, five are v0.6.0 deferrals, and `PL-R498`, the v0.5.9 cut, closes here because a cut cannot stamp itself.
