# Write plainly

**Resident, with no `paths:`.** It applies whenever a session writes prose. A
path scope would miss item briefs, commit messages, pull request bodies and
replies, because no read comes before them. The project owner asked for this
rule on 2026-10-17, and `PL-8ZTQ` has the measurement and the sources behind
each point.

Write all prose that a person will read in plain English: docstrings, comments,
error messages, documents, rules, item briefs, commit messages, pull request
bodies and replies. Write for a careful newcomer, someone who knows anesthesia
or Python but has not read this repository. They should understand each
sentence the first time they read it.

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

## Two examples from this repository

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
