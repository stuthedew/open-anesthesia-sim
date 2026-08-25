---
id: PL-J3ZK
title: Tag releases so a commit can be mapped to the version it shipped in
priority: P2
effort: S
status: ready
classes: infra, session-cost
feature: dev-tooling
touches: subprojects/docket/src/docket/release.py, .claude/skills/docket/SKILL.md
added: 2026-08-25
---

**Problem.** `v0.0.1`, `v0.0.2` and `v0.2.3` are tagged; `v0.1.0`, `v0.2.0`,
`v0.2.1` and `v0.2.2` are not. Those four were bumped in `pyproject.toml` and
shipped without a tag, so `git describe --contains` resolves nothing for any
commit between `v0.0.2` and `v0.2.3`, and there is no way to ask which release
a given change in that span went out in. v0.2.3 was tagged at release
(`7494031`), which starts the practice but does not close the gap behind it.

**Why it matters.** It cost real accuracy once already. Backfilling the
`milestone` field on historical items should have been a git query - find the
first tag containing each item's commit - and instead had to fall back to
stamping all of them `v0.2.2`, which is true but coarse: work that actually
shipped in 0.1.0 or 0.2.0 is now recorded as having shipped in 0.2.2. For a
project whose standard is that a displayed value be traceable to the exact
version that produced it, an unreliable version history is a provenance gap,
not a tidiness one.

**Where.** `subprojects/docket/src/docket/release.py` (the release command
already prints the tag to create, but nothing enforces it),
`.claude/skills/docket/SKILL.md`.

**First step.** Decide whether `docket release` should create the tag itself
or keep printing the instruction. Creating it is a write to shared history
from a tool that otherwise only edits files, which argues for keeping the
instruction and adding a check that the previous version was tagged before a
new one is cut.

**The retrospective half: partly unachievable, established 2026-08-25.**
Two passes were needed, and the first one's answer is wrong - recorded here
because it is the answer anyone will reach first.

*Pass one, superseded.* Searching for the version string in `pyproject.toml`
gives `1f655f0` for v0.2.0, whose own message says the file "was still 0.1.0
after v0.2.0 shipped", and `16939cf` for v0.1.0, a root commit that introduced
the file wholesale. Reading release commits by subject instead - the
convention both existing tags follow - gives `875ba08`/`97cc66a` for v0.1.0,
`796bf4f` for v0.2.0, `bc5f823` for v0.2.1 and `3099980` for v0.2.2. That
looked like four tags waiting to be placed. It is not.

*Pass two: the history has three unrelated roots.* `main` contains `80c7aab`
(the v0.0.2 circuit model), `674c8ae` (shared safety-critical instructions)
and `16939cf` (the line carrying the v0.1.0-to-v0.2.0 application work), first
joined at `3ab9459` "Merge remote-tracking branch 'origin/main'" on
2026-08-23. `git merge-base 796bf4f 97cc66a` returns nothing at all: the
v0.1.0 and v0.2.0 work share no ancestor, so neither can contain the other
under any tag placement, and `git log v0.1.0..v0.2.0` would be meaningless
however the two are tagged. The existing `v0.0.2` tag is on a root commit for
the same reason.

So the goal in this item's title - map a commit to the version it shipped in -
is unreachable for anything before `3ab9459`, and no choice of tag commit
changes that. It is a property of the history, not of the tags.

| Version | Commit | Status |
| --- | --- | --- |
| v0.1.0 | `875ba08` or `97cc66a` | pre-graft; tag would not answer `describe --contains` |
| v0.2.0 | `796bf4f` | pre-graft; same |
| v0.2.1 | `bc5f823` | post-graft, ordered after nothing tagged but before v0.2.2 |
| v0.2.2 | `3099980` | post-graft, ordered correctly against v0.2.1 and v0.2.3 |

**Recommendation.** Tag `v0.2.1` at `bc5f823` and `v0.2.2` at `3099980`; leave
v0.1.0 and v0.2.0 untagged and state why in `ROADMAP.md`'s versioning table.
Those two tags are monotonic against each other and against `v0.2.3`, so from
v0.2.1 onward the history answers version questions properly - which covers
every commit the milestone backfill mis-stamped. Tagging the pre-graft two
would put a version marker on a line that cannot be compared with any other,
which reads as provenance and is not: worse than the gap it appears to close,
per this project's own preference for an obvious absence over a plausible
answer.

The alternative is grafting the roots together with `git replace` or a history
rewrite. That buys a coherent `describe --contains` across the whole history
and costs every existing commit hash, including the ones this queue, the
release notes and `ROADMAP.md` now cite correctly. Not worth it for a
provenance question that only affects four weeks of prehistory - but it is the
only thing that would actually close the gap, so it is the decision, not a
detail.

**Done when.** Cutting a release either creates the tag or refuses while the
previous version is untagged; `v0.2.1` and `v0.2.2` are tagged at the commits
above; and `ROADMAP.md`'s versioning table records that v0.1.0 and v0.2.0 are
deliberately untagged, with the unrelated-roots reason.

**Context.** Found while inverting the milestone model so that a release
records what shipped rather than planning what will. The backfill is recorded
in the commit that introduced it.
