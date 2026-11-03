Review the prose below for the readers that each unit names. Each unit's
header lists them, with what each knows, what each does not know, and what
each will do with the text. Hold each unit to
.claude/rules/plain-writing.md, which you already have. Do not open a file
or run a tool. Everything you need is below, and you have one reply.

You know this field's vocabulary, and the reader may not, so do not judge
whether a sentence is clear to you. For each numbered unit and each of its
readers, return four things:

1. Each word, symbol or number that this reader would not know, judged
   against their "Does not know" line. Quote each one.
2. What this reader would take from the unit, in at most two sentences.
3. Whether the unit lets this reader do what their "Will" line says. If it
   does not, say what is missing.
4. Each sentence that your answer to 2 does not need.

Then write "[N] keep" when 1 and 4 are empty and the answer to 3 is yes.
Otherwise write "[N] rewrite" and then, in a fenced block, the new text for
the rows marked ">", exactly as they would stand in the file: the same
indentation, the same comment markers, quotes or Markdown, and lines no
longer than 100 characters. A table row stays on one line, however long.

Write the new text for the reader that the unit serves where it stands, as
.claude/rules/plain-writing.md places each fact. Carry only the facts that
this reader's takeaway needs, and rewrite only the sentences that need it.
Move each other fact to the place where its own reader will look for it,
such as the section's note for developers or the item, and name that place.
Where a term needs explaining, use a plainer word rather than a definition.
Restate a number in the reader's form only where the reader needs that
number, with the same value, such as 4e-4 as 0.04%. The new text is no
longer than the rows it replaces, counted in words. Under the block, list
each move and each restatement on a line of its own.

Keep every fact, in the new text or in the place you name for it. In the
new text, keep each unit, value, condition, exception, identifier in
backticks, item id and citation that stays. Change no code. Where you cannot
tell what a sentence means, say so in one line rather than guessing.
