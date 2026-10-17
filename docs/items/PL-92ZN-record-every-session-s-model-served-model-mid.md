---
id: PL-92ZN
title: Record every session's model, served model, mid-session switch, effort, tokens and cost in a per-session ledger written from the harness record by the model review, not by the working session, and backfill it for the sessions behind the 1,759 closed items
priority: P2
effort: M
status: ready
classes: session-cost, infra
feature: model-evidence
touches: docs/session-ledger.tsv, docs/maintainer.md, .claude/skills/model-review
added: 2026-10-17
payoff: what model and effort worked every closed item is a durable record in the tree, so the model review has data on its first run instead of in a year
verify: grep -q 'session-ledger' docs/maintainer.md && grep -q 'last_served_model' docs/session-ledger.tsv
---

**Problem.** Record every session's model, served model, mid-session switch, effort, tokens and cost in a per-session ledger written from the harness record by the model review, not by the working session, and backfill it for the sessions behind the 1,759 closed items

**Why it matters.** The choice of model and effort for an item is a cautious
default today because nothing in the tree records what worked each closed
item, so neither direction of error can be seen: a cheap session whose work
needed rework later, or an expensive session on work a cheaper one would have
done as well. The harness already records the fact per session. `get_session`
returns the configured model, the model that served the last turn, whether the
owner switched model mid-session, the effort level, token counts by kind and
the cost in dollars, and archived sessions still return all of it. Every
commit a session makes carries a `Claude-Session:` trailer that the squash
merge keeps, so the join from a closed item to its sessions exists with no new
field. What does not exist is a copy in the tree, and the harness's retention
is unknown.

Measured 2026-10-17 on `origin/main`: 1,759 closed items; 1,423 join to at
least one session id through their merge commit; 756 distinct sessions behind
them; 10 items worked by more than one session; the oldest archived record
read with model, effort and cost was from 2026-08-23. The other 336 items need
a second route, through `docs/pr-bodies/` (259 of its 267 files carry a session
link) or the pull request on GitHub. No file in the tree holds a session's
model or effort: `grep -rl effort_level docs tools subprojects` returns
nothing.

**What was decided** (project owner, 2026-10-17, ratified, over the three
routes below). The harness session record is the source of truth, and the
tree carries a dated copy: one row per session, written only by the model
review (`PL-63CB`) from `list_sessions` and `get_session`. The working session
writes nothing new about itself. Chosen over: a field or commit trailer the
working session writes, which `PL-B11M` refused on 2026-09-16 because a
self-report records the configured model and a fallback can serve another, and
which would also add a step to every session, which the owner refused; a copy
on each closed item, which would repeat a session's cost once per item it
closed and edit item files under in-flight branches; and a committed analysis
tool, which the owner refused in favour of a session doing the analysis.
`PL-B11M`'s gate, naming a decision that changes on learning a past session's
model, is met by this feature: which model and effort to use on which kind of
item. The dead-ends entry against an index beside the items refuses content
that is recomputable; this ledger is not recomputable once the harness drops a
record, and it has one writer, so the serialization cost that refused one
shared queue document does not apply.

**Done when.** A ledger file, recommended `docs/session-ledger.tsv` and
readable with the standard library, holds one row per session: session id,
title, created and updated timestamps, configured model, session-context
model, last served model, user-switched model, effort level, input, output,
cache-read and cache-write tokens, cost in USD, context used at the last read,
and the date the row was written. Every session reachable from a closed item's
merge commit or pull request body has a row, and this brief records the count
that could not be joined. The model review's procedure says how the ledger is
refreshed. No resident text, check, digest line or close-out step is added:
the owner's constraint is that this costs working sessions nothing.

**Generator check.** Work the owner asked for on 2026-10-17, which lifts the
workflow-mechanism pause for this feature. Not an instance of a head: the fact
nothing records is the harness's own session metadata, an external record no
reader here has misread.
