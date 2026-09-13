---
id: PL-H1JD
title: An outstanding needs_action is lost when its session is archived, so a request nobody acted on drops out of the closing-block read
priority: P3
effort: S
status: done
classes: infra
feature: parallel-sessions
touches: .claude/rules/instruction-writing.md
verify: python3 tools/doc_check.py check && grep -qF 'The block is a handover, not a store.' .claude/rules/instruction-writing.md
closed: 2026-09-13
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

## Decided 2026-09-13: the capture rule already covers it, and the fix is that sentence rather than a mechanism

**Answer: no mechanism.** The alternative reading this brief names is the right
one, and it is not a restatement — it is a rule that was already binding and had
never been pointed at this surface.

**The argument, from the rule this project already has.** `CLAUDE.md`: "Any
defect, risk, cleanup, optimization, inconsistency, or idea identified in a
session and not fixed in that same session gets recorded before the session
ends." An outstanding request to the project owner is squarely inside that list,
and the `v0.3.8` tag is the worked example: it was a real, unfixed thing this
session had identified, so it owed a durable record the moment the session could
not finish it. What went wrong is not that `needs_action` expires — it is that
the request lived *only* there.

**Why building something would have been the wrong answer.** The three
candidates all fail on the same point:

- **Read archived rows too.** Directly contradicts `PL-SK88`'s convention that
  an archived session is finished work, and reintroduces exactly the false
  collision `PL-D4MZ` set the `RUNNING`/`IDLE` filter to prevent. An archived
  session cannot act on its own request, so a live one reading it cannot tell a
  handed-over request from a completed one.
- **Block archiving while `needs_action` is set.** Nothing in this repository
  can enforce it: archiving is a harness action, and `docket` knows nothing
  about sessions and must not (`PL-SK88`).
- **Mirror `needs_action` into the store.** That is `bin/docket new`, reached by
  a mechanism instead of by the rule that already asks for it.

The property that made `needs_action` the cheap answer for `PL-D4MZ` — claims
expire automatically — is the same property that drops live requests, so it
cannot be fixed without giving up what it was chosen for. The store is the thing
in this project that does not expire.

**The edit, made in this session** per `CLAUDE.md`'s rule that a behavior change
takes effect in the session that asks for it. `.claude/rules/instruction-writing.md`
rule 14 gains one bullet: the block is a handover rather than a store, a line
that could reasonably outlive the sitting is `bin/docket new "..."` as well, and
a line the reader acts on now needs nothing. The last clause is deliberate — the
common case is a decision the reply is waiting on, and making *every* closing
line owe an item would turn the block into a queue-writing obligation and
recreate the log-instead-of-queue failure the housekeeping rule already guards
against.

**Cost accepted.** This adds ~11 lines to a resident file, which `make check`
counts. It is taken knowingly: the rule fires when a closing block is written,
which no read precedes, so none of the other three dispositions reaches it — the
routing test in `docs/resident-instructions.md` is what puts it here rather than
in a check or a path-scoped rule.

**Not closed as "already covered", deliberately.** Writing the sentence down is
what makes the coverage real; an unstated implication of a rule three files away
is what let `v0.3.8` sit untagged in the first place.
