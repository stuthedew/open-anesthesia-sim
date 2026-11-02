---
id: PL-H76S
title: A paragraph that follows the five plain-writing patterns and passes both reviews is still unintelligible to a clinician when it uses numerical-methods vocabulary ("operator split", "relative gap", "4e-4"), because no step in drafting, review or audit asks whether the intended reader understands it
priority: P2
effort: S
status: ready
classes: docs
feature: prose-quality
touches: .claude/skills/docket/modes/close-out.md, .claude/rules/plain-writing.md
added: 2026-11-02
payoff: the project's writing and review process produces paragraphs a clinician can follow, so the owner stops finding unreadable text after every review has passed it
not-delegable: finding why the writing process failed is a judgment about how reviews are briefed, which no command can confirm
---

**Problem.** On 2026-11-02 the owner found a paragraph of `docs/MODEL.md`
unintelligible, after the rewrite that produced it had applied the five
plain-writing patterns. The paragraph explains the tolerance that the release
comparison test allows between a run at the normal step and a run at a shorter
step. The session rewriting the required tests (`PL-70B2`, #1950) posted it
for review at 20:02Z, as a reason added so that the tolerance would not read
as a magic number:

> The 5e-3 relative tolerance was chosen when the simulator used the operator
> split. At that time, the split showed a relative gap of 4e-4 in the alveolar
> fraction between steps of 0.1 s and 0.025 s, and 5e-3 is about ten times
> that gap. The tolerance is kept as a coarse check, because with the exact
> step the same comparison gives gaps of about 1.4e-13 relative (measured
> 2026-10-03). The 1e-8 absolute tolerance covers a fraction so close to zero
> that a relative gap means little. For such a fraction, a negligible
> difference still passes.

The owner's words: "this is still unintelligible to a human" (project owner,
2026-11-02, 20:03Z, on #1950's thread), and "was this written with the plain
language guidelines? This is still unintelligible" (project owner,
2026-11-02, 20:04Z).

That paragraph was written after #1950's review passes. The paragraph beside
it, which those passes did read, has the same fault. As it stood on #1950's
pushed branch after its two blind review passes (`4fc015ed`):

> The release comparison tolerance is 5e-3 relative or 1e-8 absolute, and
> meeting either one is enough. It applies to the alveolar, vessel-rich and
> mixed-venous fractions after 60 s of the default sevoflurane wash-in. Under
> the operator split, comparing 0.1 s directly with 0.025 s exceeded the
> tolerance in the mixed-venous fraction alone. That compartment has barely
> begun to fill at 60 s, so the split's gap of 1.4e-6 in fraction between
> those two steps was 0.55% of the mixed-venous fraction. Under the exact
> step, the two runs land about 4e-17 apart there (measured 2026-10-03).

So the failure does not depend on one late paragraph. The drafting rule and
both review passes let this vocabulary through.

**Why it matters.** `docs/MODEL.md` is read by clinicians and educators. A
paragraph they cannot follow hides the model's limits from exactly the reader
the safety-critical standard is written for.

**The owner's answer: no new rule; treat it as a failure of the writing
system.** "That seems like a reactionary rule which I'm not saying is wrong
but seems like more though than a knee jerk rule. But can you not add the
rule, and file an item? This seems like a systems failure in the writing
system" (project owner, 2026-11-02, 20:07Z). A sixth plain-writing pattern
was proposed on a decision card and declined.

**What each step is told today.** These are facts about the current
instructions. They are leads for the design round, not a diagnosis.

1. The drafting rule, `.claude/rules/plain-writing.md`, names the reader as
   "a careful newcomer, someone who knows anesthesia or Python but has not
   read this repository". Its point 7 says that a unit, a value, an equation,
   a condition and a citation are not padding.
2. The prose review in `.claude/skills/docket/modes/close-out.md` step 8 gives
   its reviewer the same reader. It also says "Keep each number, unit, value,
   condition, exception, identifier in backticks, item id and citation
   exactly as written". A reviewer told this cannot turn "4e-4" into "about
   0.04%".
3. The blind review brief in `tools/blind_review.py` says "Do not report
   style, naming, or documentation polish unless it could mislead a reader
   about a clinical value". A paragraph that no clinician can read is
   therefore outside its brief.
4. Each section rewrite of `docs/MODEL.md` must account for every number
   that `tools/model_rewrite.py lost` reports as gone from the text. This
   pushes a writer to keep each figure in the text rather than move it to the
   item that holds the history.
5. No step asks a reader to say back what a paragraph means. The owner is the
   only clinician reader, and the owner's read is the only step that caught
   this.

**Earlier instances of the same failure.** Each of these was fixed by adding
a rule or a review step, and the owner then found the failure again in a new
place: `PL-8ZTQ` (awkward wording, no plain default style), `PL-BZR4` (the
first cut of `docs/MODEL.md`), `PL-ZT47` (`docs/MODEL.md` still read as
machine-written after `PL-BZR4`), `PL-VGDX` (pull request titles in the
building session's own vocabulary) and `PL-BGN1` (owner review requests in
the repository's shorthand). Triage should decide whether this item is the
head of those, recorded as a generator.

**Open question for a design round.** Why do the drafting, review and audit
steps pass prose that a clinician cannot read? Examine who each step is told
the reader is, whether any step reads as that reader rather than checking
patterns and facts, and whether keeping every figure in the text works against
a clinician's understanding. Propose the fix once the cause is known.

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
