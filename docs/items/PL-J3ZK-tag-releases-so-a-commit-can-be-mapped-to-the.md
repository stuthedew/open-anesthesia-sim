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

**The retrospective half, resolved to candidates 2026-08-25.** Do not find
these by searching for the version string. `git log -S'version = "0.2.0"' --
pyproject.toml` returns `1f655f0`, which is wrong in a way that matters:
that commit's own message says `pyproject.toml` "was still 0.1.0 after v0.2.0
shipped", so the version string trailed the release it names. The same search
for `0.1.0` returns `16939cf`, a root commit that introduced `pyproject.toml`
wholesale. The version string is a known-unreliable witness here - the project
found and fixed that staleness itself, in `1f655f0`.

What is reliable is the convention both existing tags already follow: the
release commit's subject names the version. `v0.0.1` is on `b64d768` "Build
v0.0.1 prototype" and `v0.0.2` on `80c7aab` "Build v0.0.2 circuit wash-in
model". By that rule:

| Version | Commit | Confidence |
| --- | --- | --- |
| v0.1.0 | `875ba08` "Build v0.1.0 sevo patient simulation" | ambiguous - see below |
| v0.2.0 | `796bf4f` "Add isoflurane and desflurane as additional volatile agents (v0.2.0)" | high; also the commit that added the two agent data files |
| v0.2.1 | `bc5f823` "Reject impossible inputs instead of simulating them (v0.2.1)" | high |
| v0.2.2 | `3099980` "PL-025 Release the post-v0.2.1 work as v0.2.2" | high |

Only v0.1.0 needs a judgment call: `97cc66a` "Close v0.1.0 doc/test gaps:
arterial-blood simplification, roadmap sync, required tests" lands after
`875ba08` and completes what `ROADMAP.md`'s v0.1.0 definition of done
requires, so the tag belongs on one or the other depending on whether a
version marks where the work started shipping or where it met its gate. Decide
that once; it is the same question for any future milestone built across
several commits. If it cannot be settled from the record, tag the three that
are clear and record v0.1.0 as unrecoverable rather than tagging a guess -
a wrong tag is worse than a missing one, because it answers confidently.

**Done when.** Cutting a release either creates the tag or refuses while the
previous version is untagged, and the existing untagged versions have been
tagged retrospectively at the commits that shipped them.

**Context.** Found while inverting the milestone model so that a release
records what shipped rather than planning what will. The backfill is recorded
in the commit that introduced it.
