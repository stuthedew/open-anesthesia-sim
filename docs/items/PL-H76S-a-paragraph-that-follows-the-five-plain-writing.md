---
id: PL-H76S
title: A paragraph that follows the five plain-writing patterns is still unintelligible to a clinician when it uses another field's vocabulary ("operator split", "relative tolerance", "4e-4"), because the rule's reader is someone who knows anesthesia or Python
priority: P2
effort: S
status: ready
classes: docs
feature: review-hold
touches: .claude/skills/docket/modes/close-out.md
added: 2026-11-02
payoff: the project's writing and review process produces paragraphs a clinician can follow, so the owner stops finding unreadable text after every review has passed it
not-delegable: finding why the writing process failed is a judgment about how reviews are briefed, which no command can confirm
---

**Problem.** On 2026-11-02 a rewritten paragraph of `docs/MODEL.md` passed the
five plain-writing patterns and was still unintelligible to the owner:

> The 5e-3 relative tolerance was chosen when the simulator used the operator
> split. At that time, the split showed a relative gap of 4e-4 in the alveolar
> fraction between steps of 0.1 s and 0.025 s, and 5e-3 is about ten times
> that gap. [...]

The owner's words (project owner, 2026-11-02, 20:04Z): "was this written with
the plain language guidelines? This is still unintelligible".

The rule's reader is "someone who knows anesthesia or Python". The "or" lets a
writer assume one specialty's vocabulary, and none of the five patterns is
about audience.

**Why it matters.** `docs/MODEL.md` is read by clinicians and educators. A
paragraph they cannot follow hides the model's limits from exactly the reader
the safety-critical standard is written for.

**The owner's answer: no new rule; treat it as a failure of the writing
system.** "That seems like a reactionary rule which I'm not saying is wrong
but seems like more though than a knee jerk rule. But can you not add the
rule, and file an item? This seems like a systems failure in the writing
system" (project owner, 2026-11-02, 20:07Z). A sixth plain-writing pattern
was proposed on a decision card and declined.

So the work is to find why the writing process let this paragraph through.
It passed a fact-checked prose review, blind reviews and the five patterns,
yet no step asked whether the intended reader could follow it. Candidate
causes to examine: who each review is told the reader is, whether any review
reads as that reader rather than checking the patterns, and whether a
rewrite is judged against the original's meaning only and never against a
clinician's understanding. Propose the fix once the cause is known.

A paragraph rewritten for a clinician, from the declined proposal, shows the
target the process should reach:

> The simulator checks its own accuracy by running the same case with a long
> time step and a short one, then comparing the results. They may differ by at
> most 0.5% (5e-3). That limit was set when the simulator used an older,
> approximate method, whose two results differed by about 0.04%, so 0.5% left
> ten times that as headroom. The current method is exact, and the two
> results now agree to about 1 part in 7 trillion (measured 2026-10-03), so
> the limit is now a loose safety net. When a concentration is almost zero, a
> percentage means little, so any difference smaller than 1 part in 100
> million (1e-8) also passes.

**Done when.** The cause in the writing process is named, and a fix to the
process, not a new pattern in the rule, is proposed to the owner.
