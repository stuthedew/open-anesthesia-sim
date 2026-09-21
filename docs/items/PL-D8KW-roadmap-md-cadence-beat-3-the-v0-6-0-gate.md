---
id: PL-D8KW
title: ROADMAP.md cadence beat 3, the v0.6.0 gate section and docket's release mode all name PL-6ZQY as the standing item for the pre-gate staleness sweep, but PL-6ZQY closed 2026-09-19 two days before Gate 2 froze, so the pass every gate must run before any entry is worked has no open instrument and a session that looks it up reads done
status: untriaged
feature: gate-staleness-sweep
added: 2026-09-21
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
