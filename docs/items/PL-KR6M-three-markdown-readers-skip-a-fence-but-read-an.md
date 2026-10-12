---
id: PL-KR6M
title: Three Markdown readers skip a fence but read an indented code block as prose - docket.instructions.parse, which reads an HTML block too, docket.roadmap's LITERAL_BLOCKS, and doc_check's section-mark citation readers - so a template date in one is a dated assertion, a queue-items run in one declares, and a quoted title in one is refused as a missing section; latent
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/instructions.py, tools/doc_check.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/tests/test_instructions.py, tests/unit/test_doc_check.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-12 triage in workflow group two
added: 2026-10-06
payoff: A worked example in an indented code block or an HTML comment is read as the literal it is - never as a dated rule, an entry's words or a missing section citation
verify: grep -q 'def test_a_date_in_an_indented_code_block_or_an_html_block_dates_nothing' subprojects/docket/tests/test_instructions.py && grep -q 'def test_an_indented_code_block_is_no_part_of_an_entrys_text' subprojects/docket/tests/test_roadmap.py && grep -q 'def test_a_section_cited_in_an_indented_code_block_or_a_comment_is_not_held' tests/unit/test_doc_check.py
root-cause-of: PL-2B0B, PL-MPJL, PL-XGYH
generator: spent - since PL-XGYH, met live on 2026-09-25 and fixed the next day, every member was found by a sweep for a form no tracked file holds and none was met in use, PL-R417's reading of spent; this item's fix moves its three readers onto markdown.PROSE, retiring roadmap's own list of literal kinds, and PL-2B0B stays open as an ordinary item; a member later found live reopens the head
misread: Which Markdown blocks hold a literal rather than prose a reader may judge
---

**Problem.** Three Markdown readers skip a fence but read an indented code block as prose - docket.instructions.parse, which reads an HTML block too, docket.roadmap's LITERAL_BLOCKS, and doc_check's section-mark citation readers - so a template date in one is a dated assertion, a queue-items run in one declares, and a quoted title in one is refused as a missing section; latent

**Found 2026-10-06 in `PL-R417`'s closing sweep** (link 19). `docket.markdown`
reads an indented code block (CommonMark 0.31.2 § 4.4) and an HTML block
(§ 4.6) as kinds of their own, and `PROSE` is the set a reader judging prose is
meant to pass to `statement_lines`. Three readers leave them in:
`instructions.parse` calls `statement_lines` with no `kinds`, though its
docstring skips fences because a worked example is no claim about the world;
`docket.roadmap`'s `LITERAL_BLOCKS` holds the fence and HTML kinds but not
`markdown.CODE`, so `list_entries` folds an indented code block into an entry's
text; and `check_citations`' readers of a section mark followed by a quoted
title blank fences only.

**Reproduced 2026-10-06** on `main` at `a76cbf67`, under python3 3.11.15,
against markdown-it-py 4.2.0, which reads each indented block below as a code
block:

```text
A sentence (project owner, 2026-09-01) in prose.

    Template: write the date as 2026-01-02 here.

<div>
A date 2026-03-04 inside an HTML block.
</div>

- Keep the model pure (queue item PL-F1F1).

      **literal** (queue item PL-F2F2)
```

`instructions.parse` returned the indented line and the HTML block as dated
assertions beside the prose sentence, where a fenced copy of either is skipped;
`own_scope_ids` and `_scope_entries` declared `PL-F2F2` from a Required scope
subsection holding the last two lines; and a `README.md` whose indented code
block holds a section mark and a quoted title was refused for citing a section
no documentation file has, where a fenced copy passes. Latent: no tracked
instruction file holds a date in either block, and neither `ROADMAP.md` nor any
document holds an indented code block these readers would misread.

**Re-confirmed 2026-10-11** on `main` at `16a20a4f`, in part.
`instructions.parse` still returns the indented line and the HTML block as
dated assertions beside the prose sentence, and `check_citations` still
refuses a section mark and quoted title inside an indented code block or an
HTML comment as a missing section, where a fenced copy passes. The roadmap
consequence is gone: `_scope_entries` now reads ids from `markdown.PROSE`
statements, so `own_scope_ids` is `PL-F1F1` alone. `LITERAL_BLOCKS` still
omits `markdown.CODE`, so the entry's `text` still folds the indented line
in.

**Re-confirmed 2026-10-12** on `main` at `9361765d`, under python3 3.13.16, with
the sample above: `instructions.parse` returns lines 3 and 6 as dated
assertions beside line 1; the `Required scope` entry's `text` ends `**literal**
(queue item PL-F2F2)` while its ids are `PL-F1F1` alone; and `check_citations`
refuses a section mark and quoted title in an indented code block and in an
HTML comment as sections no documentation file has.

**Why it matters.** Each reader answers from text no rendered page shows, and
each answer is one a session acts on. `docket.instructions` dates a rule for
the grooming audit, so a worked example's date in an indented block or a
comment would put an assertion in the report that nobody can honestly clear -
the reason its docstring gives for skipping a fence. An entry's `text` is what
`tools/doc_check.py` reads for a scope entry's exclusion words and quotes in its
errors, so a literal there is read as the entry's words. And a section citation
in a code example or a comment is refused as missing, so a correct document
fails `make check`, the false refusal `PL-XGYH` was in the math check.

**Generator check.** Not a member of `PL-R417`: each reader finds a block's
extent correctly and then reads the wrong kinds of block, which is the class
`PL-XGYH` fixed for the math check. This item is the head of that fact, settled
at triage on 2026-10-12, below.

**Done when.** The three readers pass `markdown.PROSE`, or add `markdown.CODE`
to what they skip, pinned by a test for each with an indented code block, and
one for `instructions.parse` with an HTML block.

[superseded 2026-10-12: settled at triage as a `spent` head on this item, below]
**Generator question, open at the 2026-10-11 triage pass; left untriaged for it.**
`PL-KR6M`, `PL-2B0B`, `PL-MPJL` and the closed `PL-XGYH` misread one fact no
head's `misread:` states: which Markdown blocks hold a literal (fence, indented
code, HTML block) rather than prose a reader may judge. `markdown.PROSE` holds it
once and `markdown.statement_lines(kinds=None)` and `roadmap.LITERAL_BLOCKS` read
past it. Two readings were put by the delegated agents: a `live` head on this item
(new members on 09-25, 10-06 and twice on 10-10), or `spent` on `PL-R417`'s
precedent, since every open member is latent and was found by a sweep, not by a
tracked file. `PL-XGYH` sits under `PL-GPJ7`, so a third reading is three
post-close instances of that head's fact. **Leaning: record it here as a `spent`
head**, on `PL-R417`'s reasoning; settle it before triaging this item. `PL-2B0B`
also has a design half: `_statement_spans` reads spans in indented code and HTML
blocks on purpose, as it reads a fence's.

**Settled at triage, 2026-10-12: a `spent` head on this item.** The fact is
which Markdown blocks hold a literal rather than prose a reader may judge, and
no head's `misread:` states it (`bin/docket generators --misread`, read
2026-10-12). Not `PL-GPJ7`'s fact, which is whether a sentence makes the claim
a gate checks; these readers misread which block holds the sentence. `spent` on
`PL-R417`'s reading of the word, the owner's answer of 2026-10-10: since
`PL-XGYH`, which was met live on 2026-09-25 and fixed the next day, every
member - this item, `PL-MPJL` and `PL-2B0B` - was found by a sweep for a form
no tracked file holds, and none was met in use. The fix recorded here makes the
three readers read the record `markdown.PROSE` already is: `roadmap` keeps the
lines of a prose block rather than skipping its own list of literal kinds, the
second spelling that left `markdown.CODE` out, and `instructions.parse` and
`check_citations`' two section readers pass `PROSE`. `PL-2B0B` stays open as
an ordinary item for `doc_check`'s span, marker and math readers and its design
half, and a member later found live reopens the head. Settled here rather than
put to the owner: the reading follows the owner's own for `PL-R417`, and a
`spent` head ranks on its band, so nothing about what is worked first changes.
