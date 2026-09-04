---
id: PL-ZSV6
title: A triage reply recommends work and drives fixes, when it should summarize what was triaged and where the queue stands
status: done
priority: P2
effort: S
classes: infra, docs
feature: worker-instructions
touches: .claude/skills/docket/SKILL.md
verify: python3 tools/doc_check.py check && grep -qF 'Triage is a queue pass, not a work session' .claude/skills/docket/SKILL.md
added: 2026-09-04
closed: 2026-09-04
---

**Problem.** `.claude/skills/docket/SKILL.md`'s "Mode: triage" said how to fill
an item's fields and nothing about what the reply is. Every other mode states
its output shape, so a triage session fell through to the general habit of
ending with recommendations - and, having read the item closely enough to
triage it, to fixing what it found.

**Observed 2026-09-04, in the session that prompted this.** A triage pass with
one untriaged item answered that item's open design question, opened a pull
request, drove it to green, and closed with three things for the owner to do -
one of which (`PL-X3WZ`, a commit that only annotates an item's brief marks it
`IN FLIGHT`) was unrelated to anything triaged. The owner's correction: "Triage
session should not provide unrelated recs to work on in the session, it should
provide a summary of the triaged items and overall project/item structure ...
It should not balloon into a fix session itself."

**Why it matters.** The cost is not the reply's length. A triage pass is cheap
and bounded by design - it is the mode a session reaches for when the queue has
drifted, not when there is usage to spend - and converting it into a work
session spends that budget on one item while leaving the queue undescribed,
which was the job. It is also the ideation-to-implementation slide the skill
already forbids twice, arriving through a door it had not closed: the reply
itself.

**Where.** `.claude/skills/docket/SKILL.md`, "Mode: triage".

**Done when.** The triage mode states what the reply contains - the triaged
items, and the queue's shape - says plainly that it ends there, routes a
genuinely pressing finding to another session rather than working it, and
declines to manufacture one when nothing pressing surfaced. Landed as three
edits: a `### What the reply says, and what it must not` subsection; a rule that
an item whose next step is a decision is triaged to `needs-decision` rather than
answered; and "a triage pass" added to the list of replies where a release is
not offered.

**Retroactive.** `PL-55JM` (drift.yml's two bare pytest runs) was triaged to
`ready` in that same session with its open question answered. Moved to
`needs-decision` under the new rule; the reasoning stays in its brief as a
recommendation, so the decision costs one read rather than a re-investigation.
