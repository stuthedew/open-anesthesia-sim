---
id: PL-B11M
title: Detect a silent model fallback: last_served_model can differ from the configured model with nothing recording it
status: untriaged
added: 2026-09-16
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
the repository's commit convention should start naming the model. It should not
— the argument is on that thread and the convention is unchanged — and the
decisive reason is what produced this item: a trailer the session writes itself
would record the *configured* id, so it would be confidently wrong at the one
moment the information mattered. That is the failure `CLAUDE.md`'s
safety-critical standard names as preferring an obvious failure state to a
plausible-looking value, arriving in provenance rather than in a clinical
number. So the gap is real; a commit trailer is simply the wrong instrument for
it, because the fact lives harness-side and per turn.

**Not yet designed, and the gate it has to clear first.** `CLAUDE.md`
§ "Prefer deterministic tooling over repeated model work" asks whether a
mechanism will genuinely run again and says the answer is no where the benefit
is unclear. It is unclear here: nobody has yet named a decision that would
change on learning a past session was downgraded. Answer that before building
anything. If it cannot be answered, the honest outcome is to close this
unbuilt — which is a legitimate result, not a loss.
