---
id: PL-92ZN
title: Record every session's model, served model, mid-session switch, effort, tokens and cost in a per-session ledger written from the harness record by the model review, not by the working session, and backfill it for the sessions behind the 1,759 closed items
priority: P2
effort: M
status: done
classes: session-cost, infra
feature: model-evidence
touches: docs/session-ledger.tsv, docs/maintainer.md, .claude/skills/model-review, docs/items/PL-63CB-add-a-model-review-skill-that-on-a-cadence-and.md, docs/dead-ends.md, docs/items/PL-G2D4-measure-the-excess-miss-rate-of-explore.md
added: 2026-10-17
closed: 2026-10-19
payoff: what model and effort worked every closed item is a durable record in the tree, so the model review has data on its first run instead of in a year
verify: grep -q 'session-ledger' docs/maintainer.md && grep -q 'last_served_model' docs/session-ledger.tsv
recurrences: 2026-10-19 PL-70M6
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

**Progress, 2026-10-19.** The first commit holds 888 rows: every session
`list_sessions` returns for this repository, back to 2026-08-22. A script
parsed them from the saved tool output, so no model retyped a value. 271
sessions named on `main` were missing, and one probe showed why: they are
Projects threads, which `list_sessions` leaves out and `get_session` still
returns. 299 session ids named in `Claude-Session:` trailers and
`docs/pr-bodies/` have no row yet. They are split into six lists in the
session's scratchpad, `ledger/threads/ids_1.txt` to `ids_6.txt`.

**Result, 2026-10-19.** The ledger holds 1,188 rows: 893 from
`list_sessions` and 295 Projects threads from `get_session`. Six Opus 5.5
runners copied the 299 thread records into JSON lines, and a script wrote the
rows. A Sonnet 5.5 copy of 279 of them agreed on every field, and a second
Opus copy of the other 20 agreed too. Four of the 299 were not threads. They
were desktop sessions whose first source was the references repository and
whose second was this one. The first builder kept a session only when this
repository was its first source, so it missed them and one more. It now keeps
a session when any source is this repository.

The join, run against `origin/main` the same day:

- 1,992 `done` items. 1,878 of them (94.3%) join to at least one ledger row.
- 114 `done` items, on 69 pull requests between `#3` and `#1587`, have no
  session id in their squash commit or in `docs/pr-bodies/`. No ledger can
  join them.
- No `done` item names a session that has no ledger row.
- 273 `dropped` items have no `pr:` and so nothing to join.

The join reads any `claude.ai/code/session_...` URL in the squash commit's
body, not only a `Claude-Session:` line. Squash bodies carry the pull request
body, where the URL usually stands on a line of its own. `PL-70M6` should
read it the same way.
