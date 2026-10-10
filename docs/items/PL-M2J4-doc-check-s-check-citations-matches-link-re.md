---
id: PL-M2J4
title: doc_check's check_citations matches LINK_RE over the raw document, where its other patterns read the text with fences blanked, so a link-shaped line inside a fence or a multi-line HTML comment is held to the tree as a link and a missing target fails the check; latent
priority: P3
effort: S
status: ready
classes: defect
feature: one-answer
touches: tools/doc_check.py, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-10 triage pass
added: 2026-10-06
payoff: a link-shaped line inside a fence or an HTML comment is never held to the tree as a link
verify: grep -qF '"links, one inside a fence' tests/unit/test_doc_check.py && grep -qF '"links, one inside an HTML comment' tests/unit/test_doc_check.py
---

**Problem.** doc_check's check_citations matches LINK_RE over the raw document, where its other patterns read the text with fences blanked, so a link-shaped line inside a fence or a multi-line HTML comment is held to the tree as a link and a missing target fails the check; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19), auditing the
second half of `tools/doc_check.py`. `check_citations` reads its section and
path patterns over the document with fences blanked and code spans skipped, and
`LINK_RE` over the raw text. A link is inline content of a paragraph or a
heading (CommonMark 0.31.2 § 6.3); a fence (§ 4.5) and an HTML block (§ 4.6),
both of which run over many lines, hold none.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0. A README whose fence holds a link-text-and-target
line naming a file that does not exist (written here with a space between the
two halves so that this brief is not read the same way), and the same line
inside a multi-line HTML comment:

```text
[guide] (docs/guide.md)
```

`check_citations` reported, for both, that the README links to `docs/guide.md`,
which does not exist; markdown-it finds no link in either, and the same line in
a paragraph gives it the one link. The same holds for the line inside a code
span, a fault within one line. Latent: of the 62 `LINK_RE` matches in the
documents, none is inside a literal.

**Why it matters.** `check_citations` fails a document whose link names a missing file, so a link-shaped literal in a fence or a comment fails a correct document.

**Generator check.** A member of `PL-R417`: a reader reads a line inside a
multi-line literal block as a statement of the document, the class of
`PL-T1X0`'s fence half. `PL-KT0H`, a member, fixed `LINK_RE`'s wrapped text,
not where it is read.

**Done when.** `LINK_RE` runs where `check_citations`' other patterns do, over
the prose `docket.markdown` reads with fences, HTML blocks and code spans left
out, pinned by a `links, ` case in `PL-R417`'s guard for the fence and the
comment, failing on today's reader.
