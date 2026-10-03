---
id: PL-JV5Q
title: Gate 3's freeze takes its list from bin/docket gate, which prints open debt only, so PL-5B1N (feature) and PL-B396 (ux, docs), both deferred to Gate 3 from Gate 2, will not be on it, and release.md's freeze mode never tells the freezing session to carry a previous gate's deferrals
priority: P2
effort: S
status: ready
classes: defect
touches: .claude/skills/docket/modes/release.md, ROADMAP.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-03 triage pass
added: 2026-10-03
payoff: Gate 3's frozen list carries every entry the v0.6.0 gate deferred to it, the two non-debt ones included
verify: grep -qi 'deferr' .claude/skills/docket/modes/release.md
---

**Problem.** Gate 3's freeze takes its list from bin/docket gate, which prints open debt only, so PL-5B1N (feature) and PL-B396 (ux, docs), both deferred to Gate 3 from Gate 2, will not be on it, and release.md's freeze mode never tells the freezing session to carry a previous gate's deferrals

**Found by `PL-YBFB`, 2026-10-03.** `ROADMAP.md` § "The cadence" beat 3 lets a
gate entry be deferred to a later gate only where the deferral names the gate
it lands in (`PL-S5Q9`), and the v0.6.0 gate section now defers six open
entries to Gate 3. The freeze mode in `.claude/skills/docket/modes/release.md` builds a
frozen list from `bin/docket gate`, which prints open items classed `defect`,
`safety`, `science`, `refactor` or `perf`, or at `needs-decision`. Four of the
six are `safety` or `science` and will be printed. `PL-5B1N` (`feature`, now at
`blocked` behind `v0.7.0`) and `PL-B396` (`ux` and `docs`, held behind
`PL-YRLM`) will not, and nothing in the freeze mode says to read the previous
gate's deferral paragraphs. `PL-YBFB` wrote the instance into `PL-5B1N`'s
paragraph, which tells the session freezing Gate 3 to write it onto that list
from there; the five's paragraph says instead that Gate 3 "inherits all five
as this gate inherited `PL-WZVZ`", which holds for the four debt entries only.
Gate 3 freezes when v0.6.0 ships, so that freeze is where it bites.

**Checked 2026-10-03 at triage.** `.claude/skills/docket/modes/release.md`
says nothing about deferrals: `grep -i deferr` finds no line in it.

**Why it matters.** Gate 3's frozen list is the debt v0.7.0 must clear before
it begins. Built from `bin/docket gate` alone it drops `PL-5B1N` and `PL-B396`
without a word, so two entries the v0.6.0 gate deferred to Gate 3 by name are
held by no gate.

**Done when.** The freeze mode in `release.md` tells the freezing session to
carry every entry the previous gate deferred to the gate being frozen, debt or
not, and the five-entry deferral paragraph in `ROADMAP.md` says how
`PL-B396`, which `bin/docket gate` does not print, reaches Gate 3's list.

**Generator check.** One of the five post-close instances of `PL-J6HP`'s fact
named in `PL-QWF8`'s check; `PL-74T0` records the head or refuses it as its
cluster 2.
