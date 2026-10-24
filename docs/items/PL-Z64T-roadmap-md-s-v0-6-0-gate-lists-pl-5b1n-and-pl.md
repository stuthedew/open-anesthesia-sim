---
id: PL-Z64T
title: ROADMAP.md's v0.6.0 gate lists PL-5B1N and PL-TDBT under the product lane, while docket computes crossing and workflow for them, and nothing holds the three lane groups to the lane each entry's touches computes
priority: P3
effort: S
status: done
classes: defect
touches: ROADMAP.md, .claude/skills/docket/modes/release.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
closed: 2026-10-24
pr: 1721
payoff: a session freezing or working a gate reads each entry's lane from bin/docket gate alone, and ROADMAP.md no longer carries a lane copy that goes stale when touches move
verify: grep -qF 'begins unless deferred - ' ROADMAP.md && grep -qF 'in one group' .claude/skills/docket/modes/release.md
---

**Problem.** ROADMAP.md's v0.6.0 gate lists PL-5B1N and PL-TDBT under the product lane, while docket computes crossing and workflow for them, and nothing holds the three lane groups to the lane each entry's touches computes

**Evidence, 2026-10-03.** Recomputed with `Item.lane(config.workflow_paths)` (`subprojects/docket/src/docket/model.py`) for every open entry under `ROADMAP.md`'s three "Cleared before v0.6.0 begins" groups: 42 open entries, 2 in the wrong group. `PL-5B1N`, listed under the product lane at `ROADMAP.md:5545`, computes `crossing`, since its `touches` includes `tools/contrast_check.py`; `PL-TDBT`, listed under the product lane at `ROADMAP.md:5580`, computes `workflow`, its one `touches` entry being `docs/pr-bodies`. `ROADMAP.md:5386` to `:5390` says the groups follow the lane `docket.toml` computes from each item's `touches`, so the grouping is stale, and no check reads it. Found by the project's coordinator session while reviewing the gate.

**Why it matters.** The groups are how the gate is meant to be worked: the product and workflow lanes share no files, so they run concurrently in two sessions. An entry in the wrong group sends a session to work it beside one it shares a file with - `PL-5B1N` touches `tools/contrast_check.py`, a workflow path - and nothing says so.

**Not covered by.** `PL-M26Q` (`bin/docket gate` prints no lane split) and `PL-KRGY` (where `workflow_paths` places a path) are neighbours, not this. `PL-YBFB` would move `PL-5B1N` out of Gate 2 altogether, which removes one of the two rows and leaves the drift unchecked.

**Re-measured 2026-10-03 at triage.** One of the two rows has moved: `PL-YBFB`
(#1309) put `PL-5B1N` among v0.6.0's deferrals to Gate 3, out of the lane
groups. `PL-TDBT` is still listed under "Cleared before v0.6.0 begins, the
product lane" (`ROADMAP.md:5694`), and its one `touches` entry,
`docs/pr-bodies`, is a `workflow_paths` entry in `docket.toml`.

**Generator check.** One of the five post-close instances of `PL-J6HP`'s fact
named in `PL-QWF8`'s check - here the lane groups restating what `Item.lane`
computes. `PL-74T0` records the head or refuses it as its cluster 2.

[superseded 2026-10-11] **Blocked on `PL-74T0`.** Whether the groups are held to `Item.lane` by a
check, or stop restating it now that `bin/docket gate` prints each lane
(`PL-M26Q`), turns on whether cluster 2's head makes a frozen gate's entries
one record, so a check built first could be work that head's fix removes.
Moving `PL-TDBT` to the workflow group is due either way and rides whichever
lands.

**Generator check, revised 2026-10-11 by `PL-74T0`.** Not a member of the gate
head `PL-8QMD`: the lane groups restate what `Item.lane` computes, which is
`PL-G424`'s fact, the link between a document sentence and the tree fact it
restates. It waited on `PL-8QMD` instead of `PL-74T0`, because the record that
head decided on decided where a gate entry's lane is written, if anywhere.

**Decision needed, 2026-10-12.** `PL-8QMD` closed today: a frozen entry's
deferral is its `deferred-from:`, and `bin/docket gate` prints every open entry
of the last frozen list under its `Item.lane`, debt or not (`PL-QWF8`), so a
lane is read from docket for every open frozen entry. Placing v0.6.0's seven
former deferral-group entries, that change put `PL-5B1N` and `PL-B396` in the
neither-lane group their `touches` compute. `PL-TDBT` is still listed in the
product lane, though done and computing `workflow`. What is left is whether
`ROADMAP.md`'s frozen lists keep grouping their entries by lane: held to
`Item.lane` by a `tools/doc_check.py` check, or no longer restating it, with
one group for what clears before the milestone and a pointer to
`bin/docket gate` and `bin/docket picks` for the split.

**Recommendation: stop restating it.** A lane is computed from `touches`,
which triage and every close-out rewrite, so a held copy owes a `ROADMAP.md`
edit for each such write - the second store `PL-WD5Z` and `PL-8QMD` removed for
dispositions - and a check would have to skip closed entries, whose `touches`
a close-out corrects. Reading the record is
`.claude/rules/apparatus-standard.md`'s answer where the project already records
the fact. What would make it wrong: the owner working a gate from `ROADMAP.md`'s
lane groups rather than from `bin/docket gate` or `picks`.

**Decided 2026-10-12, in the second workflow decision batch: stop restating
it.** Settled by a rule the repository states rather than weighed: a shared
fact has one source of truth, imported from the module that owns it and never
derived again beside it (`CLAUDE.md` § "Architecture and development
discipline", project owner, 2026-10-12). An entry's lane is `Item.lane` over
its `touches` (`subprojects/docket/src/docket/model.py`), and `bin/docket
gate` has printed it for every open frozen entry since `PL-QWF8`, so a lane
group in `ROADMAP.md` is a second copy of a fact docket already states - 2 of
42 open entries wrong when measured on 2026-10-03, and `PL-TDBT` still under
the product lane on `main` at `43d5aeaa`, done and computing `workflow` - and
a check holding the copy to `Item.lane` would be the second store `PL-WD5Z`
and `PL-8QMD` removed for dispositions. The case against, the owner working a
gate from the lane groups rather than from docket, fails on the record: the
lane split is `bin/docket gate`'s and `bin/docket picks`' to print, which the
owner chose on 2026-10-03 (`PL-M26Q`, recorded in `PL-QWF8`). The "Cleared by
v0.6.0 itself" group stays, since it restates Required scope and
`tools/doc_check.py` holds it there through `SELF_CLEARED_GROUP_RE`
(`PL-J6HP`), and `check_gate_counts` reads one group's count as it reads
three. An internal structure of one document is a session's call under rule
14 of `.claude/rules/instruction-writing.md`, so this was decided in the round
and not offered. `tools/doc_check.py` and its test leave `touches`, since no
check is built; `.claude/skills/docket/modes/release.md` joins it.

**Done when.** `ROADMAP.md`'s v0.6.0 frozen list records every entry that
clears before the milestone begins in one group, headed `**Cleared before
v0.6.0 begins unless deferred - N entries**` beside the "Cleared by v0.6.0
itself" group; the paragraph opening "Two kinds of group" says the lane split
is `bin/docket gate`'s and `bin/docket picks`' to print, in place of its three
groups; every sentence in that section placing an entry in a lane group - the
form "is product-lane work and is listed in that group", and the "Deferred
from this gate" subsection's sentences placing a triage pass's captures in the
product lane - says instead that the entry is on the list, with its lane
docket's to print; `.claude/skills/docket/modes/release.md` § "Mode: freeze a
milestone's debt gate" says the list is recorded in one group below the
self-cleared one, with lanes read from `bin/docket gate` when the list is
worked, in place of "Group the list the way `gate` prints its lanes" and
"transcribe that group with the others, by lane"; and `make check` passes.

**Re-confirmed and built 2026-10-24.** Still true when started: `ROADMAP.md`'s v0.6.0 frozen list still held three lane groups of 100, 116 and 13 entries. They are now one group, `**Cleared before v0.6.0 begins unless deferred - 229 entries**`, below the "Cleared by v0.6.0 itself" group, and the total is unchanged. The "Two kinds of group" paragraph now says the lane split is `bin/docket gate`'s and `bin/docket picks`' to print. Every sentence in the section that placed an entry in a lane or a lane group now says the entry is on the list. That covers the post-freeze `safety` entries, the thirteen untriaged at the freeze, the deferred entries and `PL-NDKC`, and the nine triage-pass sentences under "Deferred from this gate". `.claude/skills/docket/modes/release.md` § "Mode: freeze a milestone's debt gate" now says to record the list in one group and to read lanes from `bin/docket gate` or `bin/docket picks` when the list is worked. `python3 tools/doc_check.py check` reports 0 errors, so `check_gate_counts` reads the one group's count.
