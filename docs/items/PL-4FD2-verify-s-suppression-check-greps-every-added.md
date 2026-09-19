---
id: PL-4FD2
title: verify's suppression check greps every added line for the three marker substrings it knows, so prose in a docstring, an item brief or a README explaining why a suppression was not used refuses the branch
status: untriaged
feature: git-silence-channel
added: 2026-09-19
---

**Problem.** verify's suppression check greps every added line for the three marker substrings it knows, so prose in a docstring, an item brief or a README explaining why a suppression was not used refuses the branch

**Found closing `PL-Q9Z1`, 2026-09-19, and it refused that branch twice.**
`SUPPRESSIONS` in `subprojects/docket/src/docket/verify.py:51` is a tuple of
substrings, and `_added` feeds it every added line of the diff whatever file it
came from:

```python
suppressed = [line.strip() for _, line in added if any(s in line for s in SUPPRESSIONS)]
```

So a sentence *explaining* why a suppression was not used trips it. On
`PL-Q9Z1` the refusing lines were a docstring paragraph, an item brief and a
`README.md` paragraph, all saying the same thing: that a breach is recorded as
an assertion rather than marked expected-to-fail. The branch added no
suppression at all.

**Why it is worth fixing rather than writing around.** The workaround is to
avoid the word, which is what that branch did - and a check whose remedy is
"do not name the thing in prose" makes the documentation worse in exactly the
place a reader most needs it, since the reason a suppression was *refused* is
what stops the next session adding one. `CLAUDE.md`'s retirement test is the
frame: a check that fires without changing a decision costs attention forever
and trains a session to skim the block where a real finding is printed.

**Two things to weigh, not one.** The narrow fix is to apply the check only to
files a linter would read - `.py`, and whatever else grows a suppression
syntax - which leaves a Python *docstring* still tripping it. The fuller one is
to read the added line as code rather than as text: a marker is a decorator, a
call, or a trailing inline type-ignore comment, and none of those is a sentence
with the token inside backticks. `tools/doc_check.py`'s `candidates` already
draws a version of this line - it reports a term that is also an ordinary word
only where a line marks it as code - so the precedent is in the tree.

**Done when** a branch adding prose that names a suppression, in a docstring or
in Markdown, passes `bin/docket verify`, and one that adds a real marker still
fails; and a test drives both.

**This brief does not name the three tokens, and that is the finding rather than
an oversight.** Writing any of them out refuses the branch carrying this item,
so the report of the defect is refused by the defect. Read that as the strongest
available argument for fixing it: an item nobody can state plainly is one the
next session restates worse. `subprojects/docket/src/docket/verify.py:51` holds
the tuple, and reading it there is the substitute for spelling it here.
