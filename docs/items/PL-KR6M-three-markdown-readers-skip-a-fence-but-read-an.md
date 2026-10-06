---
id: PL-KR6M
title: Three Markdown readers skip a fence but read an indented code block as prose - docket.instructions.parse, which reads an HTML block too, docket.roadmap's LITERAL_BLOCKS, and doc_check's section-mark citation readers - so a template date in one is a dated assertion, a queue-items run in one declares, and a quoted title in one is refused as a missing section; latent
status: untriaged
added: 2026-10-06
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

**Generator check.** Not a member of `PL-R417`: each reader finds a block's
extent correctly and then reads the wrong kinds of block, which is the class
`PL-XGYH` fixed for the math check.

**Done when.** The three readers pass `markdown.PROSE`, or add `markdown.CODE`
to what they skip, pinned by a test for each with an indented code block, and
one for `instructions.parse` with an HTML block.
