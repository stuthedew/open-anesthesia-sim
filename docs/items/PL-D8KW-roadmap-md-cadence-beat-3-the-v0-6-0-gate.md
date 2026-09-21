---
id: PL-D8KW
title: ROADMAP.md cadence beat 3, the v0.6.0 gate section and docket's release mode all name PL-6ZQY as the standing item for the pre-gate staleness sweep, but PL-6ZQY closed 2026-09-19 two days before Gate 2 froze, so the pass every gate must run before any entry is worked has no open instrument and a session that looks it up reads done
priority: P2
effort: S
status: done
classes: defect, docs
feature: gate-staleness-sweep
touches: ROADMAP.md, .claude/skills/docket/modes/release.md
added: 2026-09-21
closed: 2026-09-21
verify: ! grep -qE "PL-6ZQY. is the standing item" ROADMAP.md .claude/skills/docket/modes/release.md
---

**Problem.** ROADMAP.md cadence beat 3, the v0.6.0 gate section and docket's release mode all name PL-6ZQY as the standing item for the pre-gate staleness sweep, but PL-6ZQY closed 2026-09-19 two days before Gate 2 froze, so the pass every gate must run before any entry is worked has no open instrument and a session that looks it up reads done

## The citations are headings, because line numbers drift

Written as `ROADMAP.md:6172` and `ROADMAP.md:5394` when this was filed on
2026-09-21, and already `6202` and `5411` the same afternoon - `#854` landed
between the two readings. `.claude/rules/citation-drift.md` states the rule this
demonstrates: a line number is not a citation anchor, and only resolvability is
scripted. So the three sites are named by heading, which is what a session
should search for:

1. `ROADMAP.md` § "The debt gate" -> "The cadence", beat 3 - the sentence
   "`PL-6ZQY` is the standing item for the pass."
2. `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Debt gate: the
   frozen list", under the bolded "What this list is not swept for yet" - the
   sentence "`PL-6ZQY` is the standing item for it, and it runs against this
   list before implementation of this milestone begins."
3. `.claude/skills/docket/modes/release.md`, § "Mode: freeze a milestone's debt
   gate" - the sentence "`PL-6ZQY` is the standing item for the pass, and its
   own brief carries a 134-item map whose verification phase never finished".

`grep -n "PL-6ZQY" ROADMAP.md .claude/skills/docket/modes/release.md` finds all
three and one unrelated mention in the v0.4.30 release row, which is a
historical record and correctly left alone.

**What the repointing must not do:** name another item that can close. The
instrument for a recurring beat has to outlive any one pass, or this defect
returns at Gate 3 under a new id. Either the sentence names no item and states
the pass, or the item it names is one that cannot reach `done` - that choice is
this item's work.

## What was done: the beat names no item at all

All three sites now instruct a session to *file* the pass under `feature:
gate-staleness-sweep` rather than to *look up* a standing one. That is the
first of the two dispositions the section above left open, and it was chosen
over the second — naming an item that cannot reach `done` — because no such
item exists in this store and inventing one would be a mechanism built to
carry a sentence.

**The near-miss worth recording: a `feature:` handle fails the same test.**
`bin/docket feature gate-staleness-sweep` looks like a durable instrument,
since a feature name is not an item and cannot close. But once Gate 2's
members close it prints `2/2 done`, and a Gate 3 session reading it learns
exactly what a session reading closed `PL-6ZQY` learned. The failure is not
that the pointer named an item; it is that the sentence was a *lookup* at all.
An imperative — file one — has no state to be stale.

The feature name survives in the new text as the label to file under, which is
a different job: it groups each gate's pass so `bin/docket feature
gate-staleness-sweep` answers "has this gate's sweep been run" for whoever
asks, without any sentence depending on the answer.

`PL-6ZQY` still appears at two of the three sites, now as provenance — what
happened, and the 134-item map whose verification never finished — which
`.claude/rules/citation-drift.md` holds to be the correct and only use of a
closed brief.
