# Write plainly

**Resident, with no `paths:`.** It applies whenever a session writes prose. A
path scope would miss item briefs, commit messages, pull request bodies and
replies, because no read comes before them. The project owner asked for this
rule on 2026-10-17, and `PL-8ZTQ` has the measurement and the sources behind
each point.

Write all prose that a person will read in plain English: docstrings, comments,
error messages, documents, rules, item briefs, commit messages, pull request
titles and bodies, replies, and every question or review request sent to the
project owner, including each field of the line `bin/docket arm` prints. In
those, say what changes for the owner or a learner, and never name a test,
check or tool by its internal name (project owner, 2026-11-02, `PL-BGN1`).
Write for a careful newcomer, someone who knows anesthesia or Python but has
not read this repository. They should understand each sentence the first time
they read it.

1. **Write whole sentences.** Keep the small words that show how a sentence
   fits together: "a" and "the", "that", "which" and "who", and the verb.
   Start a docstring or a paragraph with a sentence, not a phrase and a colon.
2. **Do not stack clauses.** "Each entry the plan was not read whole at" makes
   the reader work out where each clause ends. Write "Each entry at which the
   plan was not read in full."
3. **Use words in their everyday sense.** Prose here has drifted into private
   senses that a newcomer cannot guess. Write "returns" and "result", not
   "answers" and "answer"; "review", not "read" as a noun; "treats as", not
   "reads as"; "enforces", not "holds"; "still applies", not "stands";
   "applies to", not "reaches"; "less than", not "under"; and "bypasses", not
   "writes past". Name the rule or the exception you mean instead of calling it
   a "floor" or a "door". When the project needs a term of its own, define it
   where it first appears.
4. **Make one point per sentence.** Put the subject and its verb early and
   close together. When a sentence needs a semicolon, a dash or a second
   parenthesis, split it. Most sentences should be under 25 words.
5. **State the reason in words.** An item id, a pull request number or a
   section name can follow as a pointer, but the sentence must make sense
   without it.
6. **Say who does what.** Make each "it", "this" and "that" point at a noun the
   reader can find.
7. **Plain is not longer.** Say each thing once, where the reader needs it.
   Cut words that add nothing, but keep every fact. A unit, a value, an
   equation, a condition, an exception and a citation are not padding.
8. **Read it aloud.** If you would not say it that way to a colleague, rewrite
   it.

**Five patterns that make prose read as machine-written.** The points above
catch prose that is too compressed. These five catch the opposite failure:
padding that sounds careful and adds nothing. The project owner judged
`docs/MODEL.md` to read "like the worst kind of AI slop" on 2026-11-02 because
of them (`PL-ZT47`).

1. **A tautological aside.** A clause restates what its sentence already
   says: "The naming is Hendrickx and De Wolf's, which is the field's naming."
   Delete it. Where it carries a real fact, make that fact a sentence.
2. **A contrast nobody claimed.** "X, not Y" and "rather than Y" reject an
   option no reader proposed. State the positive claim. Keep a contrast only
   where a reader would otherwise assume Y.
3. **Narration about the text itself.** The sentence describes how the
   document records, sources or decides something, instead of the subject:
   "it is recorded at that depth", "the pages above are what the citation is
   being used for". Give the citation with its page numbers and stop. Who
   supplied a source, and how a choice was reached, belong in the item file.
4. **A defensive scope statement.** The sentence says what is not relied on,
   against an objection nobody raised: "no page beyond them is relied on
   here". Delete it. Where a reader would plausibly assume a source was used,
   say once that it was not, as a limitation.
5. **A table cell or paragraph that has grown into an essay.** Prose ordinals
   ("First", "Second" through "Sixth") or several separate points inside one
   table cell mean the content wanted to be a list. Move it to a numbered list
   or a short section, and leave the cell one sentence and a pointer.

Before, from `docs/MODEL.md` on 2026-11-02: "The naming is Hendrickx and De
Wolf's, which is the field's naming. They set out the gas-phase cascade and the
symbols F_D, F_I and F_A on pp. 161-162. [...] The project owner supplied this
source, and it is recorded at that depth. The pages above are what the
citation is being used for, and no page beyond them is relied on here."

After: "Symbols and the gas-phase cascade (F_D, F_I, F_A) follow Hendrickx and
De Wolf (pp. 161-162)." The full citation follows unchanged, and the last two
sentences go.

**A pull request title names the change plainly and briefly.** The title
becomes the squash commit's subject, the one line of `main`'s history that a
reader sees for the change. After the item ids that the `pr-title` check
requires, write a short phrase rather than a whole sentence: what the change
does, to what, and the reason when it fits. Use names a reader of the
repository already knows, such as a CI job, a check or a panel, not a term
coined while building the change. Give each number the thing it counts. Do not
describe the hoped-for effect in loose words instead of the change. When a
branch closes several items, name what they change together.

**Match the code around you, not its prose.** Copy the structure, naming and
idiom of the code you are working in. Much of the existing prose here breaks
the points above, so do not copy its sentences. Write each sentence you add or
change plainly, even when the text around it is dense. Rewriting sentences you
did not need to touch is work for its own item, in the `prose-quality`
feature.

This rule decides how a sentence is worded. It does not decide what a text
must contain or the order of a reply. The safety-critical standard in
`CLAUDE.md` and `.claude/rules/sources-and-docstrings.md` decide which facts a
docstring, an error message or a displayed value must give, and
`.claude/rules/instruction-writing.md` decides the shape of a reply. Code,
commands, paths and quoted output stay exactly as they are.

## Three examples from this repository

Before: "Refuse a volume or tissue:gas coefficient whose capacity is under the
agent held."

After: "Reject a volume or tissue:gas partition coefficient that would make the
tissue's capacity less than the amount of agent it already holds."

Before: "The fresh gas admitted over the step, and as much circuit gas
exhausted. In circuit volumes it is the step in time constants, dt/tau, formed
without the time constant, which overflows to `inf` below about 2e-306 L/min in
a 6 L circuit."

After: "`admitted_gas_l` is the volume of fresh gas that enters the circuit
during the step. The same volume of circuit gas leaves through the exhaust.
Dividing `admitted_gas_l` by the circuit volume gives the step's length in time
constants, dt/tau. The code does not compute tau first, because tau overflows
to `inf` when the fresh gas flow is below about 2e-306 L/min in a 6 L circuit."

The project owner judged three versions of one pull request title, on
`#1523`, on 2026-10-17:

- Too cryptic: "PL-ZWQS: give the first CI part 2 of every 5 ordinary tests".
  A reader cannot tell what a "CI part" or an "ordinary test" is, or what the
  2 and the 5 count.
- Too conversational: "PL-ZWQS: make CI's two test jobs finish at about the
  same time". It describes a hoped-for effect and does not say what changed.
- Plain: "PL-ZWQS: rebalance the CI test split to offset part 1's lint steps".
  It names the change, what it changes and why.
