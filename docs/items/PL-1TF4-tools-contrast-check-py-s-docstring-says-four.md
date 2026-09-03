---
id: PL-1TF4
title: tools/contrast_check.py's docstring says four known shortfalls where KNOWN_SHORTFALLS holds three
priority: P3
effort: S
status: done
classes: docs
milestone: v0.3.1
touches: tools/contrast_check.py
added: 2026-09-03
closed: 2026-09-03
pr: 249
verify: python3 tools/contrast_check.py && ! grep -q 'Four declared' tools/contrast_check.py
---

**Problem.** The module docstring states "**Four** declared pairs do not meet
their minimum today." `KNOWN_SHORTFALLS` holds three: `ACCENT`/`PANEL`,
`sevoflurane.fill`/`BACKGROUND`, and `ALVEOLAR_COLOR`/`PANEL`. One was fixed
and the prose was not updated with it.

**Why it matters.** Small, and worth fixing for where it sits rather than for
its size: this is the tool whose entire purpose is to stop a colour claim
living in "a comment nobody re-measures", carrying a stale count in its own
header. The number is also the one a reader would use to sanity-check the
output against the source, so a reader who trusts it concludes an entry is
missing from the table.

`tools/doc_check.py` cannot catch it - the marked-prose-value check holds
`docs/` prose to the data files, and this is a tool docstring restating a
constant in the same file.

**Where.** `tools/contrast_check.py`, module docstring, the paragraph
beginning "**Known shortfalls, and why they do not simply fail the build.**"

**Done when.** The docstring states the count `KNOWN_SHORTFALLS` actually
holds, and does not restate a number that a future fix will falsify again -
"the pairs listed in `KNOWN_SHORTFALLS`" says the same thing and cannot go
stale.

**Found.** 2026-09-03, reading the tool while answering the project owner's
question about whether its output nags (`PL-MHQK`).

**Done.** The sentence no longer states a count at all: "The pairs listed in
`KNOWN_SHORTFALLS` do not meet their minimum today." That is what the **Done
when.** above asked for rather than swapping four for three - a restated
number is a second copy of a fact that changes, and it had already gone stale
once. The recorded `verify:` greps for the absence of the old wording and was
watched exiting 1 before the edit.
