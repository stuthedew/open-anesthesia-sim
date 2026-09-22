---
id: PL-CPLX
title: .claude/skills/docket/SKILL.md says v0.4.26 and v0.6.0 are both milestones scoped out of turn whose gate freezes when the milestone before them ships, but v0.4.26 shipped on 2026-09-17 and took no gate of its own, so the example names a release that can no longer be waiting for anything
priority: P3
effort: S
status: ready
classes: docs
touches: .claude/skills/docket/SKILL.md
added: 2026-09-17
verify: ! grep -rqF 'v0.4.26 and v0.6.0 are both in that state' .claude/skills/docket/ && python3 tools/doc_check.py check
---

**Problem.** .claude/skills/docket/SKILL.md says v0.4.26 and v0.6.0 are both milestones scoped out of turn whose gate freezes when the milestone before them ships, but v0.4.26 shipped on 2026-09-17 and took no gate of its own, so the example names a release that can no longer be waiting for anything

**Found 2026-09-17**, by `python3 tools/doc_check.py candidates --base origin/main`
during the `PL-06YW` release cut, which named the skill's
debt-gate section as documentation touching the diff.

**The sentence.** § "Mode: freeze a milestone's debt gate" states the
out-of-turn exception - a milestone scoped before its turn freezes its gate
when the milestone *before* it ships - and ends "v0.4.26 and v0.6.0 are both in
that state." v0.4.26 shipped on 2026-09-17, and `ROADMAP.md` § "The debt gate"
-> "The cadence" says it "took no gate by its own exception", so it is not
waiting on a freeze and never was.

**Why it matters.** The sentence is the worked example a session reads to
decide whether the exception applies to the milestone in front of it, and half
of the example is now a release in the past that had no gate. That is the shape
that teaches the wrong rule quietly: a reader matching their situation against
two instances, one of which is not an instance.

**Not fixed in the session that found it**, because `CLAUDE.md`'s fix-now door
needs the change to stay inside the current item's declared `touches`, and
`PL-06YW` declares no `.claude/` path. `bin/docket verify` reads the diff for
exactly that.

**Done when.** The example names only milestones actually awaiting a freeze,
and says what happened to v0.4.26 if it is worth keeping as a closed case.

**Done when** the out-of-turn exception's worked example names only milestones
that are genuinely waiting for a freeze, and says what happened to v0.4.26 - it
shipped 2026-09-17 having taken no gate by its own exception - if that closed
case is worth keeping. A reader matching their situation against two instances,
one of which is not an instance, is the shape that teaches the wrong rule
quietly.
