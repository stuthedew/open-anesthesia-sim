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
