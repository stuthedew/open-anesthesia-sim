---
id: PL-SW0D
title: Cut v0.4.30 from the 8 items finished since v0.4.29: the release that completes generator-heads
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-19
closed: 2026-09-19
verify: grep -q '^version = "0.4.30"' pyproject.toml && test -f docs/releases/v0.4.30.md && grep -q '^## Current baseline: v0.4.30' ROADMAP.md
---

**Problem.** Cut v0.4.30 from the 8 items finished since v0.4.29: the release that completes generator-heads

**Asked for by the project owner, 2026-09-19.** Eight finished items stand
unshipped since `v0.4.29` (`bin/docket release --dry-run`), and they complete
`generator-heads`.

**Why this number.** The mechanical guess is `0.4.30` and nothing contests it:
`bin/docket wave` reports `0.5.0, 0.6.0, 0.7.0, 0.8.0, 0.9.0` as reserved by
`ROADMAP.md`, so no minor number is free, and a patch is what the content
warrants. `git diff --stat v0.4.29..HEAD -- src/` reports no file changed at
all, `src/anesthesia_sim/data/` resolves to `d9f9c5b` at both `v0.4.29` and
here so no stored scientific value moved, and `tests/reference/` resolves to
`fcb3eca` so every published-reference expected value is byte-identical and
still met. All 82 changed files are apparatus.

**The two refusals were checked rather than assumed.** `v0.4.29` is tagged on
`origin` at `27bb8d6` (`git ls-remote --tags origin`), so the
refusal-on-untagged-predecessor does not bind. And the cadence's
"no interim release is cut partway through clearing" rule does not bind either:
**none of the eight is a Gate 1 frozen entry**, checked against the list itself
- `ROADMAP.md` § "v0.5.0 - the case you can branch" -> "Debt gate: the frozen
list" - rather than against a count. `PL-YFXG` is the only one the gate section
names in a list, and that list is the later
§ "Declined to Gate 2 on the refilling-queue ground". The gate's two clearable
entries - `PL-JVHL` and `PL-7DMJ` - are untouched by this release, so no gate
work scatters into a patch.

**Why it matters.** `bin/docket release` refuses to cut a release while the
previous one is untagged, so an unshipped run of finished work compounds: the
next cut cannot start until this one is tagged, and the items stay unstamped
with no `milestone:` recording where they shipped. The release notes are also
the only place the eight are read as one thing rather than as eight files.

**Done when.** `pyproject.toml` reads `0.4.30`, `uv.lock` agrees,
`docs/releases/v0.4.30.md` exists, `ROADMAP.md` carries a `v0.4.30` version-table
row with the `current baseline` mark moved onto it and a baseline section saying
what the release was for, and `make check` passes. The tag itself is the project
owner's to push and is outstanding until they confirm it.
