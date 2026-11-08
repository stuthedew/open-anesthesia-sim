---
id: PL-13PB
title: docs/maintainer.md tells the owner to use 'the strongest available model' and names no model, so bin/docket next's per-item strongest-model flag cannot be resolved by anyone reading it
priority: P2
effort: S
status: done
classes: docs, defect
feature: model-capability-routing
milestone: v0.4.31
touches: docs/maintainer.md
added: 2026-09-19
closed: 2026-09-19
pr: 733
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

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground".

> **Two more on the model-capability reference, 2026-09-19.** `PL-13PB` records that `docs/maintainer.md` names no model behind "the strongest available model". So nobody reading that file can resolve the per-item strongest-model flag that `bin/docket next` shows. `PL-V8QG` records that the same file recommends `opusplan` as the default strong/cheap split. That names the wrong family if the strongest model is not an Opus. Both were captured that day, and both are `P2`. Neither is `safety` or `science`, and both sit wholly in the workflow lane.

> They are deferred rather than admitted, even though the flag they undermine fires on `safety`- and `science`-classed items. The reason is that they fix the *reference* a human reads when choosing a model, not any code path that produces a clinical value. `CLAUDE.md`'s safety-critical standard applies to the value and its presentation. The maintainer also reviews every safety-critical diff, whatever model drafted it. That backstop is what makes these items safe to defer. The observation that prompted them was that `PL-G424` started on a weaker model than `PL-LSR0` while both carried the flag. That cost nothing that a gate entry would have prevented.
