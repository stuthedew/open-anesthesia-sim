---
id: PL-TM9J
title: Cut v0.4.27 from the 6 finished items since v0.4.26: a patch on the v0.4.x track, carrying no learner-facing change, with v0.5.0 through v0.9.0 reserved
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items/
added: 2026-09-17
closed: 2026-09-17
pr: 659
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.27"' pyproject.toml && test -f docs/releases/v0.4.27.md && grep -q '^## Current baseline: v0.4.27' ROADMAP.md
---

**Problem.** Cut v0.4.27 from the 6 finished items since v0.4.26: a patch on the v0.4.x track, carrying no learner-facing change, with v0.5.0 through v0.9.0 reserved

**Asked for by the project owner, 2026-09-17**, on the offer
`session_01Gi9jxdTAjfoL1QZvcF87mA` left outstanding when it was archived. Six
items sit unshipped since `v0.4.26` (`bin/docket release --dry-run`):
`PL-06YW` (the v0.4.26 cut itself), `PL-C6XD` (the duplicated `RESERVED`
refusal in `render.format_status`), `PL-K82G` and `PL-L4KX` (the two
`bin/docket verify` integrity checks that had no passing route for a correct
close-out), `PL-MQHN` (Preferences and Workspaces must be separate stores) and
`PL-YHWG` (the reopened placement of item 34's area system).

**Why this number.** The mechanical bump and the named one agree at `0.4.27`
for once, so there is no version argument to make — but the reasons are worth
recording, because the last three cuts each had one. `bin/docket wave` reports
`Reserved 0.5.0, 0.6.0, 0.7.0, 0.8.0, 0.9.0`, every one of them spent by a
`ROADMAP.md` milestone section, so the `v0.4.x` patch track is the only place a
cut can land. And § "Versioning decision"'s test is the capability boundary a
release crosses: nothing in these six changes a displayed value, an equation, a
parameter, a unit or a numerical method — five are apparatus and two of those
are decisions recorded rather than code — so a patch is what it is, not a
concession to the reserved set.

**Why the no-interim-release rule does not bind.** § "The debt gate" → "The
cadence" refuses a release cut partway through clearing a gate, so that gate
work ships inside the milestone it gates rather than scattering across patches.
Checked rather than assumed: none of the six appears in Gate 1's frozen list or
in either of its deferral sections, and none appears in v0.5.0's `Required
scope`. Gate 1 stands at 167 of 170 cleared with **nothing left that it can
clear** — its three open entries (`PL-WZVZ`, `PL-Z34C`, `PL-8PS6`) are blocked
on work outside the gate. So no gate work is being scattered and no
Required-scope item ships early, which also means the v0.5.0 timeline row's
early-shipped tally (six, as of `PL-8PSW` in v0.4.26) is unchanged by this cut.

**Why cut at all, rather than waiting for v0.5.0.** `v0.4.26` is tagged on
`origin` at `4f2c2f1`, so the refusal-on-untagged-predecessor does not bind,
and the next number the plan will reach is `v0.5.0` — a milestone whose
`Required scope` is 19 of 26 closed and whose implementation is the current
beat. Leaving these six untagged means the span between them and that release
is unresolvable by `git describe --contains`, and two of the six are the
integrity checks in `bin/docket verify` that every close-out now runs: the tag
is what lets a later session say which tree first had a `verify` that could
accept the close-out procedure the skill prescribes.

**What the cut carries in `ROADMAP.md`.** The version-table row, the
`current baseline` mark moved onto it, and the baseline section rewritten onto
this release — the three `bin/docket release` names. `PL-Y1L0`'s finding, that
`outstanding_roadmap_edits` returns the same three statements whatever the
version, has no fourth edit hiding behind it here: `0.4.27` reaches no
milestone section, so there is no heading to promote.

**Why it matters.** Two of the six are the reason the close-out procedure
works at all. `PL-K82G` and `PL-L4KX` were the case where `bin/docket verify`
could not accept a correct close-out — an item whose own work falsifies a
rendered string, and a `dropped` or `not-delegable:` item with no command to
run — so the audit step the `docket` skill prescribes returned `REJECT` on work
that was right, which is exactly how a reader is trained to skim the block
where a real protected-path failure prints. A tag is what makes "the tree where
that stopped being true" nameable afterwards. `PL-C6XD` is the same shape one
level down: a second independent copy of the `RESERVED` refusal that no item
covered, in the surface a session reads to decide whether a release can be cut
at all. And `PL-MQHN` and `PL-YHWG` are decisions with no code behind them,
which is precisely the kind of work that vanishes without a release note
naming it — `PL-MQHN` constrains three items being designed now, and `PL-YHWG`
reopens where item 34's area system sits relative to v0.5.0.

**Done when.** `pyproject.toml` and `uv.lock` read `0.4.27`,
`docs/releases/v0.4.27.md` exists, the version table carries the row, the
`Current baseline` section stands on `v0.4.27`, `make check` is green, and
`v0.4.27` is tagged on the merge commit on `origin/main`.

## Cut 2026-09-17

`make release VERSION=0.4.27` stamped 6 items, wrote `docs/releases/v0.4.27.md`
and relocked `uv.lock`. Three of the six recorded no `pr` yet, so
`bin/docket record` wrote them - `PL-K82G` and `PL-L4KX` to `#655`, `PL-MQHN` to
`#654` - and the notes were regenerated afterwards through the documented resume
path (delete the notes file, re-run the same number), so all six carry their
pull request rather than three of them.

Three edits followed in `ROADMAP.md`, which is the whole of what
`bin/docket release` named: the version-table row, the `current baseline` mark
moved off the v0.4.26 row, and the baseline section rewritten onto this release.
`PL-Y1L0`'s hidden fourth edit did not apply - `0.4.27` reaches no milestone
section, so no heading needed promoting - and the v0.5.0 timeline row's
early-shipped tally is untouched, because none of the six is a Required-scope id.

**The measured claim in the release prose was measured.** `src/`, `tests/` and
`docs/MODEL.md` are byte-identical to `v0.4.26`, compared by tree object
(`git rev-parse v0.4.26:<path>` against `HEAD:<path>`) rather than by reading the
diff. Outside `docs/items/`, the release changes eleven files: `ROADMAP.md`,
`docs/interface-provenance.md`, `.claude/rules/ui-areas.md`,
`.claude/skills/docket/SKILL.md`, `subprojects/docket/README.md` and six files
under `subprojects/docket/src/` and `tests/`.

**Docs swept:** `ROADMAP.md` (table row, baseline mark, baseline section),
`docs/releases/v0.4.27.md` (generated),
`python3 tools/doc_check.py candidates --base origin/main` returned only
`pyproject.toml` and `uv.lock` mentions, which are statements about those files'
role rather than their version, plus the three new `v0.4.27` lines in
`ROADMAP.md`. The four sites naming `v0.4.26` outside the queue were read:
`docs/ARCHITECTURE.md:67` and `:741` cite the port's `## Completed:` section,
which still exists, and `subprojects/docket/README.md:949` uses the port row as
the worked example of a `-` timeline row, which is unchanged. The fourth,
`.claude/skills/docket/SKILL.md:1039`, is stale and is captured as `PL-D7T9`
rather than fixed here - it is outside this item's `touches`, so
`CLAUDE.md`'s fix-now door is shut on it.

`make check` green: 2 992 tests, 100% coverage, `docket check` 0 errors,
`doc_check` 0 errors and 0 advisories.
