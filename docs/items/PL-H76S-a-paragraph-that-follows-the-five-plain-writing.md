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

**The third failure: shorter, and still no reason a developer could use.**
At 20:20Z the session posted a version cut from 21 lines to 12:

> **The release check, and why it allows 0.5%.** The model advances in fixed
> steps of 0.1 s, and a shorter step should give almost the same result.
> Before each release, a test reruns the first minute of the default
> sevoflurane induction with steps of 0.1 s, 0.05 s and 0.025 s. Each run's
> alveolar, vessel-rich and mixed-venous concentrations must be within 0.5% of
> the run with the next shorter step. The 0.5% was set for the simulator's
> earlier calculation method, at about ten times the 0.04% alveolar
> difference that method showed. The current method's runs agree to better
> than one part in a trillion (measured 2026-10-03), so the much tighter
> limits above are the ones that would catch a real error. A compartment that
> holds almost no agent also passes if its two values differ by less than
> 0.000001 vol%, because there a tiny difference is a large percentage.

The owner's words: "I guess it's overly verbose and I still struggle to
understand the why behind it or if I am a dev or someone who forked the
project, how I would use this info to modify these values for a particular
goal" (project owner, 2026-11-02, 20:30Z, on #1950's thread). This names a
second reader of `docs/MODEL.md`, a developer or someone who forked the
project. That reader needs to know why a value is what it is and what changing
it would do, and no step in the process names them.

**What the versions show together.** The coordinator collected all five
versions of this paragraph, with the owner's reaction to each, in the
project's shared folder (`v0.7.0/pl-zt47/pl-h76s-evidence-release-check-paragraph.md`).
Each version passed `tools/doc_check.py` and carried a prose review record. Two
more facts come from that record:

1. Two versions stated reasons that no record supports. Version 2 said that
   5e-3 is "about ten times" the old method's gap, and the 20:10Z version
   repeated it and said the test runs "before each release". The test comment
   says only that the tolerance predates the exact step, and the test runs on
   every change.
2. The same test also requires each gap to stay below 1e-14 as a fraction. So
   the 0.5% limit cannot change a pass or a fail today. No version said this
   until the fifth, which was not yet read by the owner at 20:40Z. Every
   earlier version explained the number's history, and none said what the
   number does or how to change it.

The fifth version, as evidence and not as a model:

> **Why the step-size check allows 0.5%, and how to change it.**
>
> - **What it checks.** Every change must pass a test that reruns the first
>   minute of the default sevoflurane induction with steps of 0.1 s, 0.05 s
>   and 0.025 s. Each run's alveolar, vessel-rich and mixed-venous
>   concentrations must be within 0.5% of the next run's, or within 1e-8 as a
>   fraction (0.000001 vol%) near zero, where a tiny gap is a large
>   percentage.
> - **Why 0.5%.** No record says how it was chosen. It dates from an earlier,
>   approximate method, whose runs differed by about 0.04% in the alveolar
>   concentration and by more in mixed venous. The same test also requires
>   each gap to stay below 1e-14 as a fraction. Any gap that breaks 0.5% is
>   at least 1e-8, so it breaks 1e-14 too. Today the 0.5% limit changes no
>   outcome.
> - **How to change it.** A fork with an approximate method fails 1e-14 even
>   when its arithmetic is correct: a first-order method shows gaps near
>   1.4e-11. Relax 1e-14, and 0.5% becomes the working check. Set it above
>   the method's own gaps at these steps and below a difference a learner
>   could see. The constants are in `tests/reference/test_sevo_patient.py`.

The owner's words on it: "I like format and first paragraph is reasonable.
Second paragraph structure ok, but how do we not know where the 0.5% came
from? We should absolutely know where that came from. And the last paragraph
is starting to be unintelligible again" (project owner, 2026-11-02, 20:40Z).
Two more facts follow:

1. "No record says how it was chosen" was written without looking. `git log
   -S 5e-3` finds the origin: the value was set with no stated reason in the
   first v0.1.0 build (2026-08-22, `875ba085`), and checked against the old
   method and kept on 2026-08-30 (`60b3bb30`). `docs/MODEL.md` has said since
   that first build that the tolerance "must be documented before tagging",
   and its reason never was. `PL-VXM0`, filed on #1950's branch, holds that
   gap.
2. The part written for a developer slid back into jargon ("first-order
   method", "1.4e-11"). So the developer who wants to change a value needs
   plain words too.

The rewrite of `docs/MODEL.md` paused at 20:42Z, with a sixth version drafted
and not read by the owner. The evidence file holds it.

**Every rewrite quoted in this item is evidence, not a model to copy** (project
owner, 2026-11-02, 20:33Z: "The new text shouldn't be used as an exact model
to follow without thought, just as another example of where we have
shortcomings with our current set up"). That includes the declined proposal's
paragraph below.

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

**The cause.** Four faults combine. Today's failures come from them: the
jargon, the length, a reason that a developer cannot use, and two reasons that
no record supports.

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
   that two models told to act as a student answered reading questions with
   0.97 and 0.99 accuracy, against 0.66 for real students. Limiting what the
   model could use from the text closed most of that gap.
3. **No step asks what the reader needs or what they will do with the text.**
   The plain-language standard's first principle is that readers get what
   they need, and its fourth is that they can use it (ISO 24495-1:2023). The
   plain-writing rule has a step for neither. Its reader is "someone who knows
   anesthesia or Python", so a term that a Python reader knows passes, and no
   document says which of the two reads it. Nothing names the developer who
   wants to change a value, so no paragraph said what the value does or what
   changing it would do. Meanwhile three steps push each figure to stay in
   the paragraph: the rule's point 7, the prose review's "keep each number
   ... exactly as written", and `PL-ZT47`'s step 3 with `tools/model_rewrite.py
   lost`. So the 20:10Z rewrite lost its jargon and kept all its history, at
   268 words, and the 20:20Z cut still gave no reason a developer could act
   on.
4. **Asked for a reason, the writer wrote history, and supplied a reason where
   the history held none.** The owner asked that no number read as a magic
   number. The history was in the items, so each version told how the number
   arose. What the number does was in the test file, and no version read it
   until the fifth. Where no record gave a reason, two versions stated one,
   and the fifth said that no record existed without tracing the value's
   history. No step checks a stated reason against its source:
   `tools/doc_check.py` checks that a cited path exists, and the prose review
   checks wording. Behind this sits a gap in the code itself. The value's
   reason was never recorded, though the specification required it, so every
   writer had to explain a number that had no recorded explanation.

**Recommendation: build these four changes**, as one item each under
`prose-quality`, once the owner agrees.

1. **Name each document's reader in one place.** A table in
   `.claude/rules/plain-writing.md` gives each kind of text its reader, what
   that reader knows, what they do not, and what they will do with the text.
   `docs/MODEL.md` has two readers. The first is a clinician or educator who
   knows anesthesia pharmacology and physiology, does not know numerical
   methods, software terms or e-notation such as "4e-4", and wants to know
   whether to trust a displayed value. The second is a developer, or someone
   who forked the project, who wants to change a value for a goal of their
   own. That reader knows Python and the anesthesia basics, and also does not
   know numerical-methods terms such as "first-order method". A docstring's reader is a Python developer who knows the anesthesia
   basics. `tools/new_prose.py` prints the reader line beside each unit, read
   from the table, so the writer and the reviewer use the same reader. This
   replaces "knows anesthesia or Python".
2. **Decide what the reader needs before choosing words.** Before writing a
   paragraph, the writer states in one sentence what its reader should take
   from it and what they will do with it. Where the text gives a chosen
   value, the part for developers answers three questions: what the value
   does, why it is this number, and what changing it would do. Each answer
   is read from the code or test that uses the value, or from a cited
   record. Where the reason is not at hand, the writer traces the value's
   history first, with `git log -S` and the items. Where the trace finds no
   reason, that is a missing record, not a gap to write around: the writer
   files an item for it, and the text says what the trace found. A fact that
   serves
   none of this goes where its reader is: decision history to the item, and
   numerical detail to a marked note for developers in the same section.
   `docs/MODEL.md` must still hold the numerical method (`CLAUDE.md` §
   "Safety-critical clinical-output standard"), so that detail stays in the
   document. `lost` gains "moved to the note for developers" beside "moved
   to an item". The prose review may then propose moving a fact, saying
   where, and may restate a number in the reader's form, such as 4e-4 as
   0.04%. The writer still rejects any change to a value.
3. **Replace "read as a newcomer" with a takeaway test against the named
   reader.** The reviewer gets each unit and its reader line, and returns
   four things:
   - each word or number that the reader would not know, judged against the
     table's "does not know" list;
   - what this reader would take from the unit, in at most two sentences;
   - whether the unit lets this reader do what the table says they will do,
     such as change a value for a goal of their own;
   - each sentence that the takeaway does not need.

   The writer compares the takeaway with the sentence from step 2. A listed
   term, a mismatch, or a reader who cannot act means a rewrite, and each
   unneeded sentence moves or goes. This is paraphrase testing, the standard
   way of testing plain language with readers (digital.gov), with the
   standard's "usable" principle added as a question. An explicit list of
   what the reader does not know stands in for the persona, because a model
   cannot pretend not to know.
4. **Test the review against the real reader.** The owner is the only
   clinician who reads this text. Each paragraph he rejects is kept in a
   small set beside the review prompt, with his words and the accepted
   rewrite. Whenever the prompt changes, the review is run on the set, and
   it must flag every rejected paragraph. Today's versions start the set.
   This turns his reads into a regression test for the review, so it cannot
   pass again a kind of text he has already rejected.

   The set lives in one folder in the repository beside the review's
   instructions, one short file per entry. Two limits keep it small. First,
   only a miss is added: a paragraph that the review passed and the owner
   then rejected. A rejection that the current review already catches adds
   nothing. Second, the set keeps at most two entries for each kind of
   failure, such as jargon, length, a reason a developer cannot use, or a
   reason with no source. A new miss of a kind already held replaces the
   older entry of that kind. So today's six versions of one paragraph become
   four entries, one for each kind they show, and the set grows only when the
   review fails in a new way. The question was the owner's (project owner,
   2026-11-02, 22:14Z: "Where do the rejected paragraphs go? Seems like that
   could add up over time?").

**Decided in the round.** Three calls have one clearly correct option.

- The blind review brief is unchanged. Readability has one owner, the prose
  review, and two reviewers judging it would disagree with no way to settle
  it.
- `docs/MODEL.md`'s first reader is a clinician or educator, as the owner
  decided on 2026-11-02. Its second, a developer or someone who forked the
  project, comes from the owner's words at 20:30Z.
- Numerical detail moves to a note for developers in `docs/MODEL.md`, not to
  the items, because the specification must hold the numerical method.

**What it costs.** A table in the rule, a longer review prompt and reply, a
comparison step for the writer, and one model run on the set whenever the
prompt changes. None of it is a new plain-writing pattern.

**What it cannot do.** The reviewer stays a model. Only the owner's reads test
a real reader, and change 4 makes each of them count beyond the paragraph it
was about.

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
