---
id: PL-13PB
title: docs/maintainer.md tells the owner to use 'the strongest available model' and names no model, so bin/docket next's per-item strongest-model flag cannot be resolved by anyone reading it
priority: P2
effort: S
status: done
classes: docs, defect
feature: model-capability-routing
touches: docs/maintainer.md
added: 2026-09-19
closed: 2026-09-19
verify: grep -qE 'strongest available model is' docs/maintainer.md
---

**Problem.** docs/maintainer.md tells the owner to use 'the strongest available model' and names no model, so bin/docket next's per-item strongest-model flag cannot be resolved by anyone reading it

**Why it matters.** The phrase is load-bearing and unresolvable. `bin/docket
next` prints `use your strongest model` per item — `plan.py:181`, from
`model.py`'s `model_guidance` — on every item that is `safety`- or
`science`-classed or whose next step is a decision. That is both current `P1`
items and every `needs-decision` item in the store. `docs/maintainer.md` is
where `CLAUDE.md` routes the model question ("Which model a session runs is the
owner's lever rather than a session's, so it lives in `docs/maintainer.md`"),
and it names no model anywhere in § "Match model capability to the work".

So a session reading the flag has nothing to resolve it against, and the
default behaviour is to assume whatever it is already running satisfies the
instruction. Observed 2026-09-19: `PL-G424` (the apparatus-citation-drift
generator head, root cause of 21 items, flagged strongest-model) was started on
`claude-opus-5` while `PL-LSR0` ran on `claude-fable-5-1` — the project owner
confirmed the same day that Fable is the stronger of the two. Neither session
could have known from the repository.

**This is the flag being silently wrong rather than merely vague**, which is
`CLAUDE.md`'s first compounding-friction test: a check passes — the item carries
its guidance, the session reads it — while the guarantee it stands for is void.

**Scope note: a dated assertion, not a permanent one.** Whichever model is named
will stop being the strongest, so per `.claude/rules/expert-review.md` § "Say
what would falsify it" this is an *instance* and must carry its date and what
would falsify it — a new model release. Write it as
"as of DATE, the strongest available model is X", not as a rule. The
alternative considered and rejected: naming no model and instead telling the
owner to check the current lineup each time, which is what the file effectively
does now and what produced the observation above.

**Related, not duplicated.** `PL-B11M` (detect a silent model fallback:
`last_served_model` can differ from the configured model) is the *runtime*
half — a session learning what it is actually being served. This is the
*reference* half — anyone learning what the target is. Neither subsumes the
other, and together they would let a session on a strongest-model item say so
rather than assume.

**Done when.** `docs/maintainer.md` § "Match model capability to the work"
names the current strongest model with the date it was true and what would
falsify it, and a session reading `use your strongest model` from `bin/docket
next` has one place to resolve it.
