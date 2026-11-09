---
id: PL-SW0D
title: Cut v0.4.30 from the 8 items finished since v0.4.29: the release that completes generator-heads
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.31
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-19
closed: 2026-09-19
pr: 730
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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.30 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Eight items, all apparatus, and a patch because nothing crosses a capability boundary: `git diff --stat v0.4.29..HEAD -- src/` reports no file changed at all, `src/anesthesia_sim/data/` resolves to `d9f9c5b` at both `v0.4.29` and here so no stored scientific value moved, and `tests/reference/` resolves to `fcb3eca` so every published-reference expected value is byte-identical and still met. **It completes `generator-heads` at 7 of 7** - the programme of recorded root causes that `CLAUDE.md` ranks above everything but a `P0` - and in the same release repairs the tool that ranks them. **`tools/generator_check.py` was blind to the generator the project was working through it** (`PL-LSR0`): `clusters()` partitions open items by a single declared `touches` path and `STORE_PATHS` held `docs/items`, `docs/WORKING_NOTES.md` and `docs/dead-ends.md` out of that partition, an exclusion borrowed from `docket trend` - correct there, because churn counts the files a *commit* changes and every capture changes the store, and wrong here, because on the `touches` axis a capture declares its own subject. The three paths carried 24, 18 and 0 open items when it was measured and removed, and of `PL-G424`'s 21 members 8 declare `docs/WORKING_NOTES.md` and 5 declare `docs/items`, so the blind spot covered both clusters carrying the family. Ranking was the second half: size was the first tiebreak, so that 8-member cluster sorted ninth behind clusters nobody had cited, under a display limit of six; how many other open items name the path now breaks ties ahead of size, and the readings are still deliberately not combined into a score. **`PL-G424` itself was decided by counting** - all 676 line citations in the store classified, 48.0% stale in closed briefs (196/408), 15.6% in open ones (36/231) and 0.0% in the standing documents (0/5) - which killed the obvious route, since extending `PL-4FBP`'s annotation convention across the apparatus would have checked 2,286 id mentions to find nothing. `.claude/rules/citation-drift.md` records what was adopted instead: a closed brief is a historical record rather than a live assertion, so drift there is not a finding; an open brief and a standing document are live and repaired in place; and a line number is not a citation anchor. Only resolvability is scripted, in `tools/doc_check.py`. `PL-DLMM` corrects that file and the item, which both said the project owner had not taken a decision they had ratified. **`PL-YFXG` left `main` red with no documented way out**: `_number_closing` declines a pull-request number when the closing commit changed nothing outside `docs/items/`, which is right about a closure separated from its work and wrong about an item whose work *is* the queue - `PL-YTDN`'s `ceb9385` (#712) changed 12 files, all in the store, and carried both. `PL-TQFB` excuses a `housekeeping` item its `**Why it matters.**` and `**Done when.**` sections, measured against 22 triage-pass items carrying 1,127 lines of brief of which 12 repeat one rationale and 2 hold a finding. `PL-6ZQY` swept the crossing lane and corrected ten briefs that overstated what was left; `PL-CSV0` folded the day's twelve captures into the queue. `PL-GL5P`, the v0.4.29 cut, closes here.
