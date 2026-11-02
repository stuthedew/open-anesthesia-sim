---
id: PL-H76S
title: A paragraph that follows the five plain-writing patterns and passes both reviews is still unintelligible to a clinician when it uses numerical-methods vocabulary ("operator split", "relative gap", "4e-4"), because no step in drafting, review or audit asks whether the intended reader understands it
priority: P1
effort: L
status: ready
classes: docs
feature: prose-quality
touches: .claude/skills/docket/modes/close-out.md, .claude/rules/plain-writing.md
added: 2026-11-02
payoff: the project's writing and review process produces paragraphs a clinician can follow, so the owner stops finding unreadable text after every review has passed it
not-delegable: finding why the writing process failed is a judgment about how reviews are briefed, which no command can confirm
root-cause-of: PL-8ZTQ, PL-BZR4, PL-ZT47, PL-VGDX, PL-1K5X, PL-FDMJ, PL-TPS7, PL-K7N7
generator: live - the owner found unreadable prose on 2026-11-02 in a section rewrite that had passed the plain-writing rule and its reviews, after eight earlier writing items each added a rule or review step and closed
misread: Whether a paragraph can be understood by the reader it is written for
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

**The second failure ran the opposite way.** The session was told to rewrite
the paragraph for a clinician, and a reviewer read the result as a clinician
would. At 20:10Z it posted this paragraph, which replaced both paragraphs
above:

> **The release check, and why it allows 0.5%.** The simulator moves the
> model forward in fixed time steps, normally 0.1 s long. A shorter step
> should give almost the same result. If it does not, the step is too long.
> Before each release, the test runs the first minute of the default
> sevoflurane induction three times, with steps of 0.1 s, 0.05 s and
> 0.025 s. In each run, the alveolar, vessel-rich and mixed-venous
> concentrations must be within 0.5% of the run with the next shorter step.
> The 0.5% margin was set for the simulator's earlier calculation method.
> With that method, the alveolar concentrations of the 0.1 s and 0.025 s
> runs differed by about 0.04%, so the margin allowed about ten times that
> difference. The check compares each run only with the next shorter step.
> Under the earlier method, a direct comparison of the 0.1 s run with the
> 0.025 s run would have failed. Their mixed-venous concentrations, which
> have barely begun to rise at one minute, differed by 0.55%. With the
> current method, the three runs agree to better than one part in a
> trillion (measured 2026-10-03). So this check is now only a coarse safety
> net. The much tighter limit in the paragraphs above is the one that would
> catch a real error. One extra rule covers a compartment that still holds
> almost no agent. There, a tiny difference can be a large percentage, so a
> percentage means little. Two values for such a compartment also pass if
> they differ by less than 0.000001 vol%, which is one part in a hundred
> million of the gas.

The owner's words: "Way too verbose" (project owner, 2026-11-02, 20:17Z, on
#1950's thread). The jargon was gone, but every figure and the history of the
old method stayed. The same system that keeps every fact in the text turned an
unreadable paragraph into a long one. Any fix has to hold against both
failures: plain words alone produce length when nothing decides which facts a
clinician needs here and which belong in the item.

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
the repository's shorthand).

**Generator check.** A generator whose mechanism is not yet known, recorded
at the owner's word: "Set this as a generator of unknown mechanism requiring
significant effort to understand and fix. Specifically, the generator big
picture being despite a supposed plain language system we are still getting
garbage output that is passing checks. This sounds like a system issue. Not
just a one off" (project owner, 2026-11-02, 20:15Z). It is live because the
failure came back today after the eight items above each closed. The
`misread:` field names the question no step asks, which is the best current
statement of the shared fact. The design round may restate it once the
mechanism is found.

**Open question for a design round.** Why do the drafting, review and audit
steps pass prose that a clinician cannot read? Examine who each step is told
the reader is, whether any step reads as that reader rather than checking
patterns and facts, and whether keeping every figure in the text works against
a clinician's understanding. Propose the fix once the cause is known.

[superseded 2026-11-02: the owner judged the 20:10Z rewrite, which is as long
as this one, "Way too verbose". The design round below gives a shorter target.]
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

**Design round, 2026-11-02.**

**The cause.** Three faults combine. Both of today's failures, the jargon and
the length, come from them.

1. **Every step checks the text, and no step tests a reader.** The drafting
   rule lists patterns. The close-out prose review asks a model to hold the
   text to that rule. The blind review is told to leave documentation alone.
   The measurement that kept the prose review (`PL-J6CK`) had two model raters
   score defect codes such as "dropped small words". Studies of document
   evaluation sort methods into three kinds: text-focused, expert judgment and
   reader-focused (Schriver 1989). Every step here is one of the first two. In
   a direct comparison, technical writers who judged a text "only predicted a
   small proportion of the reader feedback" (de Jong and Lentz 1996). Each of
   the eight member items added another check of the same kind, which is why
   the failure kept coming back.
2. **The reviewer cannot play the reader it is told to be.** Every reviewer is
   a language model that knows numerical methods, so "operator split" and
   "4e-4" are clear to it. Telling it to read "as a careful newcomer" is the
   instruction that fails for human experts too: experts were "resistant to
   debiasing techniques intended to reduce underestimation" of what novices
   find hard (Hinds 1999). For language models, Balog and Bakken (2026) found
   that a model told to act as a student answered reading questions with
   0.97 accuracy, against 0.66 for real students. Limiting what the model
   could use from the text closed most of that gap.
3. **No step asks what the reader needs, and three steps require keeping
   every figure.** The reader is "someone who knows anesthesia or Python", so
   a term that a Python reader knows passes, and no document says which of
   the two reads it. The plain-language standard's first principle is that
   readers get what they need (ISO 24495-1:2023). The plain-writing rule has
   no step for it. Instead, its point 7, the prose review's "keep each number
   ... exactly as written", `PL-ZT47`'s step 3 and `tools/model_rewrite.py
   lost` all push each figure to stay in the paragraph. So the clinician
   rewrite at 20:10Z lost its jargon and kept all its history: 268 words.

**Recommendation: build these four changes**, as one item each under
`prose-quality`, once the owner agrees.

1. **Name each document's reader in one place.** A table in
   `.claude/rules/plain-writing.md` gives each kind of text its reader, what
   that reader knows, and what they do not. For `docs/MODEL.md`: a clinician
   or educator who knows anesthesia pharmacology and physiology, and does not
   know numerical methods, software terms or e-notation such as "4e-4". For a
   docstring: a Python developer who knows the anesthesia basics.
   `tools/new_prose.py` prints the reader line beside each unit, read from the
   table, so the writer and the reviewer use the same reader. This replaces
   "knows anesthesia or Python".
2. **Decide what the reader needs before choosing words.** Before writing a
   paragraph, the writer states in one sentence what its reader should take
   from it. A fact that does not serve that sentence goes where its reader
   is: decision history to the item, and numerical-check detail to a marked
   technical note in the same section. `docs/MODEL.md` must still hold the
   numerical method (`CLAUDE.md` § "Safety-critical clinical-output
   standard"), so that detail stays in the document. `lost` gains "moved to
   the technical note" beside "moved to an item". The prose review may then
   propose moving a fact, saying where, and may restate a number in the
   reader's form, such as 4e-4 as 0.04%. The writer still rejects any change
   to a value.
3. **Replace "read as a newcomer" with a takeaway test against the named
   reader.** The reviewer gets each unit and its reader line. It returns
   three things: each word or number the reader would not know, judged
   against the table's "does not know" list; what this reader would take
   from the unit, in at most two sentences; and each sentence that takeaway
   does not need. The writer compares the takeaway with the sentence from
   step 2. A listed term or a mismatch means a rewrite, and each unneeded
   sentence moves or goes. This is paraphrase testing, the standard way of
   testing plain language with readers (digital.gov). An explicit list of
   what the reader does not know stands in for the persona, because a model
   cannot pretend not to know.
4. **Test the review against the real reader.** The owner is the only
   clinician who reads this text. Each paragraph he rejects is kept in a
   small set beside the review prompt, with his words and the accepted
   rewrite. Whenever the prompt changes, the review is run on the set, and
   it must flag every rejected paragraph. Today's two paragraphs start the
   set. This turns his reads into a regression test for the review, so it
   cannot pass again a kind of text he has already rejected.

**Decided in the round.** Three calls have one clearly correct option.

- The blind review brief is unchanged. Readability has one owner, the prose
  review, and two reviewers judging it would disagree with no way to settle
  it.
- `docs/MODEL.md`'s reader is a clinician or educator. The owner decided on
  2026-11-02 that it should be a document clinicians can read.
- Numerical detail moves to a technical note in `docs/MODEL.md`, not to the
  items, because the specification must hold the numerical method.

**What it costs.** A table in the rule, a longer review prompt and reply, a
comparison step for the writer, and one model run on the set whenever the
prompt changes. None of it is a new plain-writing pattern.

**What the process would produce for the release check.** This is an example
for `PL-70B2`'s section, not a change this item makes. The clinician text:

> **The release check.** Before each release, a test checks that the
> simulator's time step is short enough. It runs the first minute of the
> default sevoflurane induction with steps of 0.1 s, 0.05 s and 0.025 s. Each
> run's alveolar, vessel-rich and mixed-venous concentrations must agree
> within 0.5% with the run at the next shorter step. The current method agrees
> far more closely, so this is a coarse safety net. The tighter test above is
> the one that would catch a real error.

The technical note:

> *Technical note.* The limits are 5e-3 relative or 1e-8 absolute in
> fraction, and either one passes. The absolute limit covers a fraction near
> zero. 5e-3 is about ten times the 4e-4 alveolar gap that the earlier
> operator split showed between 0.1 s and 0.025 s. The exact step now gives
> gaps of about 1.4e-13 (measured 2026-10-03).

The direct 0.1 s against 0.025 s comparison, which failed in the mixed-venous
fraction under the operator split, is history and moves to the item.

**Sources.**

- Schriver KA. Evaluating text quality: the continuum from text-focused to
  reader-focused methods. IEEE Trans Prof Commun. 1989;32(4):238-255.
  https://ieeexplore.ieee.org/abstract/document/44536
- de Jong MDT, Lentz LR. Expert judgements versus reader feedback: a
  comparison of text evaluation techniques. J Tech Writ Commun.
  1996;26(4):507-519. https://doi.org/10.2190/66YB-NJEW-JX8W-YDPR
- de Jong M, Schellens PJ. Reader-focused text evaluation: an overview of
  goals and methods. J Bus Tech Commun. 1997;11(4):402-432.
  https://doi.org/10.1177/1050651997011004003
- Hinds PJ. The curse of expertise: the effects of expertise and debiasing
  methods on predictions of novice performance. J Exp Psychol Appl.
  1999;5(2):205-221. https://doi.org/10.1037/1076-898X.5.2.205
- Balog K, Bakken AM. "Act like a 5th grader" is not enough: bounding
  knowledge in LLM-based user simulators. arXiv:2608.30033, 2026. The author
  list was read from the extracted text and may be incomplete.
  https://arxiv.org/abs/2608.30033
- ISO 24495-1:2023, Plain language, Part 1: Governing principles and
  guidelines. Principles as listed by the International Plain Language
  Federation: https://www.iplfederation.org/the-iso-plain-language-standard-part1
- Paraphrase testing. Digital.gov plain language guide.
  https://digital.gov/guides/plain-language/test/paraphrase-testing

**Done when.** The cause in the writing process is named, and a fix to the
process, not a new pattern in the rule, is proposed to the owner.
