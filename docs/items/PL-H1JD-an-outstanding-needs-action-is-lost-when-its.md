---
id: PL-H1JD
title: An outstanding needs_action is lost when its session is archived, so a request nobody acted on drops out of the closing-block read
priority: P3
effort: S
status: needs-decision
classes: infra
feature: parallel-sessions
touches: .claude/rules/instruction-writing.md
added: 2026-09-04
---

**Problem.** An outstanding needs_action is lost when its session is archived,
so a request nobody acted on drops out of the closing-block read

**Observed 2026-09-04, working `PL-D4MZ`.** The closing-block rule that item
added reads `post_turn_summary.needs_action` on the `RUNNING` and `IDLE` rows
only, following `PL-SK88`'s convention that an archived session is finished
work. That is correct for the collision the rule exists to prevent - an
archived session cannot start anything, so it cannot be the second session in
a duplicate start.

It leaves a different problem uncovered. `session_01JwiP9q` was archived while
its `needs_action` still read "git tag -a v0.3.8 ... && git push origin
v0.3.8", and v0.3.8 was in fact untagged at that moment and had been for some
hours. The request was real, outstanding, and unread by anybody. Archiving a
session discards its open request silently, and the only reason this one
survived is that a second session happened to raise the same thing.

So the field expires claims automatically, which is what made it the cheap
answer for `PL-D4MZ` - and the same property drops live requests on the floor.
Whether that is worth a mechanism is the open question: a request that matters
should arguably have become a queue item rather than living in a closing block
at all, which would make this a restatement of `CLAUDE.md`'s capture rule
rather than a gap needing new machinery.

**Why it matters.** The closing block is where an action outside a session's
reach is handed to the project owner, and `needs_action` is the only record that
it was ever asked for. A session archived with one outstanding takes the request
with it silently: v0.3.8 sat untagged for hours with the request live in an
archived session, and the only reason it was noticed is that a second session
happened to raise the same thing.

**Decision needed.** Whether this wants a mechanism at all. The alternative
reading is that anything surviving its session should have been a queue item in
the first place - `CLAUDE.md`'s capture rule already says so - which would make
this a restatement rather than a gap, and would close it by writing that
sentence into the closing-block rule instead of building anything.

**Done when.** Either the closing-block rule says what happens to an outstanding
request when its session is archived, or this item records that the capture rule
already covers it and closes.
