---
id: PL-B11M
title: Detect a silent model fallback: last_served_model can differ from the configured model with nothing recording it
priority: P3
effort: S
status: done
classes: infra, session-cost
feature: commit-provenance
touches: tools, .claude
added: 2026-09-16
closed: 2026-10-01
not-delegable: closed unbuilt on a decision: whether any project decision consumes the served model is a judgment about the rules, and the count behind it is read from the harness session list, which no command in the tree can reach
---

**Problem.** A session's configured model and the model that actually served a
turn are different facts, and they can diverge without anything in the
repository recording it. The harness falls back on overload or unavailability,
which changes the served model for that turn while leaving the configured one
alone. `get_session` reports both — `session_context.model` for what the
session is set to run, `external_metadata.last_served_model` for what ran the
latest turn — but nothing in this project reads the second, so a downgraded
session leaves no trace in the item, the commit, or the pull request.

**Why it matters.** This project delegates a great deal of judgment to
sessions: which approach is chosen, whether a rule is worth keeping resident,
whether an argument in a brief is sound. `bin/docket delegable` already reasons
explicitly about what a cheaper model may work and what proves it, so model
tier is treated as decision-relevant here. If tier matters going in, an
unrecorded change of tier mid-session is a gap in exactly the provenance chain
the project is otherwise careful about.

**Where it came from.** Raised 2026-09-16 when the project owner asked whether
the repository's commit convention should start naming the model. **Decided
against, project owner, 2026-09-16: the convention is unchanged** — the trailer
stays `Co-authored-by: Claude <noreply@anthropic.com>`, with no model id in any
pushed artifact. Three reasons, and the decisive one is what produced this
item: a trailer the session writes itself
would record the *configured* id, so it would be confidently wrong at the one
moment the information mattered. That is the failure `CLAUDE.md`'s
safety-critical standard names as preferring an obvious failure state to a
plausible-looking value, arriving in provenance rather than in a clinical
number. So the gap is real; a commit trailer is simply the wrong instrument for
it, because the fact lives harness-side and per turn.

The two supporting reasons, recorded so the question is not reopened as a
matter of taste. `Co-authored-by` is a people field that GitHub resolves to
accounts, so splitting it across model names fragments attribution for no gain
and churns on every model release. And a repository rule requiring a model id
would stand in permanent conflict with the harness instruction against one,
leaving every session with two contradictory rules — the condition Claude Code's
own documentation says it may resolve arbitrarily, and the failure `PL-5D2R`
was filed against. Inconsistent trailers are worse provenance than none.

**Not a dead-ends entry, on that file's own test.** `docs/dead-ends.md` earns a
line only where a session could propose the approach again without first
reading what refutes it. No session would propose this one: the harness pushes
the other way unprompted. The question came from the project owner, so the
answer belongs here, where it is retrieved by `bin/docket show PL-B11M` at no
cost to any session that never asks.

**Not yet designed, and the gate it has to clear first.** `CLAUDE.md`
§ "Prefer deterministic tooling over repeated model work" asks whether a
mechanism will genuinely run again and says the answer is no where the benefit
is unclear. It is unclear here: nobody has yet named a decision that would
change on learning a past session was downgraded. Answer that before building
anything. If it cannot be answered, the honest outcome is to close this
unbuilt — which is a legitimate result, not a loss.

**Done when.** Either a decision this project takes is named that would change
on learning a past session was served by a different model than it was
configured for, and the cheapest instrument that records it is built; or the
item is closed unbuilt with that answer written down, so the question is not
reopened as a matter of taste.

**Decision needed.** Whether any such decision exists. `CLAUDE.md` § "Prefer
deterministic tooling over repeated model work" gates a mechanism on whether it
will genuinely run again and says the answer is no where the benefit is unclear.
It is unclear here: `bin/docket delegable` reasons about model tier going in, and
nothing reads tier coming out. Answer that before designing anything. A session
can take this one - it rests on what this repository already does with tier, not
on what the project wants.

**Decided 2026-10-01: no decision changes, so nothing is built.** Closed unbuilt
on the brief's own test, by the session the coordinator split the session-cost
items to.

*What reads tier.* Exactly one thing: `Item.model_guidance` in
`subprojects/docket/src/docket/model.py`, which marks `safety`/`science`-tagged
items and open design decisions "strongest model" in the digest and in `plan`.
It is advice going in, and choosing the model stays the owner's lever
(`docs/maintainer.md`). `delegability()` decides what a cheaper worker may take,
and its proof is the item's `verify:` command, which passes or fails the same
whichever model wrote the diff. No rule, check or review step reads tier coming
out. So the one decision a downgrade could change would be "re-review work a
strongest-model item got from a weaker model", and the project has no such
step: `safety`/`science` work is held by its regression tests, `verify:` and
the pull request's review, none of which is keyed on the model.

*The count, taken before deciding.* Every session record from 2026-09-17 to
2026-10-01 - 400 sessions, 399 carrying `last_served_model` - read from
`list_sessions` through a subagent. 14 show a served model differing from the
configured one. All 14 also differ in `session_context.model` and carry
`external_metadata.user_switched_model` equal to the new model: owner switches,
which the harness already records, not fallbacks. Fallbacks visible at the
session level: **0 of 399**. Not counted: a fallback on a middle turn that
recovered before the last one, which only `list_events` (`model_fallback`
notices) or the session's own transcript would show.

*Why no standing instrument is owed even so.* The fact is not lost when it
matters. Archived sessions still carry `configured_model`,
`last_served_model` and `user_switched_model`, and a session's own transcript
records the model behind every assistant message (`message.model`, the file
`tools/context_reading.py` already reads). A specific doubt about a specific
past session can be answered from those on demand, at the cost of one read,
with no model id ever entering a pushed artifact.

*What would reopen it.* A decision that consumes tier coming out - for
instance, a rule that work closing a `safety`- or `science`-classed item is
re-reviewed when a weaker model served it. With that rule in place, a
`model_fallback` notice on any session that closed such an item would be the
number worth counting. Without it, recording fallbacks feeds nothing.
